' Browser Blocker Launcher - Silent Administrator Request
' Double-click this file to launch Browser Blocker GUI with Administrator privileges

Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
strScriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
strPythonScript = strScriptDir & "\browser_blocker.py"

' Check if browser_blocker.py exists
If Not objFSO.FileExists(strPythonScript) Then
    MsgBox "Error: browser_blocker.py not found!" & vbCrLf & vbCrLf & _
           "Please ensure browser_blocker.py is in the same folder as this launcher.", _
           vbCritical, "Browser Blocker"
    WScript.Quit
End If

' Try to find Python executable
pythonExe = FindPython()

If pythonExe = "" Then
    MsgBox "Error: Python not found!" & vbCrLf & vbCrLf & _
           "Please install Python from python.org", _
           vbCritical, "Browser Blocker"
    WScript.Quit
End If

' Run with Administrator privileges (UAC prompt will appear)
objShell.ShellExecute pythonExe, """" & strPythonScript & """", strScriptDir, "runas", 1

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

    For Each path In pythonPaths
        expandedPath = objShell2.ExpandEnvironmentStrings(path)

        ' If it's just a filename (in PATH), try to run it
        If InStr(expandedPath, "\") = 0 Then
            ' Check if command exists in PATH
            Set objExec = objShell2.Exec("where " & expandedPath & " 2>nul")
            Do While Not objExec.StdOut.AtEndOfStream
                foundPath = Trim(objExec.StdOut.ReadLine())
                If foundPath <> "" And objFSO.FileExists(foundPath) Then
                    FindPython = foundPath
                    Exit Function
                End If
            Loop
        Else
            ' Check if full path exists
            If objFSO.FileExists(expandedPath) Then
                FindPython = expandedPath
                Exit Function
            End If
        End If
    Next

    ' Last resort: try python.exe instead of pythonw.exe
    Set objExec = objShell2.Exec("where python.exe 2>nul")
    Do While Not objExec.StdOut.AtEndOfStream
        foundPath = Trim(objExec.StdOut.ReadLine())
        If foundPath <> "" And objFSO.FileExists(foundPath) Then
            FindPython = foundPath
            Exit Function
        End If
    Loop

    FindPython = ""
End Function
