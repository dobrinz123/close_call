' Browser Blocker (No Admin) Launcher
' Double-click to launch - NO Administrator privileges needed!

Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strPythonScript = strScriptDir & "\browser_blocker_no_admin.py"

' Check if browser_blocker_no_admin.py exists
If Not objFSO.FileExists(strPythonScript) Then
    MsgBox "Error: browser_blocker_no_admin.py not found!" & vbCrLf & vbCrLf & _
           "Please ensure browser_blocker_no_admin.py is in the same folder as this launcher.", _
           vbCritical, "Browser Blocker (No Admin)"
    WScript.Quit
End If

' Try to find Python executable
pythonExe = FindPython()

If pythonExe = "" Then
    MsgBox "Error: Python not found!" & vbCrLf & vbCrLf & _
           "Please install Python from python.org", _
           vbCritical, "Browser Blocker (No Admin)"
    WScript.Quit
End If

' Check if psutil is installed
Set objShell2 = CreateObject("WScript.Shell")
Set objExec = objShell2.Exec(pythonExe & " -c ""import psutil""")

' Wait for command to finish
Do While objExec.Status = 0
    WScript.Sleep 100
Loop

If objExec.ExitCode <> 0 Then
    result = MsgBox("psutil library is not installed!" & vbCrLf & vbCrLf & _
                   "This program requires psutil to function." & vbCrLf & vbCrLf & _
                   "Would you like to install it now?" & vbCrLf & _
                   "(This will open a command window)", _
                   vbYesNo + vbQuestion, "Browser Blocker (No Admin)")

    If result = vbYes Then
        ' Install psutil
        objShell2.Run "cmd /c pip install psutil & pause", 1, True
    Else
        WScript.Quit
    End If
End If

' Run WITHOUT Administrator privileges (normal execution)
Set objShell3 = CreateObject("WScript.Shell")
objShell3.Run """" & pythonExe & """ """ & strPythonScript & """", 1, False

' Function to find Python installation
Function FindPython()
    Dim pythonPaths
    pythonPaths = Array( _
        "pythonw.exe", _
        "python.exe", _
        "C:\Python312\pythonw.exe", _
        "C:\Python311\pythonw.exe", _
        "C:\Python310\pythonw.exe", _
        "C:\Python39\pythonw.exe", _
        "C:\Python38\pythonw.exe", _
        "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe", _
        "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe", _
        "%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe" _
    )

    ' First try pythonw.exe from PATH
    On Error Resume Next
    Set objShell2 = CreateObject("WScript.Shell")
    Set objFSO2 = CreateObject("Scripting.FileSystemObject")

    For Each path In pythonPaths
        expandedPath = objShell2.ExpandEnvironmentStrings(path)

        ' If it's just a filename (in PATH), try to run it
        If InStr(expandedPath, "\") = 0 Then
            ' Check if command exists in PATH
            Set objExec = objShell2.Exec("where " & expandedPath & " 2>nul")
            Do While Not objExec.StdOut.AtEndOfStream
                foundPath = Trim(objExec.StdOut.ReadLine())
                If foundPath <> "" And objFSO2.FileExists(foundPath) Then
                    FindPython = foundPath
                    Exit Function
                End If
            Loop
        Else
            ' Check if full path exists
            If objFSO2.FileExists(expandedPath) Then
                FindPython = expandedPath
                Exit Function
            End If
        End If
    Next

    ' Last resort: try python.exe instead of pythonw.exe
    Set objExec = objShell2.Exec("where python.exe 2>nul")
    Do While Not objExec.StdOut.AtEndOfStream
        foundPath = Trim(objExec.StdOut.ReadLine())
        If foundPath <> "" And objFSO2.FileExists(foundPath) Then
            FindPython = foundPath
            Exit Function
        End If
    Loop

    FindPython = ""
End Function
