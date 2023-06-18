@ECHO off
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions

Set "slideshow_ffmpegexe64=C:\SOFTWARE\ffmpeg\0-homebuilt-x64\ffmpeg_OpenCL.exe"
Set "slideshow_mediainfoexe64=C:\SOFTWARE\MediaInfo\MediaInfo.exe"
Set "slideshow_ffprobeexe64=C:\SOFTWARE\ffmpeg\0-homebuilt-x64\ffprobe_OpenCL.exe"
Set "slideshow_Insomniaexe64=C:\SOFTWARE\Insomnia\64-bit\Insomnia.exe"
Set "slideshow_Irfanviewexe64=C:\SOFTWARE\irfanview\i_view64.exe"

call :maketempheader
REM ECHO after call --- !COMPUTERNAME! !DATE! !TIME! tempheader="!tempheader!"

REM ENSURE that the next line has a trailing slash !!!!!!!!!!!
set "target_top_folder=T:\000-SLIDESHOW-IVIEW-CONVERTED_IMAGES\"
if /I NOT "!target_top_folder:~-1!" == "\" (
	set "target_top_folder=!target_top_folder!\"
)
set "target_top_folder_noslash=!target_top_folder!"
if /I "!target_top_folder_noslash:~-1!" == "\" (
	set "target_top_folder_noslash=!target_top_folder_noslash:~0,-1!"
)

REM the input folder dragged and dropped onto this script
set "inp=%~1"
if /I "!inp!" == "" (
	echo It looks like there was no folder dragged and dropped onto this script. Input : '!inp!'
	pause
	exit
)

REM Don't allow to run on C: drive
set "leftmost_character=!inp:~,1!"
if /I "!leftmost_character!" == "C" (
	echo Cannot run this over any folders on the C: drive : '!inp!'
	pause
	exit
)

REM Ensure there's a single trailing backslash on the input
REM add a (another?) trailing backslash in case not at top level of drive or the user hasn't dropped something with one
set "source_folder=!inp!\"
REM change any trailing double backslash to a single backslash (in case already at top level folder) by optionally removing the last character
set "rightmost_character=!source_folder:~-2!"
if /I "!rightmost_character!" == "\\" (
	set "source_folder=!source_folder:~0,-1!"
)

REM get the rightmost folder name and use that as out output filename for the slideshow result
REM eg for "C:\FOLDER1\FOLDER2\FOLDER3\" return "FOLDER3" ... what happens if it's "g:\" ?
set "source_folder_noslash=!source_folder!"
if /I "!source_folder_noslash:~-1!" == "\" (
	set "source_folder_noslash=!source_folder_noslash:~0,-1!"
)
for %%f in ("%source_folder_noslash%") do (
	set "rightmost_foldername=%%~nxf"
)
REM Don't allow to run on the root of a drive
if /I "!rightmost_foldername!" == "" (
	echo Cannot run this over a root folder : '!inp!'
	pause
	exit
)


REM ---------------------------------------------------------------------------------------------------
@echo off
REM this IF test only works if there's a trailing slash
IF NOT EXIST "!target_top_folder!" (
	mkdir "!target_top_folder!"
)
set "iview_ini_file=!target_top_folder!i_view64.ini"
call :create_irfanview_ini_file "!iview_ini_file!"
REM ---------------------------------------------------------------------------------------------------


REM ---------------------------------------------------------------------------------------------------
REM PROCESS THE TOP FOLDER WHICH IS NOT CAUGHT BY THE LOOP BELOW
set "fold=!source_folder!"
REM echo folder='!fold!'
call :irfanview_make_1920x1080 "!target_top_folder!" "!fold!" "!iview_ini_file!"

for /f "tokens=*" %%G in ('dir /b /s /a:d "!source_folder!"') DO (
	set "fold=%%G\"
	set "rightmost_character=!fold:~-2!"
	if /I "!rightmost_character!" == "\\" (
		set "fold=!fold:~0,-1!"
	)
	set "fold_noslash=!fold!"
	if /I "!fold_noslash:~-1!" == "\" (
		set "fold_noslash=!fold_noslash:~0,-1!"
	)
	REM PROCESS THE SUB-FOLDER
	REM echo folder='!fold!'
	call :irfanview_make_1920x1080 "!target_top_folder!" "!fold!" "!iview_ini_file!"
	
)
REM ---------------------------------------------------------------------------------------------------


REM ---------------------------------------------------------------------------------------------------
REM slide picture duration in seconds
set /a "picture_duration=4"
REM set the bitrates or HQ
set /a "bitrate_target=9000000"
set /a "bitrate_min=3000000"
set /a "bitrate_max=15000000"
set /a "bitrate_bufsize=15000000"
set /a "timebase_numerator=1" 
set /a "timebase_denominator=25"
REM set picture duration via the PTS as an integer multiple of the timebase_denominator, so 1*25 = 25 (1 second)
set /a "gop_size=!timebase_denominator!"
REM set audio parameters
set    "a_b=224k"
set /a "a_freq=44100"
set /a "a_cutoff=18000"
REM set the bitrates or DVD
set /a "v=9000000"
set /a "v_min=3000000"
set /a "v_max=9200000"
set /a "v_buf=1835008"
set /a "v_pkt=2048"
set /a "v_mux=10080000"
set /a "v_gop_size=15"
set /a "v_rate=25"
set    "a_b=224k"
set /a "a_freq=44100"
set /a "a_cutoff=18000"

REM find the top level "first" target subfolder to create the video(s) in
FOR %%i IN ("!source_folder!") DO (
	set "source_drive=%%~di"
	set "source_path=%%~pi"
	set "source_drive_path=%%~dpi"
)
set "target_top_subfolder=!target_top_folder!\!source_path!\"
set "target_top_subfolder=%target_top_subfolder:\\=\%"
set "target_top_subfolder=%target_top_subfolder:\\=\%"
set "target_top_subfolder=%target_top_subfolder:\\=\%"
set "target_top_subfolder=%target_top_subfolder:\\=\%"
set "target_top_subfolder=%target_top_subfolder:\\=\%"
IF NOT EXIST "!target_top_subfolder!" (
	echo mkdir "!target_top_subfolder!"
	mkdir "!target_top_subfolder!"
)

REM define the filenames for the video(s) and related files
REM rightmost_foldername is already set, way above
set "ffmpeg_concat_input_file=!target_top_subfolder!!rightmost_foldername!-!tempheader!-ffmpeg-concat-input.txt"
set "ffmpeg_concat_log_file=!target_top_subfolder!!rightmost_foldername!-!tempheader!-ffmpeg-concat-log.log"
set "ffmpeg_concat_slideshow_HQ=!target_top_subfolder!!rightmost_foldername!-!tempheader!.slideshow.HQ.mp4"
set "ffmpeg_concat_slideshow_DVD=!target_top_subfolder!!rightmost_foldername!-!tempheader!.slideshow.DVD.mpg"

REM echo ----------------------------------------------------
REM echo target_top_subfolder="!target_top_subfolder!"
REM echo ffmpeg_concat_input_file="!ffmpeg_concat_input_file!"
REM echo ffmpeg_concat_log_file="!ffmpeg_concat_log_file!"
REM echo ffmpeg_concat_slideshow_HQ="!ffmpeg_concat_slideshow_HQ!"
REM echo ffmpeg_concat_slideshow_DVD="!ffmpeg_concat_slideshow_DVD!"
REM dir "!target_top_subfolder!"
REM echo ----------------------------------------------------

DEL /F "!ffmpeg_concat_input_file!" >NUL 2>&1
DEL /F "!ffmpeg_concat_log_file!" >NUL 2>&1
REM DEL /F "!ffmpeg_concat_slideshow_HQ!" >NUL 2>&1
REM DEL /F "!ffmpeg_concat_slideshow_DVD!" >NUL 2>&1

REM overwrite any existing ffmpeg_concat_input_file in the echo :- no extra characters before the greater than character, not even a space !
echo ffconcat version 1.0> "!ffmpeg_concat_input_file!"
REM parse the files, specifically excludsing directory type files "/a:-d"
@echo off
echo Finding resized files in "!target_top_subfolder!", populating file "!ffmpeg_concat_input_file!"
set /a c=0
set "x0="
set "x="
set "xe="
set "y="
for /f "tokens=*" %%G in ('dir /b /s /a:-d "!target_top_subfolder!"') DO (
	REM first, "escape" all backslashes in the full path name
	set "y=%%G"
	set ext4=!y:~-4!
	set ext5=!y:~-5!
	set ext6=!y:~-6!
	set "vid="
	set "pic="
	IF /I "!ext4!" == ".png"   set "pic=y"
	IF /I "!ext4!" == ".jpg"   set "pic=y"
	IF /I "!ext5!" == ".jpeg"  set "pic=y"
	IF /I "!ext4!" == ".gif"   set "pic=y"
	REM IF /I "!ext4!" == ".pdf"   set "pic=y"
	REM IF /I "!ext4!" == ".mp4"   set "vid=y"
	REM IF /I "!ext6!" == ".mpeg4" set "vid=y"
	REM IF /I "!ext4!" == ".mpg"   set "vid=y"
	REM IF /I "!ext5!" == ".mpeg"  set "vid=y"
	REM IF /I "!ext4!" == ".avi"   set "vid=y"
	REM IF /I "!ext6!" == ".mjpeg" set "vid=y"
	REM IF /I "!ext4!" == ".3gp"   set "vid=y"
	IF /I NOT "!vid!!pic!" == "" (
		set "x0=%%G"
		set "x=%%G"
		set "x=!x:\=\\!"
		set "xe=!x::=\:!"
		echo file '!x!'>> "!ffmpeg_concat_input_file!"
		REM echo duration !picture_duration!>> "!ffmpeg_concat_input_file!"
		echo file_packet_meta img_source_unescaped '%%G'>> "!ffmpeg_concat_input_file!"
		echo file_packet_meta img_source_escaped '!xe!'>> "!ffmpeg_concat_input_file!"
		set /a c+=1
	)
)
REM Repeat final picture as apparently -f concat can omit it
IF /I NOT "!x!!xe!!x0!" == "" (
	echo file '!x!'>> "!ffmpeg_concat_input_file!"
	REM echo duration !picture_duration!>> "!ffmpeg_concat_input_file!"
	echo file_packet_meta img_source_unescaped '!x0!'>> "!ffmpeg_concat_input_file!"
	echo file_packet_meta img_source_escaped '!xe!'>> "!ffmpeg_concat_input_file!"
	set /a c+=1
)
echo Finished finding !c! filenames, populating file "!ffmpeg_concat_input_file!"
REM type "!ffmpeg_concat_input_file!"

REM irfanview has already resized the images maintaining aspect ratio and padded to 1920x1080
set "cmd_HQ="
set "cmd_HQ=!cmd_HQ!"!slideshow_ffmpegexe64!" "
set "cmd_HQ=!cmd_HQ! -hide_banner -v info"
set "cmd_HQ=!cmd_HQ! -stats"
set "cmd_HQ=!cmd_HQ! -reinit_filter 0 -safe 0 -auto_convert 1"
set "cmd_HQ=!cmd_HQ! -f concat -i "!ffmpeg_concat_input_file!""
set "cmd_HQ=!cmd_HQ! -sws_flags lanczos+accurate_rnd+full_chroma_int+full_chroma_inp"
set "cmd_HQ=!cmd_HQ! -colorspace bt470bg -color_primaries bt470bg -color_trc gamma28 -color_range tv "
set "cmd_HQ=!cmd_HQ! -filter_complex ""
set "cmd_HQ=!cmd_HQ!format=yuv420p,"
set "cmd_HQ=!cmd_HQ!settb=expr=!timebase_numerator!/!timebase_denominator!,setpts=!picture_duration!*N/TB,"
set "cmd_HQ=!cmd_HQ!setdar=16/9"
set "cmd_HQ=!cmd_HQ!""
REM gamma28 is the substitute for bt470bg in -trc
set "cmd_HQ=!cmd_HQ! -colorspace bt470bg -color_primaries bt470bg -color_trc gamma28 -color_range tv "
set "cmd_HQ=!cmd_HQ! -strict experimental -c:v h264_nvenc -preset p7 -multipass fullres"
set "cmd_HQ=!cmd_HQ! -forced-idr 1 -g !gop_size!"
set "cmd_HQ=!cmd_HQ! -coder:v cabac -spatial-aq 1 -temporal-aq 1 -dpb_size 0"
set "cmd_HQ=!cmd_HQ! -bf:v 0 -bf:v 3 -b_ref_mode:v 0 -rc:v vbr -b:v %bitrate_target% -minrate:v %bitrate_min% -maxrate:v %bitrate_max% -bufsize %bitrate_bufsize%"
REM set "cmd_HQ=!cmd_HQ! -bf:v 0 -bf:v 3 -b_ref_mode:v 0 -rc:v vbr -cq:v 0 -b:v %bitrate_target% -minrate:v %bitrate_min% -maxrate:v %bitrate_max% -bufsize %bitrate_bufsize%"
set "cmd_HQ=!cmd_HQ! -profile:v high -level 5.2"
set "cmd_HQ=!cmd_HQ! -movflags +faststart+write_colr"
REM set "cmd_HQ=!cmd_HQ! -c:a libfdk_aac -ac 2 -b:a %a_b% -ar %a_freq% -cutoff %a_cutoff% 
set "cmd_HQ=!cmd_HQ! -an"
set "cmd_HQ=!cmd_HQ! -y "!ffmpeg_concat_slideshow_HQ!""

echo !cmd_HQ!
echo !cmd_HQ! >>"!ffmpeg_concat_log_file!" 2>&1
!cmd_HQ! >>"!ffmpeg_concat_log_file!" 2>&1
echo. >>"!ffmpeg_concat_log_file!" 2>&1

set "cmd_DVD="
set "cmd_DVD=!cmd_DVD!"!slideshow_ffmpegexe64!" "
set "cmd_DVD=!cmd_DVD! -hide_banner -v info"
set "cmd_DVD=!cmd_DVD! -stats"
set "cmd_DVD=!cmd_DVD! -i "!ffmpeg_concat_slideshow_HQ!" -probesize 200M -analyzeduration 200M"
set "cmd_DVD=!cmd_DVD! -sws_flags lanczos+accurate_rnd+full_chroma_int+full_chroma_inp -strict experimental"
set "cmd_DVD=!cmd_DVD! -filter_complex ""
REM set "cmd_DVD=!cmd_DVD!pad=0:1080:0:-1,scale=720:576:flags='lanczos+accurate_rnd+full_chroma_int+full_chroma_inp',"
set "cmd_DVD=!cmd_DVD!scale=720:576:flags='lanczos+accurate_rnd+full_chroma_int+full_chroma_inp',"
set "cmd_DVD=!cmd_DVD!format=yuv420p,"
set "cmd_DVD=!cmd_DVD!setdar=16/9"
set "cmd_DVD=!cmd_DVD!""
set "cmd_DVD=!cmd_DVD! -target pal-dvd -r %v_rate% -g %v_gop_size%"
set "cmd_DVD=!cmd_DVD! -b:v %v% -minrate:v %v_min% -maxrate:v %v_max% -bufsize %v_buf% -packetsize %v_pkt% -muxrate %v_mux%"
REM set "cmd_DVD=!cmd_DVD! -c:a ac3 -ac 2 -b:a %a_b% -ar %a_freq%
set "cmd_DVD=!cmd_DVD! -an"
set "cmd_DVD=!cmd_DVD! -y "!ffmpeg_concat_slideshow_DVD!""
REM

echo !cmd_DVD!
echo !cmd_DVD! >>"!ffmpeg_concat_log_file!" 2>&1
!cmd_DVD! >>"!ffmpeg_concat_log_file!" 2>&1
echo. >>"!ffmpeg_concat_log_file!" 2>&1

REM ---------------------------------------------------------------------------------------------------


pause

goto :eof

:irfanview_make_1920x1080
@setlocal ENABLEDELAYEDEXPANSION
@setlocal enableextensions
REM p1 = fully qualified target top folder including trailing slash
REM p2 = fully qualified source folder including drive
REM p3 = fully qualified iview .ini file
set "ini_folder=%~dp1\"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
set "ini_folder=%ini_folder:\\=\%"
REM echo ini_folder = '!ini_folder!'
set "source_subfolder=%~2\"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
set "source_subfolder=%source_subfolder:\\=\%"
REM echo source_subfolder = '!source_subfolder!'
set "target_subfolder=%~1%~p2\"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
set "target_subfolder=%target_subfolder:\\=\%"
REM echo target_subfolder = '!target_subfolder!'
IF NOT EXIST "!target_subfolder!" (
	echo mkdir "!target_subfolder!"
	mkdir "!target_subfolder!"
)
REM echo del "!target_subfolder!*.jpg"
del "!target_subfolder!*.jpg">NUL 2>&1
REM echo del "!target_subfolder!*.jpeg"
del "!target_subfolder!*.jpeg">NUL 2>&1
REM echo del "!target_subfolder!*.gif"
del "!target_subfolder!*.gif">NUL 2>&1
REM echo del "!target_subfolder!*.png"
del "!target_subfolder!*.png">NUL 2>&1
REM echo del "!target_subfolder!*.pdf"
REM del "!target_subfolder!*.pdf">NUL 2>&1

set cmd1="!slideshow_Irfanviewexe64!" "!source_subfolder!*.jpg"  /ini="!ini_folder!" /advancedbatch /convert="!target_subfolder!*.jpg"
set cmd2="!slideshow_Irfanviewexe64!" "!source_subfolder!*.jpeg" /ini="!ini_folder!" /advancedbatch /convert="!target_subfolder!*.jpeg"
set cmd3="!slideshow_Irfanviewexe64!" "!source_subfolder!*.gif"  /ini="!ini_folder!" /advancedbatch /convert="!target_subfolder!*.gif"
set cmd4="!slideshow_Irfanviewexe64!" "!source_subfolder!*.png"  /ini="!ini_folder!" /advancedbatch /convert="!target_subfolder!*.png"
REM set cmd5="!slideshow_Irfanviewexe64!" "!source_subfolder!*.pdf"  /ini="!ini_folder!" /advancedbatch /convert="!target_subfolder!*.pdf"
echo !cmd1!
!cmd1!
echo !cmd2!
!cmd2!
echo !cmd3!
!cmd3!
echo !cmd4!
!cmd4!
REM echo !cmd5!
REM !cmd5!

goto :eof



REM ---------------------------------------------------------------------------------------------------
:create_irfanview_ini_file
REM p1 = the fully qualified .ini filename to create
REM per example at https://stackoverflow.com/questions/46135442/how-to-resize-image-with-same-width-and-height-without-quality-loss-using-irfanv
@echo off
(
echo ^[Batch^]
echo AdvCrop=0
echo AdvCropX=0
echo AdvCropY=0
echo AdvCropW=0
echo AdvCropH=0
echo AdvCropC=0
echo AdvResize=1
echo AdvResizeOpt=0
echo AdvResizeW=1920.00
echo AdvResizeH=1080.00
echo AdvResizeL=0.00
echo AdvResizeS=0.00
echo AdvResizeMP=0.00
echo AdvResample=1
echo AdvResizePerc=0
echo AdvResizePercW=0.00
echo AdvResizePercH=0.00
echo AdvDPI=0
echo AdvResizeUnit=0
echo AdvResizeRatio=1
echo AdvNoEnlarge=0
echo AdvNoShrink=0
echo AdvResizeOnDpi=0
echo AdvResizeMaxSize=1
echo AdvResizeMinSize=0
echo AdvCanvas=1
echo AdvAddText=0
echo AdvWatermark=0
echo AdvReplaceColor=0
echo AdvAddFrame=0
echo AdvUseBPP=0
echo AdvBPP=0
echo AdvUseFSDither=1
echo AdvDecrQuality=0
echo AdvAutoRGB=0
echo AdvHFlip=0
echo AdvVFlip=0
echo AdvRLeft=0
echo AdvRRight=0
echo AdvGray=0
echo AdvInvert=0
echo AdvSharpen=0
echo AdvGamma=0
echo AdvContrast=0
echo AdvBrightness=0
echo AdvSaturation=0
echo AdvColR=0
echo AdvColG=0
echo AdvColB=0
echo AdvSharpenVal=2
echo AdvGammaVal=1.05
echo AdvContrastVal=0
echo AdvBrightnessVal=0
echo AdvSaturationVal=0
echo AdvColRVal=0
echo AdvColGVal=0
echo AdvColBVal=0
echo AdvDelOrg=0
echo AdvOverwrite=1
echo AdvSubdirs=1
echo AdvSaveOldDate=1
echo AdvAllPages=1
echo UseAdvOptionsOrder=0
echo AdvFineR=0
echo AdvFineRVal=0.00
echo AdvBlur=0
echo AdvBlurVal=1
echo AdvEffects=0
echo AdvRbg=0
echo AdvBgr=0
echo AdvBrg=0
echo AdvGrb=0
echo AdvGbr=0
echo AdvAutoCrop=0
echo AdvOptionsOrder=
echo AdvEffectsValue=
echo ^[BatchText^]
echo AddText=
echo TextCoord=0;0;100;100;
echo Corner=0
echo Orientation=0
echo TranspText=1
echo SemiTranspText=0
echo FitColorW=1
echo OutlineFill=0
echo Outline=0
echo Emboss=0
echo Shadow=0
echo FontColor=65280
echo TxtBgkr=16777215
echo FontParam=-13^|0^|0^|0^|400^|0^|0^|0^|0^|1^|2^|1^|49^|
echo Font=Courier
echo Outline1=
echo Canvas=0

echo ^[BatchCanvas^]
echo CanvMethod=1
echo CanvL=10
echo CanvR=10
echo CanvT=10
echo CanvB=10
echo CanvInside=1
echo CanvW=1920
echo CanvH=1080
echo CanvCorner=4
echo CanvRatio=7
echo CanvRatioEdit=1.0000
echo CanvBlur=1
echo CanvBlurVal=50
echo CanvGammaVal=1.00
echo CanvColor=0

echo ^[BatchReplaceColor^]
echo ReplaceColorOld=0
echo ReplaceColorNew=0
echo ReplaceColorTol=0

echo ^[BatchWatermark^]
echo Option=0
echo Coord=0;0;100;100;
echo Corner=0
echo Transp=65535
echo Image=no image
echo Color=65535

echo ^[BatchFrame^]
echo FrameStyle=0
echo FrameSizes=20,0,0,0
echo FrameColors=13158600,0,0,2105376

echo ^[Effects^]
echo AutoCropTol=0
echo RotateDegrees=7.00
echo RotateColor=0
echo RotateOldCanvas=0
echo RotateNewMethod=0
echo RotateAntialias=1
echo RotateOldImage=0
echo RotateMaxOldRectangle=0
echo RotateSharpen=0
echo RotateSharpenVal=20
echo ColorDialogCustom=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;
echo HistUseCurves=3
echo Unsharp=4
echo Filter=12
echo CanvL=10
echo CanvR=10
echo CanvT=10
echo CanvB=10
echo CanvInside=1
echo CanvColor=0
echo CanvMethod=0
echo CanvW=1920
echo CanvH=1080
echo CanvCorner=4
echo CanvRatio=1
echo CanvRatioEdit=1.00
echo CanvBlur=1
echo CanvBlurVal=50
echo CanvGammaVal=1.00
echo ReplaceColorOld=0
echo ReplaceColorNew=0
echo ReplaceColorTol=0
echo Sharpen=50
echo MedianFilter=5

echo ^[JPEG^]
echo Load Grayscale=0
echo ExifRotate=1
echo Save Quality=100
echo Save Progressive=0
echo Save Grayscale=0
echo NoSampling=0
echo KeepExif=1
echo KeepXmp=1
echo KeepCom=1
echo KeepIptc=1
echo KeepQuality=0
echo ExifOrient=1
echo SetSize=0
echo FileSize=65.00
echo QuantSmooth=0
echo ShowPreview=0
echo Profile_dcw-1920x108=2;100^|0^|0^|0^|1^|1^|1^|1^|0^|1^|0^|0^|0^|2^|0^|0^|;65.00;
echo Profiles=dcw-1920x108^|
) > "%~1"
dir /b "%~1"
REM type "%~1"
goto :eof



REM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
REM --- start set a temp header to date and time
:maketempheader
set "Datex=%DATE: =0%"
set yyyy=!Datex:~10,4!
set mm=!Datex:~7,2!
set dd=!Datex:~4,2!
set "Timex=%time: =0%"
set hh=!Timex:~0,2!
set min=!Timex:~3,2!
set ss=!Timex:~6,2!
set ms=!Timex:~9,2!
ECHO !DATE! !TIME! As at !yyyy!.!mm!.!dd!_!hh!.!min!.!ss!.!ms!  COMPUTERNAME="!COMPUTERNAME!"
set tempheader=!yyyy!.!mm!.!dd!.!hh!.!min!.!ss!.!ms!-!COMPUTERNAME!
REM --- end set a temp header to date and time
goto :eof
REM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
