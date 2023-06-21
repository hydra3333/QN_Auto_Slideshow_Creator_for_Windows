@ECHO off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM DRAG AND DROP A FOLDER NAME ONTO THIS BAT

REM Sanitize FolderNames and FileNames in a folder tree.
REM Remove commas, ampersands, spaces and whatnot and replace them with underscores.
REM Identify a date in a Folder/File name and rename the folder/file with that date moved
REM to the front of the name in the format YYYY-MM-DD ... greatly assists with sorting.

REM NEVER use this on an original source tree - it renames files/folders
REM ... you know before you start that you'll not get the original folder/file names back again.

set "TopFolder=%~1"

set "script=%~dpn0.ps1"
set "log=%~dpn0.log"

powershell.exe -ExecutionPolicy Bypass -File "%script%" -TopFolder "%TopFolder%" > "!log!" 2>&1

type "!log!"
pause

exit
