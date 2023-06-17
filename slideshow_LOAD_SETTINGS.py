# 1.	Modifying the sys.path list in a module DOES NOT not affect the sys.path of other modules or the main program.
# 2.	Modifying the sys.path list in the MAIN PROGRAM WILL affect the search path for	all modules imported by that program.
# Ensure we can import modules from ".\" by adding the current default folder to the python path.
# (tried using just PYTHONPATH environment variable but it was unreliable)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import slideshow_GLOBAL_UTILITIES_AND_VARIABLES as UTIL	# define utilities and make global variables available to everyone

import vapoursynth as vs
from vapoursynth import core
core = vs.core
#core.num_threads = 1
import multiprocessing
import importlib
import re
import argparse
from functools import partial
import pathlib
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import datetime
#from datetime import datetime, date, time, timezone
from fractions import Fraction
from ctypes import *		# for mediainfo ... load via ctypes.CDLL(r'.\MediaInfo.dll')
from typing import Union	# for mediainfo
from typing import NamedTuple
from collections import defaultdict, OrderedDict
from enum import Enum
from enum import auto
#from strenum import StrEnum
#from strenum import LowercaseStrEnum
#from strenum import UppercaseStrEnum
import itertools
import math
import random
import glob
import configparser	# or in v3: configparser 
import yaml
import json
import pprint
import ast
import uuid
import logging

# for subprocess control eg using Popen
import time
from queue import Queue, Empty
from threading import Thread

import gc	# for inbuilt garbage collection
# THE NEXT STATEMENT IS ONLY FOR DEBUGGING AND WILL CAUSE EXTRANEOUS OUTPUT TO STDERR
#gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)	# for debugging, additional garbage collection settings, writes to stderr https://docs.python.org/3/library/gc.html to help detect leaky memory issues
num_unreachable_objects = gc.collect()	# collect straight away

#from PIL import Image, ExifTags, UnidentifiedImageError
#from PIL.ExifTags import TAGS

#import pydub
#from pydub import AudioSegment

#CDLL(r'MediaInfo.dll')				# note the hard-coded folder	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
#from MediaInfoDLL3 import MediaInfo, Stream, Info, InfoOption		# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
##from MediaInfoDLL3 import *											# per https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py

UTIL.DEBUG = False

### ********** end of common header ********** 
#global MI
#MI = MediaInfo()

#core.std.LoadPlugin(r'DGDecodeNV.dll')
#core.avs.LoadPlugin(r'DGDecodeNV.dll')

# Based on ChatGPT, we are no longer using settings.json, we will use SLIDESHOW_SETTINGS.py
# This will allow us to use descriptive comments in SLIDESHOW_SETTINGS.py which a user must edit.
# If the user mucks up python syntax, we rely on the module crashing on import.

# What we are doing instead is to re-import SLIDESHOW_SETTINGS.py every time load_settings() is called.
# Like this
#    import importlib
#    importlib.reload(mymodule)  # Reload the module

# check the files which should exist do exist
def check_file_exists_3333(file, text):
	if not os.path.exists(file):
		print(f"load_settings: ERROR: the specified {text} File '{file}' does not exist",flush=True,file=sys.stderr)
		sys.exit(1)
	return

def check_folder_exists_3333(folder, text):
	if not os.path.isdir(folder):
		print(f"load_settings: ERROR: the specified {text} folder does not exist: '{folder}' does not exist",flush=True,file=sys.stderr)
		sys.exit(1)
	return

def create_py_file_from_specially_formatted_list(dot_py_filename, specially_formatted_list):
	# a dict may contain strings defined like r''
	# parse a specially formatted LIST [key, value, annotation_text]
	# and create a .py file containing settings = { key: value, # annotation_text ... }
	def make_r_prefix(value):
		if isinstance(value, str):
			if  '\\' in repr(value):
				return 'r' + repr(value).replace('\\\\', '\\')
			else:
				return repr(value)
		#elif isinstance(value, int):
		#	return str(value)
		#elif isinstance(value, float):
		#	return repr(value)
		#elif isinstance(value, bool):
		#	return str(value)
		elif isinstance(value, list):
			return '[' + ', '.join(make_r_prefix(item) for item in value) + ']'
		elif isinstance(value, dict):
			return '{' + ', '.join(f'{make_r_prefix(k)}: {make_r_prefix(v)}' for k, v in value.items()) + '}'
		elif isinstance(value, tuple):
			return '(' + ', '.join(make_r_prefix(item) for item in value) + ')'
		else:
			return repr(value)
	with open(dot_py_filename, "w") as file:
		file.write("settings = {\n")
		for item in specially_formatted_list:
			key, value, annotation_text = item
			file.write(f'\t{make_r_prefix(key)}:\t{make_r_prefix(value)},\t\t# {annotation_text}\n')
		file.write("}\n")
	return

def load_settings():	
	# This will always force reload of 'setup.py' from the current default folder
	# Settings_filename is always "fixed" in the same place as the script is run from, 
	# A dict is returned with all of the settings in it.
	# Missing values are defaulted here, yielding calculated ones as well.
	
	if UTIL.DEBUG:	print(f'DEBUG: at top of load_settings DEBUG={UTIL.DEBUG}',flush=True,file=sys.stderr)

	# This is ALWAYS a fixed filename in the current default folder !!!

	SLIDESHOW_SETTINGS_MODULE_NAME				= 'SLIDESHOW_SETTINGS'.lower()	# SLIDESHOW_SETTINGS.py
	SLIDESHOW_SETTINGS_MODULE_FILENAME			= UTIL.fully_qualified_filename(os.path.join(r'.', SLIDESHOW_SETTINGS_MODULE_NAME + '.py'))

	ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS	= [ UTIL.fully_qualified_directory_no_trailing_backslash(r'.') ]
	TEMP_FOLDER									= UTIL.fully_qualified_directory_no_trailing_backslash(r'.\TEMP')				# TEMP_FOLDER
	PIC_EXTENSIONS								= [ r'.png', r'.jpg', r'.jpeg', r'.gif' ]
	VID_EXTENSIONS								= [ r'.mp4', r'.mpeg4', r'.mpg', r'.mpeg', r'.avi', r'.mjpeg', r'.3gp', r'.mov' ]
	EEK_EXTENSIONS								= [ r'.m2ts' ]
	VID_EEK_EXTENSIONS							= VID_EXTENSIONS + EEK_EXTENSIONS
	EXTENSIONS									= PIC_EXTENSIONS + VID_EXTENSIONS + EEK_EXTENSIONS

	# we need a json file to contain a dict of all chunks

	CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT			= r'chunks_file_for_all_chunks_dict.json'		# add TEMP_FOLDER later.
	SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT		= r'snippets_file_for_all_snippets_dict.json'	# add TEMP_FOLDER later.
	CHUNK_ENCODED_FFV1_FILENAME_BASE			= r'encoded_chunk_ffv1_'						# add TEMP_FOLDER later. interim encoded video from encoding process, associated with a snippet dict, full names dynamically created eg "interim_ffv1_0001.mkv"
	
	# Now we need a set of inter-step comms files
	# 1. PREPARATION: 
	# the CONTROLLER calls load_settings.load_settings() and can call a function to do the chunking into a dict and keep it in memory and write a debug copy to CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT

	# 2. ENCODER : process_video also creating a snippets file ... change the format of the snippets file to exclude the last line with a filename and change the code

	CURRENT_CHUNK_FILENAME						= r'current_chunk_file.json' 		# add TEMP_FOLDER later.	# used by the ENCODER to load a file whose .json content gives the ENCODER (a dict of the current chunk, and a filename to be encoded into)
	CURRENT_SNIPPETS_FILENAME					= r'current_snippets_file.json'		# add TEMP_FOLDER later.	# used by the ENCODER to write file whose .json content will be a dict of snippets for this chunk, and a filename/[start/end]-frames of the encoded file)
																									# the file will contain the start/end frame numbers and the fully qualified SOURCE filename for each snippet, and a filename/[start/end-frames] for the encoded file (used in calcs later)
	# 3. the CONTROLLER does snippet processsing based on snippets written by the encoder per chunk and re-read and placed into a large dict on the fly by the CONTROLLER... 
	#	 use the global snippets dict updated by the fly by the encoding CONTROLLER process
	#	 global frame numbers are now re-calculated after encoding all chunks by processing snippet dicts in sequence and recalculating the global [frame-start/frame-end] pairs for each snippet
	#	 then process snippets into the audio, re-encoding into .aac which can be muxed later.
	#	this process touches the 

	BACKGROUND_AUDIO_INPUT_FOLDER						= ".\\BACKGROUND_AUDIO_INPUT_FOLDER"
	BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME	= r'background_audio_with_overlayed_snippets.mp4'			# add TEMP_FOLDER later.

	# 5. the CONTROLLER does Final muxing of the interim video .mp4 and the interim background_audio_post_snippet_editing

	FINAL_MP4_WITH_AUDIO_FILENAME				= UTIL.fully_qualified_filename(r'.\slideshow.FINAL_MP4_WITH_AUDIO_FILENAME.mp4')

	MAX_FILES_PER_CHUNK							= int(150)		#this is a bit slower than 100, but it causes less "no transition" which occurs between encoded chunks
	TOLERANCE_PERCENT_FINAL_CHUNK				= int(20)
	RECURSIVE									= True
	DEBUG										= UTIL.DEBUG
	FFMPEG_PATH									= UTIL.fully_qualified_filename(os.path.join(r'.\Vapoursynth_x64', r'ffmpeg.exe'))
	FFPROBE_PATH								= UTIL.fully_qualified_filename(os.path.join(r'.\Vapoursynth_x64', r'ffprobe.exe'))
	VSPIPE_PATH									= UTIL.fully_qualified_filename(os.path.join(r'.\Vapoursynth_x64', r'vspipe.exe'))
	valid_FFMPEG_ENCODER						= [r'libx264'.lower() , r'h264_nvenc'.lower()]
	FFMPEG_ENCODER								= valid_FFMPEG_ENCODER[0]
	
	slideshow_CONTROLLER_path					= UTIL.fully_qualified_filename(os.path.join(r'.\slideshow_CONTROLLER.py'))
	slideshow_LOAD_SETTINGS_path				= UTIL.fully_qualified_filename(os.path.join(r'.\slideshow_LOAD_SETTINGS.py'))
	slideshow_ENCODER_legacy_path				= UTIL.fully_qualified_filename(os.path.join(r'.\slideshow_ENCODER_legacy.vpy'))

	SUBTITLE_DEPTH								= int(0)
	SUBTITLE_FONTSIZE							= int(18)
	SUBTITLE_FONTSCALE							= float(1.0)
	DURATION_PIC_SEC							= float(3.0)
	DURATION_CROSSFADE_SECS						= float(0.5)
	CROSSFADE_TYPE								= r'random'
	CROSSFADE_DIRECTION							= r'left'
	DURATION_MAX_VIDEO_SEC						= float(7200.0)
	DENOISE_SMALL_SIZE_VIDEOS					= True

	valid_TARGET_RESOLUTION_DICT				=	{	
													# These appear to work since the legacy resizing ENCODER logic caters for them.
														r'1080p_PAL'.lower():	{ 'WIDTH': int(1920), 'HEIGHT': int(1080), 'BITRATE': r'4.5M', 'FRAMERATE_NUMERATOR': int(25),    'FRAMERATE_DENOMINATOR': int(1) },
														r'4k_PAL'.lower():		{ 'WIDTH': int(3840), 'HEIGHT': int(2160), 'BITRATE': r'15M',  'FRAMERATE_NUMERATOR': int(25),    'FRAMERATE_DENOMINATOR': int(1) },
														r'2160p_PAL'.lower():	{ 'WIDTH': int(3840), 'HEIGHT': int(2160), 'BITRATE': r'15M',  'FRAMERATE_NUMERATOR': int(25),    'FRAMERATE_DENOMINATOR': int(1) } ,
														r'1080p_NTSC'.lower():	{ 'WIDTH': int(1920), 'HEIGHT': int(1080), 'BITRATE': r'4.5M', 'FRAMERATE_NUMERATOR': int(30000), 'FRAMERATE_DENOMINATOR': int(1001) },	# 29.976
														r'4k_NTSC'.lower():		{ 'WIDTH': int(3840), 'HEIGHT': int(2160), 'BITRATE': r'15M',  'FRAMERATE_NUMERATOR': int(30000), 'FRAMERATE_DENOMINATOR': int(1001) },	# 29.976
														r'2160p_NTSC'.lower():	{ 'WIDTH': int(3840), 'HEIGHT': int(2160), 'BITRATE': r'15M',  'FRAMERATE_NUMERATOR': int(30000), 'FRAMERATE_DENOMINATOR': int(1001) },	# 29.976
													}
													# These result in broken aspect ratios since the legacy resizing ENCODER logic does not cater for it.
													#	r'576p_PAL'.lower():	{ 'WIDTH': int(720),  'HEIGHT': int(576),  'BITRATE': r'2M',   'FRAMERATE_NUMERATOR': int(25),    'FRAMERATE_DENOMINATOR': int(1) },
													#	r'480p_NTSC'.lower():	{ 'WIDTH': int(720),  'HEIGHT': int(480),  'BITRATE': r'2M',   'FRAMERATE_NUMERATOR': int(30000), 'FRAMERATE_DENOMINATOR': int(1001) },	# 29.976

	TARGET_RESOLUTION							= list(valid_TARGET_RESOLUTION_DICT.keys())[0]	# the first key in the dict should be 1080p_PAL :)
	TARGET_WIDTH 								= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['WIDTH']
	TARGET_HEIGHT	 							= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['HEIGHT']
	TARGET_VIDEO_BITRATE						= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['BITRATE']		# 4.5M is ok (HQ) for h.264 1080p25 slideshow material ... dunno about 2160p, web say 25M whcih is FAR too high to be handy.
	TARGET_FPSNUM								= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['FRAMERATE_NUMERATOR']
	TARGET_FPSDEN								= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['FRAMERATE_DENOMINATOR']
	
	#TARGET_WIDTH								= int(1920)		# ; "target_width" an integer; set for hd; do not change unless a dire emergency = .
	#TARGET_HEIGHT								= int(1080)		# ; "target_height" an integer; set for hd; do not change unless a dire emergency = .
	#TARGET_VIDEO_BITRATE						= r'4.5M'		# 4.5M is ok (HQ) for h.264 1080p25 slideshow material
	#TARGET_FPSNUM								= int(25)		# ; "target_fpsnum" an integer; set for pal = .
	#TARGET_FPSDEN								= int(1)		# ; "target_fpsden" an integer; set for pal = .


	TARGET_BACKGROUND_AUDIO_FREQUENCY			= int(48000) 
	TARGET_BACKGROUND_AUDIO_CHANNELS			= int(2) 
	TARGET_BACKGROUND_AUDIO_BYTEDEPTH			= int(2)		# 2 ; bytes not bits, 2 byte = 16 bit to match pcm_s16le
	TARGET_BACKGROUND_AUDIO_CODEC				= r'libfdk_aac'
	TARGET_BACKGROUND_AUDIO_BITRATE				= r'256k'
	TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB	= int(-18)		# normalize background audio to -xxDB ; pydub calls it headroom
	TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY		= int(-30)		# reduce audio of background music during overlay of snippet audio by xxDB
	TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB		= int(-12)		# normalize snippet audio to -xxDB ; pydub calls it headroom; camera vids are usually much quieter than background music

	TEMPORARY_BACKGROUND_AUDIO_CODEC			= r'pcm_s16le'	# ; for 16 bit .wav
	TEMPORARY_AUDIO_FILENAME					= r'temporary_audio_file_for_standardization_then_input_to_pydub.wav'	# add TEMP_FOLDER later.	# file is overwritten and deleted as needed
	TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME		= r'temporary_ffmpeg_concat_list.txt'									# add TEMP_FOLDER later.	# file is overwritten and deleted as needed

	TARGET_COLORSPACE							= r'BT.709'	# ; "target_colorspace" a string; set for hd; required to render subtitles, it is fixed at this value; this item must match target_colorspace_matrix_i etc = .
	TARGET_COLORSPACE_MATRIX_I					= int(1)	# ; "target_colorspace_matrix_i" an integer; set for hd; this is the value that counts; it is fixed at this value; turn on debug_mode to see lists of these values = .
	TARGET_COLOR_TRANSFER_I						= int(1)	# ; "target_color_transfer_i" an integer; set for hd; this is the value that counts; it is fixed at this value; used by vapoursynth; turn on debug_mode to see lists of these values = .
	TARGET_COLOR_PRIMARIES_I					= int(1)	# ; "target_color_primaries_i" an integer; set for hd; this is the value that counts; it is fixed at this value; turn on debug_mode to see lists of these values = .
	TARGET_COLOR_RANGE_I						= int(0)	# ; "target_color_range_i" an integer; set for full-range, not limited-range; this is the (vapoursynth) value that counts; it is fixed at this value; used by vapoursynth; turn on debug_mode to see lists of these values = .
															# ; "target_color_range_i note: this vapoursynth value is opposite to that needed by zimg and by resizers which require the zimg (the propeer) value; internal transations vs->zimg are done = .
	UPSIZE_KERNEL								= r'Lanczos'	# ; "upsize_kernel" a string; do not change unless a dire emergency; you need the exact string name of the resizer = .
	DOWNSIZE_KERNEL								= r'Spline36'	#; "downsize_kernel" a string; do not change unless a dire emergency; you need the exact string name of the resizer = .
	BOX											= True		# ; "box" is true or false; if true, images and videos are resized vertically/horizontally to maintain aspect ratio and padded; false streches and squeezes  = .

	# compatibility
	_INI_SECTION_NAME							= r'slideshow'	# use in OLD ...  self._default_ini_values = { self._ini_section_name : { ini_value, ini_value, ini_vsalue ...} ... use like: self._ini_values[self._ini_section_name]["TARGET_WIDTH"]
																# then self.calc_ini = self._ini_values[self._ini_section_name] which pops all the settings into calc_ini and used like: self.calc_ini["PIC_EXTENSIONS"]
																# self.calc_ini us a superset of self._ini_values[self._ini_section_name] ... i.e. just {ini_value, ini_value, ...}

	WORKING_PIXEL_FORMAT						= vs.YUV444P8	# int(vs.YUV444P8.value)				# pixel format of the working clips (mainly required by vs_transitions)
	TARGET_PIXEL_FORMAT							= vs.YUV420P8	# int(vs.YUV420P8.value)				# pixel format of the target video
	DG_PIXEL_FORMAT								= vs.YUV420P16	# int(vs.YUV420P16.value)				# pixel format of the video for use by DG tools

	DOT_FFINDEX									= r'.ffindex'.lower()		# for removing temporary *.ffindex files at the end
	MODX										= int(2)	   # mods for letterboxing calculations, example, for 411 YUV as an extreme
	MODY										= int(2)	   # mods would have to be MODX=4, MODY=1 as minimum
	SUBTITLE_MAX_DEPTH							= int(10)
	ROTATION_ANTI_CLOCKWISE						= r'anti-clockwise'.lower()
	ROTATION_CLOCKWISE							= r'clockwise'.lower()
	PRECISION_TOLERANCE							= float(0.0002)	# used in float comarisons eg fps calculations and comparisons so do not have to use "==" which would almost never work

	MIN_ACTUAL_DISPLAY_TIME						= float(0.5)	# seconds

	SNIPPET_AUDIO_FADE_IN_DURATION_MS			= int(500)		# milliseconds of fade for overlaying snippet audio onto background audio
	SNIPPET_AUDIO_FADE_OUT_DURATION_MS			= int(500)		# milliseconds of fade for overlaying snippet audio onto background audio

	# EXTERNAL CONSTANTS ...
	# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
	# When calling rezisers etc, ONLY use these values:
	#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
	#	ZIMG_RANGE_FULL	 = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
	# but when obtaining from frame properties and comparing etc, use the vs values from
	# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
	ZIMG_RANGE_LIMITED  = 0		# /**< Studio (TV) legal range, 16-235 in 8 bits. */
	ZIMG_RANGE_FULL	 = 1		# /**< Full (PC) dynamic range, 0-255 in 8 bits. */
	# https://www.vapoursynth.com/doc/apireference.html?highlight=_FieldBased
	VS_INTERLACED = { 'Progressive' : 0, 'BFF' : 1, 'TFF' : 2 }		# vs documentation says frame property _FieldBased is one of 0=frame based (progressive), 1=bottom field first, 2=top field first.

	TARGET_FPS									= None		# CALCULATED LATER :	# = round(self.calc_ini["TARGET_FPSNUM"] / self.calc_ini["TARGET_FPSDEN"], 3)
	DURATION_PIC_FRAMES							= None		# CALCULATED LATER : 	# = int(math.ceil(self.calc_ini["DURATION_PIC_SEC"] * self.calc_ini["TARGET_FPS"]))
	DURATION_CROSSFADE_FRAMES					= None		# CALCULATED LATER : 	# = int(math.ceil(self.calc_ini["DURATION_CROSSFADE_SECS"] * self.calc_ini["TARGET_FPS"]))
	DURATION_BLANK_CLIP_FRAMES					= None		# CALCULATED LATER : 	# = self.calc_ini["DURATION_CROSSFADE_FRAMES"] + 1	# make equal to the display time for an image; DURATION_CROSSFADE_FRAMES will be less than this
	DURATION_MAX_VIDEO_FRAMES					= None		# CALCULATED LATER : 	# = int(math.ceil(self.calc_ini["DURATION_MAX_VIDEO_SEC"] * self.calc_ini["TARGET_FPS"]))
	TARGET_VFR_FPSNUM							= None		# CALCULATED LATER : 	# = self.calc_ini["TARGET_FPSNUM"] * 2
	TARGET_VFR_FPSDEN							= None		# CALCULATED LATER : 	# = self.calc_ini["TARGET_FPSDEN"]
	TARGET_VFR_FPS								= None		# CALCULATED LATER : 	# = self.calc_ini["TARGET_VFR_FPSNUM"] / self.calc_ini["TARGET_VFR_FPSDEN"]	
	TARGET_COLOR_RANGE_I_ZIMG					= None		# CALCULATED LATER : 	# = if something, calculate

	default_settings_dict = {
		'SLIDESHOW_SETTINGS_MODULE_NAME':					SLIDESHOW_SETTINGS_MODULE_NAME,
		'SLIDESHOW_SETTINGS_MODULE_FILENAME':				SLIDESHOW_SETTINGS_MODULE_FILENAME,
		
		'ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS': 		ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS,	# this is the ONLY file/folder thing in the NEW version that is actually already a LIST
		'TEMP_FOLDER':										TEMP_FOLDER,
		'PIC_EXTENSIONS' :									PIC_EXTENSIONS,
		'VID_EXTENSIONS' :									VID_EXTENSIONS,
		'EEK_EXTENSIONS' :									EEK_EXTENSIONS,
		'VID_EEK_EXTENSIONS':								VID_EEK_EXTENSIONS,
		'EXTENSIONS' :										EXTENSIONS,

		'CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT': 				CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT,				# add TEMP_FOLDER later.
		'SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT':			SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT,			# add TEMP_FOLDER later.
		'CHUNK_ENCODED_FFV1_FILENAME_BASE': 				CHUNK_ENCODED_FFV1_FILENAME_BASE,					# add TEMP_FOLDER later.
		'CURRENT_CHUNK_FILENAME':							CURRENT_CHUNK_FILENAME,								# add TEMP_FOLDER later.
		'CURRENT_SNIPPETS_FILENAME': 						CURRENT_SNIPPETS_FILENAME,							# add TEMP_FOLDER later.
		'BACKGROUND_AUDIO_INPUT_FOLDER':					BACKGROUND_AUDIO_INPUT_FOLDER,
		'BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME':	BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME,	# add TEMP_FOLDER later.
		'FINAL_MP4_WITH_AUDIO_FILENAME':					FINAL_MP4_WITH_AUDIO_FILENAME,

		'MAX_FILES_PER_CHUNK':								MAX_FILES_PER_CHUNK,
		'TOLERANCE_PERCENT_FINAL_CHUNK':					TOLERANCE_PERCENT_FINAL_CHUNK,
		'RECURSIVE':										RECURSIVE,
		'DEBUG':											DEBUG,
		'FFMPEG_PATH':										FFMPEG_PATH,
		'FFPROBE_PATH':										FFPROBE_PATH,
		'VSPIPE_PATH':										VSPIPE_PATH,
		'FFMPEG_ENCODER':									FFMPEG_ENCODER,
		'slideshow_CONTROLLER_path':						slideshow_CONTROLLER_path,
		'slideshow_LOAD_SETTINGS_path':						slideshow_LOAD_SETTINGS_path,
		'slideshow_ENCODER_legacy_path':					slideshow_ENCODER_legacy_path,
		
		'SUBTITLE_DEPTH':									SUBTITLE_DEPTH,
		'SUBTITLE_FONTSIZE':								SUBTITLE_FONTSIZE,
		'SUBTITLE_FONTSCALE':								SUBTITLE_FONTSCALE,
		'DURATION_PIC_SEC':									DURATION_PIC_SEC,
		'DURATION_CROSSFADE_SECS':							DURATION_CROSSFADE_SECS,
		'CROSSFADE_TYPE':									CROSSFADE_TYPE,
		'CROSSFADE_DIRECTION':								CROSSFADE_DIRECTION,
		'DURATION_MAX_VIDEO_SEC':							DURATION_MAX_VIDEO_SEC,
		'DENOISE_SMALL_SIZE_VIDEOS':						DENOISE_SMALL_SIZE_VIDEOS,

		'valid_TARGET_RESOLUTION_DICT':						valid_TARGET_RESOLUTION_DICT,
		'TARGET_RESOLUTION':								TARGET_RESOLUTION,
		'TARGET_WIDTH':										TARGET_WIDTH,
		'TARGET_HEIGHT':									TARGET_HEIGHT,
		'TARGET_FPSNUM':									TARGET_FPSNUM,
		'TARGET_FPSDEN':									TARGET_FPSDEN,
		'TARGET_VIDEO_BITRATE':								TARGET_VIDEO_BITRATE,

		'TARGET_BACKGROUND_AUDIO_FREQUENCY':				TARGET_BACKGROUND_AUDIO_FREQUENCY,
		'TARGET_BACKGROUND_AUDIO_CHANNELS':					TARGET_BACKGROUND_AUDIO_CHANNELS,
		'TARGET_BACKGROUND_AUDIO_BYTEDEPTH':				TARGET_BACKGROUND_AUDIO_BYTEDEPTH,
		'TARGET_BACKGROUND_AUDIO_CODEC':					TARGET_BACKGROUND_AUDIO_CODEC,
		'TARGET_BACKGROUND_AUDIO_BITRATE':					TARGET_BACKGROUND_AUDIO_BITRATE,
		'TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB':	TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB,
		'TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY':		TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY,
		'TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB':		TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB,

		'TEMPORARY_BACKGROUND_AUDIO_CODEC':					TEMPORARY_BACKGROUND_AUDIO_CODEC,
		'TEMPORARY_AUDIO_FILENAME':							TEMPORARY_AUDIO_FILENAME,							# add TEMP_FOLDER later.
		'TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME':			TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME,				# add TEMP_FOLDER later.

		'TARGET_COLORSPACE':								TARGET_COLORSPACE,
		'TARGET_COLORSPACE_MATRIX_I':						TARGET_COLORSPACE_MATRIX_I,
		'TARGET_COLOR_TRANSFER_I':							TARGET_COLOR_TRANSFER_I,
		'TARGET_COLOR_PRIMARIES_I':							TARGET_COLOR_PRIMARIES_I,
		'TARGET_COLOR_RANGE_I':								TARGET_COLOR_RANGE_I,
		'UPSIZE_KERNEL':									UPSIZE_KERNEL,
		'DOWNSIZE_KERNEL':									DOWNSIZE_KERNEL,
		'BOX':												BOX,

		'_INI_SECTION_NAME':								_INI_SECTION_NAME,

		'WORKING_PIXEL_FORMAT':								WORKING_PIXEL_FORMAT,
		'TARGET_PIXEL_FORMAT':								TARGET_PIXEL_FORMAT,
		'DG_PIXEL_FORMAT':									DG_PIXEL_FORMAT,
		'DOT_FFINDEX':										DOT_FFINDEX,
		'MODX':												MODX,
		'MODY':												MODY,
		'SUBTITLE_MAX_DEPTH':								SUBTITLE_MAX_DEPTH,	
		'ROTATION_ANTI_CLOCKWISE':							ROTATION_ANTI_CLOCKWISE,
		'ROTATION_CLOCKWISE':								ROTATION_CLOCKWISE,
		'PRECISION_TOLERANCE':								PRECISION_TOLERANCE,
		'MIN_ACTUAL_DISPLAY_TIME':							MIN_ACTUAL_DISPLAY_TIME,

		'SNIPPET_AUDIO_FADE_IN_DURATION_MS':				SNIPPET_AUDIO_FADE_IN_DURATION_MS,
		'SNIPPET_AUDIO_FADE_OUT_DURATION_MS':				SNIPPET_AUDIO_FADE_OUT_DURATION_MS,

		'ZIMG_RANGE_LIMITED':								ZIMG_RANGE_LIMITED,	# = 0		# /**< Studio (TV) legal range, 16-235 in 8 bits. */
		'ZIMG_RANGE_FULL':									ZIMG_RANGE_FULL,	# = 1		# /**< Full (PC) dynamic range, 0-255 in 8 bits. */
		'VS_INTERLACED':									VS_INTERLACED,		# = { 'Progressive' : 0, 'BFF' : 1, 'TFF' : 2 }		# vs documnetation says frame property _FieldBased is one of 0=frame based (progressive), 1=bottom field first, 2=top field first.

		# placeholders for calculated values - calculated after reading in the user-specified JSON
		'TARGET_FPS':										TARGET_FPS,					# CALCULATED LATER # = round(self.calc_ini["TARGET_FPSNUM"] / self.calc_ini["TARGET_FPSDEN"], 3)
		'DURATION_PIC_FRAMES':								DURATION_PIC_FRAMES,		# CALCULATED LATER # = int(math.ceil(self.calc_ini["DURATION_PIC_SEC"] * self.calc_ini["TARGET_FPS"]))
		'DURATION_CROSSFADE_FRAMES':						DURATION_CROSSFADE_FRAMES,	# CALCULATED LATER # = int(math.ceil(self.calc_ini["DURATION_CROSSFADE_SECS"] * self.calc_ini["TARGET_FPS"]))
		'DURATION_BLANK_CLIP_FRAMES':						DURATION_BLANK_CLIP_FRAMES,	# CALCULATED LATER # = self.calc_ini["DURATION_CROSSFADE_FRAMES"] + 1	# make equal to the display time for an image; DURATION_CROSSFADE_FRAMES will be less than this
		'DURATION_MAX_VIDEO_FRAMES':						DURATION_MAX_VIDEO_FRAMES,	# CALCULATED LATER # = int(math.ceil(self.calc_ini["DURATION_MAX_VIDEO_SEC"] * self.calc_ini["TARGET_FPS"]))
		'TARGET_VFR_FPSNUM':								TARGET_VFR_FPSNUM,			# CALCULATED LATER # = self.calc_ini["TARGET_FPSNUM"] * 2
		'TARGET_VFR_FPSDEN':								TARGET_VFR_FPSDEN,			# CALCULATED LATER # = self.calc_ini["TARGET_FPSDEN"]
		'TARGET_VFR_FPS':									TARGET_VFR_FPS,				# CALCULATED LATER # = self.calc_ini["TARGET_VFR_FPSNUM"] / self.calc_ini["TARGET_VFR_FPSDEN"]	
		'TARGET_COLOR_RANGE_I_ZIMG':						TARGET_COLOR_RANGE_I_ZIMG,	# CALCULATED LATER # = if something, calculated
	}

	if UTIL.DEBUG:	print(f'DEBUG: created default_settings_dict=\n{UTIL.objPrettyPrint.pformat(default_settings_dict)}',flush=True,file=sys.stderr)

	#######################################################################################################################################
	#######################################################################################################################################

	# read the user-edited settings from SLIDESHOW_SETTINGS_MODULE_NAME (SLIDESHOW_SETTINGS.py)
	
	if os.path.exists(SLIDESHOW_SETTINGS_MODULE_FILENAME):
		if SLIDESHOW_SETTINGS_MODULE_NAME not in sys.modules:
			if UTIL.DEBUG:	print(f'DEBUG: SLIDESHOW_SETTINGS_MODULE_NAME not in sys.modules',flush=True,file=sys.stderr)
			# Import the module dynamically, if it is not done already
			try:
				if UTIL.DEBUG:	print(f'DEBUG: importing SLIDESHOW_SETTINGS_MODULE_NAME={SLIDESHOW_SETTINGS_MODULE_NAME} dynamically',flush=True,file=sys.stderr)
				#importlib.invalidate_caches()
				SETTINGS_MODULE = importlib.import_module(SLIDESHOW_SETTINGS_MODULE_NAME)
			except ImportError as e:
				# Handle the ImportError if the module cannot be imported
				print(f"load_settings: ERROR: ImportError, failed to dynamically import user specified Settings from import module: '{SLIDESHOW_SETTINGS_MODULE_NAME}'\n{str(e)}",flush=True,file=sys.stderr)
				sys.exit(1)	
			except Exception as e:
				print(f"load_settings: ERROR: Exception, failed to dynamically import user specified Settings from import module: '{SLIDESHOW_SETTINGS_MODULE_NAME}'\n{str(e)}",flush=True,file=sys.stderr)
				sys.exit(1)	
		else:
			if UTIL.DEBUG:	print(f'DEBUG: SLIDESHOW_SETTINGS_MODULE_NAME IS in sys.modules',flush=True,file=sys.stderr)
			# Reload the module since it had been dynamically loaded already ... remember, global variables in thee module are not scrubbed by reloading
			try:
				if UTIL.DEBUG:	print(f'DEBUG: reloading SETTINGS_MODULE={SETTINGS_MODULE} ',flush=True,file=sys.stderr)
				#importlib.invalidate_caches()
				importlib.reload(SETTINGS_MODULE)
			except Exception as e:
				print(f"load_settings: ERROR: Exception, failed to RELOAD user specified Settings from import module: '{SLIDESHOW_SETTINGS_MODULE_NAME}'\n{str(e)}",flush=True,file=sys.stderr)
				sys.exit(1)
	
	#print(f'DEBUG: before import slideshow_settings.py static',flush=True,file=sys.stderr)
	#import slideshow_settings
	#user_specified_settings_dict = slideshow_settings.settings
	#print(f'DEBUG: after import slideshow_settings.py static',flush=True,file=sys.stderr)

	# retrieve the settigns from SLIDESHOW_SETTINGS_MODULE_NAME (SLIDESHOW_SETTINGS.py)
	if UTIL.DEBUG:	print(f"DEBUG: Attempting to load user_specified_settings_dict = SETTINGS_MODULE.settings'",flush=True,file=sys.stderr)
	try:
		user_specified_settings_dict = SETTINGS_MODULE.settings
		print(f'Successfully loaded user_specified_settings_dict=\n{UTIL.objPrettyPrint.pformat(user_specified_settings_dict)}',flush=True,file=sys.stderr)
	except Exception as e:
		user_specified_settings_dict = {}
		print(f"load_settings: WARNING: Exception, could not import 'user_specified_settings' '{SLIDESHOW_SETTINGS_MODULE_FILENAME}'",flush=True,file=sys.stderr)

	#######################################################################################################################################
	#######################################################################################################################################

	# x = {**y, **z} = CREATE A NEW MERGED DICTIONARY where items in **z overwrite items in **y
	# Similar to the dict.update method, if both dictionaries has the same key with different values,
	# then the final output will contain the value of the second dictionary. 
	
	# asssume they may have mucked with valid_TARGET_RESOLUTION_DICT ... remove it from user_specified_settings_dict just in case
	if 'valid_TARGET_RESOLUTION_DICT' in user_specified_settings_dict: del user_specified_settings_dict['valid_TARGET_RESOLUTION_DICT']
	
	final_settings_dict = {**default_settings_dict, **user_specified_settings_dict}	
	
	# FOR NOW, NOT USING THIS METHOD:
	#		create a new dict in which user settings dict items overwrite the defaults dict
	#		final_settings_dict = default_settings_dict
	#		final_settings_dict.update(user_specified)	# updates a dictiony in-place

	# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	UTIL.DEBUG =  final_settings_dict['DEBUG']	# RESET everywhere
	DEBUG = UTIL.DEBUG		# RESET fo this module's dicts
	# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

	#######################################################################################################################################
	#######################################################################################################################################

	# Once we get to here, the user dict (if any) has been merged with the default settings above.
	# The TEMP_FOLDER has not yet been inserted as defaults into thee tight places
	# And we need to format proper paths for folders and files ...
	#
	# process a LIST ... make ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS list entries all fully qualified and escaped where required
	
	ddl_fully_qualified = []									
	for ddl in final_settings_dict['ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS']:
		ddl_fully_qualified.append(UTIL.fully_qualified_directory_no_trailing_backslash(ddl))
	final_settings_dict['ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS'] = ddl_fully_qualified
	#
	final_settings_dict['SLIDESHOW_SETTINGS_MODULE_NAME'] = final_settings_dict['SLIDESHOW_SETTINGS_MODULE_NAME']
	final_settings_dict['SLIDESHOW_SETTINGS_MODULE_FILENAME'] = UTIL.fully_qualified_filename(final_settings_dict['SLIDESHOW_SETTINGS_MODULE_FILENAME'])
	
	final_settings_dict['FINAL_MP4_WITH_AUDIO_FILENAME'] = UTIL.fully_qualified_filename(final_settings_dict['FINAL_MP4_WITH_AUDIO_FILENAME'])

	final_settings_dict['FFMPEG_PATH'] = UTIL.fully_qualified_filename(final_settings_dict['FFMPEG_PATH'])
	final_settings_dict['FFPROBE_PATH'] = UTIL.fully_qualified_filename(final_settings_dict['FFPROBE_PATH'])
	final_settings_dict['VSPIPE_PATH'] = UTIL.fully_qualified_filename(final_settings_dict['VSPIPE_PATH'])
	final_settings_dict['slideshow_CONTROLLER_path'] = UTIL.fully_qualified_filename(final_settings_dict['slideshow_CONTROLLER_path'])
	final_settings_dict['slideshow_LOAD_SETTINGS_path'] = UTIL.fully_qualified_filename(final_settings_dict['slideshow_LOAD_SETTINGS_path'])
	final_settings_dict['slideshow_ENCODER_legacy_path'] = UTIL.fully_qualified_filename(final_settings_dict['slideshow_ENCODER_legacy_path'])

	# NOW WE NEED TO RECONSTRUCT THINGS WHICH BELONG IN THE TEMPORARY FOLDER
	TEMP_FOLDER = UTIL.reconstruct_full_directory_only(final_settings_dict['TEMP_FOLDER'], final_settings_dict['TEMP_FOLDER'])

	# put the new RECONSTRUCTED items (from the merged dict) back into the variables for use when later creating dict specially_formatted_settings_list 
	CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT'])	# cater for any missing folder
	SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT'])	# cater for any missing folder
	CHUNK_ENCODED_FFV1_FILENAME_BASE = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['CHUNK_ENCODED_FFV1_FILENAME_BASE'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['CHUNK_ENCODED_FFV1_FILENAME_BASE'])	# cater for any missing folder
	CURRENT_CHUNK_FILENAME = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['CURRENT_CHUNK_FILENAME'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['CURRENT_CHUNK_FILENAME'])	# cater for any missing folder
	CURRENT_SNIPPETS_FILENAME = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['CURRENT_SNIPPETS_FILENAME'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['CURRENT_SNIPPETS_FILENAME'])	# cater for any missing folder
	BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME'])	# cater for any missing folder
	TEMPORARY_AUDIO_FILENAME = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['TEMPORARY_AUDIO_FILENAME'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['TEMPORARY_AUDIO_FILENAME'])	# cater for any missing folder
	TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME = UTIL.reconstruct_full_directory_and_filename( final_settings_dict['TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME'], default_path=TEMP_FOLDER, default_filename=final_settings_dict['TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME'])	# cater for any missing folder

	BACKGROUND_AUDIO_INPUT_FOLDER = UTIL.reconstruct_full_directory_only(final_settings_dict['BACKGROUND_AUDIO_INPUT_FOLDER'], BACKGROUND_AUDIO_INPUT_FOLDER)	# re-default it if user mucked it up

	# check target resolution and reset if necessary, then store ither the resets or the new values based on the specified TARGET_RESOLUTION
	final_settings_dict['TARGET_RESOLUTION'] = final_settings_dict['TARGET_RESOLUTION'].lower()
	if final_settings_dict['TARGET_RESOLUTION'] not in valid_TARGET_RESOLUTION_DICT:
		TARGET_RESOLUTION		= list(valid_TARGET_RESOLUTION_DICT.keys())[0]	# the first key in that dict
		TARGET_WIDTH 			= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['WIDTH']
		TARGET_HEIGHT	 		= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['HEIGHT']
		TARGET_VIDEO_BITRATE	= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['BITRATE']
		TARGET_FPSNUM			= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['FRAMERATE_NUMERATOR']
		TARGET_FPSDEN			= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['FRAMERATE_DENOMINATOR']
		print(f'load_settings: WARNING: TARGET_RESOLUTION "{final_settings_dict["TARGET_RESOLUTION"]}" not one of {valid_TARGET_RESOLUTION_DICT}, resetting to "{TARGET_RESOLUTION}"',flush=True,file=sys.stderr)
		final_settings_dict['TARGET_RESOLUTION'] = TARGET_RESOLUTION
	TARGET_RESOLUTION			= final_settings_dict['TARGET_RESOLUTION']						# grab the specified TARGET_RESOLUTION
	TARGET_WIDTH 				= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['WIDTH']		# based on specified TARGET_RESOLUTION
	TARGET_HEIGHT	 			= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['HEIGHT']		# based on specified TARGET_RESOLUTION
	TARGET_VIDEO_BITRATE		= valid_TARGET_RESOLUTION_DICT[TARGET_RESOLUTION]['BITRATE']	# based on specified TARGET_RESOLUTION
	final_settings_dict['TARGET_WIDTH'] = TARGET_WIDTH											# poke back the right value based on specified TARGET_RESOLUTION
	final_settings_dict['TARGET_HEIGHT'] = TARGET_HEIGHT										# poke back the right value based on specified TARGET_RESOLUTION
	final_settings_dict['TARGET_VIDEO_BITRATE'] = TARGET_VIDEO_BITRATE							# poke back the right value based on specified TARGET_RESOLUTION
	final_settings_dict['TARGET_FPSNUM'] = TARGET_FPSNUM										# poke back the right value based on specified TARGET_RESOLUTION
	final_settings_dict['TARGET_FPSDEN'] = TARGET_FPSDEN										# poke back the right value based on specified TARGET_RESOLUTION

	if final_settings_dict['FFMPEG_ENCODER'].lower() not in valid_FFMPEG_ENCODER:
		print(f'load_settings: WARNING: FFMPEG_ENCODER "{final_settings_dict["FMPEG_ENCODER"]}" not one of {valid_FFMPEG_ENCODER}, defaulting to "{FFMPEG_ENCODER}"',flush=True,file=sys.stderr)
		final_settings_dict['FFMPEG_ENCODER'] = valid_FFMPEG_ENCODER[0]
	FFMPEG_ENCODER = final_settings_dict['FFMPEG_ENCODER']

	# put the new RECONSTRUCTED back into the merged dict as well
	final_settings_dict['CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT'] = CHUNKS_FILENAME_FOR_ALL_CHUNKS_DICT
	final_settings_dict['SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT'] = SNIPPETS_FILENAME_FOR_ALL_SNIPPETS_DICT
	final_settings_dict['CHUNK_ENCODED_FFV1_FILENAME_BASE'] = CHUNK_ENCODED_FFV1_FILENAME_BASE
	final_settings_dict['CURRENT_CHUNK_FILENAME'] = CURRENT_CHUNK_FILENAME
	final_settings_dict['CURRENT_SNIPPETS_FILENAME'] = CURRENT_SNIPPETS_FILENAME
	final_settings_dict['BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME'] = BACKGROUND_AUDIO_WITH_OVERLAYED_SNIPPETS_FILENAME
	final_settings_dict['TEMPORARY_AUDIO_FILENAME'] = TEMPORARY_AUDIO_FILENAME
	final_settings_dict['TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME'] = TEMPORARY_FFMPEG_CONCAT_LIST_FILENAME

	final_settings_dict['BACKGROUND_AUDIO_INPUT_FOLDER'] = BACKGROUND_AUDIO_INPUT_FOLDER

	if UTIL.DEBUG:	print(f'load_settings: After folders RECONSTRUCTION final_settings_dict=\n"{UTIL.objPrettyPrint.pformat(final_settings_dict)}"',flush=True,file=sys.stderr)

	# check the folders which should exist do exist
	# 1. check the folders in this LIST
	for ddl in final_settings_dict['ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS']:
		check_folder_exists_3333(ddl, r'ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS')

	# if the BACKGROUND_AUDIO_INPUT_FOLDER folder does not exist, try to create it with a try/except
	if not os.path.isdir(final_settings_dict['BACKGROUND_AUDIO_INPUT_FOLDER']):
		try:
			os.makedirs(final_settings_dict['BACKGROUND_AUDIO_INPUT_FOLDER'])
		except Exception as e:
			print(f"load_settings: ERROR: creating BACKGROUND_AUDIO_INPUT_FOLDER '{final_settings_dict['BACKGROUND_AUDIO_INPUT_FOLDER']}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		print(f'load_settings: created BACKGROUND_AUDIO_INPUT_FOLDER "{final_settings_dict["BACKGROUND_AUDIO_INPUT_FOLDER"]}"',flush=True,file=sys.stderr)

	# if the TEMP_FOLDER folder does not exist, try to create it with a try/except
	if not os.path.isdir(final_settings_dict['TEMP_FOLDER']):
		try:
			os.makedirs(final_settings_dict['TEMP_FOLDER'])
		except Exception as e:
			print(f"load_settings: ERROR: creating TEMP_FOLDER '{final_settings_dict['TEMP_FOLDER']}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		print(f'load_settings: created TEMP_FOLDER "{final_settings_dict["TEMP_FOLDER"]}"',flush=True,file=sys.stderr)

	# Check for out-of-spec values
	# for now, no validation checking of values ...

	# Consistency checks
	if (2 * final_settings_dict['DURATION_CROSSFADE_SECS'] ) + final_settings_dict['MIN_ACTUAL_DISPLAY_TIME'] > final_settings_dict['DURATION_PIC_SEC']:
		raise ValueError(f'load_settings: ERROR:  calculate_settings: ERROR: DURATION_PIC_SEC must be >= (2 * DURATION_CROSSFADE_SECS) + MIN_ACTUAL_DISPLAY_TIME \n\ DURATION_CROSSFADE_SECS={final_settings_dict["DURATION_CROSSFADE_SECS"] } DURATION_PIC_SEC={final_settings_dict["DURATION_PIC_SEC"]} MIN_ACTUAL_DISPLAY_TIME={final_settings_dict["MIN_ACTUAL_DISPLAY_TIME"]}')
	if (2 * final_settings_dict['DURATION_CROSSFADE_SECS'] ) + final_settings_dict['MIN_ACTUAL_DISPLAY_TIME'] > final_settings_dict['DURATION_MAX_VIDEO_SEC']:
		raise ValueError(f'load_settings: ERROR:  calculate_settings: ERROR: DURATION_MAX_VIDEO_SEC must be >= (2 * DURATION_CROSSFADE_SECS) + MIN_ACTUAL_DISPLAY_TIME \n\ DURATION_CROSSFADE_SECS={final_settings_dict["DURATION_CROSSFADE_SECS"] } DURATION_MAX_VIDEO_SEC={final_settings_dict["DURATION_MAX_VIDEO_SEC"]} MIN_ACTUAL_DISPLAY_TIME={final_settings_dict["MIN_ACTUAL_DISPLAY_TIME"]}')

	# Perform calculations based on updated inputs then updated the dict default_settings_dict
	final_settings_dict['TARGET_FPS']						= round(final_settings_dict['TARGET_FPSNUM'] / final_settings_dict['TARGET_FPSDEN'], 3)
	final_settings_dict['DURATION_PIC_FRAMES']				= int(math.ceil(final_settings_dict['DURATION_PIC_SEC'] * final_settings_dict['TARGET_FPS']))
	final_settings_dict['DURATION_CROSSFADE_FRAMES']		= int(math.ceil(final_settings_dict['DURATION_CROSSFADE_SECS'] * final_settings_dict['TARGET_FPS']))
	final_settings_dict['DURATION_BLANK_CLIP_FRAMES']		= final_settings_dict['DURATION_CROSSFADE_FRAMES'] + 1	# make equal to the display time for an image; DURATION_CROSSFADE_FRAMES will be less than this
	final_settings_dict['DURATION_MAX_VIDEO_FRAMES']		= int(math.ceil(final_settings_dict['DURATION_MAX_VIDEO_SEC'] * final_settings_dict['TARGET_FPS']))
	final_settings_dict['TARGET_VFR_FPSNUM']				= final_settings_dict['TARGET_FPSNUM'] * 2
	final_settings_dict['TARGET_VFR_FPSDEN']				= final_settings_dict['TARGET_FPSDEN']
	final_settings_dict['TARGET_VFR_FPS']					= final_settings_dict['TARGET_VFR_FPSNUM'] / final_settings_dict['TARGET_VFR_FPSDEN']
	# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
	# When calling rezisers etc, ONLY use these values:
	#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
	#	ZIMG_RANGE_FULL	 = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
	# but when obtaining from frame properties and comparing etc, use the vs values from
	# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
	# https://www.vapoursynth.com/doc/api/vapoursynth.h.html#enum-vspresetformat
	if final_settings_dict['TARGET_COLOR_RANGE_I'] == int(vs.ColorRange.RANGE_LIMITED.value):
		final_settings_dict['TARGET_COLOR_RANGE_I_ZIMG'] = ZIMG_RANGE_LIMITED					# use the ZIMG RANGE constants as they are correct and vapoursynth ones are not (opposite to the spec)
	elif final_settings_dict['TARGET_COLOR_RANGE_I'] == int(vs.ColorRange.RANGE_FULL.value):
		final_settings_dict['TARGET_COLOR_RANGE_I_ZIMG'] = ZIMG_RANGE_FULL						# use the ZIMG RANGE constants as they are correct and vapoursynth ones are not (opposite to the spec)
	else:
		raise ValueError(f'load_settings: ERROR: "TARGET_COLOR_RANGE_I"={TARGET_COLOR_RANGE_I} is an invalid value')

	#######################################################################################################################################
	#######################################################################################################################################

	# now  MAP these back into format/names compatible with the OLD calc_ini["SETTING_NAME"]
	# "case" of keys is important
	old_calc_ini_dict =	{	'DIRECTORY_LIST' :					final_settings_dict['ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS'],	# This is already a list []
							'TEMP_DIRECTORY' :					final_settings_dict['TEMP_FOLDER'],
							'TEMP_DIRECTORY_LIST' :				[ final_settings_dict['TEMP_FOLDER'] ],
							'CURRENT_CHUNK_FILENAME' :			final_settings_dict['CURRENT_CHUNK_FILENAME'],		# ADDED	for encoder; no need, it should use final_settings_dict for this
							'CURRENT_SNIPPETS_FILENAME' :		final_settings_dict['CURRENT_SNIPPETS_FILENAME'],	# ADDED	for encoder; no need, it should use final_settings_dict for this
							'RECURSIVE' :						final_settings_dict['RECURSIVE'],
							'SUBTITLE_DEPTH' :					final_settings_dict['SUBTITLE_DEPTH'],
							'SUBTITLE_FONTSIZE' :				final_settings_dict['SUBTITLE_FONTSIZE'],
							'SUBTITLE_FONTSCALE' :				final_settings_dict['SUBTITLE_FONTSCALE'],
							'DURATION_PIC_SEC' :				final_settings_dict['DURATION_PIC_SEC'],
							'DURATION_CROSSFADE_SECS' :			final_settings_dict['DURATION_CROSSFADE_SECS'],
							'CROSSFADE_TYPE' :					final_settings_dict['CROSSFADE_TYPE'],
							'CROSSFADE_DIRECTION' :				final_settings_dict['CROSSFADE_DIRECTION'],
							'DURATION_MAX_VIDEO_SEC' :			final_settings_dict['DURATION_MAX_VIDEO_SEC'],
							'DENOISE_SMALL_SIZE_VIDEOS' :		final_settings_dict['DENOISE_SMALL_SIZE_VIDEOS'],
							'DEBUG_MODE' :						final_settings_dict['DEBUG'],
							'TARGET_COLORSPACE' :				final_settings_dict['TARGET_COLORSPACE'],
							'TARGET_COLORSPACE_MATRIX_I' :		final_settings_dict['TARGET_COLORSPACE_MATRIX_I'],
							'TARGET_COLOR_TRANSFER_I' :			final_settings_dict['TARGET_COLOR_TRANSFER_I'],
							'TARGET_COLOR_PRIMARIES_I' :		final_settings_dict['TARGET_COLOR_PRIMARIES_I'],
							'TARGET_COLOR_RANGE_I' :			final_settings_dict['TARGET_COLOR_RANGE_I'],
							'TARGET_RESOLUTION':				final_settings_dict['TARGET_RESOLUTION'],
							'TARGET_WIDTH' :					final_settings_dict['TARGET_WIDTH'],
							'TARGET_HEIGHT' :					final_settings_dict['TARGET_HEIGHT'],
							'TARGET_FPSNUM' :					final_settings_dict['TARGET_FPSNUM'],
							'TARGET_FPSDEN' :					final_settings_dict['TARGET_FPSDEN'],
							'TARGET_VIDEO_BITRATE':				final_settings_dict['TARGET_VIDEO_BITRATE'],
							'UPSIZE_KERNEL' :					final_settings_dict['UPSIZE_KERNEL'],
							'DOWNSIZE_KERNEL' :					final_settings_dict['DOWNSIZE_KERNEL'],
							'BOX' :								final_settings_dict['BOX'],
							'PIC_EXTENSIONS':					final_settings_dict['PIC_EXTENSIONS'],
							'VID_EXTENSIONS':					final_settings_dict['VID_EXTENSIONS'],
							'EEK_EXTENSIONS':					final_settings_dict['EEK_EXTENSIONS'],
							'VID_EEK_EXTENSIONS':				final_settings_dict['VID_EEK_EXTENSIONS'],
							'EXTENSIONS':						final_settings_dict['EXTENSIONS'],
							'WORKING_PIXEL_FORMAT':				final_settings_dict['WORKING_PIXEL_FORMAT'],
							'TARGET_PIXEL_FORMAT':				final_settings_dict['TARGET_PIXEL_FORMAT'],
							'DG_PIXEL_FORMAT':					final_settings_dict['DG_PIXEL_FORMAT'],
							'TARGET_FPS':						final_settings_dict['TARGET_FPS'],
							'DURATION_PIC_FRAMES':				final_settings_dict['DURATION_PIC_FRAMES'],
							'DURATION_CROSSFADE_FRAMES':		final_settings_dict['DURATION_CROSSFADE_FRAMES'],
							'DURATION_BLANK_CLIP_FRAMES':		final_settings_dict['DURATION_BLANK_CLIP_FRAMES'],
							'DURATION_MAX_VIDEO_FRAMES':		final_settings_dict['DURATION_MAX_VIDEO_FRAMES'],
							'MODX':								final_settings_dict['MODX'],
							'MODY':								final_settings_dict['MODY'],
							'SUBTITLE_MAX_DEPTH':				final_settings_dict['SUBTITLE_MAX_DEPTH'],
							'Rotation_anti_clockwise':			final_settings_dict['ROTATION_ANTI_CLOCKWISE'],
							'Rotation_clockwise':				final_settings_dict['ROTATION_CLOCKWISE'],
							'TARGET_VFR_FPSNUM':				final_settings_dict['TARGET_VFR_FPSNUM'],
							'TARGET_VFR_FPSDEN':				final_settings_dict['TARGET_VFR_FPSDEN'],
							'TARGET_VFR_FPS':					final_settings_dict['TARGET_VFR_FPS'],
							'TARGET_VFR_FPSNUM':				final_settings_dict['TARGET_VFR_FPSNUM'],
							'TARGET_VFR_FPSDEN':				final_settings_dict['TARGET_VFR_FPSDEN'],
							'TARGET_VFR_FPS':					final_settings_dict['TARGET_VFR_FPS'],
							'precision_tolerance':				final_settings_dict['PRECISION_TOLERANCE'],				# the only one that is a lowercase ley
							'TARGET_COLOR_RANGE_I_ZIMG':		final_settings_dict['TARGET_COLOR_RANGE_I_ZIMG'],
						}

	# MAP that back into something compatible with OLD '_ini_values[self._ini_section_name]["SETTING_NAME"]'
	old_ini_dict = { final_settings_dict['_INI_SECTION_NAME']: old_calc_ini_dict }
	
	# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
	# for good measure, poke the final dict into GLOBAL_UTILITIES_AND_VARIABLES as UTIL so that everyne can access it directly if need be
	UTIL.SETTINGS_DICT =  final_settings_dict
	# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

	#######################################################################################################################################
	#######################################################################################################################################

	# re-Save DEBUG versions of those dicts. Do not care if we do it multiple time.  
	# We only load (a) once in the controller (2) once every time the encoder is run with debug on.
	if UTIL.DEBUG:
		try:
			f_debug = UTIL.fully_qualified_filename(os.path.join(TEMP_FOLDER, SLIDESHOW_SETTINGS_MODULE_NAME + r'.DEBUG.user_settings.JSON'))
			with open(f_debug, 'w') as fp:
				json.dump(user_specified_settings_dict, fp, indent=4)
		except Exception as e:
			print(f"DEBUG: load_settings: ERROR: error dumping JSON file: '{f_debug}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		#
		try:
			f_debug = UTIL.fully_qualified_filename(os.path.join(TEMP_FOLDER, SLIDESHOW_SETTINGS_MODULE_NAME + r'.DEBUG.default_settings.JSON'))
			with open(f_debug, 'w') as fp:
				json.dump(default_settings_dict, fp, indent=4)
		except Exception as e:
			print(f"DEBUG: load_settings: ERROR: error dumping JSON file: '{f_debug}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		#
		try:
			f_debug = UTIL.fully_qualified_filename(os.path.join(TEMP_FOLDER, SLIDESHOW_SETTINGS_MODULE_NAME + r'.DEBUG.final_settings.JSON'))
			with open(f_debug, 'w') as fp:
				json.dump(final_settings_dict, fp, indent=4)
		except Exception as e:
			print(f"DEBUG: load_settings: ERROR: error dumping JSON file: '{f_debug}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		#
		try:
			f_debug = UTIL.fully_qualified_filename(os.path.join(TEMP_FOLDER, SLIDESHOW_SETTINGS_MODULE_NAME + r'.DEBUG.old_ini_dict.JSON'))
			with open(f_debug, 'w') as fp:
				json.dump(old_ini_dict, fp, indent=4)
		except Exception as e:
			print(f"DEBUG: load_settings: ERROR: error dumping JSON file: '{f_debug}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	
		#
		try:
			f_debug = UTIL.fully_qualified_filename(os.path.join(TEMP_FOLDER, SLIDESHOW_SETTINGS_MODULE_NAME + r'.DEBUG.old_calc_ini_dict.JSON'))
			with open(f_debug, 'w') as fp:
				json.dump(old_calc_ini_dict, fp, indent=4)
		except Exception as e:
			print(f"DEBUG: load_settings: ERROR: error dumping JSON file: '{f_debug}'\n{str(e)}",flush=True,file=sys.stderr)
			sys.exit(1)	

	#######################################################################################################################################
	#######################################################################################################################################
	
	# if the initial settings do not exist, create a raw template then exit immediately.
	
	if not os.path.exists(SLIDESHOW_SETTINGS_MODULE_FILENAME):
		valid_resolutions = [k for k in valid_TARGET_RESOLUTION_DICT.keys()]
		valid_bitrates = [ { i : valid_TARGET_RESOLUTION_DICT[i]["BITRATE"] } for i in valid_TARGET_RESOLUTION_DICT.keys() ]
		specially_formatted_settings_list =	[
										[ 'ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS',	ROOT_FOLDER_SOURCES_LIST_FOR_IMAGES_PICS,	r'a list, one or more folders to look in for slideshow pics/videos. the r in front of the string is CRITICAL' ],
										[ 'RECURSIVE',									RECURSIVE,									r'case sensitive: whether to recurse the source folder(s) looking for slideshow pics/videos' ],
										[ 'TEMP_FOLDER',								TEMP_FOLDER,								r'folder where temporary files go; USE A DISK WITH LOTS OF SPARE DISK SPACE - CIRCA 6 GB PER 100 PICS/VIDEOS' ],
										[ 'BACKGROUND_AUDIO_INPUT_FOLDER',				BACKGROUND_AUDIO_INPUT_FOLDER,				r'Folder containing audio files (in sequence) to make an audio background track (it is not looped if too short). No files = silent background.' ],
										[ 'FINAL_MP4_WITH_AUDIO_FILENAME',				FINAL_MP4_WITH_AUDIO_FILENAME,				r'the filename of the FINAL slideshow .mp4' ],
										[ 'SUBTITLE_DEPTH',								SUBTITLE_DEPTH,								r'how many folders deep to display in subtitles; use 0 for no subtitling' ],
										[ 'SUBTITLE_FONTSIZE',							SUBTITLE_FONTSIZE,							r'fontsize for subtitles, leave this alone unless confident' ],
										[ 'SUBTITLE_FONTSCALE',							SUBTITLE_FONTSCALE,							r'fontscale for subtitles, leave this alone unless confident' ],
										[ 'DURATION_PIC_SEC',							DURATION_PIC_SEC,							r'in seconds, duration each pic is shown in the slideshow' ],
										[ 'DURATION_CROSSFADE_SECS',					DURATION_CROSSFADE_SECS,					r'in seconds duration crossfade between pic, leave this alone unless confident' ],
										[ 'CROSSFADE_TYPE',								CROSSFADE_TYPE,								r'random is a good choice, leave this alone unless confident' ],
										[ 'CROSSFADE_DIRECTION',						CROSSFADE_DIRECTION,						r'Please leave this alone unless really confident' ],
										[ 'DURATION_MAX_VIDEO_SEC',						DURATION_MAX_VIDEO_SEC,						r'in seconds, maximum duration each video clip is shown in the slideshow' ],
										[ 'TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB',	TARGET_AUDIO_BACKGROUND_NORMALIZE_HEADROOM_DB,	r'normalize background audio to this maximum db' ],
										[ 'TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY',	TARGET_AUDIO_BACKGROUND_GAIN_DURING_OVERLAY,	r'how many DB to reduce backround audio during video clip audio overlay' ],
										[ 'TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB',		TARGET_AUDIO_SNIPPET_NORMALIZE_HEADROOM_DB,		r'normalize video clip audio to this maximum db; camera vids are quieter so gain them' ],
										[ 'MAX_FILES_PER_CHUNK',						MAX_FILES_PER_CHUNK,						r'how many images/videos to process in each chunk (more=slower)' ],
										[ 'DEBUG',										DEBUG,										r'see and regret seeing, ginormous debug output' ],
										[ 'FFMPEG_PATH',								FFMPEG_PATH,								r'Please leave this alone unless really confident' ],
										[ 'FFPROBE_PATH',								FFPROBE_PATH,								r'Please leave this alone unless really confident' ],
										[ 'VSPIPE_PATH',								VSPIPE_PATH,								r'Please leave this alone unless really confident' ],
										[ 'FFMPEG_ENCODER',								FFMPEG_ENCODER,								f'Please leave this alone unless really confident. One of {valid_FFMPEG_ENCODER}. h264_nvenc only works on "nvidia 2060 Super" upward.' ],
										[ 'TARGET_RESOLUTION',							TARGET_RESOLUTION,							f'eg 1080p : One of {valid_resolutions} only. Others result in broken aspect ratios.' ],
										[ 'TARGET_VIDEO_BITRATE',						TARGET_VIDEO_BITRATE,						f'eg 4.5M : {valid_bitrates}' ],
										[ 'slideshow_CONTROLLER_path',					slideshow_CONTROLLER_path,					r'Please leave this alone unless really confident' ],
										[ 'slideshow_LOAD_SETTINGS_path',				slideshow_LOAD_SETTINGS_path,				r'Please leave this alone unless really confident' ],
										[ 'slideshow_ENCODER_legacy_path',				slideshow_ENCODER_legacy_path,				r'Please leave this alone unless really confident' ],
									]	
		if UTIL.DEBUG:	print(f'DEBUG: specially_formatted_settings_list=\n{UTIL.objPrettyPrint.pformat(specially_formatted_settings_list)}',flush=True,file=sys.stderr)
		print(f"load_settings: ERROR: File '{SLIDESHOW_SETTINGS_MODULE_FILENAME}' does not exist, creating it with template settings... you MUST edit it now ...",flush=True,file=sys.stderr)
		create_py_file_from_specially_formatted_list(SLIDESHOW_SETTINGS_MODULE_FILENAME, specially_formatted_settings_list)
		sys.exit(1)

	#######################################################################################################################################
	#######################################################################################################################################

	return final_settings_dict, old_ini_dict, old_calc_ini_dict, user_specified_settings_dict

