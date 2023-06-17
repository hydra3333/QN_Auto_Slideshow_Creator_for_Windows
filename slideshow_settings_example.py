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
	#'FFMPEG_ENCODER':	'libx264',		# Please leave this alone unless really confident. One of ['libx264', 'h264_nvenc']. h264_nvenc only works on "nvidia 2060 Super" upward.
	'FFMPEG_ENCODER':	'h264_nvenc',		# Please leave this alone unless really confident. One of ['libx264', 'h264_nvenc']. h264_nvenc only works on "nvidia 2060 Super" upward.
	'TARGET_RESOLUTION':	'1080p_pal',		# eg 1080p : One of ['1080p_pal', '4k_pal', '2160p_pal', '1080p_ntsc', '4k_ntsc', '2160p_ntsc'] only. Others result in broken aspect ratios.
	'TARGET_VIDEO_BITRATE':	'4.5M',		# eg 4.5M : [{'1080p_pal': '4.5M'}, {'4k_pal': '15M'}, {'2160p_pal': '15M'}, {'1080p_ntsc': '4.5M'}, {'4k_ntsc': '15M'}, {'2160p_ntsc': '15M'}]
	'slideshow_CONTROLLER_path':	r'D:\ssTEST\slideshow_CONTROLLER.py',		# Please leave this alone unless really confident
	'slideshow_LOAD_SETTINGS_path':	r'D:\ssTEST\slideshow_LOAD_SETTINGS.py',		# Please leave this alone unless really confident
	'slideshow_ENCODER_legacy_path':	r'D:\ssTEST\slideshow_ENCODER_legacy.vpy',		# Please leave this alone unless really confident
}
