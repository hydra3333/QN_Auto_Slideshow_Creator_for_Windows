@ECHO off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM DRAG AND DROP A FOLDER NAME ONTO THIS BAT

set "TopFolder=%~1"

set "script=%~dpn0.ps1"
set "log=%~dpn0.log"

powershell.exe -ExecutionPolicy Bypass -File "%script%" -TopFolder "%TopFolder%" > "!log!" 2>&1

type "!log!"
pause

exit
