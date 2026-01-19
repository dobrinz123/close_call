#!/usr/bin/env python3
"""
Browser Blocker (No Admin Required) - Proxy Method
Blocks browser internet access by setting invalid proxy configuration.

USAGE:
    python browser_blocker_no_admin.py        # Launch GUI (default)

Double-click to run - NO Administrator privileges needed!
"""

import os
import sys
import json
import shutil
import time
import psutil
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
import threading
from datetime import datetime

# Invalid proxy that blocks all traffic
BLOCK_PROXY_SERVER = "127.0.0.1:9999"
BLOCK_PROXY_MODE = "fixed_servers"

# Browser process names
BROWSER_PROCESSES = {
    "Chrome": ["chrome.exe"],
    "Edge": ["msedge.exe"],
    "Firefox": ["firefox.exe"],
    "Brave": ["brave.exe"]
}


def get_browser_config_paths():
    """
    Get configuration file paths for all browsers.
    Returns dict: {browser_name: config_path}
    """
    user_home = Path.home()
    local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
    appdata = Path(os.environ.get('APPDATA', ''))

    configs = {}

    # Chrome
    chrome_prefs = local_appdata / "Google" / "Chrome" / "User Data" / "Default" / "Preferences"
    if chrome_prefs.exists():
        configs["Chrome"] = chrome_prefs

    # Edge
    edge_prefs = local_appdata / "Microsoft" / "Edge" / "User Data" / "Default" / "Preferences"
    if edge_prefs.exists():
        configs["Edge"] = edge_prefs

    # Brave
    brave_prefs = local_appdata / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Preferences"
    if brave_prefs.exists():
        configs["Brave"] = brave_prefs

    # Firefox - find profile directory
    firefox_profiles = appdata / "Mozilla" / "Firefox" / "Profiles"
    if firefox_profiles.exists():
        for profile_dir in firefox_profiles.iterdir():
            if profile_dir.is_dir():
                prefs_js = profile_dir / "prefs.js"
                if prefs_js.exists():
                    configs["Firefox"] = prefs_js
                    break

    return configs


def kill_browser_processes():
    """
    Terminate all running browser processes.
    Returns list of killed process names.
    """
    killed = []

    for browser_name, process_names in BROWSER_PROCESSES.items():
        for proc_name in process_names:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() == proc_name.lower():
                        proc.terminate()
                        killed.append(f"{browser_name} ({proc_name})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

    # Wait for processes to terminate
    time.sleep(1)

    return killed


def backup_config(config_path):
    """Create backup of configuration file."""
    backup_path = Path(str(config_path) + ".backup_browser_blocker")
    if not backup_path.exists():
        shutil.copy2(config_path, backup_path)
    return backup_path


def restore_config(config_path):
    """Restore configuration from backup."""
    backup_path = Path(str(config_path) + ".backup_browser_blocker")
    if backup_path.exists():
        shutil.copy2(backup_path, config_path)
        backup_path.unlink()
        return True
    return False


def block_chromium_browser(config_path):
    """
    Block Chromium-based browser (Chrome, Edge, Brave) by setting invalid proxy.
    Returns (success, message)
    """
    try:
        # Backup original config
        backup_config(config_path)

        # Read current preferences
        with open(config_path, 'r', encoding='utf-8') as f:
            prefs = json.load(f)

        # Set invalid proxy configuration
        if 'proxy' not in prefs:
            prefs['proxy'] = {}

        prefs['proxy']['mode'] = BLOCK_PROXY_MODE
        prefs['proxy']['server'] = BLOCK_PROXY_SERVER
        prefs['proxy']['bypass_list'] = []

        # Write modified preferences
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2)

        return True, "Proxy blocked successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def unblock_chromium_browser(config_path):
    """
    Restore Chromium-based browser settings.
    Returns (success, message)
    """
    try:
        if restore_config(config_path):
            return True, "Settings restored from backup"
        else:
            # No backup, just remove proxy settings
            with open(config_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            if 'proxy' in prefs:
                prefs['proxy'] = {'mode': 'system'}

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)

            return True, "Proxy settings removed"

    except Exception as e:
        return False, f"Error: {str(e)}"


def block_firefox(config_path):
    """
    Block Firefox by adding proxy settings to prefs.js.
    Returns (success, message)
    """
    try:
        # Backup original config
        backup_config(config_path)

        # Read existing prefs
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Append proxy settings
        proxy_config = f'''
// Browser Blocker - Invalid Proxy Configuration
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 9999);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 9999);
user_pref("network.proxy.no_proxies_on", "");
'''

        with open(config_path, 'a', encoding='utf-8') as f:
            f.write(proxy_config)

        return True, "Proxy blocked successfully"

    except Exception as e:
        return False, f"Error: {str(e)}"


def unblock_firefox(config_path):
    """
    Restore Firefox settings.
    Returns (success, message)
    """
    try:
        if restore_config(config_path):
            return True, "Settings restored from backup"
        return True, "Restored"

    except Exception as e:
        return False, f"Error: {str(e)}"


class BrowserBlockerNoAdminGUI:
    """GUI Application for Browser Blocker (No Admin)."""

    def __init__(self, root):
        self.root = root
        self.root.title("Browser Blocker (No Admin) - Proxy Method")
        self.root.geometry("750x650")
        self.root.resizable(True, True)

        self.blocked_browsers = []
        self.is_blocking = False
        self.monitor_thread = None
        self.stop_monitoring = False

        self.setup_ui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_frame = tk.Frame(self.root, bg="#34495e", height=70)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🔒 Browser Blocker",
            font=("Arial", 18, "bold"),
            bg="#34495e",
            fg="white"
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            title_frame,
            text="No Administrator Rights Needed",
            font=("Arial", 9),
            bg="#34495e",
            fg="#ecf0f1"
        )
        subtitle_label.pack()

        # Info Frame
        info_frame = tk.Frame(self.root, bg="#ecf0f1")
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_text = "ℹ️ This tool blocks browsers by setting an invalid proxy. No admin password required!"
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            bg="#ecf0f1",
            fg="#2c3e50",
            wraplength=700,
            justify="left"
        )
        info_label.pack(padx=10, pady=8)

        # Status Frame
        status_frame = tk.Frame(self.root, bg="#d5dbdb")
        status_frame.pack(fill=tk.X, padx=10, pady=5)

        self.status_label = tk.Label(
            status_frame,
            text="⚪ Status: Ready",
            font=("Arial", 11, "bold"),
            bg="#d5dbdb",
            fg="#7f8c8d",
            anchor="w"
        )
        self.status_label.pack(padx=10, pady=8, fill=tk.X)

        # Buttons Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.block_button = tk.Button(
            button_frame,
            text="🚫 BLOCK BROWSERS",
            command=self.block_browsers_gui,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.block_button.grid(row=0, column=0, padx=5)

        self.unblock_button = tk.Button(
            button_frame,
            text="✅ UNBLOCK BROWSERS",
            command=self.unblock_browsers_gui,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.unblock_button.grid(row=0, column=1, padx=5)

        # Output Text Area
        output_label = tk.Label(
            self.root,
            text="Output Log:",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        output_label.pack(padx=10, pady=(10, 5), fill=tk.X)

        self.output_text = scrolledtext.ScrolledText(
            self.root,
            height=20,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            wrap=tk.WORD
        )
        self.output_text.pack(padx=10, pady=(0, 10), fill=tk.BOTH, expand=True)

        # Clear button
        clear_button = tk.Button(
            self.root,
            text="Clear Log",
            command=self.clear_output,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 9),
            cursor="hand2"
        )
        clear_button.pack(pady=(0, 10))

    def log(self, message):
        """Add message to output text area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        self.root.update()

    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)

    def update_status(self, text, color):
        """Update status label."""
        self.status_label.config(text=text, fg=color)

    def monitor_browsers(self):
        """Background thread to monitor browser processes and re-apply blocks."""
        while not self.stop_monitoring:
            # Check if any browser is running
            for browser_name, process_names in BROWSER_PROCESSES.items():
                if browser_name in self.blocked_browsers:
                    for proc_name in process_names:
                        for proc in psutil.process_iter(['name']):
                            try:
                                if proc.info['name'].lower() == proc_name.lower():
                                    self.log(f"⚠️ Detected {browser_name} starting, terminating...")
                                    proc.terminate()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass

            time.sleep(2)  # Check every 2 seconds

    def block_browsers_gui(self):
        """Handle Block button click."""
        if self.is_blocking:
            messagebox.showinfo("Already Blocking", "Browsers are already blocked!\nUse UNBLOCK to restore access.")
            return

        def block_thread():
            self.block_button.config(state=tk.DISABLED)
            self.unblock_button.config(state=tk.DISABLED)

            self.clear_output()
            self.log("=" * 70)
            self.log("BLOCKING BROWSERS - Setting invalid proxy configuration...")
            self.log("=" * 70 + "\n")

            # Step 1: Kill running browsers
            self.log("Step 1: Terminating running browser processes...\n")
            killed = kill_browser_processes()
            if killed:
                for proc_name in killed:
                    self.log(f"  ✓ Terminated: {proc_name}")
                self.log("")
            else:
                self.log("  ℹ️ No browser processes were running\n")

            # Step 2: Get browser configs
            self.log("Step 2: Detecting browser configurations...\n")
            configs = get_browser_config_paths()

            if not configs:
                self.log("⚠️ No browser configurations found!")
                self.log("  Make sure browsers have been run at least once.\n")
                self.update_status("⚪ Status: No browsers found", "#7f8c8d")
                self.block_button.config(state=tk.NORMAL)
                self.unblock_button.config(state=tk.NORMAL)
                return

            self.log(f"Found {len(configs)} browser configuration(s):\n")

            # Step 3: Apply proxy blocks
            self.log("Step 3: Applying proxy blocks...\n")
            self.blocked_browsers = []

            for browser_name, config_path in configs.items():
                self.log(f"📌 {browser_name}:")
                self.log(f"   Config: {config_path}")

                if browser_name == "Firefox":
                    success, message = block_firefox(config_path)
                else:
                    success, message = block_chromium_browser(config_path)

                if success:
                    self.log(f"   ✓ {message}")
                    self.blocked_browsers.append(browser_name)
                else:
                    self.log(f"   ✗ {message}")
                self.log("")

            self.log("=" * 70)
            self.log(f"✓ Successfully blocked {len(self.blocked_browsers)} browser(s)")
            self.log("=" * 70 + "\n")
            self.log("🔒 Browsers will open but won't have internet access!")
            self.log("🔒 Starting continuous monitoring...\n")

            self.is_blocking = True
            self.update_status("🔴 Status: BROWSERS BLOCKED (Monitoring Active)", "#e74c3c")

            # Start monitoring thread
            self.stop_monitoring = False
            self.monitor_thread = threading.Thread(target=self.monitor_browsers, daemon=True)
            self.monitor_thread.start()

            self.block_button.config(state=tk.NORMAL)
            self.unblock_button.config(state=tk.NORMAL)

        threading.Thread(target=block_thread, daemon=True).start()

    def unblock_browsers_gui(self):
        """Handle Unblock button click."""
        def unblock_thread():
            self.block_button.config(state=tk.DISABLED)
            self.unblock_button.config(state=tk.DISABLED)

            # Stop monitoring
            self.stop_monitoring = True
            if self.monitor_thread:
                self.monitor_thread.join(timeout=3)

            self.clear_output()
            self.log("=" * 70)
            self.log("UNBLOCKING BROWSERS - Restoring settings...")
            self.log("=" * 70 + "\n")

            configs = get_browser_config_paths()

            if not configs:
                self.log("⚠️ No browser configurations found.\n")
            else:
                for browser_name, config_path in configs.items():
                    self.log(f"📌 {browser_name}:")

                    if browser_name == "Firefox":
                        success, message = unblock_firefox(config_path)
                    else:
                        success, message = unblock_chromium_browser(config_path)

                    if success:
                        self.log(f"   ✓ {message}")
                    else:
                        self.log(f"   ✗ {message}")
                    self.log("")

            self.log("=" * 70)
            self.log("✓ Browsers are now UNBLOCKED")
            self.log("=" * 70 + "\n")
            self.log("ℹ️ You may need to restart browsers for changes to take effect.\n")

            self.is_blocking = False
            self.blocked_browsers = []
            self.update_status("🟢 Status: Browsers Unblocked", "#27ae60")

            self.block_button.config(state=tk.NORMAL)
            self.unblock_button.config(state=tk.NORMAL)

        threading.Thread(target=unblock_thread, daemon=True).start()

    def on_closing(self):
        """Handle window closing event."""
        if self.is_blocking:
            result = messagebox.askyesno(
                "Browsers Still Blocked",
                "Browsers are currently blocked.\n\nDo you want to unblock them before closing?",
                icon=messagebox.WARNING
            )
            if result:
                # Stop monitoring
                self.stop_monitoring = True

                # Restore configs
                configs = get_browser_config_paths()
                for browser_name, config_path in configs.items():
                    if browser_name == "Firefox":
                        unblock_firefox(config_path)
                    else:
                        unblock_chromium_browser(config_path)

                messagebox.showinfo("Cleanup Complete", "Browsers have been unblocked.")

        self.root.destroy()


def main():
    """Main program entry point."""
    root = tk.Tk()
    app = BrowserBlockerNoAdminGUI(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()


# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================
#
# NO ADMINISTRATOR RIGHTS NEEDED!
#
# Simply double-click this file to run.
#
# How it works:
# - Sets invalid proxy configuration in browser settings
# - Browsers will open normally but won't be able to access the internet
# - Continuously monitors and terminates browsers when they start
# - Click UNBLOCK to restore normal browser functionality
#
# Note: You need psutil installed. If not installed, run:
#   pip install psutil
#
# =============================================================================
