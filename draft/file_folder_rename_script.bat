@ECHO off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM Copyright (C) <2023> <ongoing>  <hydra3333>
REM 
REM    This program is free software: you can redistribute it and/or modify
REM    it under the terms of the GNU General Public License as published by
REM    the Free Software Foundation, either version 3 of the License, or
REM    (at your option) any later version.
REM 
REM    This program is distributed in the hope that it will be useful,
REM    but WITHOUT ANY WARRANTY; without even the implied warranty of
REM    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM    GNU General Public License for more details.
REM
REM    You should have received a copy of the GNU General Public License
REM    along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
