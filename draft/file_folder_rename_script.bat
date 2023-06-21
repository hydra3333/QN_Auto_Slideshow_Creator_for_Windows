@ECHO off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM DRAG AND DROP A FOLDER NAME ONTO THIS BAT

REM Sanitize FolderNames and FileNames in a folder tree.
REM Remove commas, ampersands, spaces and whatnot and replace them with underscores.
REM Identify a date in a Folder/File name and renaming the folder/file with that date moved
REM to the front of the name in the format YYYY-MM-DD ... creatly assists with sorting.

set "TopFolder=%~1"

set "script=%~dpn0.ps1"
set "log=%~dpn0.log"

powershell.exe -ExecutionPolicy Bypass -File "%script%" -TopFolder "%TopFolder%" > "!log!" 2>&1

type "!log!"
pause

exit
