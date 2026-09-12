
# Lightweight Ubuntu Clipboard Manager

A fast, native GTK3 clipboard manager built specifically for Ubuntu 22.04 LTS and newer, with full Wayland compatibility.

It runs silently in the background with a top-bar indicator, tracks your clipboard history, and provides a quick-access menu along with an advanced search and bookmarking interface.

## Features

- **System Tray Integration:** Quick-access dropdown menu for your 15 most recent and pinned items.
- **Pinning & Bookmarking:** Save important snippets (★) so they are never overwritten by the 50-item cleanup limit.
- **Live Search:** Instantly filter your clipboard history as you type.
- **Auto-Close:** The UI automatically dismisses itself when an item is copied to your clipboard.
- **Keyboard Shortcut Ready:** Trigger the advanced UI instantly using a custom system shortcut.

## Security & Privacy Considerations

Because this application tracks global system clipboard events, users should be aware of how their data is handled locally.

- **Plaintext Storage:** Your clipboard history is saved to `~/.config/light_clipboard.json` in unencrypted text. Passwords, API keys, or other sensitive data copied to the clipboard may therefore be written to disk.
- **Strict File Permissions:** The application automatically enforces `600` (`-rw-------`) permissions on the configuration file so that only the owner account can read or modify it.
- **Password Manager Interference:** This utility does not respect hidden "do not track" clipboard tags used by some password managers, such as Bitwarden or 1Password. Passwords copied to the clipboard may be added to the history.

> **Security recommendation:** Avoid copying passwords, API keys, or other sensitive information when possible. If sensitive information is stored in the clipboard history, remove it from the history or delete the configuration file.

## Step 1: Install Prerequisites

Install the required Ubuntu packages using the following commands:

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1 git
````

These packages provide the Python GTK3 bindings, GTK3 libraries, Ayatana AppIndicator support, and Git.

## Step 2: Clone the Repository

Clone the repository into your home directory:

```bash
cd ~
git clone https://github.com/SivinSaji/lightweight-clipboard-manager.git
cd lightweight-clipboard-manager
```

Make the clipboard manager executable:

```bash
chmod +x clipboard_manager.py
```

> **Note:** Replace `YOUR_USERNAME` with your actual GitHub username, or replace the repository URL with your actual repository URL.

## Step 3: Start and Test

Run the application in the background:

```bash
./clipboard_manager.py &
```

A clipboard icon should appear in the top-right area of your desktop.

If the icon appears, the application is running successfully.

## Step 4: Set Up Autostart

To start the clipboard manager automatically whenever you log in, create the local autostart directory:

```bash
mkdir -p ~/.config/autostart
```

Then create the desktop entry:

```bash
cat <<EOF > ~/.config/autostart/clipboard_manager.desktop
[Desktop Entry]
Type=Application
Exec=$HOME/lightweight-clipboard-manager/clipboard_manager.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Lightweight Clipboard
Comment=Starts the custom clipboard manager
EOF
```

The clipboard manager will now start automatically when you log into Ubuntu.

## Step 5: Set Up a Custom Keyboard Shortcut

Because modern Ubuntu systems using Wayland restrict background keyloggers for security, this application uses the `SIGUSR1` system signal to toggle the advanced search window.

1. Open **Settings**.

2. Select **Keyboard** from the left sidebar.

3. Scroll down to **View and Customize Shortcuts**.

4. Select **Custom Shortcuts**.

5. Click **Add Shortcut** or the **+** button.

6. Enter the following:

   **Name**

   ```text
   Toggle Clipboard
   ```

   **Command**

   ```bash
   pkill -SIGUSR1 -f clipboard_manager.py
   ```

7. Click the shortcut field and press your preferred key combination, for example:

   ```text
   Ctrl + Shift + V
   ```

8. Click **Add**.

## Usage Guide

### Quick Paste

Click the clipboard icon in the top-right of your screen to view your 15 most recent and pinned items.

Click any item to instantly copy it back to your clipboard.

### Search & Advanced UI

Press your custom keyboard shortcut, such as:

```text
Ctrl + Shift + V
```

Alternatively, click **Search & Bookmarks...** from the tray menu.

The advanced window will open with the search bar automatically focused.

### Bookmarks (★)

Click the star icon next to any item in the advanced window.

Pinned items are protected from the automatic 50-item cleanup and are always sorted to the top of the list.

## Configuration

The clipboard history is stored locally at:

```text
~/.config/light_clipboard.json
```

The application keeps a maximum of **50 clipboard items**.

Pinned items are protected from automatic cleanup.

## Troubleshooting

### Clipboard Icon Does Not Appear

Make sure the required packages are installed:

```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-ayatanaappindicator3-0.1
```

Then run the application manually:

```bash
cd ~/lightweight-clipboard-manager
./clipboard_manager.py
```

Check the terminal output for any errors.

### Keyboard Shortcut Does Not Work

First, check whether the clipboard manager is running:

```bash
ps aux | grep clipboard_manager.py
```

You can also test the signal manually:

```bash
pkill -SIGUSR1 -f clipboard_manager.py
```

If the application is running correctly, the advanced search window should open or close.

### Stop the Application

To completely stop the clipboard manager:

```bash
pkill -f clipboard_manager.py
```

## License

Use, modify, and distribute this script according to your project's requirements.
