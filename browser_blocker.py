#!/usr/bin/env python3
"""
Browser Blocker - Windows Firewall Tool
Blocks internet access for web browsers (Chrome, Edge, Firefox, Brave) while running.

USAGE:
    Run as Administrator:
    python browser_blocker.py --block       # Block browsers (default)
    python browser_blocker.py --unblock     # Remove blocking rules
    python browser_blocker.py --dry-run     # Show what would be done

Press Ctrl+C to stop blocking and cleanup rules.
"""

import os
import sys
import subprocess
import argparse
import signal
import time
import ctypes
from pathlib import Path

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
        help="Block browsers (default action)"
    )
    group.add_argument(
        "--unblock",
        action="store_true",
        help="Remove all BrowserBlocker firewall rules"
    )
    group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    # Default to --block if no argument specified
    if not args.unblock and not args.dry_run:
        args.block = True

    # Check admin privileges
    check_admin_privileges()

    # Execute requested action
    if args.unblock:
        unblock_browsers(dry_run=False)

    elif args.dry_run:
        block_browsers(dry_run=True)
        print("\nTo actually block browsers, run:")
        print("  python browser_blocker.py --block")

    else:  # args.block
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
# 1. Open Command Prompt or PowerShell as Administrator:
#    - Press Win + X
#    - Select "Windows Terminal (Admin)" or "Command Prompt (Admin)"
#
# 2. Navigate to the directory containing this script:
#    cd C:\path\to\script
#
# 3. Run the script:
#    python browser_blocker.py --block       # Start blocking browsers
#    python browser_blocker.py --unblock     # Remove all blocking rules
#    python browser_blocker.py --dry-run     # Preview what would happen
#
# 4. To stop blocking (if using --block):
#    Press Ctrl+C in the terminal window
#
# The program will automatically cleanup firewall rules when stopped.
#
# =============================================================================
