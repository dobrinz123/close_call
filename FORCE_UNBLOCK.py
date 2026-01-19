#!/usr/bin/env python3
"""
FORCE UNBLOCK - Complete Browser Recovery
Removes ALL proxy settings and restores browser internet access
NO ADMIN REQUIRED
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
import winreg

print("=" * 70)
print("🚨 FORCE UNBLOCK - EMERGENCY BROWSER RECOVERY 🚨")
print("=" * 70)
print("\nThis will completely remove all proxy settings.")
print("Your browsers will work normally after this.\n")
input("Press ENTER to start recovery...")

# Kill all browsers
print("\n[1/5] Closing all browsers...")
browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"]
for browser in browsers:
    try:
        subprocess.run(["taskkill", "/F", "/IM", browser],
                      capture_output=True, check=False)
        print(f"  ✓ Closed {browser}")
    except:
        pass

import time
time.sleep(2)

# Reset Windows System Proxy
print("\n[2/5] Resetting Windows system proxy...")
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                        0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
    winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "")
    winreg.CloseKey(key)
    print("  ✓ System proxy cleared")
except Exception as e:
    print(f"  ⚠ Could not clear system proxy: {e}")

# Chrome
print("\n[3/5] Fixing Chrome...")
chrome_prefs = Path(os.environ.get('LOCALAPPDATA', '')) / "Google" / "Chrome" / "User Data" / "Default" / "Preferences"
if chrome_prefs.exists():
    try:
        # Try backup first
        backup = Path(str(chrome_prefs) + ".backup_browser_blocker")
        if backup.exists():
            shutil.copy2(backup, chrome_prefs)
            print("  ✓ Chrome restored from backup")
        else:
            # Manual fix
            with open(chrome_prefs, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            # Remove proxy completely
            if 'proxy' in prefs:
                del prefs['proxy']

            # Force system proxy
            prefs['proxy'] = {"mode": "system"}

            with open(chrome_prefs, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            print("  ✓ Chrome proxy removed")
    except Exception as e:
        print(f"  ✗ Chrome fix failed: {e}")
else:
    print("  ℹ Chrome not found")

# Edge
print("\n[4/5] Fixing Edge...")
edge_prefs = Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "Edge" / "User Data" / "Default" / "Preferences"
if edge_prefs.exists():
    try:
        backup = Path(str(edge_prefs) + ".backup_browser_blocker")
        if backup.exists():
            shutil.copy2(backup, edge_prefs)
            print("  ✓ Edge restored from backup")
        else:
            with open(edge_prefs, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            if 'proxy' in prefs:
                del prefs['proxy']

            prefs['proxy'] = {"mode": "system"}

            with open(edge_prefs, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            print("  ✓ Edge proxy removed")
    except Exception as e:
        print(f"  ✗ Edge fix failed: {e}")
else:
    print("  ℹ Edge not found")

# Brave
print("\nFixing Brave...")
brave_prefs = Path(os.environ.get('LOCALAPPDATA', '')) / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Preferences"
if brave_prefs.exists():
    try:
        backup = Path(str(brave_prefs) + ".backup_browser_blocker")
        if backup.exists():
            shutil.copy2(backup, brave_prefs)
            print("  ✓ Brave restored from backup")
        else:
            with open(brave_prefs, 'r', encoding='utf-8') as f:
                prefs = json.load(f)

            if 'proxy' in prefs:
                del prefs['proxy']

            prefs['proxy'] = {"mode": "system"}

            with open(brave_prefs, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            print("  ✓ Brave proxy removed")
    except Exception as e:
        print(f"  ✗ Brave fix failed: {e}")
else:
    print("  ℹ Brave not found")

# Firefox
print("\n[5/5] Fixing Firefox...")
firefox_profiles = Path(os.environ.get('APPDATA', '')) / "Mozilla" / "Firefox" / "Profiles"
if firefox_profiles.exists():
    fixed = False
    for profile_dir in firefox_profiles.iterdir():
        if profile_dir.is_dir():
            prefs_js = profile_dir / "prefs.js"
            if prefs_js.exists():
                try:
                    backup = Path(str(prefs_js) + ".backup_browser_blocker")
                    if backup.exists():
                        shutil.copy2(backup, prefs_js)
                        print(f"  ✓ Firefox restored from backup")
                        fixed = True
                    else:
                        # Remove proxy lines
                        with open(prefs_js, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        # Filter out proxy lines
                        clean_lines = [line for line in lines if 'network.proxy' not in line.lower()]

                        with open(prefs_js, 'w', encoding='utf-8') as f:
                            f.writelines(clean_lines)

                        print(f"  ✓ Firefox proxy removed")
                        fixed = True
                except Exception as e:
                    print(f"  ⚠ Firefox profile fix failed: {e}")

    if not fixed:
        print("  ℹ No Firefox profiles found")
else:
    print("  ℹ Firefox not found")

print("\n" + "=" * 70)
print("✅ RECOVERY COMPLETE!")
print("=" * 70)
print("\n🎯 Next steps:")
print("1. Open your browser")
print("2. Try accessing any website")
print("3. If still not working, try the manual fix below\n")

print("📌 MANUAL FIX (if browser still doesn't work):")
print("-" * 70)
print("1. Open your browser")
print("2. Go to Settings")
print("3. Search for 'proxy'")
print("4. Click 'Open your computer's proxy settings'")
print("5. Turn OFF 'Use a proxy server'")
print("6. Turn ON 'Automatically detect settings'")
print("7. Click Save and restart browser")
print("-" * 70)

input("\nPress ENTER to close...")
