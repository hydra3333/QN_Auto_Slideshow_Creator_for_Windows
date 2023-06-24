@echo off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

REM -->> -->> -->> -->> please see comments below about how to use/edit this file

if %NUMBER_OF_PROCESSORS% LEQ 2 ( set use_cores=1 ) else ( set /a use_cores=%NUMBER_OF_PROCESSORS%/2 )

set "vs_CD=%CD%"
if /I NOT "%vs_CD:~-1%" == "\" (set "vs_CD=%vs_CD%\")
set "vs_CD_bb=%vs_CD:\=\\%"

set "vs_path=%vs_CD%Vapoursynth_x64"
if /I NOT "%vs_path:~-1%" == "\" (set "vs_path=%vs_path%\")
set "vs_path_bb=%vs_path:\=\\%"

set "vs_temp=%vs_CD%temp"
if /I NOT "%vs_temp:~-1%" == "\" (set "vs_temp=%vs_temp%\")
set "vs_temp_bb=%vs_temp:\=\\%"

REM py_path and vs_path should ALWAYS be the same
set "py_path=%vs_path%"

REM ffmpeg and mediainfo exes located elsewhere are more up to date
set "python_exe=%py_path%python.exe"

set "PYTHONPATH=.\Vapoursynth_x64"
REM import sys
REM sys.path.insert(0,".\Vapoursynth_x64")

REM
REM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
REM

@ECHO OFF

REM Imagine you are organised and have separated your pics into groups
REM of say 1,000 or so, each group within it's own folder tree,
REM and you pop every group folder into one main folder.
REM
REM This script will run over the main folder
REM and produce a slideshow for each of the folders it finds there.
REM
REM EACH SLIDESHOW WILL COMPRISE THAT FOUND GROUP FOLDER AND ITS SUBFOLDERS
REM AND THE SLIDESHOW .MP4 FILENAME WILL BE THE SAME AS THE GROUP FOLDER NAME.
REM eg	main_folder
REM 		- group_folder_1
REM 			- folder_A
REM 				- folder_A_A
REM 			- folder_B
REM 		- group_folder_2
REM 			- folder_C
REM 			- folder_D
REM will produce a slideshow "group_folder_1.mp4" and another slideshow "group_folder_2.mp4
REM
REM Assumptions:
REM		- Will not work if ANY filenames or foldernames contain single quotes or double quotes, so you must have renamed them first ... have a look in the "draft" folder :)
REM 	- the slideshow .mp4 files will go into the same place as this script and the other .py files ".\"
REM 	- BACKGROUND_AUDIO_INPUT_FOLDER folder is in the same place as this script and the other .py files  - ".\BACKGROUND_AUDIO_INPUT_FOLDER"
REM 	- temp folder is in the same place as this script and the other .py files  - ".\TEMP"
REM		- see other settings below, you can edit them ... careful to ensure syntax is EXACT and precisely maintained

REM Edit this variable to point to the "main" folder mentioned above:
set "top_folder=G:\main-Pat.and.Ted.Photos"

REM Edit this variable to declare a prefix to be prepended to each .mp4 slideshow's filename:
set "mp4_filename_prefix=slideshow.of.Pat.and.Ted_Photos."

REM now you are ready to save your changes to this .bat and then double-click on it to run it.

set "ffprobeexe64=C:\SOFTWARE\ffmpeg\ffprobe.exe"
set "mediainfoexe=C:\SOFTWARE\MediaInfo\MediaInfo.exe"

set "script=.\slideshow_CONTROLLER.py"
set "log=!script!.log"
REM del /F "!log! >NUL 2>&1



set "ss=.\slideshow_settings.py"
for /D %%F in ("%top_folder%\*") do (
    set "folderName=%%~fF"
    set "mp4_filename=!mp4_filename_prefix!%%~nF.mp4"
	echo.
    echo folderName: !folderName! mp4_filename1: !mp4_filename!
	del /F "!ss!" >NUL 2>&1
	del /F ".\!mp4_filename!" >NUL 2>&1
	echo.
	echo settings = { >>"!ss!"
	echo 'ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS': [ r'!folderName!', ], >>"!ss!"
	echo 'FINAL_MP4_WITH_AUDIO_FILENAME': r'.\!mp4_filename!', >>"!ss!"
	echo 'SORT_TYPE': 'alphabetic_files_folders', >>"!ss!"
	echo 'RECURSIVE': True, >>"!ss!"
	echo 'TEMP_FOLDER': r'.\TEMP', >>"!ss!"
	echo 'BACKGROUND_AUDIO_INPUT_FOLDER': r'.\BACKGROUND_AUDIO_INPUT_FOLDER', >>"!ss!"
	echo 'SUBTITLE_DEPTH': 4, >>"!ss!"
	echo 'SUBTITLE_FONTSIZE': 19, >>"!ss!"
	echo 'SUBTITLE_FONTSCALE': 1.0, >>"!ss!"
	echo 'DURATION_PIC_SEC': 4.0, >>"!ss!"
	echo 'DURATION_MAX_VIDEO_SEC': 7200.0, >>"!ss!"
	echo 'DURATION_CROSSFADE_SECS': 0.5, >>"!ss!"
	echo 'CROSSFADE_TYPE': 'random', >>"!ss!"
	echo 'CROSSFADE_DIRECTION': 'left', >>"!ss!"
	echo #'TARGET_BACKGROUND_AUDIO_CODEC':'aac', >>"!ss!"
	echo 'TARGET_BACKGROUND_AUDIO_CODEC': 'libfdk_aac', >>"!ss!"
	echo 'TARGET_RESOLUTION': '1080p_pal', >>"!ss!"
	echo 'TARGET_VIDEO_BITRATE': '4M', >>"!ss!"
	echo #'FFMPEG_ENCODER':'libx264', >>"!ss!"
	echo 'FFMPEG_ENCODER':'h264_nvenc', >>"!ss!"
	echo 'TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB': -18, >>"!ss!"
	echo 'TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY':	-24, >>"!ss!"
	echo 'TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB': -12, >>"!ss!"
	echo 'MAX_FILES_PER_CHUNK': 150, >>"!ss!"
	echo 'DEBUG': False, >>"!ss!"
	echo } >>"!ss!"
	REM TYPE "!SS!" >>"!log!" 2>&1
	REM "!python_exe!" "!script!" >>"!log!" 2>&1
	REM echo "!mediainfoexe!" --full "G:\2021.06.14-Pat.and.Ted-Photos-SLIDESHOW\slideshow.0TEST.mp4" >>"!log!" 2>&1
	REM "!mediainfoexe!" --full "G:\2021.06.14-Pat.and.Ted-Photos-SLIDESHOW\slideshow.0TEST.mp4" >>"!log!" 2>&1
	TYPE "!ss!"
	echo "!python_exe!" "!script!"
	"!python_exe!" "!script!"
	REM pause
)

REM "!log!"

pause
goto :eof