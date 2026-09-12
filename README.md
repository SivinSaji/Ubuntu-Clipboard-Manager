# Lightweight Ubuntu Clipboard Manager

A fast, native GTK3 clipboard manager built specifically for Ubuntu 22.04 LTS and newer (fully Wayland compatible). It runs silently in the background with a top-bar indicator, tracks your clipboard history, and provides a quick-access menu alongside an advanced search and bookmarking UI.

## Features
* **System Tray Integration:** Quick-access dropdown menu for your 15 most recent and pinned items.
* **Pinning & Bookmarking:** Save important snippets (★) so they are never overwritten by the 50-item limit cleanup.
* **Live Search:** Instantly filter your clipboard history as you type.
* **Auto-Close:** The UI automatically dismisses itself when an item is copied to your clipboard.
* **Keyboard Shortcut Ready:** Trigger the advanced UI instantly via custom system shortcuts, completely bypassing the mouse.

## Prerequisites
This app relies on native Ubuntu libraries for rendering the UI and top-bar icon. Install them via your terminal:
```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
