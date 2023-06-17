# Q'N Auto Slideshow Creator for Windows   

Download / Setup / Configure then Fire-and-wait-a-long-time.    

A python3/vapoursynth script using ffmpeg to create a 'HD' .mp4 slideshow
from images and video clips in specified folders,
with background audio from a nominated folder of audio files, 
with video audio overlayed onto the background audio.    

This is a hack-up of good stuff provided earlier by \_AI\_ in thread   
https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio 
\_AI\_ has much better and elegant code which works with audio ... consider looking for that on GITHUB.    
___


## Limitations

The process is quite slow, so we automatically encode 150 pics/videos or so 
at a time in `chunks` and concatenate them at the end.    

The background audio is not looped, if it is shorter than the resulting slideshow video then there will be silence at the end.
You can easily add more background audio, it's up to you, background audio is auto-trimmed to the duration of the slideshow video.

We're good for 1,000 or so images/videos in a set of directory trees per slideshow, perhaps 5,000 max,
although the number really is up to you. Recommend you estimate the duration as `num_pics_and_images * 3` 
(3 seconds per pic) although videos clip durations will affect estimate a fair bit.    

Attempting `4k` resolutions requires really **huge** amounts of temporary disk space and **very long** encode times... _c'est la vie_.
Testing shows `4k` slideshows of home pictures does not appear any better (and sometimes worse) than `1080p` on a TV.   

The legacy encoder logic does not handle 576p nor 480p resolutions (Anamorphic).

If you wanted a .mpg file to burn to DVD then use another tool, eg FFmpeg, to convert (transcode)
the final mp4. It's easy enough.    

# How-to : short version

1. Create a new _empty_ folder on a disk with **lots** of free space
2. Download `Setup.bat` from https://raw.githubusercontent.com/hydra3333/vpy_slideshow/main/Setup.bat into that folder    
3. Download `wget.exe` from https://eternallybored.org/misc/wget/1.21.3/64/wget.exe into that folder    
4. Double-click `Setup.bat` to download and prepare the necessary files
6. Double-click `QN_Auto_Slideshow_Creator_for_Windows.bat` to create a template `slideshow_settings.py`
7. Edit `slideshow_settings.py`. Syntax is **critical**. All brackets, matching quotes, and commas etc must be **perfect** or the process will fail. 
8. Double-click `QN_Auto_Slideshow_Creator_for_Windows.bat` which will consume `slideshow_settings.py` and create the slideshow according to your settings
9. Look for the resulting slideshow file you specified with settings `FINAL_MP4_WITH_AUDIO_FILENAME`

# How-to : the details

## Portable "Installation" (x64 only)

It's portable. Stuff all goes into the folder tree which you create first.    
To uninstall later, just delete the folder.    

Portable Python3 and Portable Vapoursynth (matching versions) and FFmpeg and MediaInfo etc need to
be downloaded into the folder tree and a bunch of dependencies "portable installed" into there as well.

### 1. Create a fresh new directory   

Create a new EMPTY directory somewhere on a disk which has a LOT of free disk space. Try not to use `C:`.   
I will need, say, 5 Gb free disk space per 100 pics/videos, which will be used for temporary working files.   
Later, once installed and configured, you may choose to re-configure to use a temporary folder on another disk.   

**For the purpose of examples below, let's assume you created a new folder called `D:\QN_Auto_Slideshow_Creator_for_Windows`**    

### 2. Download a fresh copy of the portable stuff

#### 2.0 A note about security
Many people are wary of downloading exe files etc.   So am I.    
If you are as well, look in the file `Setup.bat` to see what needs downloading and unzipping and placed where;
and what `portable pip` and `vsrepo` commands you could do yourself in a dos window when cd'd into the right directories.   
Good luck with trying to do it yourself, it's a bit involved.    
Recommend you just review it and use the `Setup.bat` thing below.    

#### 2.1 Download the Setup et al

Look at this url in a browser: https://github.com/hydra3333/vpy_slideshow   
Notice file `Setup.bat`   

Download `Setup.bat` using this link https://raw.githubusercontent.com/hydra3333/vpy_slideshow/main/Setup.bat    
... once it is displayed in your browser, "save as" into the fresh new directory you created above.

Download the ubiquitous `wget.exe` with this link https://eternallybored.org/misc/wget/1.21.3/64/wget.exe and
also save it into the fresh new directory you created above.  

**Notes:**    
- `wget.exe` will be used to download stuff like portable Python, portable VapourSynth, a recent ffmpeg build,
and the other files necessary to make a slideshow.    
- If you don't download `wget.exe` into the same directory as `Setup.bat` the Setup Process will fail.    
- Nothing gets "installed", everything is just all files in the directory tree.    
- _More gobbledygook:_ ... except for the pip module installs ... pip puts bits of them (eg dependencies which get collected) 
in your username's temporary folder, i.e. something like `C:\Users\your_username\AppData\Local\Temp`,
instead of where we tell pip to install the module for which the pip "collecting process" is occurring. "A choice
of one", so we just live with it.    

### 2.1 Run Setup et al

Now that you have downloaded `Setup.bat`, in File Explorer double-click on `Setup.bat` to run it.    
A DOS window will pop up showing all the downloads and pip's and vsrepo's and unzips as they happen.   

When `Setup.bat` is finished, you can see all of the files in the directory tree.    
These give you   
- portable Python x64 (3.11.2 last time I looked) ... version has to match the Vapoursynth version requirement   
- portable Vapoursynth x64 (R62 last time I looked, depends on python 3.11.x)   
- relevant Python x64 pip dependencies   
- relevant Vapoursynth vsrepo x64 dependencies   
- latest FFmpeg and MediaInfo exes and MediaInfo dll
- a few files necessary to run Q'N Auto Slideshow Creator for Windows   

## Preparation then Configuration    

### 1. Preparation

Check your disks and their free disk space.    
During configuration you may choose to specify a different disk/folder to hold
the very large set of temporary files ... circa 5 Gb per 100 files will be required.

You need to create a folder somewhere to hold audio files (eg music) you want played
during the slideshow as "background audio" ... even if you do not want any background audio.   
Per the install example, something like this is good: `D:\QN_Auto_Slideshow_Creator_for_Windows\BACKGROUND_AUDIO_INPUT_FOLDER`.    

Copy any audio files to that folder.  Uplifting type background instrumental music is good, even classical :)    
Rename the copied files to your liking, since they will be read in alphabetical order into one background audio track.

### 2. Create and edit Configuration file `slideshow_settings.py`    

Configuration file `slideshow_settings.py` tells your requirements to the process.    

In File Explorer, double-click on `QN_Auto_Slideshow_Creator_for_Windows.bat` and it will yield a pop-up dos box
with bunch of messages to ignore, and also generate a template file called `slideshow_settings.py`.    
That is a once-off thing, unless you delete `slideshow_settings.py` to start afresh.    
You can safely close the pop-up dos box after it's completed.    

Now, using your favourite text editor, eg Notepad, edit `slideshow_settings.py` and make required changes.   
Syntax is critical, all brackets, matching quotes, and commas etc must be **perfect** or the process will fail.    
Look for and change the settings you need. Please be careful or you will have to re-edit ;)    

**At a minimum:**
- `ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS` - specify one or more quoted and comma separated Folder names of pics/videos
- `BACKGROUND_AUDIO_INPUT_FOLDER` - specify a Folder containing audio files (in sequence) to make an audio background track (it is not looped if too short). No files in folder = silent background
- `FINAL_MP4_WITH_AUDIO_FILENAME` - specify the directory and filename of the FINAL slideshow .mp4    

**Optionally:**    
- `RECURSIVE` - whether to recurse into the subfolders of `ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS`
- `TARGET_RESOLUTION` - `HD 1080p` is the sweet spot, testing shows. PAL `1080p_pal`, or in NTSC land `1080p_ntsc` to get 29.976 framerate
- `TARGET_VIDEO_BITRATE` ... the defaults are close enough, use one of them matching `TARGET_RESOLUTION`
- `DURATION_PIC_SEC` - in seconds, duration that each pic is displayed in the slideshow
- `DURATION_MAX_VIDEO_SEC`- in seconds, maximum duration a video clip to be shown in the slideshow (trimmed to this)
- `TEMP_FOLDER` - point to a folder on a disk with plenty of free disk space 
- `SUBTITLE_DEPTH` - you  can have subtitles of the folder containing each pic/image
- `MAX_FILES_PER_CHUNK` ... more than 150 files encoded at one will slow the process to a crawl, like 2 day execution times or worse ... 50 to 150 is "doable"

**Don't touch any of the other settings unless you're prepared to fix things.**    

Here's an example of settings with edits already made:   
```
settings = {
	'ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS':	[
													r'H:\our_home_pics\1994',
													r'H:\our_home_pics\1995',
												],	# a list, one or more folders to look in for slideshow pics/videos. the r in front of the string is CRITICAL
	'RECURSIVE':	True,		# case sensitive: whether to recurse the source folder(s) looking for slideshow pics/videos
	'TEMP_FOLDER':	r'D:\QN_Auto_Slideshow_Creator_for_Windows\TEMP',		# folder where temporary files go; USE A DISK WITH LOTS OF SPARE DISK SPACE - CIRCA 6 GB PER 100 PICS/VIDEOS
	'BACKGROUND_AUDIO_INPUT_FOLDER':	r'H:\some_existing_directory\BACKGROUND_AUDIO_INPUT_FOLDER',		# Folder containing audio files (in sequence) to make an audio background track (it is not looped if too short). No files = silent background.
	'FINAL_MP4_WITH_AUDIO_FILENAME':	r'D:\some_existing_directory\slideshow_1994_1995.mp4',		# the filename of the FINAL slideshow .mp4
	'SUBTITLE_DEPTH':	0,		# how many folders deep to display in subtitles; use 0 for no subtitling
	'SUBTITLE_FONTSIZE':	18,		# fontsize for subtitles, leave this alone unless confident
	'SUBTITLE_FONTSCALE':	1.0,		# fontscale for subtitles, leave this alone unless confident
	'DURATION_PIC_SEC':	3.0,		# in seconds, duration each pic is shown in the slideshow
	'DURATION_CROSSFADE_SECS':	0.5,		# in seconds duration crossfade between pic, leave this alone unless confident
	'CROSSFADE_TYPE':	'random',		# random is a good choice, leave this alone unless confident
	'CROSSFADE_DIRECTION':	'left',		# Please leave this alone unless really confident
	'DURATION_MAX_VIDEO_SEC':	7200.0,		# in seconds, maximum duration each video clip is shown in the slideshow
	'TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB':	-18,		# normalize background audio to this maximum db
	'TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY':	-30,		# how many DB to reduce backround audio during video clip audio overlay
	'TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB':	-12,		# normalize video clip audio to this maximum db; camera vids are quieter so gain them
	'MAX_FILES_PER_CHUNK':	150,		# how many images/videos to process in each chunk (more=slower)
	'DEBUG':	False,		# see and regret seeing, ginormous debug output
	'FFMPEG_PATH':	r'D:\ssTEST\Vapoursynth_x64\ffmpeg.exe',		# Please leave this alone unless really confident
	'FFPROBE_PATH':	r'D:\ssTEST\Vapoursynth_x64\ffprobe.exe',		# Please leave this alone unless really confident
	'VSPIPE_PATH':	r'D:\ssTEST\Vapoursynth_x64\vspipe.exe',		# Please leave this alone unless really confident
	'FFMPEG_ENCODER':	'libx264',		# Please leave this alone unless really confident. One of ['libx264', 'h264_nvenc']. h264_nvenc only works on "nvidia 2060 Super" upward.
	'TARGET_RESOLUTION':	'1080p_pal',		# eg 1080p : One of ['1080p_pal', '4k_pal', '2160p_pal', '1080p_ntsc', '4k_ntsc', '2160p_ntsc'] only. Others result in broken aspect ratios.
	'TARGET_VIDEO_BITRATE':	'4.5M',		# eg 4.5M : [{'1080p_pal': '4.5M'}, {'4k_pal': '15M'}, {'2160p_pal': '15M'}, {'1080p_ntsc': '4.5M'}, {'4k_ntsc': '15M'}, {'2160p_ntsc': '15M'}]
	'slideshow_CONTROLLER_path':	r'D:\ssTEST\slideshow_CONTROLLER.py',		# Please leave this alone unless really confident
	'slideshow_LOAD_SETTINGS_path':	r'D:\ssTEST\slideshow_LOAD_SETTINGS.py',		# Please leave this alone unless really confident
	'slideshow_ENCODER_legacy_path':	r'D:\ssTEST\slideshow_ENCODER_legacy.vpy',		# Please leave this alone unless really confident
}
```

## Starting the slideshow process    

1. If it already exists (eg in a re-run), delete the file you specified in `FINAL_MP4_WITH_AUDIO_FILENAME`   

2. In File Explorer, double-click on `QN_Auto_Slideshow_Creator_for_Windows.bat` and it will yield a pop-up dos box
with bunch of messages to ignore.    

3. Let it run. It will take a long time, showing unintelligible log messages qas it goes.

4. If the final messages in the pop-up dos box look like an error, examine the final messages ... since there
is likely an error in your edits to `slideshow_settings.py`.    

5. You can safely close the pop-up dos box after it's completed.    

6. Locate try to play the file you specified in `FINAL_MP4_WITH_AUDIO_FILENAME`   

7. If it failed, look for and delete all temporary files in the folder you specified in `TEMP_FOLDER`


## Re-running the slideshow process    

OK, you created a slideshow and want to create another.    

So, re-edit `slideshow_settings.py` and make required changes, specifically to use new inputs/output:
- `ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS` - specify one or more quoted and comma separated Folder names of pics/videos
- `FINAL_MP4_WITH_AUDIO_FILENAME` - specify the directory and filename of the FINAL slideshow .mp4    

Then refer above to **Starting the slideshow process**


___
## of no possible interest to anyone

I ran a 'show_unique_properties' thing over our archive of home pics and videos, and found a variety of cameras used. 
Each camera probably had its own issues with, and settings for, video and image properties and metadata.
Yes, testing indicated they were all different.  

`Q'N Auto Slideshow Creator for Windows` handles all that (mostly).    

```
 'EXIF_Model': '',
 'EXIF_Model': '<KENOX S630  / Samsung S630>',
 'EXIF_Model': '1234',
 'EXIF_Model': '5300',
 'EXIF_Model': '5800 Xpres',
 'EXIF_Model': '5MP-9Q3',
 'EXIF_Model': '6120c',
 'EXIF_Model': '6288',
 'EXIF_Model': '6300',
 'EXIF_Model': 'A411',
 'EXIF_Model': 'C4100Z,C4000Z',
 'EXIF_Model': 'C8080WZ',
 'EXIF_Model': 'Canon DIGITAL IXUS 430',
 'EXIF_Model': 'Canon DIGITAL IXUS 50',
 'EXIF_Model': 'Canon DIGITAL IXUS 500',
 'EXIF_Model': 'Canon DIGITAL IXUS 980 IS',
 'EXIF_Model': 'Canon DIGITAL IXUS v3',
 'EXIF_Model': 'Canon EOS-1D',
 'EXIF_Model': 'Canon EOS-1D X',
 'EXIF_Model': 'Canon EOS-1Ds Mark II',
 'EXIF_Model': 'Canon EOS 10D',
 'EXIF_Model': 'Canon EOS 200D',
 'EXIF_Model': 'Canon EOS 20D',
 'EXIF_Model': 'Canon EOS 20D\x00',
 'EXIF_Model': 'Canon EOS 300D DIGITAL',
 'EXIF_Model': 'Canon EOS 30D',
 'EXIF_Model': 'Canon EOS 350D DIGITAL',
 'EXIF_Model': 'Canon EOS 40D',
 'EXIF_Model': 'Canon EOS 550D',
 'EXIF_Model': 'Canon EOS 5D',
 'EXIF_Model': 'Canon EOS 60D',
 'EXIF_Model': 'Canon EOS 6D',
 'EXIF_Model': 'Canon EOS 7D',
 'EXIF_Model': 'Canon EOS DIGITAL REBEL',
 'EXIF_Model': 'Canon EOS DIGITAL REBEL XT',
 'EXIF_Model': 'Canon EOS DIGITAL REBEL XTi',
 'EXIF_Model': 'Canon EOS Kiss Digital N',
 'EXIF_Model': 'Canon MG3600 series Network',
 'EXIF_Model': 'Canon PowerShot A3100 IS',
 'EXIF_Model': 'Canon PowerShot A3200 IS',
 'EXIF_Model': 'Canon PowerShot A3200 IS\x00\x00\x00\x00\x00\x00\x00',
 'EXIF_Model': 'Canon PowerShot A400',
 'EXIF_Model': 'Canon PowerShot A520',
 'EXIF_Model': 'Canon PowerShot A570 IS',
 'EXIF_Model': 'Canon PowerShot A620',
 'EXIF_Model': 'Canon PowerShot A720 IS',
 'EXIF_Model': 'Canon PowerShot A75',
 'EXIF_Model': 'Canon PowerShot A80',
 'EXIF_Model': 'Canon PowerShot A95',
 'EXIF_Model': 'Canon PowerShot A95\x00',
 'EXIF_Model': 'Canon PowerShot G5',
 'EXIF_Model': 'Canon PowerShot G6',
 'EXIF_Model': 'Canon PowerShot S1 IS',
 'EXIF_Model': 'Canon PowerShot S2 IS',
 'EXIF_Model': 'Canon PowerShot S3 IS',
 'EXIF_Model': 'Canon PowerShot S50',
 'EXIF_Model': 'CONTAX i4R    ',
 'EXIF_Model': 'COOLPIX P530',
 'EXIF_Model': 'COOLPIX P600',
 'EXIF_Model': 'COOLPIX S6100',
 'EXIF_Model': 'CYBERSHOT',
 'EXIF_Model': 'DC-3305    ',
 'EXIF_Model': 'Digimax 201',
 'EXIF_Model': 'DiMAGE A1',
 'EXIF_Model': 'DiMAGE Z5',
 'EXIF_Model': 'DMC-FT2',
 'EXIF_Model': 'DMC-FT3',
 'EXIF_Model': 'DMC-FT5',
 'EXIF_Model': 'DMC-FT6',
 'EXIF_Model': 'DMC-FX7',
 'EXIF_Model': 'DMC-FX8',
 'EXIF_Model': 'DMC-FZ30',
 'EXIF_Model': 'DMC-TS2',
 'EXIF_Model': 'DMC-TS3',
 'EXIF_Model': 'DSC-H2',
 'EXIF_Model': 'DSC-H5',
 'EXIF_Model': 'DSC-N1',
 'EXIF_Model': 'DSC-P10',
 'EXIF_Model': 'DSC-P92',
 'EXIF_Model': 'DSC-P93',
 'EXIF_Model': 'DSC-RX100',
 'EXIF_Model': 'DSC-T7',
 'EXIF_Model': 'DSC-TX20',
 'EXIF_Model': 'DSC-W1',
 'EXIF_Model': 'DSC-W40',
 'EXIF_Model': 'DSLR-A100',
 'EXIF_Model': 'DYNAX 5D',
 'EXIF_Model': 'E-300',
 'EXIF_Model': 'E-300           ',
 'EXIF_Model': 'E-500           ',
 'EXIF_Model': 'E-500           \x00',
 'EXIF_Model': 'E-510           ',
 'EXIF_Model': 'E4500',
 'EXIF_Model': 'E5653\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
 'EXIF_Model': 'E5700',
 'EXIF_Model': 'E5900',
 'EXIF_Model': 'E65',
 'EXIF_Model': 'E8700',
 'EXIF_Model': 'FinePix F50fd  ',
 'EXIF_Model': 'FinePix L30',
 'EXIF_Model': 'FinePix S5600  ',
 'EXIF_Model': 'FinePix S9100',
 'EXIF_Model': 'GT-C5510',
 'EXIF_Model': 'GT-I9100',
 'EXIF_Model': 'GT-I9100\x00',
 'EXIF_Model': 'GT-I9305T',
 'EXIF_Model': 'HERO4 Silver',
 'EXIF_Model': 'HERO7 Black\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
 'EXIF_Model': 'HP pstc6100',
 'EXIF_Model': 'HTC Desire',
 'EXIF_Model': 'iPad',
 'EXIF_Model': 'iPhone 3GS',
 'EXIF_Model': 'iPhone 4',
 'EXIF_Model': 'iPhone 5c',
 'EXIF_Model': 'iPhone 6',
 'EXIF_Model': 'iPhone 6 Plus',
 'EXIF_Model': 'iPhone 6s',
 'EXIF_Model': 'iPhone SE (2nd generation)',
 'EXIF_Model': 'iPhone X',
 'EXIF_Model': 'KODAK CX6330 ZOOM DIGITAL CAMERA',
 'EXIF_Model': 'KODAK EASYSHARE C1013 DIGITAL CAMERA',
 'EXIF_Model': 'KODAK EASYSHARE DX3700 Digital Camera',
 'EXIF_Model': 'KS360',
 'EXIF_Model': 'MG6200 series',
 'EXIF_Model': 'MP270 series',
 'EXIF_Model': 'my411X',
 'EXIF_Model': 'NIKON D200',
 'EXIF_Model': 'NIKON D50',
 'EXIF_Model': 'NIKON D70',
 'EXIF_Model': 'NIKON D70\x00',
 'EXIF_Model': 'NIKON D7000',
 'EXIF_Model': 'NIKON D70s',
 'EXIF_Model': 'NIKON D7200',
 'EXIF_Model': 'NIKON D80',
 'EXIF_Model': 'NIKON D800',
 'EXIF_Model': 'Omni-vision OV9655-SXGA',
 'EXIF_Model': 'OPPO A72',
 'EXIF_Model': 'PENTAX *ist DS     ',
 'EXIF_Model': 'PENTAX Optio 33LF',
 'EXIF_Model': 'PENTAX Optio WP',
 'EXIF_Model': 'Perfection V600',
 'EXIF_Model': 'Portable Scanner',
 'EXIF_Model': 'RS4110Z     ',
 'EXIF_Model': 'S8300',
 'EXIF_Model': 'SAMSUNG ES30/VLUU '
 'EXIF_Model': 'SLP1000SE',
 'EXIF_Model': 'SM-A520F',
 'EXIF_Model': 'SM-G900I',
 'EXIF_Model': 'SM-G925I',
 'EXIF_Model': 'SM-G935F',
 'EXIF_Model': 'SM-G955F',
 'EXIF_Model': 'SM-G973F',
 'EXIF_Model': 'SM-G975F',
 'EXIF_Model': 'SM-J100Y',
 'EXIF_Model': 'SM-J250G',
 'EXIF_Model': 'ST66 / ST68',
 'EXIF_Model': 'Sx500A',
 'EXIF_Model': 'T4_T04',
 'EXIF_Model': 'u20D,S400D,u400D',
 'EXIF_Model': 'u30D,S410D,u410D',
 'EXIF_Model': 'u790SW,S790SW   ',
 'EXIF_Model': 'uD800,S800      ',
 'EXIF_Model': 'Unknown',
 'EXIF_Model': 'VG140,D715      ',
 'EXIF_Model': 'Z610i',
{'EXIF_Model': 'Canon EOS 300D DIGITAL',
{'EXIF_Model': 'KODAK Z740 ZOOM DIGITAL CAMERA',
{'EXIF_Model': 'Sony Visual Communication Camera', 'EXIF_Software': 'ArcSoft WebCam Companion 3', 'EXIF_Copyright': 'ArcSoft Inc.'}
```
