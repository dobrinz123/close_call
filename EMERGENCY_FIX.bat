@echo off
echo ========================================
echo BROWSER BLOCKER - EMERGENCY FIX
echo ========================================
echo.
echo This will restore your browser settings.
echo.
pause

echo.
echo Closing all browsers...
taskkill /F /IM chrome.exe 2>nul
taskkill /F /IM msedge.exe 2>nul
taskkill /F /IM firefox.exe 2>nul
taskkill /F /IM brave.exe 2>nul
timeout /t 2 >nul

echo.
echo Restoring Chrome settings...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences.backup_browser_blocker" (
    copy /Y "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences.backup_browser_blocker" "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences"
    echo Chrome backup restored!
) else (
    echo No Chrome backup found. Resetting proxy in Preferences...
    powershell -Command "(Get-Content '%LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences' -Raw) -replace '\"proxy\":\s*{[^}]*}', '\"proxy\": {\"mode\": \"system\"}' | Set-Content '%LOCALAPPDATA%\Google\Chrome\User Data\Default\Preferences'" 2>nul
)

echo.
echo Restoring Edge settings...
if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Preferences.backup_browser_blocker" (
    copy /Y "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Preferences.backup_browser_blocker" "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Preferences"
    echo Edge backup restored!
) else (
    echo No Edge backup found. Resetting proxy in Preferences...
    powershell -Command "(Get-Content '%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Preferences' -Raw) -replace '\"proxy\":\s*{[^}]*}', '\"proxy\": {\"mode\": \"system\"}' | Set-Content '%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Preferences'" 2>nul
)

echo.
echo Restoring Brave settings...
if exist "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Preferences.backup_browser_blocker" (
    copy /Y "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Preferences.backup_browser_blocker" "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Preferences"
    echo Brave backup restored!
) else (
    echo No Brave backup found. Resetting proxy in Preferences...
    powershell -Command "(Get-Content '%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Preferences' -Raw) -replace '\"proxy\":\s*{[^}]*}', '\"proxy\": {\"mode\": \"system\"}' | Set-Content '%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Preferences'" 2>nul
)

echo.
echo Restoring Firefox settings...
for /d %%p in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
    if exist "%%p\prefs.js.backup_browser_blocker" (
        copy /Y "%%p\prefs.js.backup_browser_blocker" "%%p\prefs.js"
        echo Firefox backup restored!
    ) else (
        echo Removing proxy lines from Firefox prefs.js...
        powershell -Command "(Get-Content '%%p\prefs.js') | Where-Object { $_ -notmatch 'network.proxy' } | Set-Content '%%p\prefs.js.temp'" 2>nul
        if exist "%%p\prefs.js.temp" move /Y "%%p\prefs.js.temp" "%%p\prefs.js"
    )
)

echo.
echo Resetting Windows system proxy...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /t REG_SZ /d "" /f >nul

echo.
echo ========================================
echo DONE! Your browsers should work now.
echo ========================================
echo.
echo Please restart your browser.
echo.
pause
