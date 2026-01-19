#!/usr/bin/env python3
"""
Browser Blocker - Windows Firewall Tool
Blocks internet access for web browsers (Chrome, Edge, Firefox, Brave) while running.

USAGE:
    Run as Administrator:
    python browser_blocker.py              # Launch GUI (default)
    python browser_blocker.py --block      # Block browsers (CLI mode)
    python browser_blocker.py --unblock    # Remove blocking rules (CLI mode)
    python browser_blocker.py --dry-run    # Show what would be done (CLI mode)
    python browser_blocker.py --no-gui     # Force CLI mode

Press Ctrl+C to stop blocking and cleanup rules (CLI mode).
"""

import os
import sys
import subprocess
import argparse
import signal
import time
import ctypes
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
import threading

# Get current process ID for unique rule naming
CURRENT_PID = os.getpid()
RULE_PREFIX = "BrowserBlocker"


def is_admin():
    """Check if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def check_admin_privileges():
    """Verify admin privileges and exit if not running as admin."""
    if not is_admin():
        print("=" * 70)
        print("ERROR: Administrator privileges required!")
        print("=" * 70)
        print("\nThis program needs to modify Windows Firewall rules.")
        print("\nTo run this program:")
        print("  1. Open Command Prompt or PowerShell as Administrator")
        print("  2. Navigate to the script directory")
        print("  3. Run: python browser_blocker.py")
        print("\nAlternatively, right-click Python and select 'Run as Administrator'")
        print("=" * 70)
        sys.exit(1)


def get_browser_paths():
    """
    Detect browser executables in standard Windows locations.
    Returns a dictionary: {browser_name: [list of existing paths]}
    """
    browser_definitions = {
        "Edge": [
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ],
        "Chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ],
        "Firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ],
        "Brave": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
        ]
    }

    detected_browsers = {}

    for browser_name, paths in browser_definitions.items():
        existing_paths = []
        for path in paths:
            if Path(path).exists():
                existing_paths.append(path)

        if existing_paths:
            detected_browsers[browser_name] = existing_paths

    return detected_browsers


def generate_rule_name(browser_name, exe_path):
    """Generate unique firewall rule name."""
    # Use simple index based on path to keep names consistent
    path_hash = abs(hash(exe_path)) % 1000
    return f"{RULE_PREFIX}-{browser_name}-{CURRENT_PID}-{path_hash}"


def add_firewall_rule(browser_name, exe_path, dry_run=False):
    """
    Add Windows Firewall outbound rule to block a browser executable.
    Returns (success: bool, rule_name: str, message: str)
    """
    rule_name = generate_rule_name(browser_name, exe_path)

    cmd = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name}",
        "dir=out",
        "action=block",
        f"program={exe_path}",
        "enable=yes",
        "profile=any"
    ]

    if dry_run:
        return True, rule_name, f"[DRY RUN] Would add rule: {rule_name}"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            return True, rule_name, f"✓ Added rule: {rule_name}"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, rule_name, f"✗ Failed to add rule: {error_msg}"

    except Exception as e:
        return False, rule_name, f"✗ Exception adding rule: {str(e)}"


def remove_firewall_rule(rule_name, dry_run=False):
    """
    Remove a specific Windows Firewall rule.
    Returns (success: bool, message: str)
    """
    cmd = [
        "netsh", "advfirewall", "firewall", "delete", "rule",
        f"name={rule_name}"
    ]

    if dry_run:
        return True, f"[DRY RUN] Would remove rule: {rule_name}"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            return True, f"✓ Removed rule: {rule_name}"
        else:
            # Rule might not exist, which is not necessarily an error
            return False, f"⚠ Could not remove rule: {rule_name} (may not exist)"

    except Exception as e:
        return False, f"✗ Exception removing rule: {str(e)}"


def list_existing_rules():
    """
    List all firewall rules created by this program.
    Returns list of rule names.
    """
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            return []

        # Parse output to find our rules
        rules = []
        for line in result.stdout.split('\n'):
            if line.strip().startswith("Rule Name:"):
                rule_name = line.split(":", 1)[1].strip()
                if rule_name.startswith(RULE_PREFIX):
                    rules.append(rule_name)

        return rules

    except Exception:
        return []


def block_browsers(dry_run=False):
    """
    Main function to block browsers by adding firewall rules.
    Returns list of added rule names.
    """
    print("\n" + "=" * 70)
    print("BROWSER BLOCKER - Detecting browsers...")
    print("=" * 70 + "\n")

    browsers = get_browser_paths()

    if not browsers:
        print("⚠ No browsers detected in standard locations.")
        print("  Searched for: Chrome, Edge, Firefox, Brave")
        return []

    print(f"Found {len(browsers)} browser(s):\n")

    added_rules = []

    for browser_name, paths in browsers.items():
        print(f"📌 {browser_name}:")
        for exe_path in paths:
            print(f"   Path: {exe_path}")
            success, rule_name, message = add_firewall_rule(browser_name, exe_path, dry_run)
            print(f"   {message}")

            if success:
                added_rules.append(rule_name)

        print()

    if dry_run:
        print("=" * 70)
        print("DRY RUN MODE - No changes were made")
        print("=" * 70)
    else:
        print("=" * 70)
        print(f"✓ Successfully blocked {len(added_rules)} browser executable(s)")
        print("=" * 70)

    return added_rules


def unblock_browsers(dry_run=False):
    """
    Remove all firewall rules created by this program.
    """
    print("\n" + "=" * 70)
    print("BROWSER BLOCKER - Removing firewall rules...")
    print("=" * 70 + "\n")

    # Find all rules with our prefix
    existing_rules = list_existing_rules()

    if not existing_rules:
        print("⚠ No BrowserBlocker rules found.")
        return

    print(f"Found {len(existing_rules)} rule(s) to remove:\n")

    removed_count = 0
    for rule_name in existing_rules:
        success, message = remove_firewall_rule(rule_name, dry_run)
        print(f"  {message}")
        if success:
            removed_count += 1

    print("\n" + "=" * 70)
    if dry_run:
        print("DRY RUN MODE - No changes were made")
    else:
        print(f"✓ Removed {removed_count} firewall rule(s)")
    print("=" * 70 + "\n")


def cleanup_on_exit(added_rules):
    """Remove firewall rules on program exit."""
    if not added_rules:
        return

    print("\n\n" + "=" * 70)
    print("CLEANUP - Removing firewall rules...")
    print("=" * 70 + "\n")

    removed_count = 0
    for rule_name in added_rules:
        success, message = remove_firewall_rule(rule_name, dry_run=False)
        print(f"  {message}")
        if success:
            removed_count += 1

    print("\n" + "=" * 70)
    print(f"✓ Cleanup complete - Removed {removed_count} rule(s)")
    print("=" * 70 + "\n")


class BrowserBlockerGUI:
    """GUI Application for Browser Blocker."""

    def __init__(self, root):
        self.root = root
        self.root.title("Browser Blocker - Windows Firewall")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.added_rules = []
        self.is_blocking = False

        # Set window icon if possible
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        self.setup_ui()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the user interface."""
        # Title
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X, padx=0, pady=0)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🔒 Browser Blocker",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=15)

        # Status Frame
        status_frame = tk.Frame(self.root, bg="#ecf0f1")
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        self.status_label = tk.Label(
            status_frame,
            text="⚪ Status: Ready",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
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
            width=18,
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
            width=18,
            height=2,
            cursor="hand2"
        )
        self.unblock_button.grid(row=0, column=1, padx=5)

        self.dryrun_button = tk.Button(
            button_frame,
            text="👁 DRY RUN",
            command=self.dry_run_gui,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            width=18,
            height=2,
            cursor="hand2"
        )
        self.dryrun_button.grid(row=0, column=2, padx=5)

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
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()

    def clear_output(self):
        """Clear the output text area."""
        self.output_text.delete(1.0, tk.END)

    def update_status(self, text, color):
        """Update status label."""
        self.status_label.config(text=text, fg=color)

    def block_browsers_gui(self):
        """Handle Block button click."""
        if self.is_blocking:
            messagebox.showinfo("Already Blocking", "Browsers are already blocked!\nUse UNBLOCK to restore access.")
            return

        def block_thread():
            self.block_button.config(state=tk.DISABLED)
            self.unblock_button.config(state=tk.DISABLED)
            self.dryrun_button.config(state=tk.DISABLED)

            self.clear_output()
            self.log("=" * 70)
            self.log("BLOCKING BROWSERS - Detecting browsers...")
            self.log("=" * 70 + "\n")

            browsers = get_browser_paths()

            if not browsers:
                self.log("⚠ No browsers detected in standard locations.")
                self.log("  Searched for: Chrome, Edge, Firefox, Brave\n")
                self.update_status("⚪ Status: No browsers found", "#7f8c8d")
                self.block_button.config(state=tk.NORMAL)
                self.unblock_button.config(state=tk.NORMAL)
                self.dryrun_button.config(state=tk.NORMAL)
                return

            self.log(f"Found {len(browsers)} browser(s):\n")

            self.added_rules = []

            for browser_name, paths in browsers.items():
                self.log(f"📌 {browser_name}:")
                for exe_path in paths:
                    self.log(f"   Path: {exe_path}")
                    success, rule_name, message = add_firewall_rule(browser_name, exe_path, dry_run=False)
                    self.log(f"   {message}")

                    if success:
                        self.added_rules.append(rule_name)
                self.log("")

            self.log("=" * 70)
            self.log(f"✓ Successfully blocked {len(self.added_rules)} browser executable(s)")
            self.log("=" * 70 + "\n")
            self.log("🔒 Browsers are now BLOCKED from accessing the internet.")
            self.log("🔒 Click UNBLOCK to restore access.\n")

            self.is_blocking = True
            self.update_status("🔴 Status: BROWSERS BLOCKED", "#e74c3c")

            self.block_button.config(state=tk.NORMAL)
            self.unblock_button.config(state=tk.NORMAL)
            self.dryrun_button.config(state=tk.NORMAL)

        threading.Thread(target=block_thread, daemon=True).start()

    def unblock_browsers_gui(self):
        """Handle Unblock button click."""
        def unblock_thread():
            self.block_button.config(state=tk.DISABLED)
            self.unblock_button.config(state=tk.DISABLED)
            self.dryrun_button.config(state=tk.DISABLED)

            self.clear_output()
            self.log("=" * 70)
            self.log("UNBLOCKING BROWSERS - Removing firewall rules...")
            self.log("=" * 70 + "\n")

            # Remove rules created by this instance
            if self.added_rules:
                self.log(f"Removing {len(self.added_rules)} rule(s) from current session:\n")
                removed_count = 0
                for rule_name in self.added_rules:
                    success, message = remove_firewall_rule(rule_name, dry_run=False)
                    self.log(f"  {message}")
                    if success:
                        removed_count += 1
                self.added_rules = []
                self.log(f"\n✓ Removed {removed_count} rule(s) from current session\n")

            # Also check for any other BrowserBlocker rules
            existing_rules = list_existing_rules()
            if existing_rules:
                self.log(f"Found {len(existing_rules)} additional BrowserBlocker rule(s):\n")
                removed_count = 0
                for rule_name in existing_rules:
                    success, message = remove_firewall_rule(rule_name, dry_run=False)
                    self.log(f"  {message}")
                    if success:
                        removed_count += 1
                self.log(f"\n✓ Removed {removed_count} additional rule(s)\n")
            else:
                if not self.added_rules:
                    self.log("⚠ No BrowserBlocker rules found.\n")

            self.log("=" * 70)
            self.log("✓ Browsers are now UNBLOCKED")
            self.log("=" * 70 + "\n")

            self.is_blocking = False
            self.update_status("🟢 Status: Browsers Unblocked", "#27ae60")

            self.block_button.config(state=tk.NORMAL)
            self.unblock_button.config(state=tk.NORMAL)
            self.dryrun_button.config(state=tk.NORMAL)

        threading.Thread(target=unblock_thread, daemon=True).start()

    def dry_run_gui(self):
        """Handle Dry Run button click."""
        def dryrun_thread():
            self.block_button.config(state=tk.DISABLED)
            self.unblock_button.config(state=tk.DISABLED)
            self.dryrun_button.config(state=tk.DISABLED)

            self.clear_output()
            self.log("=" * 70)
            self.log("DRY RUN MODE - Simulating block operation...")
            self.log("=" * 70 + "\n")

            browsers = get_browser_paths()

            if not browsers:
                self.log("⚠ No browsers detected in standard locations.")
                self.log("  Searched for: Chrome, Edge, Firefox, Brave\n")
                self.block_button.config(state=tk.NORMAL)
                self.unblock_button.config(state=tk.NORMAL)
                self.dryrun_button.config(state=tk.NORMAL)
                return

            self.log(f"Found {len(browsers)} browser(s):\n")

            rule_count = 0

            for browser_name, paths in browsers.items():
                self.log(f"📌 {browser_name}:")
                for exe_path in paths:
                    self.log(f"   Path: {exe_path}")
                    success, rule_name, message = add_firewall_rule(browser_name, exe_path, dry_run=True)
                    self.log(f"   {message}")
                    if success:
                        rule_count += 1
                self.log("")

            self.log("=" * 70)
            self.log("DRY RUN COMPLETE - No changes were made")
            self.log(f"Would have blocked {rule_count} browser executable(s)")
            self.log("=" * 70 + "\n")
            self.log("To actually block browsers, click the BLOCK BROWSERS button.\n")

            self.block_button.config(state=tk.NORMAL)
            self.unblock_button.config(state=tk.NORMAL)
            self.dryrun_button.config(state=tk.NORMAL)

        threading.Thread(target=dryrun_thread, daemon=True).start()

    def on_closing(self):
        """Handle window closing event."""
        if self.is_blocking and self.added_rules:
            result = messagebox.askyesno(
                "Browsers Still Blocked",
                "Browsers are currently blocked.\n\nDo you want to unblock them before closing?",
                icon=messagebox.WARNING
            )
            if result:
                # Cleanup rules
                for rule_name in self.added_rules:
                    remove_firewall_rule(rule_name, dry_run=False)
                messagebox.showinfo("Cleanup Complete", "Browsers have been unblocked.")

        self.root.destroy()


def launch_gui():
    """Launch the GUI application."""
    # Check admin privileges first
    if not is_admin():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Administrator Required",
            "This program requires Administrator privileges!\n\n"
            "Please:\n"
            "1. Right-click on this program\n"
            "2. Select 'Run as Administrator'\n\n"
            "Or run from an Administrator command prompt."
        )
        sys.exit(1)

    root = tk.Tk()
    app = BrowserBlockerGUI(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


def main():
    """Main program entry point."""
    parser = argparse.ArgumentParser(
        description="Block web browsers from accessing the internet using Windows Firewall",
        epilog="Remember to run as Administrator!"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--block",
        action="store_true",
        default=False,
        help="Block browsers (CLI mode)"
    )
    group.add_argument(
        "--unblock",
        action="store_true",
        help="Remove all BrowserBlocker firewall rules (CLI mode)"
    )
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes (CLI mode)"
    )
    group.add_argument(
        "--no-gui",
        action="store_true",
        help="Force CLI mode without GUI"
    )

    args = parser.parse_args()

    # Launch GUI if no arguments provided
    if len(sys.argv) == 1:
        launch_gui()
        return

    # CLI mode
    if args.no_gui and not any([args.block, args.unblock, args.dry_run]):
        args.block = True

    # Check admin privileges for CLI mode
    check_admin_privileges()

    # Execute requested action
    if args.unblock:
        unblock_browsers(dry_run=False)

    elif args.dry_run:
        block_browsers(dry_run=True)
        print("\nTo actually block browsers, run:")
        print("  python browser_blocker.py --block")

    elif args.block or args.no_gui:
        added_rules = block_browsers(dry_run=False)

        if not added_rules:
            print("\nNo browsers to block. Exiting.")
            return

        # Setup signal handler for cleanup
        def signal_handler(sig, frame):
            cleanup_on_exit(added_rules)
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Keep running until interrupted
        print("\n" + "🔒" * 35)
        print("Browsers are now BLOCKED from accessing the internet.")
        print("Press Ctrl+C to stop blocking and restore access.")
        print("🔒" * 35 + "\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            cleanup_on_exit(added_rules)


if __name__ == "__main__":
    main()


# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================
#
# GUI MODE (Default - Recommended):
# -----------------------------------
# 1. Right-click on browser_blocker.py
# 2. Select "Run with PowerShell" or "Run as Administrator"
# 3. A window will open with three buttons:
#    - 🚫 BLOCK BROWSERS: Block all browsers from internet
#    - ✅ UNBLOCK BROWSERS: Restore browser access
#    - 👁 DRY RUN: Preview what would be blocked
#
# OR double-click the file (if Python is associated with .py files)
#
# -----------------------------------
# CLI MODE (Advanced):
# -----------------------------------
# 1. Open Command Prompt or PowerShell as Administrator:
#    - Press Win + X
#    - Select "Windows Terminal (Admin)" or "Command Prompt (Admin)"
#
# 2. Navigate to the directory containing this script:
#    cd C:\path\to\script
#
# 3. Run the script:
#    python browser_blocker.py               # Launch GUI (default)
#    python browser_blocker.py --block       # Start blocking browsers (CLI)
#    python browser_blocker.py --unblock     # Remove all blocking rules (CLI)
#    python browser_blocker.py --dry-run     # Preview what would happen (CLI)
#
# 4. To stop blocking (CLI mode):
#    Press Ctrl+C in the terminal window
#
# The program will automatically cleanup firewall rules when stopped.
#
# =============================================================================
