@ECHO OFF
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

REM DRAG AND DROP a slideshow .MP4 onto this .bat to convert it to DVD .MPG

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

Set "slideshow_ffmpegexe64=%vs_path%ffmpeg.exe"
set "input_mp4=%~f1"
set "output=%~f1.NTSC-DVD.mpg"
set "log=%~f1.NTSC-DVD.mpg.log"

IF NOT EXIST "!slideshow_ffmpegexe64!" (
	echo FFmpeg file '!slideshow_ffmpegexe64!' does not exist.
	echo Exiting without success.
	pause
	exit
)

IF NOT EXIST "!input_mp4!" (
	echo The input file '!input_mp4!' does not exist. Drag and drop a .mp4 onto this .bat
	echo Exiting without success.
	pause
	exit
)

REM set the bitrates or DVD
set  "v_bitrate=9M"
set  "v_min=7M"
set  "v_max=9.2M"
set  "v_buf=2M"
set  "v_pkt=2048"
set  "v_mux=10M"
set  "v_framerate=29.976"
set  "v_gop_size=12"

set  "a_bitrate=256k"
set  "a_freq=48000"

@echo on
set "cmd_DVD="
set "cmd_DVD=!cmd_DVD!"!slideshow_ffmpegexe64!" "
set "cmd_DVD=!cmd_DVD! -hide_banner -v info "
set "cmd_DVD=!cmd_DVD! -stats "
set "cmd_DVD=!cmd_DVD! -i "!input_mp4!" -probesize 200M -analyzeduration 200M "
set "cmd_DVD=!cmd_DVD! -sws_flags lanczos+accurate_rnd+full_chroma_int+full_chroma_inp -strict experimental "
set "cmd_DVD=!cmd_DVD! -filter_complex "scale=720:480:flags='lanczos+accurate_rnd+full_chroma_int+full_chroma_inp',format=yuv420p,setdar=16/9" "
set "cmd_DVD=!cmd_DVD! -target ntsc-dvd "
REM set "cmd_DVD=!cmd_DVD! -r %v_framerate% "
set "cmd_DVD=!cmd_DVD! -g %v_gop_size% -mpv_flags +strict_gop "
set "cmd_DVD=!cmd_DVD! -b:v %v_bitrate% -minrate:v %v_min% -maxrate:v %v_max% -bufsize %v_buf% -packetsize %v_pkt% -muxrate %v_mux% "
set "cmd_DVD=!cmd_DVD! -c:a ac3 "
set "cmd_DVD=!cmd_DVD! -ac 2 "
set "cmd_DVD=!cmd_DVD! -b:a %a_bitrate% "
set "cmd_DVD=!cmd_DVD! -ar %a_freq% "
set "cmd_DVD=!cmd_DVD! -y "!output!" "
REM

echo !cmd_DVD!
!cmd_DVD!

dir "!input_mp4!"
dir "!output!"

pause
exit
