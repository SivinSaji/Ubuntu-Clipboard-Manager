#!/usr/bin/env python3
import gi
import os
import json
import signal
import time

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')

from gi.repository import Gtk, Gdk, GLib
from gi.repository import AyatanaAppIndicator3 as AppIndicator

CONFIG_FILE = os.path.expanduser("~/.config/light_clipboard.json")
MAX_ITEMS = 50


class ClipRow(Gtk.ListBoxRow):
    def __init__(self, item_data, app):
        super().__init__()
        self.item_data = item_data
        self.app = app

        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )
        self.add(hbox)

        clean_text = item_data['text'].replace('\n', ' ')
        display_text = clean_text[:40] + (
            "..." if len(clean_text) > 40 else ""
        )

        self.label = Gtk.Label(label=display_text)
        self.label.set_halign(Gtk.Align.START)
        hbox.pack_start(self.label, True, True, 10)

        self.pin_btn = Gtk.ToggleButton(
            label="★" if item_data['pinned'] else "☆"
        )
        self.pin_btn.set_active(item_data['pinned'])
        self.pin_btn.connect("toggled", self.on_pin_toggled)
        self.pin_btn.set_relief(Gtk.ReliefStyle.NONE)
        hbox.pack_end(self.pin_btn, False, False, 5)

    def on_pin_toggled(self, btn):
        self.item_data['pinned'] = btn.get_active()
        btn.set_label(
            "★" if self.item_data['pinned'] else "☆"
        )
        self.app.save_data()
        self.app.listbox.invalidate_sort()
        self.app.rebuild_menu()


class ClipboardManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Clipboard")

        self.set_default_size(320, 500)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        self.reposition_window()

        vbox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5
        )
        self.add(vbox)

        header = Gtk.Box(spacing=10)

        title = Gtk.Label(
            label="<b>Clipboard Manager</b>",
            use_markup=True
        )

        quit_btn = Gtk.Button(label="×")
        quit_btn.set_relief(Gtk.ReliefStyle.NONE)
        quit_btn.connect(
            "clicked",
            lambda w: self.hide()
        )

        header.pack_start(title, False, False, 10)
        header.pack_end(quit_btn, False, False, 5)
        vbox.pack_start(header, False, False, 5)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(
            "Search clipboard..."
        )
        self.search_entry.connect(
            "search-changed",
            self.on_search_changed
        )
        vbox.pack_start(
            self.search_entry,
            False,
            False,
            5
        )

        self.listbox = Gtk.ListBox()
        self.listbox.set_filter_func(self.filter_func)
        self.listbox.set_sort_func(self.sort_func)
        self.listbox.connect(
            "row-activated",
            self.on_row_activated
        )

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(
            Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC
        )
        scrolled.add(self.listbox)
        vbox.pack_start(
            scrolled,
            True,
            True,
            0
        )

        self.history = []
        self.last_text = ""

        self.indicator = AppIndicator.Indicator.new(
            "lightweight-clipboard",
            "edit-paste",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )

        self.indicator.set_status(
            AppIndicator.IndicatorStatus.ACTIVE
        )

        self.load_data()
        self.rebuild_menu()

        self.clipboard = Gtk.Clipboard.get(
            Gdk.SELECTION_CLIPBOARD
        )

        self.clipboard.connect(
            "owner-change",
            self.on_clipboard_change
        )

        self.connect(
            "delete-event",
            self.on_delete_event
        )

        GLib.unix_signal_add(
            GLib.PRIORITY_DEFAULT,
            signal.SIGUSR1,
            self.on_sigusr1
        )

    def on_sigusr1(self):
        self.toggle_window(None)
        return True

    def rebuild_menu(self):
        new_menu = Gtk.Menu()

        item_show = Gtk.MenuItem(
            label="🔍 Search & Bookmarks..."
        )

        item_show.connect(
            "activate",
            self.toggle_window
        )

        new_menu.append(item_show)
        new_menu.append(Gtk.SeparatorMenuItem())

        display_items = sorted(
            self.history,
            key=lambda x: (
                x.get('pinned', False),
                x.get('time', 0)
            ),
            reverse=True
        )

        for item in display_items[:15]:
            clean_text = item['text'].replace('\n', ' ')
            display_text = clean_text[:40] + (
                "..." if len(clean_text) > 40 else ""
            )

            if item.get('pinned'):
                display_text = "★ " + display_text

            menu_item = Gtk.MenuItem(
                label=display_text
            )

            menu_item.connect(
                "activate",
                self.on_tray_item_clicked,
                item['text']
            )

            new_menu.append(menu_item)

        new_menu.show_all()
        self.indicator.set_menu(new_menu)

    def on_tray_item_clicked(self, widget, text):
        self.last_text = text
        self.clipboard.set_text(text, -1)

    def reposition_window(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()

        if monitor is None:
            monitor = display.get_monitor(0)

        if monitor is not None:
            geometry = monitor.get_geometry()
            self.move(
                geometry.width - 330,
                40
            )
        else:
            self.move(1000, 40)

    def toggle_window(self, widget):
        if self.is_visible():
            self.hide()
        else:
            self.reposition_window()
            self.show_all()
            self.present()
            self.search_entry.grab_focus()

    def on_delete_event(self, widget, event):
        self.hide()
        return True

    def load_data(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

        now = time.time()

        for i, item in enumerate(
            reversed(self.history)
        ):
            if 'time' not in item:
                item['time'] = (
                    now -
                    (len(self.history) - i)
                )

        for item in self.history:
            self.listbox.add(
                ClipRow(item, self)
            )

    def save_data(self):
        os.makedirs(
            os.path.dirname(CONFIG_FILE),
            exist_ok=True
        )

        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.history, f)
            
        # Force strict read/write permissions for the owner only (Security Mitigation)
        os.chmod(CONFIG_FILE, 0o600)

    def on_clipboard_change(
        self,
        clipboard,
        event
    ):
        clipboard.request_text(
            self.on_text_received,
            None
        )

    def on_text_received(
        self,
        clipboard,
        text,
        data
    ):
        if text and text != self.last_text:
            self.last_text = text

            for item in self.history:
                if item['text'] == text:
                    if item.get('pinned'):
                        return
                    else:
                        self.history.remove(item)

                        for child in (
                            self.listbox.get_children()
                        ):
                            if child.item_data == item:
                                self.listbox.remove(child)
                                break

                        break

            new_item = {
                "text": text,
                "pinned": False,
                "time": time.time()
            }

            self.history.insert(0, new_item)

            self.listbox.insert(
                ClipRow(new_item, self),
                0
            )

            if len(self.history) > MAX_ITEMS:
                for item in reversed(self.history):
                    if not item.get('pinned'):
                        self.history.remove(item)

                        for child in (
                            self.listbox.get_children()
                        ):
                            if child.item_data == item:
                                self.listbox.remove(child)
                                break

                        break

            self.save_data()
            self.listbox.invalidate_sort()
            self.rebuild_menu()

            if self.is_visible():
                self.show_all()

    def on_row_activated(
        self,
        listbox,
        row
    ):
        text = row.item_data['text']
        self.last_text = text
        self.clipboard.set_text(text, -1)
        self.hide()

    def on_search_changed(self, entry):
        self.listbox.invalidate_filter()

    def filter_func(self, row):
        search_query = (
            self.search_entry
            .get_text()
            .lower()
        )

        if not search_query:
            return True

        return (
            search_query
            in row.item_data['text'].lower()
        )

    def sort_func(self, row1, row2):
        if (
            row1.item_data.get('pinned')
            and not row2.item_data.get('pinned')
        ):
            return -1

        if (
            not row1.item_data.get('pinned')
            and row2.item_data.get('pinned')
        ):
            return 1

        t1 = row1.item_data.get('time', 0)
        t2 = row2.item_data.get('time', 0)

        if t1 > t2:
            return -1

        if t1 < t2:
            return 1

        return 0


if __name__ == "__main__":
    app = ClipboardManager()
    Gtk.main()
