### LEGACY CODE

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

from PIL import Image, ExifTags, UnidentifiedImageError
from PIL.ExifTags import TAGS

import pydub
from pydub import AudioSegment

CDLL(r'MediaInfo.dll')				# note the hard-coded folder	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
from MediaInfoDLL3 import MediaInfo, Stream, Info, InfoOption		# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
#from MediaInfoDLL3 import *											# per https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py

#core.std.LoadPlugin(r'DGDecodeNV.dll')
#core.avs.LoadPlugin(r'DGDecodeNV.dll')

global TERMINAL_WIDTH					# for use by PrettyPrinter
TERMINAL_WIDTH = 250
global objPrettyPrint
objPrettyPrint = pprint.PrettyPrinter(width=TERMINAL_WIDTH, compact=False, sort_dicts=False)	# facilitates formatting and printing of text and dicts etc

#def UTIL.normalize_path(path):
#	#if DEBUG:	print(f"DEBUG: UTIL.normalize_path:  incoming path='{path}'",flush=True,file=sys.stderr)
#	# Replace single backslashes with double backslashes
#	path = path.rstrip(os.linesep).strip('\r').strip('\n').strip()
#	r1 = r'\\'
#	r2 = r1 + r1
#	r4 = r2 + r2
#	path = path.replace(r1, r4)
#	# Add double backslashes before any single backslashes
#	for i in range(0,20):
#		path = path.replace(r2, r1)
#	#if DEBUG:	print(f"DEBUG: UTIL.normalize_path: outgoing path='{path}'",flush=True,file=sys.stderr)
#	return path

# A Special function needed at the top DEFAULT_INI_FILE_SPECIFYING_PARAMETERS and DEFAULT_DIRECTORY_LIST
#def UTIL.fully_qualified_directory_no_trailing_backslash(directory_name):
#	# make into a fully qualified directory string stripped and without a trailing backslash
#	# also remove extraneous backslashes which get added by things like abspath
#	new_directory_name = os.path.abspath(directory_name).rstrip(os.linesep).strip('\r').strip('\n').strip()
#	if directory_name[-1:] == (r'\ '.strip()):		# r prefix means the string is treated as a raw string so all escape codes will be ignored. EXCEPT IF THE \ IS THE LAST CHARACTER IN THE STRING !
#		new_directory_name = directory_name[:-1]	# remove any trailing backslash
#	new_directory_name = UTIL.normalize_path(new_directory_name)
#	return new_directory_name

#def UTIL.fully_qualified_filename(file_name):
#	# Make into a fully qualified filename string using double backslashes
#	# to later print/write with double backslashes use eg
#	#	converted_string = UTIL.fully_qualified_filename('D:\\a\\b\\\\c\\\\\\d\\e\\f\\filename.txt')
#	#	print(repr(converted_string),flush=True,file=sys.stderr)
#	# yields 'D:\\a\\b\\c\\d\\e\\f\\filename.txt'
#	new_file_name = os.path.abspath(file_name).rstrip(os.linesep).strip('\r').strip('\n').strip()
#	if new_file_name.endswith('\\'):
#		new_file_name = new_file_name[:-1]  # Remove trailing backslash
#	new_file_name = UTIL.normalize_path(new_file_name)
#	return new_file_name


###
# Define GLOBALS and initialize them
#
global FFMPEG_PATH
FFMPEG_PATH = 'this_is_set_in_class_settings'
global IS_DEBUG
IS_DEBUG = False						# default DEBUG to False
global IS_DEBUG_SYSTEM_OVERRIDE
IS_DEBUG_SYSTEM_OVERRIDE = False		# for major debugging ONLY: this is always FALSE otherwide ...
global A_DEBUG_IS_ON
A_DEBUG_IS_ON = IS_DEBUG or IS_DEBUG_SYSTEM_OVERRIDE
#
# 2022.03.19, see what happens with multi [ "MI = MediaInfo()" and matching "del MI" ] instead of one global declaration
#global MI
#MI = MediaInfo()	# initialize a global for mediainfo per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
#

##########
global objSettings	# a global object for the class which deals with settings.
objSettings = None

##########
# some "working" globals
global last_file_opened_with_ffms2
global last_file_opened_with_imwri
global last_file_opened_with_LWLibavSource
global last_file_opened_with_LibavSMASHSource
global Count_of_files
#
# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
# When calling rezisers etc, ONLY use these values:
#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
# but when obtaining from frame properties and comparing etc, use the vs values from
# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
global ZIMG_RANGE_LIMITED
ZIMG_RANGE_LIMITED  = 0		# /**< Studio (TV) legal range, 16-235 in 8 bits. */
global ZIMG_RANGE_FULL
ZIMG_RANGE_FULL     = 1		# /**< Full (PC) dynamic range, 0-255 in 8 bits. */

# https://www.vapoursynth.com/doc/apireference.html?highlight=_FieldBased
global vs_interlaced
vs_interlaced = { 'Progressive' : 0, 'BFF' : 1, 'TFF' : 2 }		# vs documnetation says frame property _FieldBased is one of 0=frame based (progressive), 1=bottom field first, 2=top field first.

###
# Public Domain software: vs_transitions
#		https://github.com/OrangeChannel/vs-transitions
# vs-transitions SOURCE CODE:
#		https://raw.githubusercontent.com/OrangeChannel/vs-transitions/master/vs_transitions/__init__.py
# vs-transitions DOCUMENTATION:
#		https://vapoursynth-transitions.readthedocs.io/en/latest/api.html
# modified and saved as vs_transitions.py from
#		https://raw.githubusercontent.com/OrangeChannel/vs-transitions/master/vs_transitions/__init__.py
import vs_transitions
###
global crossfade_type_list
crossfade_type_list = list(map(str.lower,[		'none',
												'random',
												'fade', 
												'fade_to_black',
												'fade_from_black',
												'wipe',
												'push', 
												'slide_expand',
												'squeeze_slide', 
												'squeeze_expand', 
												'cover', 
												'reveal', 
												'curtain_cover', 
												'curtain_reveal', 
												'peel', 
												'pixellate',
												'cube_rotate', 
												#'linear_boundary', 
												]))
global crossfade_type_list_no_black_fades
crossfade_type_list_no_black_fades = list(map(str.lower,[
												'none',
												#'random',
												'fade', 
												#'fade_to_black',
												#'fade_from_black',
												'wipe',
												'push', 
												'slide_expand',
												'squeeze_slide', 
												'squeeze_expand', 
												'cover', 
												'reveal', 
												'curtain_cover', 
												'curtain_reveal', 
												'peel', 
												'pixellate',
												'cube_rotate', 
												#'linear_boundary', 
												]))
global crossfade_direction_list
crossfade_direction_list = []
for v in vs_transitions.Direction:
	crossfade_direction_list.append(v.value)


###
def print_DEBUG(*args, **kwargs):	# PRINT TO stderr
	# per https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
	if A_DEBUG_IS_ON:
		right_now = datetime.datetime.now().strftime('%Y-%m-%d.%H:%M:%S.%f')
		print(f'{right_now} DEBUG:', *args, **kwargs, file=sys.stderr, flush=True)

###
def print_NORMAL(*args, **kwargs):	# PRINT TO stderr
	# per https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
	right_now = datetime.datetime.now().strftime('%Y-%m-%d.%H:%M:%S.%f')
	print(f'{right_now}', *args, **kwargs, file=sys.stderr, flush=True)


###
class settings:
	# class global variables shared across instances
	_ini_section_name = 'slideshow'
	SETTINGS_DICT = {}
	USER_SPECIFIED_SETTINGS_DICT = {}
	_ini_values =  { _ini_section_name : {} }
	calc_ini = {}
	def __init__(self):
		global IS_DEBUG
		global A_DEBUG_IS_ON
		global FFMPEG_PATH
		import slideshow_LOAD_SETTINGS	# from same folder .\
		self.SETTINGS_DICT, self._ini_values, self.calc_ini, self.USER_SPECIFIED_SETTINGS_DICT = slideshow_LOAD_SETTINGS.load_settings()
		# slideshow_LOAD_SETTINGS.load_settings() returns 4 things:
		# SETTINGS_DICT					contains user settings with defaults appled plus "closed" settings added
		# INI_DICT						an old dict compatible with the "chunk encoder" which has an older code base (with changes to understand modern chunk and snippet)
		# CALC_INI_DICT	 				per "INI_DICT" but with extra fields calculated and added per the legacy CALC_INI
		# USER_SPECIFIED_SETTINGS_DICT	the settings which were specified by the user

		if self.SETTINGS_DICT['DEBUG']:
			IS_DEBUG = True
		else:
			IS_DEBUG = False
		A_DEBUG_IS_ON = IS_DEBUG or IS_DEBUG_SYSTEM_OVERRIDE
		FFMPEG_PATH = self.SETTINGS_DICT['FFMPEG_PATH']


		# make class variables from the self.calc_ini dictionary	# https://www.geeksforgeeks.org/how-to-change-a-dictionary-into-a-class/
		# Having made class variables from the self.SETTINGS_DICT dictionary
		# we can read them as normal class variables like thing.variable_name
		#               or as   dictionary variables like thing.calc_ini["key_name"]
		# *** Remembering the dict and the class-global variables are SEPARATE VARIABLES and 
		#     that overwriting one does NOT overwrite the other and mismatches WILL then occur ...
		# OR ...
		# self.__dict__.update(self.calc_ini)	# per https://www.sobyte.net/post/2022-04/python-dict-2-member-variables/ # this updates existing variables with new values per https://www.geeksforgeeks.org/python-dictionary-update-method/
		for key in self.SETTINGS_DICT:
			if not key.startswith(';'):
				setattr(self, key, self.SETTINGS_DICT[key])	# this updates existing variables with new values

		# THIS NEXT BIT IS REQUIRED AND RELIED ON THROUGHOUT THIS LEGACY CODE
		# make class variables from the self.calc_ini dictionary	# https://www.geeksforgeeks.org/how-to-change-a-dictionary-into-a-class/
		for key in self.calc_ini:
			if not key.startswith(';'):
				setattr(self, key, self.calc_ini[key])	# this updates existing variables with new values
		#

	def class_variables_and_values(self):
		# yield class variables and values as a dict
		return self.__dict__

	def debug_print_class_vars(self):
		#members = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
		#print(members, file=sys.stderr, flush=True)
		# we need to convert  vars(self).items() to a LIST, since dict does not allow duplicate keys
		#objPrettyPrint.pprint(vars(self), file=sys.stderr, flush=True)
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: CLASS VARIABLES IN ALPHABETIC NAME ORDER')
		c = sorted(vars(self).items(), key=lambda yvar: str(yvar[0]).lower() )
		choppy = 48
		for d,e in c:
			sd = str(d)
			L = min(choppy,len(sd))
			sd = sd[0:L]
			s = ' ' * (choppy-len(sd)+1)
			if A_DEBUG_IS_ON: print_DEBUG(f'"{sd}"{s} = "{e}"')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: {len(c)} VARIABLES IN ALPHABETIC NAME ORDER')
		del c
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: CLASS VARIABLES IN ALPHABETIC VALUE ORDER')
		f = sorted(vars(self).items(), key=lambda yvar: str(yvar[1]).lower() )
		choppy = 64
		for g,h in f:
			sh = str(h)
			m = max(0,choppy-len(sh)+1)
			s = ' '*m
			if A_DEBUG_IS_ON: print_DEBUG(f'"{sh}"{s} = "{g}"')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: {len(f)} VARIABLES IN ALPHABETIC VALUE ORDER')
		del f
	
###
class OBOLETE_legacy_settings:
	# class global variables shared across instances
	_default_ini_file = r'.\SLIDESHOW_PARAMETERS.ini'
	_pre_default_directories_list = [ r'.' ]
	_default_temp_directory = r'.\\temp'
	_default_snippets_filename_path = r'.\\snippets_data.txt'
	_default_output_mkv_filename_path = r'.\\slideshow.txt'
	_ini_section_name = 'slideshow'
	_default_ini_values =  { _ini_section_name : {} }
	_ini_values =  { _ini_section_name : {} }
	DEFAULT_INI_FILE_SPECIFYING_PARAMETERS = ''
	DEFAULT_DIRECTORY_LIST = []
	DEFAULT_TEMP_DIRECTORY_LIST = []
	DEFAULT_SNIPPETS_FILENAME_PATH_LIST = []
	DEFAULT_OUTPUT_MKV_FILENAME_PATH_LIST = []
	#
	ini_file_specifying_parameters = ''
	calc_ini = {}

	def __repr__(self):
		# override the __repr__ method of our class and make it print out something a more useful, like class variables
		# https://www.blog.pythonlibrary.org/2014/02/14/python-101-how-to-change-a-dict-into-a-class/
		attrs = str([x for x in self.__dict__])
		#attrs = str([x for x in dir(self) if not x.startswith('__')])	# also could have done this:
		#return "<settings: %s="">" % attrs
		return "<settings: %s"">" % attrs

	def class_variables_and_values(self):
		return self.__dict__

	def debug_print_class_vars(self):
		#members = [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__")]
		#print(members, file=sys.stderr, flush=True)
		# we need to convert  vars(self).items() to a LIST, since dict does not allow duplicate keys
		#objPrettyPrint.pprint(vars(self), file=sys.stderr, flush=True)
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: CLASS VARIABLES IN ALPHABETIC NAME ORDER')
		c = sorted(vars(self).items(), key=lambda yvar: str(yvar[0]).lower() )
		choppy = 48
		for d,e in c:
			sd = str(d)
			L = min(choppy,len(sd))
			sd = sd[0:L]
			s = ' ' * (choppy-len(sd)+1)
			if A_DEBUG_IS_ON: print_DEBUG(f'"{sd}"{s} = "{e}"')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: {len(c)} VARIABLES IN ALPHABETIC NAME ORDER')
		del c
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: CLASS VARIABLES IN ALPHABETIC VALUE ORDER')
		f = sorted(vars(self).items(), key=lambda yvar: str(yvar[1]).lower() )
		choppy = 64
		for g,h in f:
			sh = str(h)
			m = max(0,choppy-len(sh)+1)
			s = ' '*m
			if A_DEBUG_IS_ON: print_DEBUG(f'"{sh}"{s} = "{g}"')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: {len(f)} VARIABLES IN ALPHABETIC VALUE ORDER')
		del f
		return

	def __init__(self):
		global IS_DEBUG
		global A_DEBUG_IS_ON
		self.DEFAULT_INI_FILE_SPECIFYING_PARAMETERS = UTIL.fully_qualified_directory_no_trailing_backslash(self._default_ini_file)	# r prefix means the string is treated as a raw string so all escape codes will be ignored. EXCEPT IF THE \ is the last character in the string ! So don't put one there.
		self.ini_file_specifying_parameters = UTIL.fully_qualified_directory_no_trailing_backslash(self.DEFAULT_INI_FILE_SPECIFYING_PARAMETERS)
		for ddl in self._pre_default_directories_list:
			self.DEFAULT_DIRECTORY_LIST.append(UTIL.fully_qualified_directory_no_trailing_backslash(ddl))			
		self.DEFAULT_TEMP_DIRECTORY_LIST = [ UTIL.fully_qualified_directory_no_trailing_backslash(self._default_temp_directory) ]
		self.DEFAULT_SNIPPETS_FILENAME_PATH_LIST = [ UTIL.fully_qualified_filename(self._default_snippets_filename_path) ]
		self.DEFAULT_OUTPUT_MKV_FILENAME_PATH_LIST = [ UTIL.fully_qualified_filename(self._default_output_mkv_filename_path) ]
		self._default_ini_values = { 
							self._ini_section_name : {
							'; CRITICAL NOTES re "directory_list" and "temp_directory"' : '.',
							';   1. paths MUST ALWAYS contain DOUBLE backslashes in every instance - a single backslash causes problems and the result, if any, will be extremely uncertain' : '.',
							';   2. paths must NEVER end with a backslash; backslashes are "escaping" notifiers - if a path ends in a backslash, always put a space character after it at the end of string' : '.',
							'; remember : always use double-backslashes in all paths' : '.',
							'; remember : never end a path with a backslash as the last character (you would rue it)' : '.',
							';' : '.',
							'; "DIRECTORY_LIST" is defined as a list of paths (double-backslashed); beware: .\\\\ by itself means current default path' : '.',
							'DIRECTORY_LIST' :					str(self.DEFAULT_DIRECTORY_LIST),						# must convert LIST to a STR or it all fails
							'; "TEMP_DIRECTORY_LIST" is defined as a list of paths (for coding convenience) however only the first path in the list will be used' : '.',
							'TEMP_DIRECTORY_LIST' :				str(self.DEFAULT_TEMP_DIRECTORY_LIST),
							'; "SNIPPETS_FILENAME_PATH_LIST" is defined as a list of paths (for coding convenience) however only the first path in the list will be used' : '.',
							'SNIPPETS_FILENAME_PATH_LIST' :			str(self.DEFAULT_SNIPPETS_FILENAME_PATH_LIST),
							'; "OUTPUT_MKV_FILENAME_PATH_LIST" is defined as a list of paths (for coding convenience) however only the first path in the list will be used' : '.',
							'OUTPUT_MKV_FILENAME_PATH_LIST' :			str(self.DEFAULT_OUTPUT_MKV_FILENAME_PATH_LIST),
							'; "RECURSIVE" is True or False; if True, it also walks the sub-directory tree(s) looking for images/videos' : '.',
							'RECURSIVE' :						True,
							'; "SUBTITLE_DEPTH" an integer; it subtitles with the path/filename of the image/video from the right up to the nominated depth; 0 turns it off' : '.',
							'SUBTITLE_DEPTH' :					3,													# adds a subtitle in the bottom right corner containing the last specified number of  parts of the path to the image/video
							'; "SUBTITLE_FONTSIZE" an integer; the fontsize used for subtitling (18 is good)' : '.',
							'SUBTITLE_FONTSIZE' :				18,
							'; "SUBTITLE_FONTSCALE" a real number; scale applied to the fontsize (1.0 to 3.0 is good)' : '.',
							'SUBTITLE_FONTSCALE' :				1.0,
							'; "DURATION_PIC_SEC" a real number; the number of seconds a pic is displayed in trhe slideshow' : '.',
							'DURATION_PIC_SEC' :				4.0,												### MAXIMUM duration of display of an image, in seconds
							'; "DURATION_CROSSFADE_SECS" a real number; the number of seconds for a crossfade between each image/video' : '.',
							'DURATION_CROSSFADE_SECS':			0.5,													# 0.5 sec is best. # could be 0.2
							'; "CROSSFADE_TYPE" a string; the type of crossfade if DURATION_CROSSFADE_SECS > 0' : '.',
							f'; "CROSSFADE_TYPE" must be one of {crossfade_type_list}' : '.',
							'CROSSFADE_TYPE':					'random',
							'; "CROSSFADE_DIRECTION" a string; the direction of crossfade type if DURATION_CROSSFADE_SECS > 0' : '.',
							f'; "CROSSFADE_DIRECTION" must be one of {crossfade_direction_list}' : '.',
							f'; CROSSFADE_DIRECTION" could be be one of "{vs_transitions.Direction.LEFT.value}" "{vs_transitions.Direction.RIGHT.value}" "{vs_transitions.Direction.UP.value}" "{vs_transitions.Direction.DOWN.value}" if crossfade type not "curtain_cover" or "curtain_reveal"' : '.',
							f'; CROSSFADE_DIRECTION" could be be "{vs_transitions.Direction.HORIZONTAL.value}" or "{vs_transitions.Direction.VERTICAL.value}" if crossfade type is "curtain_cover" or "curtain_reveal"' : '.',
							'CROSSFADE_DIRECTION':				vs_transitions.Direction.LEFT.value,
							'; "DURATION_MAX_VIDEO_SEC" a real number; the maximum number of seconds a video runs before it is clipped off' : '.',
							'DURATION_MAX_VIDEO_SEC' :			15.0,												# Maximum duration of a video clip in seconds (incoming video will get clipped at this point)
							'; "DENOISE_SMALL_SIZE_VIDEOS" is True or False; if True, smaller framesize videos (which tend to be older and noisier) will be slightly denoised using mv.Degrain1' : '.',
							'DENOISE_SMALL_SIZE_VIDEOS' :		True,
							'; "DEBUG_MODE" is True or False; if True, you will rue the day - an unbelievable volume of debug messages as used during development/debugging' : '.',
							'DEBUG_MODE' :						False,
							'; Does not matter what you specify for TARGET_COLOR* stuff here, we always used fixed values ahs shown below' : '',
							'; "TARGET_COLORSPACE" a string; set for HD; required to render subtitles, it is fixed at this value; this item MUST MATCH TARGET_COLORSPACE_MATRIX_I etc' : '.',
							'TARGET_COLORSPACE' : 				r'BT.709',											# for subtitling. # colorspace Rec2020, BT.2020 Rec709, BT.709, Rec601, BT.601, PC.709, PC.601, TV.fcc, PC.fcc, TV.240m, PC.240m; When no hint found in ASS script and colorspace parameter is empty then the default is BT.601
							# ALSO ... A note about fixed output colour characteristics (the y4m YUV4MPEG2 container doesn't mention them.
							# https://forum.videohelp.com/newreply.php?do=postreply&t=408230#post2684387
							# So we always output BT.709 and related characteristics per what we specify here in _default_ini_values
							'; "TARGET_COLORSPACE_MATRIX_I" an integer; set for HD; this is the value that counts; it is fixed at this value; turn on DEBUG_MODE to see lists of these values' : '.',
							'TARGET_COLORSPACE_MATRIX_I' :		int(vs.MatrixCoefficients.MATRIX_BT709.value),
							'; "TARGET_COLOR_TRANSFER_I" an integer; set for HD; this is the value that counts; it is fixed at this value; used by Vapoursynth; turn on DEBUG_MODE to see lists of these values' : '.',
							'TARGET_COLOR_TRANSFER_I' :			int(vs.TransferCharacteristics.TRANSFER_BT709.value),
							'; "TARGET_COLOR_PRIMARIES_I" an integer; set for HD; this is the value that counts; it is fixed at this value; turn on DEBUG_MODE to see lists of these values' : '.',
							'TARGET_COLOR_PRIMARIES_I' :		int(vs.ColorPrimaries.PRIMARIES_BT709.value),
							# NOTE THESE IN REGARD TO VS "bug" in RANGE values not agreeing with the spec:
							#	https://github.com/vapoursynth/vapoursynth/issues/940
							#	https://github.com/vapoursynth/vapoursynth/issues/857
							# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
							# When calling rezisers etc, ONLY use these values:
							#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
							#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
							# but when obtaining from frame properties and comparing etc, use the vs values from
							# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
							# BUT BUT BUT here we are working solely with vapoursynth settings, not resizers, so stick with using vapoursynth constants and not zimg ones
							'; "TARGET_COLOR_RANGE_I" an integer; set for full-range, not limited-range; this is the (Vapoursynth) value that counts; it is fixed at this value; used by Vapoursynth; turn on DEBUG_MODE to see lists of these values' : '.',
							'; "TARGET_COLOR_RANGE_I note: this Vapoursynth value is opposite to that needed by ZIMG and by resizers which require the ZIMG (the propeer) value; internal transations vs->zimg are done' : '.',
							'TARGET_COLOR_RANGE_I' :			int(vs.ColorRange.RANGE_FULL.value),
							'; "TARGET_WIDTH" an integer; set for HD; do not change unless a dire emergency' : '.',
							'TARGET_WIDTH' :					1920,
							'; "TARGET_HEIGHT" an integer; set for HD; do not change unless a dire emergency' : '.',
							'TARGET_HEIGHT' :					1080,
							'; "TARGET_FPSNUM" an integer; set for PAL' : '.',
							'TARGET_FPSNUM' :					25,													# for fps numerator		... PAL world bias
							'; "TARGET_FPSDEN" an integer; set for PAL' : '.',
							'TARGET_FPSDEN' :					1,													# for fps denominator	... PAL world bias
							'; "UPSIZE_KERNEL" a string; do not change unless a dire emergency; you need the EXACT string name of the resizer' : '.',
							'UPSIZE_KERNEL' :					r'Lanczos',
							'; "DOWNSIZE_KERNEL" a string; do not change unless a dire emergency; you need the EXACT string name of the resizer' : '.',
							'DOWNSIZE_KERNEL' :					r'Spline36',
							'; "BOX" is True or False; if True, images and videos are resized vertically/horizontally to maintain aspect ratio and padded; False streches and squeezes ' : '.',
							'BOX' :								True,											# True would initiate letterboxing or pillarboxing. False fills to TARGET_WIDTH,TARGET_HEIGHT
							}
						}
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: __init__: _default_ini_values=\n{objPrettyPrint.pformat(self._default_ini_values)}')
		#for k, v in _default_ini_values[self._ini_section_name].items():
		#	if A_DEBUG_IS_ON: print_DEBUG(f'USING A FOR LOOP, _default_ini_values {objPrettyPrint.pformat(k)}"] = "{objPrettyPrint.pformat(v)}"')
		self.read_ini_and_calculate_settings()
		return

	def read_ini_and_calculate_settings(self):
		global IS_DEBUG
		global A_DEBUG_IS_ON
		self._ini_values = self._default_ini_values	# default to the defaults funnily enough
		config = None
		config = configparser.ConfigParser(self._default_ini_values[self._ini_section_name], allow_no_value=True)	# create a configparser objeft which also uses the default values we set above
		reset_to_ini_defaults = False
		if os.path.isfile(self.ini_file_specifying_parameters):
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: .ini file "{self.ini_file_specifying_parameters}" exists ... about to try reading that .ini file ...')
			input_file = open(self.ini_file_specifying_parameters,'r')
			config.read_file(input_file)
			input_file.close()
			if config.has_section(self._ini_section_name):
				if config.has_option(self._ini_section_name, "DEBUG_MODE"):
					if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: config.has_option(self._ini_section_name, "DEBUG_MODE") detected in .ini, value={config.getboolean(self._ini_section_name, "DEBUG_MODE")}')
					IS_DEBUG = config.getboolean(self._ini_section_name, "DEBUG_MODE")	# if enabled, turn on DEBUG immediately
					A_DEBUG_IS_ON = IS_DEBUG or IS_DEBUG_SYSTEM_OVERRIDE
				###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: "{self._ini_section_name}" detected in config, config={objPrettyPrint.pformat(config[self._ini_section_name].items())}')
				#for k,v in config[self._ini_section_name].items():
				#	if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: \tRAW, READ FROM .ini WITH DEFAULTS: config["{self._ini_section_name}"]["{objPrettyPrint.pformat(k)}"] = {objPrettyPrint.pformat(v)}')
				reset_to_ini_defaults = False
			else:
				print_NORMAL(f'ENCODER: class settings: read_ini_and_calculate_settings: WARNING: Missing section "{self._ini_section_name}" in .ini file "{self.ini_file_specifying_parameters}". Using defaults.')
				reset_to_ini_defaults = True
		else:
			print_NORMAL(f'ENCODER: class settings: read_ini_and_calculate_settings: WARNING: Missing .ini file "{self.ini_file_specifying_parameters}". Using defaults.')
			reset_to_ini_defaults = True
		if reset_to_ini_defaults:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: Reverting to default ini settngs')
			config = configparser.ConfigParser(allow_no_value=True)	# don't apply defaults here, do't want them written to the .ini file
			# ... the ini is not yet fleshed out with extra values but re-save it anyway
			config.read_dict(self._default_ini_values)
			# re-write the .ini file with newly defaulted values
			o_f = open(self.ini_file_specifying_parameters,'w')
			config.write(o_f)
			o_f.close()
			# re-read the parameters from the newly re-created .ini file, applying defaults to the read operation
			config = configparser.ConfigParser(self._default_ini_values[self._ini_section_name], allow_no_value=False)
			i_f = open(self.ini_file_specifying_parameters,'r')
			config.read_file(i_f)
			i_f.close()
			if config.has_option(self._ini_section_name, "DEBUG_MODE"):
				if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: .ini re-read: config.getboolean(self._ini_section_name, "DEBUG_MODE") detected value={config.getboolean(self._ini_section_name, "DEBUG_MODE")}')
				IS_DEBUG = config.getboolean(self._ini_section_name, "DEBUG_MODE")	# if enabled, turn on/off DEBUG_MODE immediately
				A_DEBUG_IS_ON = IS_DEBUG or IS_DEBUG_SYSTEM_OVERRIDE
		else:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: Using settings from .ini file "{self.ini_file_specifying_parameters}"')
			pass
		if A_DEBUG_IS_ON: print_DEBUG(f'Final setting of DEBUG_MODE={config.getboolean(self._ini_section_name, "DEBUG_MODE")} ... global DEBUG_MODE={IS_DEBUG} A_DEBUG_IS_ON={A_DEBUG_IS_ON}')
		#
		# grab the .ini settings that the user has specified, or the defaults we have set, or combined both
		if config.has_section(self._ini_section_name):
			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as config.get(self._ini_section_name, "DIRECTORY_LIST")={config.get(self._ini_section_name, "DIRECTORY_LIST")}')
			self._ini_values[self._ini_section_name]["DIRECTORY_LIST"]				= ast.literal_eval(config.get(self._ini_section_name, 'DIRECTORY_LIST'))		# convert str back into a list with ast
			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as self._ini_values[self._ini_section_name]["DIRECTORY_LIST"]={self._ini_values[self._ini_section_name]["DIRECTORY_LIST"]}')
			ddl_fully_qualified = []									# make DIRECTORY_LIST entries all fully qualified and escaped where required
			for ddl in self._ini_values[self._ini_section_name]["DIRECTORY_LIST"]:
				ddl_fully_qualified.append(UTIL.fully_qualified_directory_no_trailing_backslash(ddl))
			self._ini_values[self._ini_section_name]["DIRECTORY_LIST"]				= ddl_fully_qualified

			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as config.get(self._ini_section_name, "TEMP_DIRECTORY_LIST")={config.get(self._ini_section_name, "TEMP_DIRECTORY_LIST")}')
			self._ini_values[self._ini_section_name]["TEMP_DIRECTORY_LIST"]			= ast.literal_eval(config.get(self._ini_section_name, 'TEMP_DIRECTORY_LIST'))		# convert str back into a list
			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as self._ini_values[self._ini_section_name]["TEMP_DIRECTORY_LIST"]={self._ini_values[self._ini_section_name]["TEMP_DIRECTORY_LIST"]}')
			td_fully_qualified = []
			for td in self._ini_values[self._ini_section_name]["TEMP_DIRECTORY_LIST"]:	# should only be 1 in the list. if more then we convert them all but only use the first
				td_fully_qualified.append(UTIL.fully_qualified_directory_no_trailing_backslash(td))
			self._ini_values[self._ini_section_name]["TEMP_DIRECTORY_LIST"]			= td_fully_qualified

			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as config.get(self._ini_section_name, "SNIPPETS_FILENAME_PATH_LIST")={config.get(self._ini_section_name, "SNIPPETS_FILENAME_PATH_LIST")}')
			self._ini_values[self._ini_section_name]["SNIPPETS_FILENAME_PATH_LIST"]	= ast.literal_eval(config.get(self._ini_section_name, 'SNIPPETS_FILENAME_PATH_LIST'))		# convert str back into a list
			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as self._ini_values[self._ini_section_name]["SNIPPETS_FILENAME_PATH_LIST"]={self._ini_values[self._ini_section_name]["SNIPPETS_FILENAME_PATH_LIST"]}')
			sfp_fully_qualified = []
			for sfp in self._ini_values[self._ini_section_name]["SNIPPETS_FILENAME_PATH_LIST"]:	# should only be 1 in the list. if more then we convert them all but only use the first
				sfp_fully_qualified.append(UTIL.fully_qualified_filename(sfp))
			self._ini_values[self._ini_section_name]["SNIPPETS_FILENAME_PATH_LIST"]	= sfp_fully_qualified

			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as config.get(self._ini_section_name, "OUTPUT_MKV_FILENAME_PATH_LIST")={config.get(self._ini_section_name, "OUTPUT_MKV_FILENAME_PATH_LIST")}')
			self._ini_values[self._ini_section_name]["OUTPUT_MKV_FILENAME_PATH_LIST"]	= ast.literal_eval(config.get(self._ini_section_name, 'OUTPUT_MKV_FILENAME_PATH_LIST'))		# convert str back into a list
			###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: RAW config .ini read as self._ini_values[self._ini_section_name]["OUTPUT_MKV_FILENAME_PATH_LIST"]={self._ini_values[self._ini_section_name]["OUTPUT_MKV_FILENAME_PATH_LIST"]}')
			amf_fully_qualified = []
			for amf in self._ini_values[self._ini_section_name]["OUTPUT_MKV_FILENAME_PATH_LIST"]:	# should only be 1 in the list. if more then we convert them all but only use the first
				amf_fully_qualified.append(UTIL.fully_qualified_filename(amf))
			self._ini_values[self._ini_section_name]["OUTPUT_MKV_FILENAME_PATH_LIST"]	= amf_fully_qualified

			self._ini_values[self._ini_section_name]["RECURSIVE"]					= config.getboolean(self._ini_section_name, 'RECURSIVE')
			self._ini_values[self._ini_section_name]["SUBTITLE_DEPTH"]				= int(config.getint(self._ini_section_name, 'SUBTITLE_DEPTH'))
			self._ini_values[self._ini_section_name]["SUBTITLE_FONTSIZE"]			= int(config.getint(self._ini_section_name, 'SUBTITLE_FONTSIZE'))
			self._ini_values[self._ini_section_name]["SUBTITLE_FONTSCALE"]			= float(config.getfloat(self._ini_section_name, 'SUBTITLE_FONTSCALE'))
			self._ini_values[self._ini_section_name]["DURATION_PIC_SEC"]			= float(config.getfloat(self._ini_section_name, 'DURATION_PIC_SEC'))
			self._ini_values[self._ini_section_name]["DURATION_CROSSFADE_SECS"]		= float(config.getfloat(self._ini_section_name, 'DURATION_CROSSFADE_SECS'))
			self._ini_values[self._ini_section_name]["CROSSFADE_TYPE"]				= config.get(self._ini_section_name, 'CROSSFADE_TYPE')
			self._ini_values[self._ini_section_name]["CROSSFADE_DIRECTION"]			= config.get(self._ini_section_name, 'CROSSFADE_DIRECTION')
			self._ini_values[self._ini_section_name]["DURATION_MAX_VIDEO_SEC"]		= float(config.getfloat(self._ini_section_name, 'DURATION_MAX_VIDEO_SEC'))
			self._ini_values[self._ini_section_name]["DENOISE_SMALL_SIZE_VIDEOS"]	= config.getboolean(self._ini_section_name, 'DENOISE_SMALL_SIZE_VIDEOS')
			self._ini_values[self._ini_section_name]["DEBUG_MODE"]					= config.getboolean(self._ini_section_name, 'DEBUG_MODE')
			# A note about fixed output colour characteristics (the y4m YUV4MPEG2 container doesn't mention them.
			# https://forum.videohelp.com/newreply.php?do=postreply&t=408230#post2684387
			# So we always output BT.709 and related characteristics per what we specify in self._default_ini_values
			# Hence we comment out TARGET_COLOR* ini-read stuff so as to only use our DEFAULT settings and take the defaults from self._default_ini_values we poked in earlier
			#self._ini_values[self._ini_section_name]["TARGET_COLORSPACE"] 			= config.get(self._ini_section_name, 'TARGET_COLORSPACE')	# for subtitliing
			#self._ini_values[self._ini_section_name]["TARGET_COLORSPACE_MATRIX_I"]	= int(config.getint(self._ini_section_name, 'TARGET_COLORSPACE_MATRIX_I'))
			#self._ini_values[self._ini_section_name]["TARGET_COLOR_TRANSFER_I"]	= int(config.getint(self._ini_section_name, 'TARGET_COLOR_TRANSFER_I'))
			#self._ini_values[self._ini_section_name]["TARGET_COLOR_PRIMARIES_I"]	= int(config.getint(self._ini_section_name, 'TARGET_COLOR_PRIMARIES_I'))
			#self._ini_values[self._ini_section_name]["TARGET_COLOR_RANGE_I"]		= int(config.get(self._ini_section_name, 'TARGET_COLOR_RANGE_I'))
			self._ini_values[self._ini_section_name]["TARGET_WIDTH"]				= int(config.getint(self._ini_section_name, 'TARGET_WIDTH'))
			self._ini_values[self._ini_section_name]["TARGET_HEIGHT"]				= int(config.getint(self._ini_section_name, 'TARGET_HEIGHT'))
			self._ini_values[self._ini_section_name]["TARGET_FPSNUM"]				= int(config.getint(self._ini_section_name, 'TARGET_FPSNUM'))
			self._ini_values[self._ini_section_name]["TARGET_FPSDEN"]				= int(config.getint(self._ini_section_name, 'TARGET_FPSDEN'))
			self._ini_values[self._ini_section_name]["UPSIZE_KERNEL"]				= config.get(self._ini_section_name, 'UPSIZE_KERNEL')
			self._ini_values[self._ini_section_name]["DOWNSIZE_KERNEL"]				= config.get(self._ini_section_name, 'DOWNSIZE_KERNEL')
			self._ini_values[self._ini_section_name]["BOX"]							= config.getboolean(self._ini_section_name, 'BOX')
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: values read in from the .ini values (defaults applied from the .ini file)')
		else:
			raise ValueError(f'class settings: read_ini_and_calculate_settings: ERROR: .ini file unable to be read or recreated properly')
		# add EXTRA clarifying information to and re-save the updated set of .ini values over the top of the existing .ini file
		with open(self.ini_file_specifying_parameters, 'w') as configfile:
			# add the new set of .ini value to be saved
			update_config =  configparser.ConfigParser(allow_no_value=True)
			##update_config[self._ini_section_name] = self._default_ini_values[self._ini_section_name]
			update_config[self._ini_section_name] = self._ini_values[self._ini_section_name]
			# add example values to make it easier for a human reader of the .ini file
			tmp_name = 'Enum_vs.MatrixCoefficients'
			tmp_dict = { tmp_name : {}}
			for v in vs.MatrixCoefficients:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.TransferCharacteristics'
			tmp_dict = { tmp_name : {}}
			for v in vs.TransferCharacteristics:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.ColorPrimaries'
			tmp_dict = { tmp_name : {}}
			for v in vs.ColorPrimaries:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.ColorRange'
			tmp_dict = { tmp_name : {}}
			for v in vs.ColorRange:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_ZIMG.ColorRange'
			tmp_dict = { tmp_name : {"ZIMG.RANGE_LIMITED" : ZIMG_RANGE_LIMITED, "ZIMG.RANGE_FULL" : ZIMG_RANGE_FULL}}
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.PresetFormat'
			tmp_dict = { tmp_name : {}}
			for v in vs.PresetFormat:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.ColorFamily'
			tmp_dict = { tmp_name : {}}
			for v in vs.ColorFamily:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.ChromaLocation'
			tmp_dict = { tmp_name : {}}
			for v in vs.ChromaLocation:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			tmp_name = 'Enum_vs.FieldBased'
			tmp_dict = { tmp_name : {}}
			for v in vs.FieldBased:
				tmp_dict[tmp_name][str(v)] = v.value
				pass
			update_config[tmp_name] = tmp_dict[tmp_name]
			# update the .ini file
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: Saving updated .ini file: ini_values=\n{objPrettyPrint.pformat(self._ini_values)}')
			update_config.write(configfile)
		print_NORMAL(f'class settings: read_ini_and_calculate_settings: Saved updated .ini "{self.ini_file_specifying_parameters}"')
		# calculate required  values and create a new updated calculated values dict
		self.calc_ini = self._ini_values[self._ini_section_name]
		self.calc_ini["PIC_EXTENSIONS"]					= [".png", ".jpg", ".jpeg", ".gif"]								# always lower case
		self.calc_ini["VID_EXTENSIONS"]					= [".mp4", ".mpeg4", ".mpg", ".mpeg", ".avi", ".mjpeg", ".3gp", ".mov"]	# always lower case
		self.calc_ini["EEK_EXTENSIONS"]					= [".m2ts"]														# always lower case
		self.calc_ini["VID_EEK_EXTENSIONS"]				= self.calc_ini["VID_EXTENSIONS"] + self.calc_ini["EEK_EXTENSIONS"]
		self.calc_ini["EXTENSIONS"]						= self.calc_ini["PIC_EXTENSIONS"] + self.calc_ini["VID_EXTENSIONS"] + self.calc_ini["EEK_EXTENSIONS"]
		self.calc_ini["WORKING_PIXEL_FORMAT"]			= vs.YUV444P8	# int(vs.YUV444P8.value)				# pixel format of the working clips (mainly required by vs_transitions)
		self.calc_ini["TARGET_PIXEL_FORMAT"]			= vs.YUV420P8	# int(vs.YUV420P8.value)				# pixel format of the target video
		self.calc_ini["DG_PIXEL_FORMAT"]				= vs.YUV420P16	# int(vs.YUV420P16.value)				# pixel format of the video for use by DG tools
		self.calc_ini["TARGET_FPS"]						= round(self.calc_ini["TARGET_FPSNUM"] / self.calc_ini["TARGET_FPSDEN"], 3)
		self.calc_ini["DURATION_PIC_FRAMES"]			= int(math.ceil(self.calc_ini["DURATION_PIC_SEC"] * self.calc_ini["TARGET_FPS"]))
		self.calc_ini["DURATION_CROSSFADE_FRAMES"]		= int(math.ceil(self.calc_ini["DURATION_CROSSFADE_SECS"] * self.calc_ini["TARGET_FPS"]))
		self.calc_ini["DURATION_BLANK_CLIP_FRAMES"]		= self.calc_ini["DURATION_CROSSFADE_FRAMES"] + 1	# make equal to the display time for an image; DURATION_CROSSFADE_FRAMES will be less than this
		self.calc_ini["DURATION_MAX_VIDEO_FRAMES"]		= int(math.ceil(self.calc_ini["DURATION_MAX_VIDEO_SEC"] * self.calc_ini["TARGET_FPS"]))
		self.calc_ini["DOT_FFINDEX"]					= ".ffindex".lower()		# for removing temporary *.ffindex files at the end
		self.calc_ini["MODX"]							= int(2)	   # mods for letterboxing calculations, example, for 411 YUV as an extreme
		self.calc_ini["MODY"]							= int(2)	   # mods would have to be MODX=4, MODY=1 as minimum
		self.calc_ini["SUBTITLE_MAX_DEPTH"]				= int(10)
		self.calc_ini["Rotation_anti_clockwise"]		= "anti-clockwise".lower()
		self.calc_ini["Rotation_clockwise"]				= "clockwise".lower()
		self.calc_ini["TARGET_VFR_FPSNUM"]				= self.calc_ini["TARGET_FPSNUM"] * 2
		self.calc_ini["TARGET_VFR_FPSDEN"]				= self.calc_ini["TARGET_FPSDEN"]
		self.calc_ini["TARGET_VFR_FPS"]					= self.calc_ini["TARGET_VFR_FPSNUM"] / self.calc_ini["TARGET_VFR_FPSDEN"]	
		self.calc_ini["precision_tolerance"]			= 0.0002	# used in float comarisons eg fps calculations and comparisons so do not have to use "==" which would almost never work
		# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
		# When calling rezisers etc, ONLY use these values:
		#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
		#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
		# but when obtaining from frame properties and comparing etc, use the vs values from
		# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
		# https://www.vapoursynth.com/doc/api/vapoursynth.h.html#enum-vspresetformat
		if self.calc_ini["TARGET_COLOR_RANGE_I"] == int(vs.ColorRange.RANGE_LIMITED.value):
			self.calc_ini["TARGET_COLOR_RANGE_I_ZIMG"] = ZIMG_RANGE_LIMITED					# use the ZIMG RANGE constants as they are correct and vapoursynth ones are not (opposite to the spec)
		elif self.calc_ini["TARGET_COLOR_RANGE_I"] == int(vs.ColorRange.RANGE_FULL.value):
			self.calc_ini["TARGET_COLOR_RANGE_I_ZIMG"] = ZIMG_RANGE_FULL						# use the ZIMG RANGE constants as they are correct and vapoursynth ones are not (opposite to the spec)
		else:
			raise ValueError(f'class settings: read_ini_and_calculate_settings: ERROR: self.calc_ini["TARGET_COLOR_RANGE_I"]={self.calc_ini["TARGET_COLOR_RANGE_I"]} is an invalid value')
		#++++++++++++++++++++
		# Consistency checks
		min_actual_display_time = 0.5	# seconds
		if (2 * self._ini_values[self._ini_section_name]["DURATION_CROSSFADE_SECS"]) + min_actual_display_time > self._ini_values[self._ini_section_name]["DURATION_PIC_SEC"]:
			raise ValueError(f'class settings: read_ini_and_calculate_settings: ERROR: DURATION_PIC_SEC must be >= (2 * DURATION_CROSSFADE_SECS) + min_actual_display_time \n\ DURATION_CROSSFADE_SECS={self._ini_values[self._ini_section_name]["DURATION_CROSSFADE_SECS"]} DURATION_PIC_SEC={self._ini_values[self._ini_section_name]["DURATION_PIC_SEC"]} min_actual_display_time={min_actual_display_time}')
		if (2 * self._ini_values[self._ini_section_name]["DURATION_CROSSFADE_SECS"]) + min_actual_display_time > self._ini_values[self._ini_section_name]["DURATION_MAX_VIDEO_SEC"]:
			raise ValueError(f'class settings: read_ini_and_calculate_settings: ERROR: DURATION_MAX_VIDEO_SEC must be >= (2 * DURATION_CROSSFADE_SECS) + min_actual_display_time \n\ DURATION_CROSSFADE_SECS={self._ini_values[self._ini_section_name]["DURATION_CROSSFADE_SECS"]} DURATION_MAX_VIDEO_SEC={self._ini_values[self._ini_section_name]["DURATION_MAX_VIDEO_SEC"]} min_actual_display_time={min_actual_display_time}')
		#++++++++++++++++++++
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------')
		for v in vs.PresetFormat:	# eg vs.YUV420P8
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.PresetFormat ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.MatrixCoefficients:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.MatrixCoefficients ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.TransferCharacteristics:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.TransferCharacteristics ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.ColorPrimaries:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.ColorPrimaries ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.ColorRange:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.ColorRange ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.ColorFamily:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.ColorFamily ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.ChromaLocation:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.ChromaLocation ENUM: {str(v)} = {v.value}')
			pass
		for v in vs.FieldBased:
			if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: vs.FieldBased ENUM: {str(v)} = {v.value}')
			pass
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: \nself._default_ini_values=\n{objPrettyPrint.pformat(self._default_ini_values)}')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: \nself._ini_values=\n{objPrettyPrint.pformat(self._ini_values)}')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: \nself.calc_ini=\n{objPrettyPrint.pformat(self.calc_ini)}')
		###if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------')
		#
		# make class variables from the self.calc_ini dictionary	# https://www.geeksforgeeks.org/how-to-change-a-dictionary-into-a-class/
		for key in self.calc_ini:
			if not key.startswith(';'):
				setattr(self, key, self.calc_ini[key])	# this updates existing variables with new values
		# Having made class variables from the self.calc_ini dictionary
		# we can read them as normal class variables like thing.variable_name
		#               or as   dictionary variables like thing.calc_ini["key_name"]
		# *** Remembering they are separate variabkes and overwriting one does NOT overwrite the other and mismatches will then occur ...
		# OR ...
		# self.__dict__.update(self.calc_ini)	# per https://www.sobyte.net/post/2022-04/python-dict-2-member-variables/ # this updates existing variables with new values per https://www.geeksforgeeks.org/python-dictionary-update-method/
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------------')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------------')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: CLASS VARIABLES AND VALUES:\n{objPrettyPrint.pformat(self.class_variables_and_values())}')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------------')
		if A_DEBUG_IS_ON: print_DEBUG(f'class settings: read_ini_and_calculate_settings: ----------------------------------------------------------------------------------------------------------------------------------')
		return

###
def get_mediainfo_specs(path: Union[Path,str]):
# THIS IS A CUSTOM FUNCTION 
# WHICH DOES ADDITIONAL THINGS WITH RETURNED VALUES BESIDE RETRIEVING THEM
	mi_video_params = [
	'Format',                                        # : Format used
	'Format/String',                                 # : Format used + additional features
	'Format_Profile',                                # : Profile of the Format (old XML Profile@Level@Tier format
	'Format_Level',                                  # : Level of the Format (only MIXML)
	'Format_Tier',                                   # : Tier of the Format (only MIXML)
	'HDR_Format',                                    # : Format used
	'HDR_Format_Version',                            # : Version of this format
	'HDR_Format_Profile',                            # : Profile of the Format
	'HDR_Format_Level',                              # : Level of the Format
	'HDR_Format_Settings',                           # : Settings of the Format
	'HDR_Format_Compatibility',                      # : Compatibility with some commercial namings
	'MaxCLL',                                        # : Maximum content light level
	'MaxFALL',                                       # : Maximum frame average light level
	'Duration',                                      # : Play time of the stream in ms
	'Width',                                         # : Width (aperture size if present) in pixel
	'Height',                                        # : Height in pixel
	'PixelAspectRatio',                              # : Pixel Aspect ratio
	'DisplayAspectRatio',                            # : Display Aspect ratio
	'Rotation',                                      # : Rotation as a real number eg 180.00	# CLOCKWISE in mediainfo
	'FrameRate',                                     # : Frames per second
	'FrameRate_Num',                                 # : Frames per second, numerator
	'FrameRate_Den',                                 # : Frames per second, denominator
	'FrameCount',                                    # : Number of frames
	#
	'Recorded_Date',								 # : Time/date/year that the recording began ... this can be None so use Encoded_Date instead. date_recorded = datetime.strptime(mi_dict["Recorded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	'Encoded_Date',									 # : Time/date/year that the encoding of this content was completed. date_encoded = datetime.strptime(mi_dict["Encoded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	#
	'FrameRate_Mode',								 # : Frame rate mode (CFR, VFR)
	'FrameRate_Minimum',							 # : Minimum Frames per second
	'FrameRate_Nominal',							 # : Nominal Frames per second
	'FrameRate_Maximum',							 # : Maximum Frames per second
	'FrameRate_Real',								 # : Real (capture) frames per second
	'ScanType',										 # : ??? progressive interlaced
	'ScanOrder',									 # : ??? TFF BFF
	'ScanOrder_Stored',
	'ScanOrder_StoredDisplayedInverted',
	#
	'Standard',                                      # : NTSC or PAL
	'ColorSpace',                                    # : 
	'ChromaSubsampling',                             # : 
	'BitDepth',                                      # : 16/24/32
	'ScanType',                                      # : 
	'colour_description_present',                    # : Presence of colour description "Yes" or not "Yes" if not None
	'colour_range',                                  # : Colour range for YUV colour space
	'colour_primaries',                              # : Chromaticity coordinates of the source primaries
	'transfer_characteristics',                      # : Opto-electronic transfer characteristic of the source picture
	'matrix_coefficients',                           # : Matrix coefficients used in deriving luma and chroma signals from the green, blue, and red primaries
	]
	###if A_DEBUG_IS_ON: print_DEBUG(f'get_mediainfo_specs: path={path} type(path)={type(path)} mi_video_params=\n{objPrettyPrint.pformat(mi_video_params)}')
	mi_video_dict = {'path' : path } | mediainfo_value_dict(Stream.Video, 0, mi_video_params, path)		# returns a filled-in dict, with keys and possibly None values

	if mi_video_dict["FrameCount"] is None or mi_video_dict["FrameCount"] <= 0:	mi_video_dict["FrameCount"] = 0
	if mi_video_dict["FrameRate"] is None or mi_video_dict["FrameRate"] <=0 :
		mi_video_dict["FrameRate"] = 0
		mi_video_dict["FrameRate_Num"] = 0
		mi_video_dict["FrameRate_Den"] = 0
		mi_video_dict["FrameRate_Minimum"] = 0
		mi_video_dict["FrameRate_Nominal"] = 0
		mi_video_dict["FrameRate_Maximum"] = 0
		mi_video_dict["FrameRate_Real"] = 0
	if mi_video_dict["FrameRate_Mode"] is None:			mi_video_dict["FrameRate_Mode"] = "CFR"
	if mi_video_dict["ScanType"] is None:				mi_video_dict["ScanType"] = "Progressive"
	if mi_video_dict["ScanOrder"] is None:				mi_video_dict["ScanOrder"] = "TFF"		# IF SCAN ORDER IS BFF then yadif/zeedi settngs will be different for deinterlacing
	if mi_video_dict["FrameRate_Nominal"] is None:		mi_video_dict["FrameRate_Nominal"] = mi_video_dict["FrameRate"]
	# sometimes, who knows why, mediainfo returns NO FrameRate_Num/FrameRate_Den although FrameRate is returned
	if mi_video_dict["FrameRate_Num"] is None:		
		mi_video_dict["FrameRate_Num"] = int(mi_video_dict["FrameRate"] * 1000.0)
		mi_video_dict["FrameRate_Den"] = 1000
	## REMINDER: if FPS was zero from mediainfo here, we set it to clip.fps values when in get_clip_from_path
	###if A_DEBUG_IS_ON: print_DEBUG(f'get_mediainfo_specs: mediainfo specs=\n{objPrettyPrint.pformat(mi_video_dict)}')
	return mi_video_dict

###
def mediainfo_value_dict(stream:int, track:int, param:list, path: Union[Path,str]) -> Union[int,float,str]:
	# A wrapper for mediainfo_value_worker
	# Given a LIST of parameter names, return a dict of names/values of properties
	# eg
	#	param:
	#	[ 	'ColorSpace',                                    # : 
	#		'ChromaSubsampling',                             # : 
	#		'BitDepth',                                      # : 16/24/32
	#		'ScanType',                                      # : 
	#		'colour_description_present',                    # : Presence of colour description "Yes" or not "Yes" if not None
	#		'colour_range',                                  # : Colour range for YUV colour space
	#		'colour_primaries',                              # : Chromaticity coordinates of the source primaries
	#		'transfer_characteristics',                      # : Opto-electronic transfer characteristic of the source picture
	#		'matrix_coefficients',                           # : Matrix coefficients used in deriving luma and chroma signals from the green, blue, and red primaries
	#	]
	#	returns something like this (some values can be None):
	#		{'ColorSpace': 'YUV', 'ChromaSubsampling': '4:2:0', 'BitDepth': 8, 'ScanType': 'Progressive', 
	#		'colour_description_present': 'Yes', 'colour_range': 'Limited', 'colour_primaries': 'BT.709',
	#		'transfer_characteristics': 'BT.709', 'matrix_coefficients': 'BT.709'}
	#global MI
	if not stream in range(0,8):
		raise ValueError(f'ERROR: mediainfo_value_dict: stream must be a Stream attribute: General, Video, Audio, Text, Other, Image, Menu, Max')
	if not isinstance(track, int) or track<0:
		raise ValueError(f'ERROR: mediainfo_value_dict: track must be a positive integer')
	if not isinstance(param, list):
		raise ValueError(f'ERROR: mediainfo_value_dict: param must be a list of str parameters for a particular stream, in_Static("Info_Parameters")')	# https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py
	if not isinstance(path, (Path, str)):
		raise ValueError(f'ERROR: mediainfo_value_dict: path must be Path or str class')
	MI = MediaInfo()
	MI.Open(str(path))
	local_dict = {}
	for p in param:
		value = mediainfo_value_worker(MI, stream, track, p, path)
		local_dict[p] = value	# any of str, int, float, or None
		###if A_DEBUG_IS_ON: print_DEBUG(f'"{p}" = \t\t\t\t"{value}"\t\t\ttype={type(value)}\t\t\tisinstance(value,str)={isinstance(value,str)}\t\tisinstance(value,int)={isinstance(value,int)}\t\tisinstance(value,bool)={isinstance(value,bool)}\t\tisinstance(value,float)={isinstance(value,float)}')
	MI.Close()
	del MI	# free the object
	return local_dict

###
def mediainfo_value(stream:int, track:int, param:str, path: Union[Path,str]) -> Union[int,float,str]:
	# A wrapper for mediainfo_value_worker, which gets and returns a single parameter
	# This function permits mediainfo_value_worker to be recycled elsewhere to be called mutiple times per a single MI.open
	#global MI
	if not stream in range(0,8):
		raise ValueError(f'ERROR: mediainfo_value: stream must be a Stream attribute: General, Video, Audio, Text, Other, Image, Menu, Max')
	if not isinstance(track, int) or track<0:
		raise ValueError(f'ERROR: mediainfo_value: track must be a positive integer')
	if not isinstance(param, str):
		raise ValueError(f'ERROR: mediainfo_value: param must be a string for particular stream, in_Static("Info_Parameters")')	# https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py
	if not isinstance(path, (Path, str)):
		raise ValueError(f'ERROR: mediainfo_value: path must be Path or str class')   
	MI = MediaInfo()
	MI.Open(str(path))
	val = mediainfo_value_worker(MI, stream, track, param, path)
	MI.Close()
	del MI	# free the object
	return val

###
def mediainfo_value_worker(MI, stream:int, track:int, param:str, path: Union[Path,str]) -> Union[int,float,str]:
	# gets and returns a single parameter
	#global MI
	if not stream in range(0,8):
		raise ValueError(f'ERROR: mediainfo_value_worker: stream must be a Stream attribute: General, Video, Audio, Text, Other, Image, Menu, Max')
	if not isinstance(track, int) or track<0:
		raise ValueError(f'ERROR: mediainfo_value_worker: track must be a positive integer')
	if not isinstance(param, str):
		raise ValueError(f'ERROR: mediainfo_value_worker: param must be a string for particular stream, in_Static("Info_Parameters")')	# https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py
	if not isinstance(path, (Path, str)):
		raise ValueError(f'ERROR: mediainfo_value_worker: path must be Path or str class')    
	#MI = MediaInfo()
	#MI.Open(str(path)) # CHANGED: open/close in calling routine, allowing this to be called mutiple times
	str_value = MI.Get(stream, track, param)
	info_option =  MI.Get(stream, track, param, InfoKind=Info.Options)
	#MI.Close() 		# CHANGED: open/close in calling routine, allowing this to be called mutiple times
	#del MI	# free the object
	if not str_value:
		del str_value
		del info_option
		return None
	if info_option:
		#returning a proper value type, int, float or str for particular parameter
		type_ = info_option[InfoOption.TypeOfValue] #type_=info_option[3] #_type will be 'I', 'F', 'T', 'D' or 'B'
		try:	# sometimes mediainfo flags an INT or a FLOAT which cannou be ocnverted, so catch those
			val = {'I':int, 'F':float, 'T':str, 'D':str, 'B':str}[type_](str_value)
		except Exception as e:
			if A_DEBUG_IS_ON: print_DEBUG(f'CONVERSION EXCEPTION ON val =["I":int, "F":float, "T":str, "D":str, "B":str][type_](str_value) ... type_="{type_}" param="{param}" str_value="{str_value}" path={path}')
			if A_DEBUG_IS_ON: print_DEBUG(f"Unexpected Error {e=}, {type(e)=} {str(e)=}")
			val = None
			#raise
			pass
	else:
		raise ValueError(f'ERROR: mediainfo_value_worker: wrong parameter: "{param}" for given stream: {stream}')
	del str_value
	del info_option
	return val

###
def boxing(clip, W, H):
	# ensure aspect ratio of an original image/video is preserved by adding black bars where necessary
	source_width, source_height = clip.width, clip.height
	if W/H > source_width/source_height:
		w = source_width*H/source_height
		x = int((W-w)/2)
		x = x - x%objSettings.MODX
		x = max(0, min(x,W))
		clip = resize_clip(clip, W-2*x, H)
		if x:
			return clip.std.AddBorders(left=x, right=x, color=(16,128,128))  #RGB is out then (16,16,16)
		else:
			return clip
	else:
		h = source_height*W/source_width
		y = int((H-h)/2)
		y = y - y%objSettings.MODY
		y = max(0, min(y,H))
		clip = resize_clip(clip, W, H-2*y)
		if y:
			return clip.std.AddBorders(top=y, bottom=y, color=(16,128,128))
		else:
			return clip

###
def resize_clip(clip,w,h):
	# w = calculated interim target width  before addborders
	# h = calculated interim target height before addborders
	W = clip.width					# current clip width before resizing
	H = clip.height					# current clip height before resizing
	resize = None
	xyz = None
	if w>=W or h>=H:	# the clip needs to be increased in size in at least one dimension, or is the same
		resize = getattr(clip.resize, objSettings.UPSIZE_KERNEL)	# get the resize function object ?handle? with the nominated kernel
		xyz = "UPSIZE_KERNEL"
	else:			# the clip needs to be reduced in size in at least one dimension
		resize = getattr(clip.resize, objSettings.DOWNSIZE_KERNEL)	# get the resize function object ?handle? with the nominated kernel
		xyz = "DOWNSIZE_KERNEL"
	c = clip
	if c.format.color_family==vs.RGB:
		#rgb to YUV, perhaps only for png images, figure out what matrix out is needed ... use the HD one REC.709
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties before RGB resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with d.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming frame properties before RGB resize: w={c.width} h={c.height} fps={c.fps} {objPrettyPrint.pformat(c)} {objPrettyPrint.pformat(f.props)}')
			pass
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: TARGET resize properties: width={w}, height={h}, format={objSettings.WORKING_PIXEL_FORMAT}, objSettings.TARGET_COLOR_RANGE_I_ZIMG={objSettings.TARGET_COLOR_RANGE_I_ZIMG}), primaries={objSettings.TARGET_COLOR_PRIMARIES_I}, transfer={objSettings.TARGET_COLOR_TRANSFER_I},  matrix={objSettings.TARGET_COLORSPACE_MATRIX_I}')
		# https://www.vapoursynth.com/doc/functions/video/resize.html https://www.itu.int/rec/T-REC-H.265
		c = resize(width=w, height=h, format=objSettings.WORKING_PIXEL_FORMAT, matrix=objSettings.TARGET_COLORSPACE_MATRIX_I, transfer=objSettings.TARGET_COLOR_TRANSFER_I, primaries=objSettings.TARGET_COLOR_PRIMARIES_I, range=objSettings.TARGET_COLOR_RANGE_I_ZIMG)
		c = core.std.AssumeFPS(clip=c, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties after RGB resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with c.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: outgoing frame properties after RGB resize: w={c.width} h={c.height} fps={c.fps} {c} {objPrettyPrint.pformat(f.props)}')
			pass
	elif c.format.color_family==vs.YUV:
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties before YUV resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with c.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming frame properties before YUV resize: w={c.width} h={c.height} fps={c.fps} {objPrettyPrint.pformat(c)} {objPrettyPrint.pformat(f.props)}')
			pass
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: TARGET resize properties: width={w}, height={h}, format={objSettings.WORKING_PIXEL_FORMAT}, objSettings.TARGET_COLOR_RANGE_I_ZIMG={objSettings.TARGET_COLOR_RANGE_I_ZIMG}), primaries={objSettings.TARGET_COLOR_PRIMARIES_I}, transfer={objSettings.TARGET_COLOR_TRANSFER_I},  matrix={objSettings.TARGET_COLORSPACE_MATRIX_I}')
		# https://www.vapoursynth.com/doc/functions/video/resize.html https://www.itu.int/rec/T-REC-H.265
		c = resize(width=w, height=h, format=objSettings.WORKING_PIXEL_FORMAT, matrix=objSettings.TARGET_COLORSPACE_MATRIX_I, transfer=objSettings.TARGET_COLOR_TRANSFER_I, primaries=objSettings.TARGET_COLOR_PRIMARIES_I, range=objSettings.TARGET_COLOR_RANGE_I_ZIMG)	
		c = core.std.AssumeFPS(clip=c, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
		# AH !!! the above line with matrix_s='709' can cause this error:
		# 		Resize error 3074: no path between colorspaces (2/2/2 => 1/1/1). May need to specify additional colorspace parameters.
		# It usually means the matrix/transfer/primaries are unknown 
		# *** and you have to specify the input colorspace parameters yourself. *** Note: 2 means “unspecified” according to the ITU-T recommendation.
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties after YUV resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with c.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: outgoing frame properties after YUV resize: w={c.width} h={c.height} fps={c.fps} {c} {objPrettyPrint.pformat(f.props)}')
			pass
	else:
		#resize.(vnode clip[, int width, int height, int format, enum matrix, enum transfer, enum primaries, enum range, 
		#			enum chromaloc, enum matrix_in, enum transfer_in, enum primaries_in, enum range_in, enum chromaloc_in, 
		#			float filter_param_a, float filter_param_b, string resample_filter_uv, float filter_param_a_uv, float filter_param_b_uv, 
		#			string dither_type="none", string cpu_type, float src_left, float src_top, float src_width, float src_height, float nominal_luminance])
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties before non-vs.RGB,non-vs.YUV resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with c.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming frame properties before non-vs.RGB,non-vs.YUV resize: w={c.width} h={c.height} fps={c.fps} {objPrettyPrint.pformat(c)} {objPrettyPrint.pformat(f.props)}')
			pass
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: TARGET resize properties: width={w}, height={h}, format={objSettings.WORKING_PIXEL_FORMAT}, objSettings.TARGET_COLOR_RANGE_I_ZIMG={objSettings.TARGET_COLOR_RANGE_I_ZIMG}), primaries={objSettings.TARGET_COLOR_PRIMARIES_I}, transfer={objSettings.TARGET_COLOR_TRANSFER_I},  matrix={objSettings.TARGET_COLORSPACE_MATRIX_I}')
		# https://www.vapoursynth.com/doc/functions/video/resize.html https://www.itu.int/rec/T-REC-H.265
		c = resize(width=w, height=h, format=objSettings.WORKING_PIXEL_FORMAT, matrix=objSettings.TARGET_COLORSPACE_MATRIX_I, transfer=objSettings.TARGET_COLOR_TRANSFER_I, primaries=objSettings.TARGET_COLOR_PRIMARIES_I, range=objSettings.TARGET_COLOR_RANGE_I_ZIMG)	# https://www.vapoursynth.com/doc/functions/video/resize.html# https://www.itu.int/rec/T-REC-H.265
		c = core.std.AssumeFPS(clip=c, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
		# AH !!! the avove line with matrix_s='709' can cause this error:
		# 		Resize error 3074: no path between colorspaces (2/2/2 => 1/1/1). May need to specify additional colorspace parameters.
		# It usually means the matrix/transfer/primaries are unknown 
		# *** and you have to specify the input colorspace parameters yourself. *** Note: 2 means “unspecified” according to the ITU-T recommendation.
		if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: incoming clip properties after non-vs.RGB,non-vs.YUV resize: c.format.name="{c.format.name}" c.format.color_family="{c.format.color_family}" c.format.sample_type="{c.format.sample_type}" c.format.bits_per_sample="{c.format.bits_per_sample}" c.format.bytes_per_sample="{c.format.bytes_per_sample}" c.format.num_planes="{c.format.num_planes}" c.format.subsampling_w="{c.format.subsampling_w}" c.format.subsampling_h="{c.format.subsampling_h}"')
		with c.get_frame(0) as f:
			if A_DEBUG_IS_ON: print_DEBUG(f'resize_clip: outgoing frame properties after non-vs.RGB,non-vs.YUV resize: w={c.width} h={c.height} fps={c.fps} {c} {objPrettyPrint.pformat(f.props)}')
			pass
	del resize
	del xyz
	return c

###
def get_clip_specs(clip=None, path=None, ext=None, mediainfo_specs:dict=None, rotation_degrees=None, rotation_direction=None):
	# find and return specs about the clip ... rotation_degrees, rotation_direction may have already been called beforehand and passed here
	global last_file_opened_with_ffms2
	global last_file_opened_with_imwri
	global last_file_opened_with_LWLibavSource
	global last_file_opened_with_LibavSMASHSource
	if clip is None:
		raise ValueError(f'ERROR: get_clip_specs: "clip" not passed as an argument to get_clip_specs')
	if path is None:
		##raise ValueError(f'ERROR: get_clip_specs: "path" not passed as an argument to get_clip_specs')
		# we can use get_clip_specs on any clip including blank_clip and forego rotation checks if we check for is None then
		pass
	if ext is None:
		raise ValueError(f'ERROR: get_clip_specs: "ext" not passed as an argument to get_clip_specs')
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: clip=\n{clip}')
	## https://www.vapoursynth.com/doc/pythonreference.html
	# Create a local dict of Clip and Frame properties, ready for later validation/resetting if need be of _Matrix/_Transfer/_Primaries/_ColorRange
	clip_specs = {}
	clip_specs["width"] = clip.width
	clip_specs["height"] = clip.height
	clip_specs["num_frames"] = clip.num_frames
	clip_specs["fps"] = clip.fps
	clip_specs["format_name"] = clip.format.name
	clip_specs["color_family"] = clip.format.color_family.value		# .value
	clip_specs["sample_type"] = clip.format.sample_type.value		# .value	If the format is integer or floating point based.
	clip_specs["bits_per_sample"] = clip.format.bits_per_sample
	clip_specs["bytes_per_sample"] = clip.format.bytes_per_sample
	clip_specs["num_planes"] = clip.format.num_planes
	clip_specs["subsampling_w"] = clip.format.subsampling_w
	clip_specs["subsampling_h"] = clip.format.subsampling_h
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: JUST BEFORE "with clip.get_frame(0) as f:" path="{path}" ext="{ext}" clip={clip} clip_specs={objPrettyPrint.pformat(clip_specs)}')
	with clip.get_frame(0) as f:
		clip_specs["_Matrix"] = f.props["_Matrix"] if "_Matrix" in f.props else None
		clip_specs["_Transfer"] = f.props["_Transfer"] if "_Transfer" in f.props else None
		clip_specs["_Primaries"] = f.props["_Primaries"] if "_Primaries" in f.props else None
		clip_specs["_ColorRange"] = f.props["_ColorRange"] if "_ColorRange" in f.props else None
		clip_specs["_ChromaLocation"] = f.props["_ChromaLocation"] if  "_ChromaLocation" in f.props else None
		clip_specs["_DurationDen"] = f.props["_DurationDen"] if "_DurationDen" in f.props else None
		clip_specs["_DurationNum"] = f.props["_DurationNum"] if "_DurationNum" in f.props else None
		clip_specs["_FieldBased"] = f.props["_FieldBased"] if "_FieldBased" in f.props else None	# 0=frame based (progressive), 1=bottom field first, 2=top field first. # https://www.vapoursynth.com/doc/apireference.html?highlight=_FieldBased
		clip_specs["_PictType"] = f.props["_PictType"] if "_PictType" in f.props else None
	# check for picture/video rotation specified perhaps in EXIF but not auto-processed here by the file openers
	if path is None:
		rotation_degrees = 0
		rotation_direction = objSettings.Rotation_clockwise
	else:
		# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		# so ... rotation_direction is returned as "anti-clockise" or "clockwise" using  objSettings.Rotation_anti_clockwise and objSettings.Rotation_clockwise
		if rotation_degrees is None or rotation_direction is None:	# valid degrees and direction may have already been passed
			if ext in objSettings.VID_EEK_EXTENSIONS:
				rotation_degrees, rotation_direction = auto_rotation_value_MediaInfo(path)	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678326
			else: # source is not a video type, i.e. an image
				rotation_degrees, rotation_direction  = auto_rotation_value_PIL(path)	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678326
		else:
			pass	# rotation_degrees, rotation_direction are not None so must have been validly passed
	clip_specs["auto_rotation_degrees"] = rotation_degrees
	clip_specs["auto_rotation_direction"] = rotation_direction
	clip_specs["opened_with_ffms2"] = last_file_opened_with_ffms2
	clip_specs["opened_with_imwri"] = last_file_opened_with_imwri
	clip_specs["opened_with_LWLibavSource"] = last_file_opened_with_LWLibavSource
	clip_specs["opened_with_LibavSMASHSource"] = last_file_opened_with_LibavSMASHSource
	# try to obtain mediainfo specs for the current file
	# which we can use in guessing frame properties when ffms2 fails to yield them
	# Of interest, sample example values of use in the returned dict:
	# 	'ColorSpace': 'YUV'
	#	'ChromaSubsampling': '4:2:0'
	#	'BitDepth': 8
	#	'ScanType': 'Progressive'
	#	'colour_description_present': 'Yes'
	#	'colour_range': 'Limited'
	#	'colour_primaries': 'BT.709'
	#	'transfer_characteristics': 'BT.709'
	#	'matrix_coefficients': 'BT.709'
	#
	# we may already have retrieved mediainfo_specs, it not then do so now and save it in clip_specs
	if path is None or ext not in objSettings.VID_EEK_EXTENSIONS:		# most, if not all, images do not have matrix etc reported by mediainfo
		mediainfo_specs = {}											# rotation is retrieved from mediainfo separately anyway
	else:
		if mediainfo_specs is None:
			mediainfo_specs = get_mediainfo_specs(path)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: retrieved previously-not-retrieved mediainfo specs=\n{objPrettyPrint.pformat(mediainfo_specs)}')
	clip_specs["mediainfo_specs"] = mediainfo_specs
	#
	# OK we have retrieved whatever specs are availabe from the image/clip.
	# There may be gaps in those.
	# Sometimes, ffms2 delvers content with missing metadata tellng us what the source frame properties are.
	# Perhaps mediainfo can find out for us.
	# Experience show usually not though, but it can't hurt to try

	if A_DEBUG_IS_ON: 
		print_DEBUG(f'\n{100*"?"}\n')
		print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, BEFORE GUESSING: path="{path}"\nclip_specs=\n{UTIL.objPrettyPrint.pformat(clip_specs)}\n')
		print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, BEFORE GUESSING: path="{path}"\nmediainfo_specs=\n{UTIL.objPrettyPrint.pformat(mediainfo_specs)}\n')
		print_DEBUG(f'\n{100*"?"}\n')

	# **********
	# Guess the Specs Pass #1 before we resort to total guesses.
	# **********
	# initialise whether we made guesses, and put in draft settings
	clip_specs["guessed_Matrix"] = False
	clip_specs["proposed_Matrix"] = clip_specs["_Matrix"]
	clip_specs["guessed_Primaries"] = False
	clip_specs["proposed_Primaries"] = clip_specs["_Primaries"]
	clip_specs["guessed_Transfer"] = False
	clip_specs["proposed_Transfer"] = clip_specs["_Transfer"]
	clip_specs["guessed_ColorRange"] = False
	clip_specs["proposed_ColorRange"] = clip_specs["_ColorRange"]

	# **********
	# Define translation tables from mediainfo (a bit of these are calculated based on the current clip, so do not create these globally)
	# Define translation tables from mediainfo return values to "vs" constants used to inform other choices
	# **********
	mi_standard_list = { 'Component', 'NTSC', 'PAL', None,}
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: translation_table mi_standard_list=\n{objPrettyPrint.pformat(mi_standard_list)}')
	# values of video stream colour_primaries seen returned by  mediainfo used to convert mediainfo to "vs" ColorPrimaries
	mi_color_primaries_dict = {			'BT.2020' : 				vs.ColorPrimaries.PRIMARIES_BT2020,
										'BT.601 NTSC' :				vs.ColorPrimaries.PRIMARIES_ST170_M,		# ? newer than ColorPrimaries.PRIMARIES_BT470_M 
										'BT.601 PAL' :				vs.ColorPrimaries.PRIMARIES_BT470_BG,
										'BT.709' :					vs.ColorPrimaries.PRIMARIES_BT709,
										#None :						None,
										# not seen, check them anyway
										'BT.470_BG' :				vs.ColorPrimaries.PRIMARIES_BT470_BG,
										'BT.470 BG' :				vs.ColorPrimaries.PRIMARIES_BT470_BG,
										'BT.470 PAL' :				vs.ColorPrimaries.PRIMARIES_BT470_BG,
										'BT.470_PAL' :				vs.ColorPrimaries.PRIMARIES_BT470_BG,
										'BT.470_M' :				vs.ColorPrimaries.PRIMARIES_ST170_M,
										'BT.470 M' :				vs.ColorPrimaries.PRIMARIES_ST170_M,
										'BT.470 NTSC' :				vs.ColorPrimaries.PRIMARIES_ST170_M,
										}
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: translation_table mi_color_primaries_dict=\n{objPrettyPrint.pformat(mi_color_primaries_dict)}')
	# values of video stream transfer_characteristics seen returned by  mediainfo used to convert mediainfo to "vs" TransferCharacteristics
	mi_transfer_characteristics_dict = {'BT.470 System B/G' :		vs.TransferCharacteristics.TRANSFER_BT470_BG,
										'BT.601' :					vs.TransferCharacteristics.TRANSFER_BT601,
										'BT.709' :					vs.TransferCharacteristics.TRANSFER_BT709 ,
										#None :						None,
										# not seen, check them anyway
										'BT.470 System M' :			vs.TransferCharacteristics.TRANSFER_BT470_M,
										'BT.BT2020 10' :			vs.TransferCharacteristics.TRANSFER_BT2020_10,
										'BT.BT2020 12' :			vs.TransferCharacteristics.TRANSFER_BT2020_12,
										'ST.2084' :					vs.TransferCharacteristics.TRANSFER_ST2084,
										}
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: translation_table mi_transfer_characteristics_dict=\n{objPrettyPrint.pformat(mi_transfer_characteristics_dict)}')
	# values of video stream matrix_coefficients seen returned by  mediainfo used to convert mediainfo to "vs" MatrixCoefficients
	mc_bt601 = vs.MatrixCoefficients.MATRIX_BT470_BG
	if 'Standard' in mediainfo_specs and mediainfo_specs['Standard'] is not None:
		if 'NTSC'.lower() in mediainfo_specs['Standard'].lower():
			mc_bt601 = vs.MatrixCoefficients.MATRIX_ST170_M
	if 'colour_primaries' in mediainfo_specs  and mediainfo_specs['colour_primaries'] is not None:
		if 'NTSC'.lower() in  mediainfo_specs['colour_primaries'].lower():	# if the substring string is in the string
			mc_bt601 = vs.MatrixCoefficients.MATRIX_ST170_M
		if  mediainfo_specs['colour_primaries'].lower() in list(map(str.lower,[ 'BT.470 M', 'BT.470 M', 'BT.470_M', 'BT.601 NTSC', 'BT.470 NTSC' ])):
			mc_bt601 = vs.MatrixCoefficients.MATRIX_ST170_M
	mi_matrix_coefficients_dict = {		'BT.470 System B/G' :		vs.MatrixCoefficients.MATRIX_BT470_BG,
										'BT.601' : 					mc_bt601,									# assume PAL unless colour_primaries/Standard say NTSC then vs.MatrixCoefficients.MATRIX_ST170_M 
										'BT.709' :					vs.MatrixCoefficients.MATRIX_BT709,
										'BT.2020 non-constant' :	vs.MatrixCoefficients.MATRIX_BT2020_NCL,
										'BT.2020 constant' :		vs.MatrixCoefficients.MATRIX_BT2020_CL,
										#None :						None,
										# not seen, check them anyway
										}
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: translation_table mi_matrix_coefficients_dict=\n{objPrettyPrint.pformat(mi_matrix_coefficients_dict)}')
	# values of video stream colour_range seen returned by  mediainfo # used to convert mediainfo to "vs" ColorRange
	mi_colour_range_dict = {			'Full' :					vs.ColorRange.RANGE_FULL,
										'Limited' :					vs.ColorRange.RANGE_LIMITED,
										#None :						None,
										}
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: translation_table mi_colour_range_dict={objPrettyPrint.pformat(mi_colour_range_dict)}')
	
	# **********
	# now start making the guessing in pass #1

	if True:
		# 2023.06.17 make a wild guess if nothing known, i.e bt.709 based
		if clip_specs["_Matrix"] is None and clip_specs["_Transfer"] is None and clip_specs["_Primaries"] is None and clip_specs["_ColorRange"] is None :
			# eveything is empty, default to HD BT709 ?
			#
			clip_specs["guessed_Matrix"] = True
			#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT470_BG
			#clip_specs["proposed_Matrix"] = mc_bt601
			clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT709
			#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_NCL
			#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_CL
			clip_specs["_Matrix"] = clip_specs["proposed_Matrix"] 
			#
			clip_specs["guessed_Transfer"] = True
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT470_BG
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT601
			clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT709
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT470_M
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT2020_10
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT2020_12
			#clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_ST2084
			clip_specs["_Transfer"] = clip_specs["proposed_Transfer"] 
			#
			clip_specs["guessed_Primaries"] = True
			#clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT470_BG	# for PAL rec.601	https://kdenlive.org/en/project/color-hell-ffmpeg-transcoding-and-preserving-bt-601/
			#clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_ST170_M		# for NTSC rec.601	https://kdenlive.org/en/project/color-hell-ffmpeg-transcoding-and-preserving-bt-601/
			clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT709
			#clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT2020
			clip_specs["_Primaries"] = clip_specs["proposed_Primaries"] 
			#
			clip_specs["guessed_ColorRange"] = True
			clip_specs["proposed_ColorRange"] = vs.ColorRange.RANGE_FULL
			#clip_specs["proposed_ColorRange"] = vs.ColorRange.RANGE_LIMITED
			clip_specs["_ColorRange"] = clip_specs["proposed_ColorRange"] 
			#
			if A_DEBUG_IS_ON: 
				print_DEBUG(f'\n{100*"?"}\n')
				print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, made a wild guess since nothing known, i.e bt.709 based path="{path}"\nclip_specs=\n{UTIL.objPrettyPrint.pformat(clip_specs)}\n')
				print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, made a wild guess since nothing known, i.e bt.709 based path="{path}"\nmediainfo_specs=\n{UTIL.objPrettyPrint.pformat(mediainfo_specs)}\n')
				print_DEBUG(f'\n{100*"?"}\n')
		else:
				print_DEBUG(f'\n{100*"?"}\n')
				print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, NO wild guess since bits of clip_specs known path="{path}"\nclip_specs=\n{UTIL.objPrettyPrint.pformat(clip_specs)}\n')
				print_DEBUG(f'\nget_clip_specs: IN get_clip_specs, BEFORE RESIZING, NO wild guess since bits of clip_specs known path="{path}"\nmediainfo_specs=\n{UTIL.objPrettyPrint.pformat(mediainfo_specs)}\n')
				print_DEBUG(f'\n{100*"?"}\n')
	
		if  clip_specs["_Matrix"] == vs.MatrixCoefficients.MATRIX_UNSPECIFIED or clip_specs["_Matrix"] is None:	# _Matrix is usually defined and the rest may not be. (ffms2 seems to usually yield MATRIX_BT470_BG ?)
			if 'matrix_coefficients' in mediainfo_specs:
				if mediainfo_specs['matrix_coefficients'] is not None:
					clip_specs["guessed_Matrix"] = True
					clip_specs["proposed_Matrix"] = mi_matrix_coefficients_dict[mediainfo_specs['matrix_coefficients']]	# translate to "vs." if possible
					if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: Guess the Specs Pass #1 translated mediainfo matrix_coefficients "{mediainfo_specs["matrix_coefficients"]}" to "{clip_specs["proposed_Matrix"]}"')

		if  clip_specs["_Transfer"] == vs.TransferCharacteristics.TRANSFER_UNSPECIFIED or clip_specs["_Transfer"] is None:
			if 'transfer_characteristics' in mediainfo_specs:
				if mediainfo_specs['transfer_characteristics'] is not None:
					clip_specs["guessed_Transfer"] = False
					clip_specs["proposed_Transfer"] = mi_transfer_characteristics_dict[mediainfo_specs['transfer_characteristics']]	# translate to "vs." if possible
					if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: Guess the Specs Pass #1 translated mediainfo transfer_characteristics "{mediainfo_specs["transfer_characteristics"]}" to "{clip_specs["proposed_Transfer"]}"')

		if  clip_specs["_Primaries"] == vs.ColorPrimaries.PRIMARIES_UNSPECIFIED or clip_specs["_Primaries"] is None:
			if 'colour_primaries' in mediainfo_specs:
				if mediainfo_specs['colour_primaries'] is not None:
					clip_specs["guessed_Primaries"] = True
					clip_specs["proposed_Primaries"] = mi_color_primaries_dict[mediainfo_specs['colour_primaries']]	# translate to "vs." if possible
					if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: Guess the Specs Pass #1 translated mediainfo colour_primaries "{mediainfo_specs["colour_primaries"]}" to "{clip_specs["proposed_Primaries"]}"')

		if clip_specs["_ColorRange"] is None:
			if 'colour_range' in mediainfo_specs:
				if mediainfo_specs['colour_range'] is not None:
					clip_specs["guessed_ColorRange"] = True
					clip_specs["proposed_ColorRange"] = mi_colour_range_dict[mediainfo_specs['colour_range']]	# translate to "vs." if possible
					if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: Guess the Specs Pass #1 translated mediainfo colour_range "{mediainfo_specs["colour_range"]}" to "{clip_specs["proposed_ColorRange"]}"')












	# **********
	# Guess the Specs Pass #2 once we've had a god with medinfo values ..
	# Sometimes, ffms2 delvers content with missing metadata tellng us what the source frame properties are 
	# So ... now we really guess.
	# **********
	# if not already specified, guess a new _Matrix ... explainer: https://docs.rs/av-data/0.4.1/av_data/pixel/index.html https://docs.rs/av-data/0.4.1/av_data/pixel/enum.MatrixCoefficients.html
	if  clip_specs["_Matrix"] == vs.MatrixCoefficients.MATRIX_UNSPECIFIED or clip_specs["_Matrix"] is None:	# _Matrix is usually defined and the rest may not be. (ffms2 usually yields MATRIX_BT470_BG)
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: MatrixCoefficients.MATRIX_UNSPECIFIED: incoming clip_specs=\n{objPrettyPrint.pformat(clip_specs)}')
		clip_specs["guessed_Matrix"] = True
		if ext in objSettings.PIC_EXTENSIONS:	#PIC # assume opened by ffms2 (ffms2 usually yields MATRIX_BT470_BG for images)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: PIC: MatrixCoefficients.MATRIX_UNSPECIFIED in PIC, choosing a default')
			if last_file_opened_with_ffms2:
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT470_BG
				if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: PIC: MatrixCoefficients.MATRIX_UNSPECIFIED in PIC, opened by ffms2, replacement _Matrix={clip_specs["proposed_Matrix"]}')
			else:
				if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: PIC: MatrixCoefficients.MATRIX_UNSPECIFIED in PIC, opened by non-ffms2')
				#### This is a poor guess, last resort, if there is no other way to deduce matrix.
				# NOTE: ffms2 usually yields MATRIX_BT470_BG for IMAGES regardless of what width/height they may be.
				if  clip_specs["width"] <= 720 and clip_specs["height"] <= 480:				# Likely NTSC SD
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_ST170_M
				elif clip_specs["width"]  <= 720 and clip_specs["height"] <= 576:				# Likely PAL SD
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT470_BG
				elif clip_specs["width"]  <= 1280 and clip_specs["height"] <= 720:				# Likely PAL HD
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT709
				elif clip_specs["width"]  <= 1920 and clip_specs["height"] <= 1088:				# Likely PAL HD
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT709
				elif clip_specs["width"]  <= 3840 and clip_specs["height"] <= 2160:				# Likely UHD
					# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
					# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
					# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
					# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
					# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
					# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
					# because the benefits are considered modest and entail some additional complexity
					#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_CL					#     Constant Luminance
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_NCL				# Non-Constant Luminance
				elif clip_specs["width"]  <= 7680 and clip_specs["height"] <= 4320:				# Likely 8K
					# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
					# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
					# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
					# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
					# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
					# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
					# because the benefits are considered modest and entail some additional complexity
					#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_CL					#     Constant Luminance
					clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_NCL 				# Non-Constant Luminance
				else:
					raise ValueError(f'ERROR: get_clip_specs: PIC: unable to guess default _Matrix in PIC to replace MatrixCoefficients.MATRIX_UNSPECIFIED')
				if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: PIC: MatrixCoefficients.MATRIX_UNSPECIFIED ({vs.MatrixCoefficients.MATRIX_UNSPECIFIED}) in PIC, opened by non-ffms2, replacement _Matrix={clip_specs["proposed_Matrix"]}')
		elif ext in objSettings.VID_EEK_EXTENSIONS:	#VID 
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: VID: MatrixCoefficients.MATRIX_UNSPECIFIED in VID')
			#### This is a poor guess, last resort, if there is no other way to deduce matrix.
			# NOTE: ffms2 usually yields MATRIX_BT470_BG for IMAGES regardless of what width/height they may be.
			if  clip_specs["width"] <= 720 and clip_specs["height"] <= 480:	# Likely NTSC SD
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_ST170_M
			elif clip_specs["width"]  <= 720 and clip_specs["height"] <= 576:				# Likely PAL SD
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT470_BG
			elif clip_specs["width"]  <= 1280 and clip_specs["height"] <= 720:				# Likely PAL HD
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT709						# HD
			elif clip_specs["width"]  <= 1920 and clip_specs["height"] <= 1088:				# Likely PAL HD
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT709						# HD
			elif clip_specs["width"]  <= 3840 and clip_specs["height"] <= 2160:				# Likely UHD
				# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
				# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
				# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
				# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
				# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
				# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
				# because the benefits are considered modest and entail some additional complexity
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_CL					#     Constant Luminance
				#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_NCL				# Non-Constant Luminance
			elif clip_specs["width"]  <= 7680 and clip_specs["height"] <= 4320:				# Likely 8K
				# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
				# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
				# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
				# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
				# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
				# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
				# because the benefits are considered modest and entail some additional complexity
				clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_CL					#     Constant Luminance
				#clip_specs["proposed_Matrix"] = vs.MatrixCoefficients.MATRIX_BT2020_NCL 				# Non-Constant Luminance
			else:
				raise ValueError(f'ERROR: get_clip_specs: VID: unable to guess default _Matrix in PIC to replace MatrixCoefficients.MATRIX_UNSPECIFIED')
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: VID: MatrixCoefficients.MATRIX_UNSPECIFIED ({vs.MatrixCoefficients.MATRIX_UNSPECIFIED}) in VID, replacement _Matrix={clip_specs["proposed_Matrix"]}')
		else:
			raise ValueError(f'ERROR: get_clip_specs: VID: ext "{ext}" not recognised in VID to replace MatrixCoefficients.MATRIX_UNSPECIFIED')
	# **********
	# if not already specified, guess new _Primaries. explainer: https://docs.rs/av-data/0.4.1/av_data/pixel/index.html https://docs.rs/av-data/0.4.1/av_data/pixel/enum.ColorPrimaries.html
	if  clip_specs["_Primaries"] == vs.ColorPrimaries.PRIMARIES_UNSPECIFIED or clip_specs["_Primaries"] is None:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: ColorPrimaries.PRIMARIES_UNSPECIFIED: incoming clip_specs=\n{objPrettyPrint.pformat(clip_specs)}')
		clip_specs["guessed_Primaries"] = True
		if clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_ST170_M:
			clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_ST170_M
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT470_BG:
			clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT470_BG
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT709:
			clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT709
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT2020_CL or clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT2020_NCL:
			clip_specs["proposed_Primaries"] = vs.ColorPrimaries.PRIMARIES_BT2020
		else:
			raise ValueError(f'ERROR: get_clip_specs: unable to guess default _Primaries to replace ColorPrimaries.PRIMARIES_UNSPECIFIED')
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: ColorPrimaries.PRIMARIES_UNSPECIFIED ({vs.ColorPrimaries.PRIMARIES_UNSPECIFIED}), replacement _Primaries={clip_specs["proposed_Primaries"]}')
	# **********
	# if not already specified, guess new _Transfer. explainer: https://docs.rs/av-data/0.4.1/av_data/pixel/index.html https://docs.rs/av-data/0.4.1/av_data/pixel/enum.TransferCharacteristic.html
	if  clip_specs["_Transfer"] == vs.TransferCharacteristics.TRANSFER_UNSPECIFIED or clip_specs["_Transfer"] is None:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: ColorPrimaries.PRIMARIES_UNSPECIFIED: incoming clip_specs=\n{objPrettyPrint.pformat(clip_specs)}')
		clip_specs["guessed_Transfer"] = True
		if clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_ST170_M:
			clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT601
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT470_BG:
			clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT470_BG
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT709:
			clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT709
		elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT2020_CL or clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT2020_NCL:
			if clip_specs["bits_per_sample"] == 10:
				# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
				# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
				# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
				# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
				# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
				# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
				# because the benefits are considered modest and entail some additional complexity
				clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT2020_10
			elif clip_specs["bits_per_sample"] == 12:
				# https://www.benq.com/en-us/knowledge-center/knowledge/bt2020.html
				# HDR is defined by contrast/brightness enhancements which are not explicitly outlined in BT.2020’s package of specifications
				# To address this gap, the ITU in 2016 released its newest recommendations, BT.2100, to include HDR in its specifications, essentially making BT.2100 just BT.2020 plus HDR
				# https://www.itu.int/dms_pub/itu-r/opb/rep/R-REP-BT.2390-1-2016-PDF-E.pdf
				# The constant luminance (CL) method specified in Recommendation ITU-R BT.2020 helps reduce Error propagation from chroma to luma channels 
				# BUT THIS SOLUTION IS NOT BEING WIDELY ADOPTED 
				# because the benefits are considered modest and entail some additional complexity
				clip_specs["proposed_Transfer"] = vs.TransferCharacteristics.TRANSFER_BT2020_12
			else:
				raise ValueError(f'ERROR: get_clip_specs: unable to guess {clip_specs["bits_per_sample"]}-bit default _Transfer to replace TransferCharacteristics.TRANSFER_UNSPECIFIED')
		else:
			raise ValueError(f'ERROR: get_clip_specs: unable to guess default _Transfer to replace TransferCharacteristics.TRANSFER_UNSPECIFIED')
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: TransferCharacteristics.TRANSFER_UNSPECIFIED ({vs.TransferCharacteristics.TRANSFER_UNSPECIFIED}), replacement _Transfer={clip_specs["proposed_Transfer"]}')
	# **********
	# if not already specified, guess new _ColorRange. explainer: https://docs.rs/av-data/0.4.1/av_data/pixel/index.html https://docs.rs/av-data/0.4.1/av_data/pixel/enum.YUVRange.html
	# NOTE THESE IN REGARD TO VS "bug" in RANGE values not agreeing with the spec:
	#	https://github.com/vapoursynth/vapoursynth/issues/940
	#	https://github.com/vapoursynth/vapoursynth/issues/857
	# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
	# When calling rezisers etc, ONLY use these values:
	#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
	#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
	# but when obtaining from frame properties and comparing etc, use the vs values from
	# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
	# BUT BUT BUT here we are working solely with vapoursynth settings, not resizers, so stick with using vapoursynth constants and not zimg ones
	if clip_specs["_ColorRange"] is None:
		clip_specs["guessed_ColorRange"] = True
		clip_specs["proposed_ColorRange"] = vs.ColorRange.RANGE_FULL
	# **********
	# guess at a possible incoming colour source
	if   clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_BT470_BG:
		clip_specs["possible_colour_source"] = "PAL".upper()
	elif clip_specs["proposed_Matrix"] == vs.MatrixCoefficients.MATRIX_ST170_M:
		clip_specs["possible_colour_source"] = "NTSC".upper()
	elif clip_specs["proposed_Transfer"] == vs.TransferCharacteristics.TRANSFER_BT470_BG:
		clip_specs["possible_colour_source"] = "PAL".upper()
	elif clip_specs["proposed_Transfer"] in [vs.TransferCharacteristics.TRANSFER_BT470_M, vs.TransferCharacteristics.TRANSFER_ST240_M]:
		clip_specs["possible_colour_source"] = "NTSC".upper()
	elif clip_specs["proposed_Primaries"] == vs.ColorPrimaries.PRIMARIES_BT470_BG:
		clip_specs["possible_colour_source"] = "PAL".upper()
	elif clip_specs["proposed_Primaries"] in [vs.ColorPrimaries.PRIMARIES_ST170_M, vs.ColorPrimaries.PRIMARIES_BT470_M, vs.ColorPrimaries.PRIMARIES_ST170_M, vs.ColorPrimaries.PRIMARIES_ST240_M]:
		clip_specs["possible_colour_source"] = "PAL".upper()
	# allow for incoming errors in fps, use ranges instead of values
	elif (clip_specs["fps"] >=23.5 and clip_specs["fps"] <= 24.49) or (clip_specs["fps"] >=29 and clip_specs["fps"] <= 31):
		clip_specs["possible_colour_source"] = "NTSC".upper()		# possibly NTSC although 30fps could still be PAL in phone cameras :(
	elif (clip_specs["fps"] >=24.5 and clip_specs["fps"] <= 25.5):
		clip_specs["possible_colour_source"] = "PAL".upper()
	else:	# deault to PAL since, well, I'm in a PAL country
		clip_specs["possible_colour_source"] = "PAL".upper()
	#
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_specs: AFTER GUESSING, clip_specs=\n{objPrettyPrint.pformat(clip_specs)}')
	del mi_standard_list
	del mi_color_primaries_dict
	del mi_transfer_characteristics_dict
	del mi_matrix_coefficients_dict
	del mi_colour_range_dict
	del mediainfo_specs
	return clip_specs

###
def auto_rotation_value_PIL(path):
	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
	# from PIL import Image, ExifTags, UnidentifiedImageError   # pip install Pillow, or equivalent
	# PIL Pillow module loads an image, checks if EXIF data, checks for 'Orientation'
	# The Python Pillow library is a fork of an older library called PIL. 
	# Older PIL stands for Python Imaging Library, and it's the original library that enabled Python to deal with images. 
	# PIL was discontinued in 2011 (that author died) and only supports Python 2.23 ... so use Pillow instead.
	# https://python-pillow.org/
	if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: Entered with path="{path}"')
	rotation_degrees = 0
	try:
		image = Image.open(str(path))
	except UnidentifiedImageError:
		if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: except UnidentifiedImageError immediate return now')
		try:
			image.close()
		except:
			pass
		return rotation_degrees, objSettings.Rotation_anti_clockwise
	except PermissionError:
		if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: except PermissionError Permission denied to load: {path} immediate return now')
		try:
			image.close()
		except:
			pass
		return rotation_degrees, objSettings.Rotation_anti_clockwise
	except Exception as e:
		if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: except Exception {e} {type(e)} {str(e)} - immediate return now')
		try:
			image.close()
		except:
			pass
		return rotation_degrees, objSettings.Rotation_anti_clockwise
	if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: try on Image.open succeeded')
	value = 0
	try:		
		for key in ExifTags.TAGS.keys():
			if ExifTags.TAGS[key] == 'Orientation':
				break
		exif = dict(image.getexif().items())
		if ExifTags.TAGS[key] == 'Orientation':
			value = exif[key]
		else:
			value = 0
	except (AttributeError, KeyError, IndexError):
		if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: except AttributeError during for key in ExifTags.TAGS.keys(), immediate return now')
		try:
			image.close()
		except:
			pass
		return rotation_degrees, objSettings.Rotation_anti_clockwise
	else:
		if value == 0:
			rotation_degrees = 0
			###if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: PIL says auto-Rotating ANTI-CLOCKWISE by 0 degrees {path}')
		elif value == 3:
			rotation_degrees = 180
			###if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: PIL says auto-Rotating ANTI-CLOCKWISE by 180 degrees {path}')
		elif value == 8:
			rotation_degrees = 90
			###if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: PIL says auto-Rotating ANTI-CLOCKWISE by  90 degrees {path}')
		elif value == 6:
			rotation_degrees = 270
			###if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: PIL says auto-Rotating ANTI-CLOCKWISE by 270 degrees {path}')
	try:
		image.close()
	except:
		pass
	if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_PIL: PIL says auto-Rotating ANTI-CLOCKWISE by {rotation_degrees} degrees {path}')
	return rotation_degrees, objSettings.Rotation_anti_clockwise

###
def auto_rotation_value_MediaInfo(path):
	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
	if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_MediaInfo: Entered with path="{path}"')
	rotation_degrees = 0
	param = 'Rotation'
	value = mediainfo_value(Stream.Video, 0, param, path)
	if param == 'Rotation':
		if value is None:
			rotation_degrees = 0
		else:
			rotation_degrees = int(float(value)) # for some reason Rotation value type mediainfo carries as a string,  like: '180.00'
	if A_DEBUG_IS_ON: print_DEBUG(f'auto_rotation_value_MediaInfo: MediaInfo says auto-Rotating CLOCKWISE by {rotation_degrees} degrees {path}')
	return rotation_degrees, objSettings.Rotation_clockwise

###
def deinterlace_clip(clip, ScanOrder):
	# znedi3 
	#	field: 0: Same rate, keep bottom field. 1: Same rate, keep top field.2: Double rate, start with bottom field. 3: Double rate, start with top field.
	# yadifmod
	#	order: Sets the field order  in the source frames. 0 = bff 1 = tff
	#	field: Controls which field to keep when using same rate output. -1 = set equal to order 0 = keep bottom field 1 = keep top field
	#	mode: Controls double rate vs same rate output, and whether or not the spatial interlacing check is performed.
	#			0 = same rate, do spatial check 1 = double rate, do spatial check 2 = same rate, no spatial check 3 = dou
	if A_DEBUG_IS_ON: print_DEBUG(f'deinterlace_clip: Entered with ScanOrder="{ScanOrder}" clip=\n{clip}')
	yadif_mode = 0
	if ScanOrder.upper() == "TFF".upper():
		nnedi3_field = 1	# TFF
		yadif_order = 1		# TFF
		yadif_field = 1		# TFF
	else:
		nnedi3_field = 0	# BFF
		yadif_order = 0		# BFF
		yadif_field = 1		# BFF
	return core.yadifmod.Yadifmod(clip=clip, edeint=core.znedi3.nnedi3(clip=clip,field=nnedi3_field), order=yadif_order, field=yadif_field, mode=yadif_mode) 

###
def get_clip_from_path_with_VFR_fixed(path, ext, mediainfo_specs):	# opens VID_EXTENSIONS only using FFMS2
	# THIS IS THE BRUTE-FORCE method, no mvflow
	#
	# With VFR the  FFMS2 "Source" below "should" already have specified twice the target framerate 
	#	in fpsnum=objSettings.TARGET_VFR_FPSNUM and fpsden=objSettings.TARGET_VFR_FPSDEN
	#	so that FFMS2 converts the clip to CFR by dups and drops
	#	... we make that fps HIGH since some clips are 60fps and for PAL target 25fps in the end
	global last_file_opened_with_ffms2
	global last_file_opened_with_imwri
	global last_file_opened_with_LWLibavSource
	global last_file_opened_with_LibavSMASHSource
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed: Entered with path="{path}" ext="{ext}" mediainfo_specs=\n{objPrettyPrint.pformat(mediainfo_specs)}')
	if not ext in objSettings.VID_EXTENSIONS:
		raise ValueError(f'get_clip_from_path_with_VFR_fixed: expected {path} to have extension in {objSettings.VID_EXTENSIONS} ... aborting')
	try:
		ffcachefile = UTIL.get_random_ffindex_filename(path)
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed: about to ffms2.Source("{str(path)}", cachefile="{ffcachefile}", fpsnum={objSettings.TARGET_VFR_FPSNUM}, fpsden={objSettings.TARGET_VFR_FPSDEN}')
		c = core.ffms2.Source(str(path), cachefile=ffcachefile, fpsnum=objSettings.TARGET_VFR_FPSNUM, fpsden=objSettings.TARGET_VFR_FPSDEN)	# force dups and drops to "convert" to VFR
		last_file_opened_with_ffms2 = True
	except Exception as e:
		print_NORMAL(f'ENCODER: WARNING: error opening file via "ffms2": "{str(path)}" ; ignoring this video clip. The error was:\n{e}\n{type(e)}\n{str(e)}')
		return None
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed: OPENED FILE with ffms2 specifying fpsnum={objSettings.TARGET_VFR_FPSNUM}, fpsden={objSettings.TARGET_VFR_FPSDEN}')
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed:                         clip says fpsnum={c.fps_num}, fpsden={c.fps_den} clip=\n{c}')
	################ IF mediainfo_specs SAYS THIS IS A VFR VIDEO THEN THE OTHER VALUES LIKE FrameRate_Maximum MAY BE RETRIEVED PROPERLY ... IF NOT THEN JUST LET IT CRASH
	################ IMMEDIATELY TRIM VFR CLIP FIRST using  est_num_VFR_frames_to_keep
	################ SO THAT WE ONLY PROCESS A MINIMAL NUMBER OF FRAMES INSTEAD OF A VERY LARGE CLIP
	# We MUST NOT use mediainfo_specs["FrameRate_Maximum"] for trimming, as ffms2 has already FIXED to objSettings.TARGET_VFR_FPSNUM and fpsden=objSettings.TARGET_VFR_FPSDEN
	# BAD: est_num_VFR_frames_to_keep = min((mediainfo_specs["FrameRate_Maximum"] * objSettings.DURATION_MAX_VIDEO_SEC) * 1.1, c.num_frames)	# was mediainfo_specs["FrameCount"]
	est_num_VFR_frames_to_keep = min((c.fps * objSettings.DURATION_MAX_VIDEO_SEC) + 1, c.num_frames)	# was mediainfo_specs["FrameCount"]
	clip = core.std.Trim(clip=c, first=0, last=max((est_num_VFR_frames_to_keep-1),0))
	del c
	# Now turn VFR into CFR by a BRUTE FORCE method
	#	https://forum.doom9.org/showthread.php?p=1921016#post1921016
	#	https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio/page3#post2685569
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed: turning high framerate clip into fpsnum={objSettings.TARGET_FPSNUM}, fpsden={objSettings.TARGET_FPSDEN} ... (separatefields/deinterlace is a part of that blending).')
	clip = core.std.SetFieldBased(clip=clip, value=2)	# AssumeTFF # SetFieldBased sets _FieldBased to value and deletes the _Field frame property. 0 = Frame Based 1 = Bottom Field First 2 = Top Field First 
	clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_VFR_FPSNUM, fpsden=objSettings.TARGET_VFR_FPSDEN)	# should be double the target framerate, i.e. 50fps
	# THIS IS 50p->50i TFF (aka 25i TFF):
	clip = core.std.SeparateFields(clip,tff=True).std.SelectEvery(cycle=4,offsets=[0,3]).std.DoubleWeave(tff=True).std.SelectEvery(cycle=2,offsets=0)	# produces TFF i.e. with (4,0,3); BFF = (4,1,2)
	clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
	clip = deinterlace_clip(clip, 'TFF')
	clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
	#
	# We COULD have tried this to use mv to motion interpolate down to the target fps ...
	#
	# clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_VFR_FPSNUM, fpsden=objSettings.TARGET_VFR_FPSDEN)	# should be double the target framerate, i.e. 50fps
	# clip = make_fps_compatible(clip)
	# clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)	#
	# clip = deinterlace_clip(clip, 'TFF')
	#
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path_with_VFR_fixed: final CFR clip says fpsnum={clip.fps_num}, fpsden={clip.fps_den} clip=\n{clip}')
	return clip		# which is now CFR at our desired framerate, although not necessarily of the required number of frames duration (not trimmed/padded here)


###
def get_clip_from_path(path, ext, mediainfo_specs):		# opens VID_EEK_EXTENSIONS only ... Source filter depends on extension
	# NOT for VFR videos !!!  ONLY for videos not at the required target framerate
	global last_file_opened_with_ffms2
	global last_file_opened_with_imwri
	global last_file_opened_with_LWLibavSource
	global last_file_opened_with_LibavSMASHSource
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path: Entered with path="{path}" ext="{ext}" mediainfo_specs=\n{objPrettyPrint.pformat(mediainfo_specs)}')
	if not ext in objSettings.VID_EXTENSIONS:
		raise ValueError(f'get_clip_from_path: expected {path} to have extension in {objSettings.VID_EEK_EXTENSIONS} ... aborting')
	if ext in objSettings.VID_EXTENSIONS:
		try:
			ffcachefile = UTIL.get_random_ffindex_filename(path)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path: about to ffms2.Source("{str(path)}", cachefile="{ffcachefile}"')
			c = core.ffms2.Source(str(path), cachefile=ffcachefile)
			last_file_opened_with_ffms2 = True
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: opened ffmps2 Video {path.name} clip:\n{c}')
		except Exception as e:
			print_NORMAL(f'ENCODER: WARNING: error opening file via "ffms2": "{str(path)}" ; ignoring this video clip. The error was:\n{e}\n{type(e)}\n{str(e)}')
			return None
	elif  ext in objSettings.EEK_EXTENSIONS:
		try:
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path: Attempting to open path="{path}" ext="{ext}" with "LWLibavSource"')
			c = core.lsmas.LWLibavSource(str(path))
			last_file_opened_with_LWLibavSource = True
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: opened lsmas Video {path.name} clip:\n{c}')
		except Exception as e:
			print_NORMAL(f'ENCODER: WARNING: error opening file via "lsmas": "{path.name}" ; ignoring this video clip. The error was:\n{e}\n{type(e)}\n{str(e)}')
			return None
	else:
		raise ValueError(f'get_clip_from_path: expected {path} to have extension in {objSettings.VID_EEK_EXTENSIONS} ... aborting')
	################ IMMEDIATELY TRIM CLIP FIRST using  est_num_frames_to_keep
	################ SO THAT WE ONLY PROCESS A MINIMAL NUMBER OF FRAMES INSTEAD OF A VERY LARGE CLIP
	# now the clip is open and it is notionally CFR, fix the odd cases where mediainfo returns a zero framerate  OR  ffms2 returns a different fps than mediainfo ... use the clip's fps
	if (mediainfo_specs["FrameRate"] <= 0) or (abs(c.fps - mediainfo_specs["FrameRate"]) > objSettings.precision_tolerance):
		if A_DEBUG_IS_ON: print_DEBUG(f'ENCODER: WARNING: {path} mediainfo framerate {mediainfo_specs["FrameRate"]} fps is not close to clip.fps {c.fps} fps; using clip fps anyway')
		mediainfo_specs["FrameRate_Num"] = c.fps_num
		mediainfo_specs["FrameRate_Den"] = c.fps_den
		mediainfo_specs["FrameRate"] = c.fps
	est_num_frames_to_keep = min((c.fps * objSettings.DURATION_MAX_VIDEO_SEC) * 1.1, c.num_frames)	# was mediainfo_specs["FrameCount"]
	clip = core.std.Trim(clip=c, first=0, last=max((est_num_frames_to_keep-1),0))
	clip = core.std.AssumeFPS(clip=clip, fpsnum=mediainfo_specs["FrameRate_Num"], fpsden=mediainfo_specs["FrameRate_Den"])
	del c
	return clip

###
def get_clip_from_pic(path, ext):
	global last_file_opened_with_ffms2
	global last_file_opened_with_imwri
	global last_file_opened_with_LWLibavSource
	global last_file_opened_with_LibavSMASHSource
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_path: Entered with path="{path}" ext="{ext}"')
	if ext in objSettings.PIC_EXTENSIONS:
		try:
			ffcachefile = UTIL.get_random_ffindex_filename(path)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_pic: about to ffms2.Source("{str(path)}", cachefile="{ffcachefile}"')
			clip = core.ffms2.Source(str(path), cachefile=ffcachefile)
			last_file_opened_with_ffms2 = True
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_pic: opened ffms2 Picture "{path.name}" info:\n{clip}')
			###if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_pic: ffms2 PIC {path.name} info:\n{clip}')
			## NOTE: imwri returns no frame properties ! eg "_Matrix" ! and thus IS NO GOOD AT ALL FOR US
			##clip = core.imwri.Read(str(path)) # ImageMagick Writer-Reader, if installed into vapoursynth directory
			##last_file_opened_with_imwri = True
			####if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_from_pic: imwri Video info:\n{clip}')
		except Exception as e:
			print_NORMAL(f'ENCODER: WARNING: error opening file via "ffms2": "{path.name}" ; ignoring this picture. The error was:\n{e}\n{type(e)}\n{str(e)}')
			return None
	else:
		raise ValueError(f'get_clip_from_pic: expected {path} to have extension in {objSettings.PIC_EXTENSIONS} ... aborting')
	return trim_pad_clip_accurately(clip, ext)

###
def get_mv_data_and_vectors_1(clip,
		it=140, scp=15, fpsnum=25, fpsden=1, preset='slow',
		pel=2, sharp=2, block=True, flow_mask=None, block_mode=None,
		blksize=8, blksizev=8, search=None, truemotion=True, searchparam=2, overlap=4, overlapv=None,
		dct=0, blend=True, badSAD=10000, badrange=24, divide=0, ml=100, Mblur=15):
	#	NOTE: it = thscd1    ;    scp=thscd2/255*100
	#	https://htmlpreview.github.io/?https://github.com/pinterf/mvtools/blob/mvtools-pfmod/Documentation/mvtools2.html
	if A_DEBUG_IS_ON: print_DEBUG(f'get_mv_data_and_vectors_1: Entered with {clip.width}x{clip.height} num_frames={clip.num_frames} fps={clip.fps}')
	if not isinstance(clip, vs.VideoNode):
		raise TypeError(f'make_fps_compatible: input clip is not of type clip!')
	#############
	if preset == 'fast':
		pnum=0
	elif preset == 'medium':
		pnum=1
	elif preset == 'slow':
		pnum=2
	else:
		raise TypeError(f'make_fps_compatible: preset "{preset}" should be one of fast/medium/slow')
	overlapv = overlap
	#############
	if search is None : search = [0,3,3][pnum]
	if block_mode is None : block_mode = [0,0,3][pnum]
	if flow_mask is None : flow_mask = [0,0,2][pnum]
	#############
	analParams = {
		'overlap' : overlap,
		'overlapv':overlapv,
		'search' : search,
		'dct':dct,
		'truemotion' : truemotion,
		'blksize' : blksize,
		'blksizev':blksizev,
		'searchparam':searchparam,
		'badsad':badSAD,
		'badrange':badrange,
		'divide':divide
		}
	############
	#block or flow Params 
	bofp = {
		'thscd1':it,
		'thscd2':int(scp*255/100),
		'blend':blend,
		'num':fpsnum,
		'den':fpsden
		}
	############
	sup = core.mv.Super(clip, pel=pel, sharp=sharp, rfilter=4)
	bvec1 = core.mv.Analyse(sup, isb=True, **analParams)
	fvec1 = core.mv.Analyse(sup, isb=False, **analParams)
	return sup, bvec1, fvec1

def make_fps_compatible(clip,
		it=140, scp=15, fpsnum=25, fpsden=1, preset='slow',
		pel=2, sharp=2, block=True, flow_mask=None, block_mode=None,
		blksize=8, blksizev=8, search=None, truemotion=True, searchparam=2, overlap=4, overlapv=None,
		dct=0, blend=True, badSAD=10000, badrange=24, divide=0, ml=100, Mblur=15):
	# NOT for VFR videos !!!  ONLY for CFR videos not at the required target framerate
	# convert the incoming clip's fps to target fps
	# Has NO svp ... which requires something running in the background ... not nice, not free,  so we do not use that
	# Code from:
	#	function mvfrc in xyx98's xvs.py
	#	https://github.com/xyx98/my-vapoursynth-script/blob/master/xvs.py
	#	https://raw.githubusercontent.com/xyx98/my-vapoursynth-script/4813e7b9d7bedf08d3d584c929c41c12a2aeb431/xvs.py
	# Relies on:
	#	mvtools2 from https://github.com/dubhater/vapoursynth-mvtools	... is in vsrepo https://vsdb.top/plugins/mv
	# Was:
	#	def mvfrc(input,it=140,scp=15,num=25,den=1,preset='fast',
	#		pel=2,block=True,flow_mask=None,block_mode=None,
	#		blksize = 8,blksizev=8,search=None,truemotion=True,searchparam=2,overlap=0,overlapv=None,
	#		dct=0,blend=True,badSAD=10000,badrange=24,divide=0,ml=100,Mblur=15):
	#	NOTE: it = thscd1    ;    scp=thscd2/255*100
	#	https://htmlpreview.github.io/?https://github.com/pinterf/mvtools/blob/mvtools-pfmod/Documentation/mvtools2.html
	#
	if A_DEBUG_IS_ON: print_DEBUG(f'make_fps_compatible: Entered with {clip.width}x{clip.height} num_frames={clip.num_frames} fps={clip.fps} changing from fpsnum={clip.fps_num} fpsden={clip.fps_den} to fpsnum={fpsnum} fpsden={fpsden}')
	if not isinstance(clip, vs.VideoNode):
		raise TypeError(f'make_fps_compatible: input clip is not of type clip!')
	#############
	if preset == 'fast':
		pnum=0
	elif preset == 'medium':
		pnum=1
	elif preset == 'slow':
		pnum=2
	else:
		raise TypeError(f'make_fps_compatible: preset "{preset}" should be one of fast/medium/slow')
	overlapv = overlap
	#############
	if search is None : search = [0,3,3][pnum]
	if block_mode is None : block_mode = [0,0,3][pnum]
	if flow_mask is None : flow_mask = [0,0,2][pnum]
	#############
	sup, bvec1, fvec1 = get_mv_data_and_vectors_1(clip,
							it=it, scp=scp, fpsnum=fpsnum, fpsden=fpsden, preset=preset,
							pel=pel, sharp=sharp, block=block, flow_mask=flow_mask, block_mode=block_mode,
							blksize=blksize, blksizev=blksizev, search=search, truemotion=truemotion,
							searchparam=searchparam, overlap=overlap, overlapv=overlapv,
							dct=dct, blend=blend, badSAD=badSAD, badrange=badrange, divide=divide, ml=ml, Mblur=Mblur)
	#############
	analParams = {
		'overlap' : overlap,
		'overlapv':overlapv,
		'search' : search,
		'dct':dct,
		'truemotion' : truemotion,
		'blksize' : blksize,
		'blksizev':blksizev,
		'searchparam':searchparam,
		'badsad':badSAD,
		'badrange':badrange,
		'divide':divide
		}
	############
	#block or flow Params 
	bofp = {
		'thscd1':it,
		'thscd2':int(scp*255/100),
		'blend':blend,
		'num':fpsnum,
		'den':fpsden
		}
	############
	if clip.fps_num/clip.fps_den > fpsnum/fpsden:	# if reducing fps of  the incoming clip, blur a bit first
		clip = core.mv.FlowBlur(clip, sup, bvec1, fvec1, blur=Mblur)
	if block == True:	# block is the usual way
		c =  core.mv.BlockFPS(clip, sup, bvec1, fvec1, **bofp, mode=block_mode)
	else:
		c = core.mv.FlowFPS(clip, sup, bvec1, fvec1, **bofp, mask=flow_mask)
	del sup
	del bvec1
	del fvec1
	del clip
	return c

###
def trim_pad_clip_accurately(clip, ext):
	# the incoming clip may not be the desired number of frames ... 
	# minimum = same as PIC duration, maximum = max duration of a video clip
	# so trim and/or pad it to exactly the right length
	if A_DEBUG_IS_ON: print_DEBUG(f'trim_pad_clip_accurately: Entered with {clip.width}x{clip.height} ext="{ext}" num_frames={clip.num_frames} fps={clip.fps}')
	if ext in objSettings.VID_EEK_EXTENSIONS:	#if any sort of video, probably an old hand-held camera or phone, sometimes variable fps ...
		# annotate the video with debug stuff
		if IS_DEBUG_SYSTEM_OVERRIDE: clip = core.text.Text(clip, str(path), alignment=3, scale=1)
		if IS_DEBUG_SYSTEM_OVERRIDE: clip = core.text.FrameNum(clip, alignment=5, scale=1)
		if IS_DEBUG_SYSTEM_OVERRIDE: clip = core.text.ClipInfo(clip, alignment=8, scale=1)
		if IS_DEBUG_SYSTEM_OVERRIDE: clip = core.text.FrameProps(clip, alignment=2, scale=1)
		source_fpsnum = clip.fps.numerator		# eg 25	# numerator   is 0 when the clip has a variable framerate.
		source_fpsden = clip.fps.denominator	# eg 1	# denominator is 1 when the clip has a variable framerate.
		source_fps = round(source_fpsnum / source_fpsden,3)
		source_duration_frames = clip.num_frames
		source_duration_secs = round((source_duration_frames / source_fps),3)
		source_width, source_height = clip.width, clip.height
		###if A_DEBUG_IS_ON: print_DEBUG(f'trim_pad_clip_accurately: data= {source_width}x{source_height} source_fpsnum:{source_fpsnum} source_fpsden:{source_fpsden} source_fps:{source_fps} source_duration_frames:{source_duration_frames} source_duration_secs:{source_duration_secs}')
		#clip = clip.std.AssumeFPS(fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
		# if duration greater than out review maximum, clip it
		if source_duration_frames > (objSettings.DURATION_MAX_VIDEO_FRAMES-1):
			# clip is too long, trim it
			clip = core.std.Trim(clip, first=0, last=(objSettings.DURATION_MAX_VIDEO_FRAMES-1))
		if len(clip) < objSettings.DURATION_PIC_FRAMES:
			# clip is too short, pad it out using its final frame
			how_many_frames_to_pad = objSettings.DURATION_PIC_FRAMES - len(clip)
			if how_many_frames_to_pad > 0:
				frame_to_pad_with = clip[-1:]	# final frame of clip
				if A_DEBUG_IS_ON: print_DEBUG(f'frame_to_pad_with len={len(frame_to_pad_with)} width={frame_to_pad_with.width} height={frame_to_pad_with.height} ... clip len={len(clip)} width={clip.width} height={clip.height} \n frame_to_pad_with={frame_to_pad_with} \n clip={clip}')
				clip = clip + (clip[-1:] * how_many_frames_to_pad)	# right pad with the final frame of the newly opened video clip
				if A_DEBUG_IS_ON: print_DEBUG(f'Padded video clip "{path}" of {len(clip)} frames by {how_many_frames_to_pad} frames to be a total of {objSettings.DURATION_PIC_FRAMES} long.')
			else:
				raise ValueError(f'ERROR: trim_pad_clip_accurately: how_many_frames_to_pad<=0 ... BUT padding video clip "{path}" of {len(clip)} frames by {how_many_frames_to_pad} frames to be a total of {objSettings.DURATION_PIC_FRAMES} long.')
	elif ext in objSettings.PIC_EXTENSIONS: # source is not a video type, i.e. it must be an image (picture)
		# ensure duration of a clip of an image is the proper number of frames
		if len(clip) < objSettings.DURATION_PIC_FRAMES:
			clip = clip[0]*objSettings.DURATION_PIC_FRAMES	# reset it by repeating the first frame (base 0)
	else:
		raise ValueError(f'ERROR: trim_pad_clip_accurately: Unrecognised ext="{ext}" ... aborting')
	if A_DEBUG_IS_ON: print_DEBUG(f'trim_pad_clip_accurately: Exiting with {clip.width}x{clip.height} ext="{ext}" clip.num_frames={clip.num_frames}')
	return clip

###
def UnsharpMask(clip, strength=64, radius=3, threshold=8):
	# """Ported by Myrsloik""" https://github.com/dubhater/vapoursynth-limitedsharpen2/blob/master/LimitedSharpen2.py
	if A_DEBUG_IS_ON: print_DEBUG(f'UnsharpMask: Entered with {clip.width}x{clip.height} num_frames={clip.num_frames} fps={clip.fps}')
	maxvalue = (1 << clip.format.bits_per_sample) - 1
	threshold = threshold * maxvalue // 255
	blurclip = clip.std.Convolution(matrix=[1] * (radius * 2 + 1), planes=0, mode='v')
	blurclip = blurclip.std.Convolution(matrix=[1] * (radius * 2 + 1), planes=0, mode='h')
	expressions = ['x y - abs {} > x y - {} * x + x ?'.format(threshold, strength / 128)]
	if clip.format.color_family != vs.GRAY:
		expressions.append("")
	return core.std.Expr(clips=[clip, blurclip], expr=expressions)

###
def denoise_clip(clip,
		it=140, scp=15, fpsnum=25, fpsden=1, preset='slow',
		pel=2, sharp=2, block=True, flow_mask=None, block_mode=None,
		blksize=8, blksizev=8, search=None, truemotion=True, searchparam=2, overlap=4, overlapv=None,
		dct=0, blend=True, badSAD=10000, badrange=24, divide=0, ml=100, Mblur=15):
	#	NOTE: it = thscd1    ;    scp=thscd2/255*100
	#	https://htmlpreview.github.io/?https://github.com/pinterf/mvtools/blob/mvtools-pfmod/Documentation/mvtools2.html
	if A_DEBUG_IS_ON: print_DEBUG(f'denoise_clip: Entered with {clip.width}x{clip.height} num_frames={clip.num_frames} fps={clip.fps}')
	if not isinstance(clip, vs.VideoNode):
		raise TypeError(f'make_fps_compatible: input clip is not of type clip!')
	#############
	if preset == 'fast':
		pnum=0
	elif preset == 'medium':
		pnum=1
	elif preset == 'slow':
		pnum=2
	else:
		raise TypeError(f'make_fps_compatible: preset "{preset}" should be one of fast/medium/slow')
	overlapv = overlap
	#############
	if search is None : search = [0,3,3][pnum]
	if block_mode is None : block_mode = [0,0,3][pnum]
	if flow_mask is None : flow_mask = [0,0,2][pnum]
	#############
	sup, bvec1, fvec1 = get_mv_data_and_vectors_1(clip,
							it=it, scp=scp, fpsnum=fpsnum, fpsden=fpsden, preset=preset,
							pel=pel, sharp=sharp, block=block, flow_mask=flow_mask, block_mode=block_mode,
							blksize=blksize, blksizev=blksizev, search=search, truemotion=truemotion,
							searchparam=searchparam, overlap=overlap, overlapv=overlapv,
							dct=dct, blend=blend, badSAD=badSAD, badrange=badrange, divide=divide, ml=ml, Mblur=Mblur)
	MDegrain1_thSAD = 400	# fixed values, moderate motion-compensation denoising
	MDegrain1_planes = 4
	MDegrain1_thSCD1 = 400
	# pinterf's version is not in vsrepo.  It has a different function name  too.
	#c = core.mv.MDegrain1(clip, sup, bvec1, fvec1, thSAD=MDegrain1_thSAD, plane=MDegrain1_planes, thSCD1=MDegrain1_thSCD1)
	# pinterf:	MDeGrain1 MDeGrain1 ( clip, clip super, clip mvbw, clip mvfw, int  thSAD (400), int  thSADC (thSAD), int  plane (4), float limit (255.0), float limitC (limit), int  thSCD1, int  thSCD2, bool isse, bool planar, bool lsb (false), bool out16 (false) )
	#
	# vsrepo has the version from https://github.com/dubhater/vapoursynth-mvtools so we have to use that
	c = core.mv.Degrain1(clip, sup, bvec1, fvec1, thsad=MDegrain1_thSAD, plane=MDegrain1_planes, thscd1=MDegrain1_thSCD1)
	# mv.Degrain1(clip clip, clip super, clip mvbw, clip mvfw[, int thsad=400, int thsadc=thsad, int plane=4, int limit=255, int limitc=limit, int thscd1=400, int thscd2=130, bint opt=True])
	# mv.Degrain2(clip clip, clip super, clip mvbw, clip mvfw, clip mvbw2, clip mvfw2[, int thsad=400, int thsadc=thsad, int plane=4, int limit=255, int limitc=limit, int thscd1=400, int thscd2=130, bint opt=True])
	# mv.Degrain3(clip clip, clip super, clip mvbw, clip mvfw, clip mvbw2, clip mvfw2, clip mvbw3, clip mvfw3[, int thsad=400, int thsadc=thsad, int plane=4, int limit=255, int limitc=limit, int thscd1=400, int thscd2=130, bint opt=True])
	del sup
	del bvec1
	del fvec1
	del clip
	return c

###
def LSFmod_small(clip, strength=100, Smode=1, Lmode=1, Smethod=3, edgemode=0, soft=True, soothe=True, keep=25):
	# A Self-Limiting Sharpener
	# As sourced and then modded from:
	#		LimitedSharpenFaster MOD : function LSFmod(), as Modded Version by LaTo INV, v1.9 - 05 October 2009
	# as located in "havsfunc" at
	#	https://github.com/HomeOfVapourSynthEvolution/havsfunc/blob/master/havsfunc.py
	#	Holy's ported AviSynth functions for VapourSynth.
	# See http://avisynth.nl/index.php/LSFmod for an explanation of parameters
	#
	# Changes from LimitedSharpenFaster MOD :
	#	Code has been significantly pared down to restricted modes and values outlined below.  A lot of parameters have been removed.
	#		Strength	is restricted to 1..200 inclusive, default 100
	#		Smode		is pared down to 1 : Range sharpening  2 : Nonlinear sharpening (corrected version), default 1
	#		Lmode		is pared down to 1 : Limit to over/undershoot
	#		Smethod		is pared down to 1 : 3x3 kernel  2 : Min/Max  =3 : Min/Max + 3x3 kernel, default 3
	#		edgemode	is pared down to 0 : Sharpening all  1 : Sharpening only edges, default 0
	#		soft		is changed to a Bool, False: 0: no softening  and  True: -2 : new auto calculate, no other soft values now, default True
	#		soothe		is pared down  True : Enable soothe temporal stabilization   False : Disable soothe temporal stabilization, default True
	#		keep		is changed to default of 25 percent
	#		kernel		is now fixed at 11 only
	#
	### strength [int]
	### --------------
	### Strength of the sharpening
	###    = 1 to 200 inclusive, default 100
	### ----------------------
	### Smode [int: 1,2,3]
	### Sharpen mode:
	###    =1 : Range sharpening
	###    =2 : Nonlinear sharpening (corrected version)
	### ----------------------
	### Lmode [int: ...,0,1,2,3,4]
	### Limit mode:
	###    =1 : Limit to over/undershoot
	### ----------------------
	### Smethod [int: 1,2,3]
	### Sharpen method: (only used in Smode=1,2)
	###    =1 : 3x3 kernel
	###    =2 : Min/Max
	###    =3 : Min/Max + 3x3 kernel
	### ----------------------
	### edgemode [int: -1,0,1,2]
	###    = 0 : Sharpening all
	###    = 1 : Sharpening only edges
	### ----------------------
	### soft [bool]
	### Soften the sharpening effect:
	### False: 0 : no softening
	### True: -2 : new auto calculate
	### ----------------------
	### soothe [bool]
	###    =True  : Enable soothe temporal stabilization
	###    =False : Disable soothe temporal stabilization
	### ----------------------
	### keep [int: 0...100]
	### Minimum percent of the original sharpening to keep (only with soothe=True)
	### ----------------------
	### NOW CHANGED TO BE NOT PARAMETERS:
	### -------------------
	### ss_x ; ss_y [float]
	### Supersampling factor (reduce aliasing on edges)
	### is fixed at 1.0
	### +----------------------+
	### | NONLINEAR SHARPENING |
	### +----------------------+
	### Szrp [int]
	### Zero Point:
	###    - differences below Szrp are amplified (overdrive sharpening)
	###    - differences above Szrp are reduced   (reduced sharpening)
	### -------------------
	### Spwr [int]
	### Power: exponent for sharpener
	### -------------------
	### SdmpLo [int]
	### Damp Low: reduce sharpening for small changes [0:disable]
	### -------------------
	### SdmpHi [int]
	### Damp High: reduce sharpening for big changes [0:disable]
	### -------------------
	#
	if A_DEBUG_IS_ON: print_DEBUG(f'LSFmod_small: {clip.width}x{clip.height} clip=\n{clip}')
	# constants
	kernel = 11 			# we only have code for 11 below
	ss_x = 1.0				# FIXED TO 1.0 no supersampling
	ss_y = 1.0				# FIXED TO 1.0 no supersampling
	Szrp = 16
	Spwr = 4
	SdmpLo = 4
	SdmpHi = 48
	ox = clip.width		# original width
	oy = clip.height	# original height
	dest_x = ox
	dest_y = oy	
	str = strength / 100
	overshoot = strength // 100
	overshoot2 = overshoot * 2
	undershoot2 = overshoot2
	# variables to be deleted later
	RemoveGrain = None
	tmp = None
	dark_limit = None
	bright_limit = None
	pre = None
	method = None
	tmpScaled = None
	methodScaled = None
	expr = None
	normsharp = None
	normal = None
	edge = None
	limit1 = None
	limit2 = None
	soft_value = None
	sharpdiff = None
	diff = None
	PP1 = None
	PP2 = None
	#
	if strength not in range(1,201):	ValueError(f'LSFmod_small: strength is not in range (1-200)')
	if Smode not in [1, 2]:				ValueError(f'LSFmod_small: Smode is not in range (1-2)')
	if Lmode not in [1]:				ValueError(f'LSFmod_small: Lmode is not in range (1 only)') 
	if Smethod not in [1, 2, 3]:		ValueError(f'LSFmod_small: Smethod is not in range (1-3)')
	if edgemode not in [0, 1]:			ValueError(f'LSFmod_small: edgemode is not in range (0-1)')
	if preblur not in [True, False]:	ValueError(f'LSFmod_small: preblur is not in range (True,False)')
	if secure not in [True, False]:		ValueError(f'LSFmod_small: secure is not in range (True,False)')
	if edgemaskHQ not in [True, False]:	ValueError(f'LSFmod_small: edgemaskHQ is not in range (True,False)')
	if soft not in [True, False]:		ValueError(f'LSFmod_small: soft is not in range (True,False)')
	if soothe not in [True, False]:		ValueError(f'LSFmod_small: soothe is not in range (True,False)')
	if keep not in range(0,101):		ValueError(f'LSFmod_small: keep is not in range (1-100)')
	#
	isGray = (clip.format.color_family == vs.GRAY)
	isInteger = (clip.format.sample_type == vs.INTEGER)
	if isInteger:
		neutral = 1 << (clip.format.bits_per_sample - 1)
		peak = (1 << clip.format.bits_per_sample) - 1
		factor = 1 << (clip.format.bits_per_sample - 8)
	else:
		neutral = 0.0
		peak = 1.0
		factor = 255.0
	# kernel=11 is the following
	RemoveGrain = partial(core.std.Convolution, matrix=[1, 2, 1, 2, 4, 2, 1, 2, 1])
	#
	if isGray:
		tmp = clip
	else:	# if not isGray:	# if not Gray colour family, get the right plane, deal with it, and put it back at the end with ShufflePlanes
		tmp = core.std.ShufflePlanes(clip, 0, vs.GRAY)	# get the y plane (luma)
	#	
	if preblur:
		# preblur the clip preblur=3 with DTFTEST
		expr = 'x {i} < {peak} x {j} > 0 {peak} x {i} - {peak} {j} {i} - / * - ? ?'.format(i=scale(16, peak), j=scale(75, peak), peak=peak)
		pre = core.std.MaskedMerge(tmp.dfttest.DFTTest(tbsize=1, slocation=[0.0,4.0, 0.2,9.0, 1.0,15.0]), tmp, tmp.std.Expr(expr=[expr]))
	else:
		pre = tmp
	#
	dark_limit = pre.std.Minimum()
	bright_limit = pre.std.Maximum()
	#
	if Smethod == 1:	# =1 : 3x3 kernel
		method = RemoveGrain(pre)
	elif Smethod == 2:	# =2 : Min/Max
		method = core.std.Merge(dark_limit, bright_limit)
	elif Smethod == 3:	# =3 : Min/Max + 3x3 kernel
		method = RemoveGrain(core.std.Merge(dark_limit, bright_limit))
	#
	if secure:
		method = core.std.Expr([method, pre], expr=['x y < x {i} + x y > x {i} - x ? ?'.format(i=scale(1, peak))])
	#
	if preblur:
		method = core.std.MakeDiff(tmp, core.std.MakeDiff(pre, method))
	#
	#### BEGIN
	if Smode == 1:
		normsharp = core.std.Expr([tmp, method], expr=[f'x x y - {Str} * +'])
	else:	# Smode == 2:
		tmpScaled = tmp.std.Expr(expr=[f'x {1 / factor if isInteger else factor} *'], format=tmp.format.replace(sample_type=vs.FLOAT, bits_per_sample=32))
		methodScaled = method.std.Expr(expr=[f'x {1 / factor if isInteger else factor} *'], format=method.format.replace(sample_type=vs.FLOAT, bits_per_sample=32))
		expr = f'x y = x x x y - abs {Szrp} / {1 / Spwr} pow {Szrp} * {Str} * x y - dup abs / * x y - dup * {Szrp * Szrp} {SdmpLo} + * x y - dup * {SdmpLo} + {Szrp * Szrp} * / * 1 {SdmpHi} 0 = 0 {(Szrp / SdmpHi) ** 4} ? + 1 {SdmpHi} 0 = 0 x y - abs {SdmpHi} / 4 pow ? + / * + ? {factor if isInteger else 1 / factor} *'
		normsharp = core.std.Expr([tmpScaled, methodScaled], expr=[expr], format=tmp.format)
	#
	### LIMIT
	normal = mt_clamp(normsharp, bright_limit, dark_limit, scale(overshoot, peak), scale(undershoot, peak))
	limit1 = normal		# for Lmode == 1
	#
	### EDGES
	if edgemaskHQ:
		edge = tmp.std.Sobel(scale=2)
	else:
		edge = core.std.Expr([tmp.std.Maximum(), tmp.std.Minimum()], expr=['x y -'])
	edge = edge.std.Expr(expr=[f'x {1 / factor if isInteger else factor} * {128 if edgemaskHQ else 32} / 0.86 pow 255 * {factor if isInteger else 1 / factor} *'])

	if edgemode == 0:		# = 0 : Sharpening all
		limit2 = limit1
	else:	 				# edgemode == 1 : Sharpening only edges
		limit2 = core.std.MaskedMerge(tmp, limit1, edge.std.Inflate().std.Inflate().std.Convolution(matrix=[1, 2, 1, 2, 4, 2, 1, 2, 1]))
	#
	### SOFT ... we ONLY have code for none or "new auto calculate"
	if soft:	# new auto calculate
		soft_value = int((1 + 2 / (ss_x + ss_y)) * math.sqrt(strength))
	else:
		soft_value = 0
	soft_value = min(soft, 100)
	if soft:	# new auto calculate
		sharpdiff = core.std.MakeDiff(tmp, limit2)
		sharpdiff = core.std.Expr([sharpdiff, sharpdiff.std.Convolution(matrix=[1, 1, 1, 1, 0, 1, 1, 1, 1])], expr=[f'x {neutral} - abs y {neutral} - abs > y {soft_value} * x {100 - soft_value} * + 100 / x ?'])
		PP1 = core.std.MakeDiff(tmp, sharpdiff)
	else:		# no softening
		PP1 = limit2
	#
	### SOOTHE
	if soothe:
		diff = core.std.MakeDiff(tmp, PP1)
		diff = core.std.Expr([diff, AverageFrames(diff, weights=[1] * 3, scenechange=32 / 255)],
							expr=[f'x {neutral} - y {neutral} - * 0 < x {neutral} - 100 / {keep} * {neutral} + x {neutral} - abs y {neutral} - abs > x {keep} * y {100 - keep} * + 100 / x ? ?'])
		PP2 = core.std.MakeDiff(tmp, diff)
	else:
		PP2 = PP1
	#
	### OUTPUT
	if isGray:
		out = PP2
	else:
		out = core.std.ShufflePlanes([PP2, clip], planes=[0, 1, 2], colorfamily=clip.format.color_family)
	#
	### CLEANUP
	del RemoveGrain
	del tmp
	del dark_limit
	del bright_limit
	del pre
	del method
	del tmpScaled
	del methodScaled
	del expr
	del normsharp
	del normal
	del edge
	del limit1
	del limit2
	del soft_value
	del sharpdiff
	del diff
	del PP1
	del PP2
	del clip
	#
	### return the sharpened clip
	return out

###
def get_clip_2(path):
	# open a clip and transform it into someting usable
	global last_file_opened_with_ffms2
	global last_file_opened_with_imwri
	global last_file_opened_with_LWLibavSource
	global last_file_opened_with_LibavSMASHSource
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: Entered with path="{path}"')
	if path is None:
		raise ValueError(f'ERROR: get_clip_2: "path" not passed as an argument to get_clip_2')
		pass
	ext = path.suffix.lower()
	#ext = os.path.splitext(path)[1].lower()
	#++++++++++++++++++++
	last_file_opened_with_ffms2 = False
	last_file_opened_with_imwri = False
	last_file_opened_with_LWLibavSource = False
	last_file_opened_with_LibavSMASHSource = False
	mediainfo_specs = None
	video_is_VFR = False
	video_is_INTERLACED = False
	video_is_FPS_COMPATIBLE = False
	rotation_degrees = 0
	rotation_direction = objSettings.Rotation_clockwise			# mediainfo returns is clockwise rotations
	if ext in objSettings.VID_EEK_EXTENSIONS:
		mediainfo_specs = get_mediainfo_specs(path)		# remember: if FPS was zero from mediainfo, set it to clip.fps values when in get_clip_from_path
		if mediainfo_specs["ScanType"].lower() != "Progressive".lower():	video_is_INTERLACED = True
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: retrieved mediainfo specs=\n{objPrettyPrint.pformat(mediainfo_specs)}')
		# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		# so ... rotation_direction is returned as "anti-clockise" or "clockwise" using  objSettings.Rotation_anti_clockwise and objSettings.Rotation_clockwise
		rotation_degrees, rotation_direction = auto_rotation_value_MediaInfo(path)	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678326
		# Check for a VFR video
		# See
		#	https://forum.doom9.org/showthread.php?p=1921016#post1921016
		#	https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio/page3#post2685569
		if mediainfo_specs["FrameRate_Mode"].lower() == "VFR".lower():
			video_is_VFR = True
			video_is_FPS_COMPATIBLE = False		# making into CFR makes it compatible but it is not compatible originally
		#+++
		if video_is_VFR:															# VFR is never interlaced nor compatible, but made to be compatible
			clip = get_clip_from_path_with_VFR_fixed(path, ext, mediainfo_specs)					# is always type objSettings.VID_EXTENSIONS
			if clip is None:	return None
		else:
			clip = get_clip_from_path(path, ext, mediainfo_specs)									# open depends on ext, the rest is the same
			if clip is None:	return None
			#source_fpsnum = clip.fps.numerator		# eg 25	# numerator   is 0 when the clip has a variable framerate.
			#source_fpsden = clip.fps.denominator	# eg 1	# denominator is 1 when the clip has a variable framerate.
			#source_fps = round(source_fpsnum / source_fpsden,3)
			source_fps = clip.fps	# was but should not be = round(mediainfo_specs["FrameRate_Num"] / mediainfo_specs["FrameRate_Den"],3)
			if abs(source_fps - objSettings.TARGET_FPS) < objSettings.precision_tolerance: 
				video_is_FPS_COMPATIBLE = True
				mediainfo_specs["FrameRate_Num"] = objSettings.TARGET_FPSNUM		# use these to set the clip if video_is_FPS_COMPATIBLE WITH ASSUMEfps
				mediainfo_specs["FrameRate_Den"] = objSettings.TARGET_FPSDEN		# use these to set the clip if video_is_FPS_COMPATIBLE WITH ASSUMEfps
				mediainfo_specs["FrameRate"]     = objSettings.TARGET_FPS			# use these to set the clip if video_is_FPS_COMPATIBLE WITH ASSUMEfps
			else:
				video_is_FPS_COMPATIBLE = False
			if video_is_INTERLACED:				clip = deinterlace_clip(clip, mediainfo_specs["ScanOrder"])		# always deinterlace when at original framerate
			if not video_is_FPS_COMPATIBLE:		clip = make_fps_compatible(clip)								# change the source FPS to the target FPS
		clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
	elif ext in objSettings.PIC_EXTENSIONS:
		# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		# so ... rotation_direction is returned as "anti-clockise" or "clockwise" using  objSettings.Rotation_anti_clockwise and objSettings.Rotation_clockwise
		rotation_degrees, rotation_direction  = auto_rotation_value_PIL(path)	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678326
		#+++
		clip = get_clip_from_pic(path, ext)
		if clip is None:	return None
		clip = core.std.AssumeFPS(clip=clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
		#+++
	else:
		raise ValueError(f'get_clip_2: "{path}" - UNRECOGNISED file extension "{ext}", aborting ...')

	#+++ NOTE THE TRIM HERE AT THE END OF PIC/VIDEO GETTING/FIXING **********
	clip = trim_pad_clip_accurately(clip, ext)
	#+++ NOTE THE TRIM HERE AT THE END OF PIC/VIDEO GETTING/FIXING **********
	
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#
	# CLIP IS NOT YET RESIZED/BOXIFIED
	#
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	
	#so if denoising small sized videos was requested,
	# go ahead using fixed values for moderate motion-compensation denoising with MDegrain1
	if ext in objSettings.VID_EEK_EXTENSIONS:
		if objSettings.DENOISE_SMALL_SIZE_VIDEOS and (clip.width < objSettings.TARGET_WIDTH) and (clip.width < objSettings.TARGET_HEIGHT):
			if IS_DEBUG_SYSTEM_OVERRIDE:
				# for debug, show BOTH before and after denoised clips
				clip = clip + denoise_clip(clip)	# using default values both in the parameters and inside the function
			else:
				clip = denoise_clip(clip)	# using default values both in the parameters and inside the function

	#++++++++++++++++++++
	# Apply an auto-rotate if specified in the source file
	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
	# https://www.vapoursynth.com/doc/functions/video/transpose.html
	# https://www.vapoursynth.com/doc/functions/video/flipvertical_fliphorizontal.html
	if rotation_degrees is None or rotation_degrees == 0:
		###if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: zero auto-rotation of clip {path}')
		pass
	elif rotation_degrees == 90 or rotation_degrees == -270:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: auto-Rotating {rotation_direction} by {rotation_degrees} degrees {path}')
		if rotation_direction == objSettings.Rotation_anti_clockwise:
			clip = clip.std.Transpose().std.FlipVertical()		# ANTICLOCKWISE ROTATION 90 DEGREES
		elif rotation_direction == objSettings.Rotation_clockwise:
			clip = clip.std.Transpose().std.FlipHorizontal()	# CLOCKWISE ROTATION 90 DEGREES
		else:
			raise ValueError(f'ERROR: get_clip_2: auto_rotation_degrees "{rotation_degrees}" unrecognised direction={rotation_direction} unable to be processed for "{path}" : only 0/90/180/270 are valid')
	elif rotation_degrees == 180:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: auto-Rotating {rotation_direction} by {rotation_degrees} degrees {path}')
		if rotation_direction == objSettings.Rotation_anti_clockwise:
			clip = clip.std.Turn180()
		elif rotation_direction == objSettings.Rotation_clockwise:
			clip = clip.std.Turn180()
		else:
			raise ValueError(f'ERROR: get_clip_2: auto_rotation_degrees "{rotation_degrees}" unrecognised direction={rotation_direction} unable to be processed for "{path}" : only 0/90/180/270 are valid')
	elif rotation_degrees == 270 or rotation_degrees == -90:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip_2: auto-Rotating {rotation_direction} by {rotation_degrees} degrees {path}')
		if rotation_direction == objSettings.Rotation_anti_clockwise:
			clip = clip.std.Transpose().std.FlipHorizontal()	# ANTICLOCKWISE ROTATION 270 degrees
		elif rotation_direction == objSettings.Rotation_clockwise:
			clip = clip.std.Transpose().std.FlipVertical()		# CLOCKWISE ROTATION 270 degrees
		else:
			raise ValueError(f'ERROR: get_clip_2: auto_rotation_degrees "{rotation_degrees}" unrecognised direction={rotation_direction} unable to be processed for "{path}" : only 0/90/180/270 are valid')
	else:
		raise ValueError(f'ERROR: get_clip_2: auto_rotation_degrees "{rotation_degrees}" direction={rotation_direction} unable to be processed for "{path}" : only 0/90/180/270 are valid')
	#++++++++++++++++++++

	# BY NOW we have clip of a video or a pic, which is at the correct framerate and trimmed/padded to the required length
	# IT HAS NOT YET BEEN RESIZED, so we can use it to guess colour characteristics

	#++++++++++++++++++++
	# Double-check and return None if the clip is empty so it can be ignored
	if clip is None:
		clip_specs = None
		return None

	#++++++++++++++++++++
	# retieve the clip specs ... if mediainfo has already been done (it was in VID_EXTENSIONS) then re-use it that rather than re-read the file
	clip_specs = get_clip_specs(clip, path, ext=ext, mediainfo_specs=mediainfo_specs, rotation_degrees=rotation_degrees, rotation_direction=rotation_direction)	# rotation_degrees, rotation_direction have already been retrieved, pass them along to prevent a double-read
	
	if A_DEBUG_IS_ON: 
		print_DEBUG(f'\n{100*"?"}\n')
		print_DEBUG(f'\nget_clip: AFTER clip_specs, BEFORE RESIZING, AFTER GUESSING: path="{path}"\nclip_specs=\n{UTIL.objPrettyPrint.pformat(clip_specs)}\n')
		print_DEBUG(f'\nget_clip: AFTER clip_specs, BEFORE RESIZING, AFTER GUESSING: path="{path}"\nmediainfo_specs=\n{UTIL.objPrettyPrint.pformat(mediainfo_specs)}\n')
		print_DEBUG(f'\n{100*"?"}\n')
	
	#++++++++++++++++++++
	# SET missing frame properties with guessed values
	if clip_specs["guessed_Matrix"]:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: SetFrameProps _Matrix from existing "{clip_specs["_Matrix"]}" to guessed "{clip_specs["proposed_Matrix"]}"')
		clip = core.std.SetFrameProps(clip, _Matrix=clip_specs["proposed_Matrix"])
	if clip_specs["guessed_Primaries"]:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: SetFrameProps _Primaries from existing "{clip_specs["_Primaries"]}" to guessed "{clip_specs["proposed_Primaries"]}"')
		clip = core.std.SetFrameProps(clip, _Primaries=clip_specs["proposed_Primaries"])
	if clip_specs["guessed_Transfer"]:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: SetFrameProps _Transfer from existing "{clip_specs["_Transfer"]}" to guessed "{clip_specs["proposed_Transfer"]}"')
		clip = core.std.SetFrameProps(clip, _Transfer=clip_specs["proposed_Transfer"])
	# NOTE THESE IN REGARD TO VS "bug" in RANGE values not agreeing with the spec:
	#	https://github.com/vapoursynth/vapoursynth/issues/940
	#	https://github.com/vapoursynth/vapoursynth/issues/857
	# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
	# When calling rezisers etc, ONLY use these values:
	#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
	#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
	# but when obtaining from frame properties and comparing etc, use the vs values from
	# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
	# BUT BUT BUT here we are working solely with vapoursynth settings, not resizers, so stick with using vapoursynth constants and not zimg ones
	if clip_specs["guessed_ColorRange"]:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: SetFrameProps _ColorRange from existing "{clip_specs["_ColorRange"]}" to guessed "{clip_specs["proposed_ColorRange"]}"')
		clip = core.std.SetFrameProps(clip, _ColorRange=clip_specs["proposed_ColorRange"])
	#
	# either add borders to maintain aspect ratio (boxing), or just stretch to fit (yuk)
	if objSettings.BOX:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: boxing the clip, also doing format conversion and resizing')
		clip = boxing(clip, objSettings.TARGET_WIDTH, objSettings.TARGET_HEIGHT)									# new clip format from resize ... replace into clip_specs
	else:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: NOT boxing the clip, also doing format conversion and resizing')
		clip = resize_clip(clip, objSettings.TARGET_WIDTH, objSettings.TARGET_HEIGHT)	# new clip format is consistent with boxing as it uses the same resizer

	#****************************************************************************************************************************************
	# both BOX/non-BOX resizes above convert "format" to objSettings.WORKING_PIXEL_FORMAT (i.e. YUV444) and change to target color spaces  etc etc
	# at this point, clip_specs is stale
	#****************************************************************************************************************************************

	#++++++++++++++++++++
	# Add a subtitle being the trailing x parts of the path
	if objSettings.SUBTITLE_DEPTH > 0:	# Add a subtitle being up to the trailing objSettings.SUBTITLE_MAX_DEPTH parts of the path
		pwp = PureWindowsPath(path)
		num_parts = len(pwp.parts)
		text_subpath_for_subtitles = ''
		max_depth_this_time = min(num_parts-1, objSettings.SUBTITLE_MAX_DEPTH, objSettings.SUBTITLE_DEPTH) # maybe (num_parts-1) should be ) ?
		if max_depth_this_time > 0:
			for i in range((num_parts - max_depth_this_time), (num_parts)):
				text_subpath_for_subtitles = text_subpath_for_subtitles + "/" + pwp.parts[i]
				if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: Subtitling loop: num_parts={num_parts} i={i} pwp.parts[{i}]= {pwp.parts[i]} text_subpath_for_subtitles="{text_subpath_for_subtitles}"')
			subtitle_style = f'sans-serif,{str(objSettings.SUBTITLE_FONTSIZE).strip()},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0.9,0.5,3,2,2,2,1'
			clip = core.assrender.Subtitle(clip, text_subpath_for_subtitles, style=subtitle_style, scale=objSettings.SUBTITLE_FONTSCALE, colorspace=objSettings.TARGET_COLORSPACE)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: Subtitling performed. objSettings.SUBTITLE_DEPTH={objSettings.SUBTITLE_DEPTH} pwp={pwp} num_parts={num_parts} max_depth_this_time={max_depth_this_time} text_subpath_for_subtitles="{text_subpath_for_subtitles}"')
		else:
			if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: No subtitling performed since max_depth_this_time <= 0. objSettings.SUBTITLE_DEPTH={objSettings.SUBTITLE_DEPTH} pwp={pwp} num_parts={num_parts} max_depth_this_time={max_depth_this_time}')
			pass
		# To tinker with .ass subs, see https://snapcraft.io/install/aegisub-procles/ubuntu
		# Also note from an aegisub created .ass file
		#	Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
		#	Style: h3333,Arial,18,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0.9,0.5,3,2,2,2,1
		# whereas default .assrender.Subtitle style="sans-serif,18,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1"
		# https://github.com/AmusementClub/assrender
		# assrender.Subtitle(clip clip, string[] text, [string style="sans-serif,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,10,10,10,1", int[] start, int[] end, string vfr, int hinting=0, float scale=1.0, float line_spacing=1.0, float dar, float sar, bool set_default_storage_size=True, int top=0, int bottom=0, int left=0, int right=0, string charset, int debuglevel, string fontdir="", string srt_font="sans-serif", string colorspace])
		#	colorspace Rec2020, BT.2020 Rec709, BT.709, Rec601, BT.601, PC.709, PC.601, TV.fcc, PC.fcc, TV.240m, PC.240m
		#	When no hint found in ASS script and colorspace parameter is empty then the default is BT.601
	else:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: No subtitling performed. objSettings.SUBTITLE_DEPTH={objSettings.SUBTITLE_DEPTH}')
		pass
	if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: returning working clip properties: clip.format.name="{clip.format.name}" clip.format.color_family="{clip.format.color_family}" clip.format.sample_type="{clip.format.sample_type}" clip.format.bits_per_sample="{clip.format.bits_per_sample}" clip.format.bytes_per_sample="{clip.format.bytes_per_sample}" clip.format.num_planes="{clip.format.num_planes}" clip.format.subsampling_w="{clip.format.subsampling_w}" clip.format.subsampling_h="{clip.format.subsampling_h}"')
	with clip.get_frame(0) as f:
		if A_DEBUG_IS_ON: print_DEBUG(f'get_clip: returning working frame properties: w={clip.width} h={clip.height} fps={clip.fps} {clip} {objPrettyPrint.pformat(f.props)}')
		pass
	del clip_specs
	return clip

###
def get_path(path_generator):
	# get next path of desired extensions from generator, ignoring extensions we have not specified
	while 1:	# loop until we do a "return", hitting past the end of the iterator returns None
		try:
			path = next(path_generator)
			if A_DEBUG_IS_ON: print_DEBUG(f'get_path: get success, path.name=' + path.name)
		except StopIteration:
			return None
		if path.suffix.lower() in objSettings.EXTENSIONS:	# only return files which are in known extensions
			if A_DEBUG_IS_ON: print_DEBUG(f'get_path: in objSettings.EXTENSIONS success, path.name=' + path.name)
			return path
		  
###
def crossfade(a, b, crossfade_duration_frames):
	# THIS FUNCTION IS NO LONGER USED
	# gets crosfade part from end of clip a and start of clip b
	# bug: in the context of the caller, it duplicates bits of clips and looks very strange
	def fade_image(n, a, b):
		return core.std.Merge(a, b, weight=n/crossfade_duration_frames)
	if a.format.id != b.format.id or a.height != b.height or a.width != b.width:
		raise ValueError(f'ERROR: crossfade: Both clips must have the same dimensions and format.')
	# https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/
	# string[start:end]	: all characters from start to (end - 1) : base 0
	# string[start:]	: all characters from "start" to the end of the string : base 0
	# string[0:]		: all characters (which is 0 to the end of the string) : base 0
	# string[1:]		: character 1 to the end of the string : base 0
	# string[:5]		: characters 0 to 4 inclusive : base 0
	# string[0:5]		: characters 0 to 4 inclusive : base 0
	# string[2:6]		: characters 2 to 5 inclusive : base 0
	# string[-1:]		: rightmost 1 character of the string
	# string[-5:]		: rightmost 5 characters of a string
	# string[:-1]		: all characters excluding the the rightmost character : base 0
	# string[:-5]		: all characters excluding the the rightmost 5 characters : base 0
	# string[1:-4]		: all characters except the leftmost character and last 4 characters : base 0
	# THE SAME APPLIES TO FRAMES
	#
	a_clipped = a[-crossfade_duration_frames:]	# rightmost "crossfade_duration_frames" frames of a
	b_clipped = b[:crossfade_duration_frames]	# leftmost  "crossfade_duration_frames" frames of b
	crossfade_clip = core.std.FrameEval(a_clipped, partial(fade_image, a=a_clipped, b=b_clipped))
	return crossfade_clip

###
def crossfade_merge(a=None, b=None, crossfade_duration_frames:int=4, crossfade_type:str=None, crossfade_direction:str=None):
	# (sort of) APPEND clip_b to the end of clip_a
	# using a crossfade transition to merge them, returning a merged clip HOWEVER
	# the TOTAL LENGTH of the returned clip will be (original_length_a + original_length_b - (2 * crossfade_duration_frames)) 
	#		... there is no crossfade on the right, so crossfade_duration_frames is merged from a and from b, making a reduction of (2 * crossfade_duration_frames)
	#		... except for crossfade_type="none"
	# since "crossfade_duration_frames" is used from each clips to make the transition merger
	#
	# https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/
	# string[start:end]	: all characters from start to (end - 1) : base 0
	# string[start:]	: all characters from "start" to the end of the string : base 0
	# string[0:]		: all characters (which is 0 to the end of the string) : base 0
	# string[1:]		: character 1 to the end of the string : base 0
	# string[:5]		: characters 0 to 4 inclusive : base 0
	# string[0:5]		: characters 0 to 4 inclusive : base 0
	# string[2:6]		: characters 2 to 5 inclusive : base 0
	# string[-1:]		: rightmost 1 character of the string
	# string[-5:]		: rightmost 5 characters of a string
	# string[:-1]		: all characters excluding the the rightmost character : base 0
	# string[:-5]		: all characters excluding the the rightmost 5 characters : base 0
	# string[1:-4]		: all characters except the leftmost character and last 4 characters : base 0
	# THE SAME APPLIES TO FRAMES
	#
	# vs-transitions DOCUMENTATION:
	#		https://vapoursynth-transitions.readthedocs.io/en/latest/api.html
	#
	# vs-transitions Enums and Constants:
	#		https://vapoursynth-transitions.readthedocs.io/en/latest/api.html
	#
	global crossfade_type_list
	global crossfade_type_list_no_black_fades
	global crossfade_direction_list
	global Count_of_files
	
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: ENTERED from call: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}"\na={a}\nb={b}')
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: ENTERED from call: a={a} a={a.width}x{a.height}')
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: ENTERED from call: b={b} b={b.width}x{b.height}')
	
	if a is None:
		raise ValueError(f'ERROR: crossfade_merge: crossfade_type "{crossfade_type}" Clip "a" must be a clip. \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
	if crossfade_type is None:
		crossfade_type = "random".lower()
		print_NORMAL(f'ENCODER: WARNING: crossfade_merge: unspecified crossfade_type "{crossfade_type}", using "random" instead.')
	else:
		crossfade_type = crossfade_type.lower()
		if crossfade_type not in crossfade_type_list:
			print_NORMAL(f'ENCODER: WARNING: crossfade_merge: unrecognised crossfade_type "{crossfade_type}", using "random" instead.')
			crossfade_type = "random".lower()
	if crossfade_type in list(map(str.lower,[ 'fade_to_black', 'fade_from_black', ])):	# these only consume clip a, and so clip b can be none
		pass	# these 2 crossfade_types do not need nor want a clip b
	else:
		if a.format.id != b.format.id or a.height != b.height or a.width != b.width:
			raise ValueError(f'ERROR: crossfade_merge: crossfade_type "{crossfade_type}" Both clips must have the same dimensions and format. \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
	###if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: about to enter "random" choice(): crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
	i = 0
	if crossfade_type == 'random'.lower():
		while crossfade_type in list(map(str.lower,[ 'random', 'linear_boundary', ])):	# in the 'banned' list for random. perhaps peel too
			i = i + i
			if i > 10:
				crossfade_type = 'curtain_reveal'.lower()
				break
			crossfade_type = random.choice(crossfade_type_list_no_black_fades)
		# take care of suitable directions if 'random'
		if 'curtain'.lower() in crossfade_type:
			crossfade_direction = random.choice([vs_transitions.Direction.HORIZONTAL.value, vs_transitions.Direction.VERTICAL.value])
		else:
			crossfade_direction = random.choice([vs_transitions.Direction.LEFT.value, vs_transitions.Direction.RIGHT.value, vs_transitions.Direction.UP.value, vs_transitions.Direction.DOWN.value])
	###if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: after "random" choice(): crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
	# Check for a valid direction, if required
	#for v in vs_transitions.Direction:		``			
	#	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: vs_transitions.Direction ENUM: {str(v)} = {v.value}')
	if crossfade_type not in list(map(str.lower,[ 'none', 'fade', 'fade_to_black', 'fade_from_black', 'pixellate', ])):	# i.e. it actually requires a valid direction
		if crossfade_direction not in crossfade_direction_list:	# ensure the direction is valid
			raise ValueError(f'ERROR: crossfade_merge: crossfade_type "{crossfade_type}" required crossfade_direction "crossfade_direction" is not one of {crossfade_direction_list}.') 
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: about to ACT via "match": crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
	if 'curtain'.lower() in crossfade_type:
		d = [vs_transitions.Direction.HORIZONTAL.value, vs_transitions.Direction.VERTICAL.value]
		if crossfade_direction not in d:
			o = crossfade_direction
			crossfade_direction = random.choice(d)
			print_NORMAL(f'ENCODER: WARNING: crossfade_merge: crossfade_type="{crossfade_type}" invalid crossfade_direction="{o}" so random direction="{crossfade_direction}" chosen')
	else:
		d = [vs_transitions.Direction.LEFT.value, vs_transitions.Direction.RIGHT.value, vs_transitions.Direction.UP.value, vs_transitions.Direction.DOWN.value]
		if crossfade_direction not in d:
			o = crossfade_direction
			crossfade_direction = random.choice(d)
			print_NORMAL(f'ENCODER: WARNING: crossfade_merge: crossfade_type="{crossfade_type}" invalid crossfade_direction="{o}" so random direction="{crossfade_direction}" chosen')
	#
	# https://www.freecodecamp.org/news/how-to-substring-a-string-in-python/
	# string[start:end]	: all characters from start to (end - 1) : base 0
	# string[start:]	: all characters from "start" to the end of the string : base 0
	# string[0:]		: all characters (which is 0 to the end of the string) : base 0
	# string[1:]		: character 1 to the end of the string : base 0
	# string[:5]		: characters 0 to 4 inclusive : base 0
	# string[0:5]		: characters 0 to 4 inclusive : base 0
	# string[2:6]		: characters 2 to 5 inclusive : base 0
	# string[-1:]		: rightmost 1 character of the string
	# string[-5:]		: rightmost 5 characters of a string
	# string[:-1]		: all characters excluding the the rightmost character : base 0
	# string[:-5]		: all characters excluding the the rightmost 5 characters : base 0
	# string[1:-4]		: all characters except the leftmost character and last 4 characters : base 0
	# THE SAME APPLIES TO FRAMES
	a_leftmost_without_crossfade_frames  = a[                            : -crossfade_duration_frames ]		# all frames excluding the rightmost (crossfade_duration_frames) frames : base 0
	a_crossfading_frames                 = a[ -crossfade_duration_frames : ]								# rightmost (crossfade_duration_frames) frames inclusive
	b_rightmost_without_crossfade_frames = b[  crossfade_duration_frames : ]								# middle frame (crossfade_duration_frames) to the end of the frames inclusive : base 0
	b_crossfading_frames                 = b[                            : crossfade_duration_frames ]		# leftmost "crossfade_duration_frames" frames of b ... 
	len_a = len(a)

	len_a_leftmost_without_crossfade_frames = len(a_leftmost_without_crossfade_frames)

	len_a_crossfading_frames = len(a_crossfading_frames)
	len_b = len(b)
	len_b_rightmost_without_crossfade_frames = len(b_rightmost_without_crossfade_frames)
	len_b_crossfading_frames = len(b_crossfading_frames)
	if (len_a_leftmost_without_crossfade_frames + len_a_crossfading_frames) != len_a:
		raise ValueError(f'ERROR: crossfade_merge: calculation issue: len(clip_a)={len_a} != ( len(a_leftmost_without_crossfade_frames)={len_a_leftmost_without_crossfade_frames} +  len(a_crossfading_frames)={len_a_crossfading_frames} ({len_a_leftmost_without_crossfade_frames + len_a_crossfading_frames}))')
	if (len_b_rightmost_without_crossfade_frames + len_b_crossfading_frames) != len_b:
		raise ValueError(f'ERROR: crossfade_merge: calculation issue: len(clip_b)={len_b} != ( len(b_rightmost_without_crossfade_frames)={len_b_rightmost_without_crossfade_frames} +  len(b_crossfading_frames)={len_b_crossfading_frames} ) ({len_b_rightmost_without_crossfade_frames + len_b_crossfading_frames})')
	
	# Calculate the frame number where the second clip starts merging
	snippet_video_frame_number = len_a_leftmost_without_crossfade_frames
	#print(f"crossfade_merge: The second clip starts merging at frame number: {snippet_video_frame_number}", file=sys.stderr, flush=True)
	# Calculate the number of frames in the second clip (duration as number of frames)
	snippet_num_frames = len_b
	#print(f"crossfade_merge: The number of frames in the second clip being merged is {snippet_num_frames}.", file=sys.stderr, flush=True)

	crossfaded_clips = None
	# ok, there is intentionally NOT a case 'linear_boundary':
	try:
		match crossfade_type:
			case 'none':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "none"')
				#crossfaded_clips = a_crossfading_frames + b_crossfading_frames	# original non-faded parts of clips, joined : this clip will be longer than the other crossfaded clips below since the other crossfades chew into the original clip display time and this one doesn't
				crossfaded_clips = vs_transitions.add_together(a_crossfading_frames, b_crossfading_frames)
				pass
			case 'fade': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "fade"')
				crossfaded_clips = vs_transitions.fade(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames)
				pass
			case 'fade_to_black':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "fade_to_black"')
				crossfaded_clips = vs_transitions.fade_to_black(a, frames=crossfade_duration_frames)
				pass
			case 'fade_from_black':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "fade_from_black"')
				crossfaded_clips = vs_transitions.fade_from_black(a, frames=crossfade_duration_frames)
				pass
			case 'pixellate':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "pixellate"')
				if crossfade_duration_frames < 4:
					crossfade_duration_frames = 4
				crossfaded_clips = vs_transitions.pixellate(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, lowest_target_w=2, lowest_target_h=2)
				pass
			case 'wipe':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "wipe"')
				crossfaded_clips = vs_transitions.wipe(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'push': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "push"')
				crossfaded_clips = vs_transitions.push(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'slide_expand':
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "slide_expand"')
				crossfaded_clips = vs_transitions.slide_expand(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'squeeze_slide': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "squeeze_slide"')
				crossfaded_clips = vs_transitions.squeeze_slide(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'squeeze_expand': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "squeeze_expand"')
				crossfaded_clips = vs_transitions.squeeze_expand(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'cover': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "cover"')
				crossfaded_clips = vs_transitions.cover(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'reveal': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "reveal"')
				crossfaded_clips = vs_transitions.reveal(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'curtain_cover': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_axis="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "curtain_cover"')
				crossfaded_clips = vs_transitions.curtain_cover(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, axis=crossfade_direction)		# vs_transitions.Direction.HORIZONTAL
				pass
			case 'curtain_reveal': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_axis="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "curtain_reveal"')
				crossfaded_clips = vs_transitions.curtain_reveal(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, axis=crossfade_direction)	# vs_transitions.Direction.HORIZONTAL
				pass
			case 'peel': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "pass"')
				crossfaded_clips = vs_transitions.peel(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction)
				pass
			case 'cube_rotate': 
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for "cube_rotate"')
				crossfaded_clips = vs_transitions.cube_rotate(a_crossfading_frames, b_crossfading_frames, frames=crossfade_duration_frames, direction=crossfade_direction, exaggeration=100)
				pass
			case _:	# the "_" means a final "else".	should be an error ... just concatenate the clips like 'none'
				if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: calling: crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height} calling for case else "none"')
				#crossfaded_clips = a_crossfading_frames + a_crossfading_frames
				crossfaded_clips = vs_transitions.add_together(a_crossfading_frames, b_crossfading_frames)
				pass
	except:
		print_NORMAL(f'ERROR: crossfade_merge: exception returned from vs_transitions: File_number={Count_of_files} crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}" \na={a} a={a.width}x{a.height}\nb={b} b={b.width}x{b.height}')
		raise

	if crossfaded_clips is None or len(crossfaded_clips) == 0:
		raise ValueError(f'ERROR: crossfade_merge: empty cross-faded clips detected. crossfaded_clips={crossfaded_clips}')

	return_clip = a_leftmost_without_crossfade_frames + crossfaded_clips + b_rightmost_without_crossfade_frames
	del a_leftmost_without_crossfade_frames
	del a_crossfading_frames
	del b_rightmost_without_crossfade_frames
	del b_crossfading_frames
	del crossfaded_clips
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: RETURNING from called with crossfade_type="{crossfade_type}" crossfade_duration_frames={crossfade_duration_frames} crossfade_direction="{crossfade_direction}"')
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: RETURNING from call a={a} a={a.width}x{a.height}')
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: RETURNING from call b={b} b={b.width}x{b.height}')
	if A_DEBUG_IS_ON: print_DEBUG(f'crossfade_merge: RETURNING from call return_clip={return_clip} {return_clip.width}x{return_clip.height}')
	return return_clip, snippet_video_frame_number, snippet_num_frames

###
def print_exif_data(exif_data):
	# for images
	for tag_id in exif_data:
		tag = TAGS.get(tag_id, tag_id)
		content = exif_data.get(tag_id)
		if isinstance(content, bytes):
			content = r'byte content'	#content.decode()
		if A_DEBUG_IS_ON: print_DEBUG(f'{tag:25}: {content}')
	if A_DEBUG_IS_ON: print_DEBUG(f'exif_data:\n{objPrettyPrint.pformat(exif_data)}\n')
	return
		
###
def print_exif_data2(exif_data):
	# for images
	for tag_id in exif_data:
		tag = TAGS.get(tag_id, tag_id)
		content = exif_data.get(tag_id)
		if isinstance(content, bytes):
			content = r'byte content'	#content.decode()
		if A_DEBUG_IS_ON: print_DEBUG(f'{tag:25}: {content}')
	if A_DEBUG_IS_ON: print_DEBUG(f'exif_data2:\n{objPrettyPrint.pformat(exif_data)}\n')
	return

###
def perform_rotation_PIL(clip, path, save_rotated_image=False):
	# THIS FUNCTION IS NO LONGER USED
	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
	# from PIL import Image, ExifTags, UnidentifiedImageError   # pip install Pillow, or equivalent
	# PIL Pillow module loads an image, checks if EXIF data, checks for 'Orientation'
	# The Python Pillow library is a fork of an older library called PIL. 
	# Older PIL stands for Python Imaging Library, and it's the original library that enabled Python to deal with images. 
	# PIL was discontinued in 2011 (that author died) and only supports Python 2.23 ... so use Pillow instead.
	# https://python-pillow.org/
	if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL entered - this is bad')
	raise ValueError(f'ERROR: perform_rotation_PIL sould never have been called')
	try:
		image = Image.open(str(path))
	except UnidentifiedImageError:
		if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL: except UnidentifiedImageError immediate return now')
		try:
			image.close()
		except:
			pass
		return clip
	except PermissionError:
		if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL: except PermissionError Permission denied to load: {path} {e} {type(e)} {str(e)} - immediate return now')
		try:
			image.close()
		except:
			pass
		return clip
	except Exception as e:
		if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL: except Exception {e} {type(e)} {str(e)} - immediate return now')
		try:
			image.close()
		except:
			pass
		return clip
	if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL try on Image.open succeeded')
	try:		
		for key in ExifTags.TAGS.keys():
			if ExifTags.TAGS[key] == 'Orientation':
				break
		exif = dict(image.getexif().items())
		value = exif[key]
	except (AttributeError, KeyError, IndexError):
		if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_PIL except AttributeError during for key in ExifTags.TAGS.keys(), immediate return now')
		try:
			image.close()
		except:
			pass
		return clip
	else:
		if   value == 3:
			if A_DEBUG_IS_ON: print_DEBUG(f'PIL says auto-Rotating anti-clockwise by 180 degrees {path}')
			clip = clip.std.Turn180()							# 180 DEGREE CLOCKWISE AND ANTI-CLOCLWISE ARE IDENTICAL
		elif value == 8:
			if A_DEBUG_IS_ON: print_DEBUG(f'PIL says auto-Rotating by anti-clockwise  90 degrees {path}')
			clip = clip.std.Transpose().std.FlipVertical()		# THIS IS ANTICLOCKWISE
		elif value == 6:
			if A_DEBUG_IS_ON: print_DEBUG(f'PIL says auto-Rotating anti-clockwise by 270 degrees {path}')
			clip = clip.std.Transpose().std.FlipHorizontal()	# THIS IS ANTICLOCKWISE
		else:
			if A_DEBUG_IS_ON: print_DEBUG(f'PIL says auto-Rotating IGNORED value={value} {path}')
			pass
		if save_rotated_image and value in [3,8,6]:
			#rotation degrees are in counterclockwise direction!
			rotate = {3:Image.ROTATE_180, 6:Image.ROTATE_270, 8:Image.ROTATE_90}
			image = image.transpose(rotate[value])
			path2 = path.parent / f'{path.stem}_rotated{path.suffix}'
			##image.save(str(path2))	# comment this out ... no writing new images, please
			if A_DEBUG_IS_ON: print_DEBUG(f'Rotated image {path} was NOT saved as requested into {path2}')
	#if A_DEBUG_IS_ON: exif = image.getexif()
	#if A_DEBUG_IS_ON: print_exif_data(exif)
	#if A_DEBUG_IS_ON: if A_DEBUG_IS_ON: print_DEBUG(f'')
	#if A_DEBUG_IS_ON: print_exif_data(exif.get_ifd(0x8769))
	#if A_DEBUG_IS_ON: print_DEBUG(f'')
	#if A_DEBUG_IS_ON: print_exif_data2(image.getexif())
	#if A_DEBUG_IS_ON: if A_DEBUG_IS_ON: print_DEBUG(f'')
	#if A_DEBUG_IS_ON: print_exif_data2(image._getexif())
	#if A_DEBUG_IS_ON: print_DEBUG(f'')
	try:
		image.close()
	except:
		pass
	return clip

###
def perform_rotation_MediaInfo(clip, path, save_rotated_image=False):
	# THIS FUNCTION IS NO LONGER USED
	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
	if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_MediaInfo entered - this is bad')
	raise ValueError(f'ERROR: perform_rotation_MediaInfo should never have been called')
	param = 'Rotation'
	value = mediainfo_value(Stream.Video, 0, param, path)
	if param == 'Rotation':
		if value is None:
			value = 0
		else:
			value = int(float(value)) # for some reason Rotation value type mediainfo carries as a string,  like: '180.00'
	###if A_DEBUG_IS_ON: print_DEBUG(f'perform_rotation_MediaInfo: auto-Rotating by value={value} for {path}')
	if   value == 180 or value == -180:
		if A_DEBUG_IS_ON: print_DEBUG(f'MediaInfo says auto-Rotating clockwise by 180 degrees {path}')	# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		clip = clip.std.Turn180()							# 180 DEGREE CLOCKWISE AND ANTI-CLOCLWISE ARE IDENTICAL
	elif value == 90 or value == -270:
		# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		if A_DEBUG_IS_ON: print_DEBUG(f'MediaInfo says auto-Rotating clockwise by 90 degrees {path}')
		#clip = clip.std.Transpose().std.FlipVertical()		# THIS IS ANTICLOCKWISE
		clip = clip.std.Transpose().std.FlipHorizontal()	# THIS IS CLOCKWISE
	elif value == 270 or value == -90:
		# A TRICK FOR NEW PLAYERS ... MEDIAINFO YIELDS ROTATION VALUES FOR CLOCKWISE ROTATIONS for videos !!! NOT ANTI-CLOCKWISE like PIL !!!
		if A_DEBUG_IS_ON: print_DEBUG(f'MediaInfo says auto-Rotating clockwise by 270 degrees {path}')
		#clip = clip.std.Transpose().std.FlipHorizontal()	# THIS IS ANTICLOCKWISE
		clip = clip.std.Transpose().std.FlipVertical()		# THIS IS CLOCKWISE
	else:
		if A_DEBUG_IS_ON: print_DEBUG(f'MediaInfo says auto-Rotating clockwise IGNORED value={value} {path}')
		pass
	return clip


###################################################################################################################################################
###################################################################################################################################################
###################################################################################################################################################

### NEVER hide .vpy behind this: "if __name__=='__main__':"
### BECAUSE IT DOES NOT GET RUN BY VSPIPE NOR FFMPEG and thus everything then mucks up

# A note about fixed output colour characteristics (the y4m YUV4MPEG2 container doesn't mention them.
# https://forum.videohelp.com/newreply.php?do=postreply&t=408230#post2684387
# So we always output BT.709 and related characteristics per what we specify in default_ini_values

#++++++++++++++++++++
# Read and process the .ini file and use defaults where appropriate
# modified to use nre NEW settings Class
objSettings = settings()

objSettings.debug_print_class_vars()

if objSettings.DEBUG: print_DEBUG(f"DEBUG={objSettings.DEBUG} IS_DEBUG={IS_DEBUG} IS_DEBUG_SYSTEM_OVERRIDE={IS_DEBUG_SYSTEM_OVERRIDE} A_DEBUG_IS_ON={A_DEBUG_IS_ON}")

#++++++++++++++++++++
if not os.path.isdir(objSettings.TEMP_DIRECTORY_LIST[0]):
	try: 
		os.mkdir(objSettings.TEMP_DIRECTORY_LIST[0]) 
		print_NORMAL(f'Created new directory: "{objSettings.TEMP_DIRECTORY_LIST[0]}"')
	except OSError as error: 
		###if A_DEBUG_IS_ON: print_DEBUG(error) 
		pass
#++++++++++++++++++++
if A_DEBUG_IS_ON: print_DEBUG(f'Creating blank_clip with the desired  target properties')
blank_clip = core.std.BlankClip(format=objSettings.WORKING_PIXEL_FORMAT, width=objSettings.TARGET_WIDTH, height=objSettings.TARGET_HEIGHT, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN, length=objSettings.DURATION_BLANK_CLIP_FRAMES) #, color=(0,128,128))	 # notice no colorspace,"range" etc can be specified
blank_clip = core.std.AssumeFPS(clip=blank_clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
last_file_opened_with_ffms2 = True	# JUST A DUMMY FOR get_clip_specs
last_file_opened_with_imwri = False
last_file_opened_with_LWLibavSource = False
last_file_opened_with_LibavSMASHSource = False
blank_clip_specs = get_clip_specs(blank_clip, path=None, ext=".mp4", mediainfo_specs=None)
# now guess and set any missing specs in blank_clip
if blank_clip_specs["guessed_Matrix"]:
	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: SetFrameProps _Matrix from existing "{blank_clip_specs["_Matrix"]}" to guessed "{blank_clip_specs["proposed_Matrix"]}"')
	blank_clip = core.std.SetFrameProps(blank_clip, _Matrix=blank_clip_specs["proposed_Matrix"])
if blank_clip_specs["guessed_Primaries"]:
	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: SetFrameProps _Primaries from existing "{blank_clip_specs["_Primaries"]}" to guessed "{blank_clip_specs["proposed_Primaries"]}"')
	blank_clip = core.std.SetFrameProps(blank_clip, _Primaries=blank_clip_specs["proposed_Primaries"])
if blank_clip_specs["guessed_Transfer"]:
	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: SetFrameProps _Transfer from existing "{blank_clip_specs["_Transfer"]}" to guessed "{blank_clip_specs["proposed_Transfer"]}"')
	blank_clip = core.std.SetFrameProps(blank_clip, _Transfer=blank_clip_specs["proposed_Transfer"])
# NOTE THESE IN REGARD TO VS "bug" in RANGE values not agreeing with the spec:
#	https://github.com/vapoursynth/vapoursynth/issues/940
#	https://github.com/vapoursynth/vapoursynth/issues/857
# https://github.com/vapoursynth/vapoursynth/issues/940#issuecomment-1465041338
# When calling rezisers etc, ONLY use these values:
#	ZIMG_RANGE_LIMITED  = 0,  /**< Studio (TV) legal range, 16-235 in 8 bits. */
#	ZIMG_RANGE_FULL     = 1   /**< Full (PC) dynamic range, 0-255 in 8 bits. */
# but when obtaining from frame properties and comparing etc, use the vs values from
# frame properties even though the vapoursynth values are incorrect (opposite to the spec)
# BUT BUT BUT here we are working solely with vapoursynth settings, not resizers, so stick with using vapoursynth constants and not zimg ones
#if blank_clip_specs["guessed_ColorRange"]:
#	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: SetFrameProps _ColorRange from existing "{blank_clip_specs["_ColorRange"]}" to guessed "{blank_clip_specs["proposed_ColorRange"]}"')
#	blank_clip = core.std.SetFrameProps(blank_clip, _ColorRange=blank_clip_specs["proposed_ColorRange"])
# Ensure the colour range of the blank_clip is what we require, by using a resizer to set the properties
with blank_clip.get_frame(0) as f:
	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: incoming frame properties before resize: w={blank_clip.width} h={blank_clip.height} fps={blank_clip.fps} {objPrettyPrint.pformat(blank_clip)} {objPrettyPrint.pformat(f.props)}')
	pass
if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: TARGET resize properties: width={blank_clip.width}, height={blank_clip.height}, format={objSettings.WORKING_PIXEL_FORMAT}, objSettings.TARGET_COLOR_RANGE_I_ZIMG={objSettings.TARGET_COLOR_RANGE_I_ZIMG}), primaries={objSettings.TARGET_COLOR_PRIMARIES_I}, transfer={objSettings.TARGET_COLOR_TRANSFER_I},  matrix={objSettings.TARGET_COLORSPACE_MATRIX_I}')
blank_clip_resize = getattr(blank_clip.resize, objSettings.UPSIZE_KERNEL)	# get the resize function object ?handle? with the nominated kernel
#
blank_clip = blank_clip_resize(width=objSettings.TARGET_WIDTH, height=objSettings.TARGET_HEIGHT, format=objSettings.WORKING_PIXEL_FORMAT, matrix=objSettings.TARGET_COLORSPACE_MATRIX_I, transfer=objSettings.TARGET_COLOR_TRANSFER_I, primaries=objSettings.TARGET_COLOR_PRIMARIES_I, range=objSettings.TARGET_COLOR_RANGE_I_ZIMG)
blank_clip = core.std.AssumeFPS(clip=blank_clip, fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
with blank_clip.get_frame(0) as f:
	if A_DEBUG_IS_ON: print_DEBUG(f'blank_clip: outgoing frame properties after resize: w={blank_clip.width} h={blank_clip.height} fps={blank_clip.fps} {objPrettyPrint.pformat(blank_clip)} {objPrettyPrint.pformat(f.props)}')
	pass
#
last_file_opened_with_ffms2 = False
if A_DEBUG_IS_ON: print_DEBUG(f'Created blank_clip with the desired  target properties')

#++++++++++++++++++++
crossfade_blank_clip = blank_clip[0]*objSettings.DURATION_BLANK_CLIP_FRAMES
prior_clip_for_crossfade = crossfade_blank_clip
#if objSettings.DURATION_CROSSFADE_FRAMES > 0:
#	#if len(blank_clip) < objSettings.DURATION_CROSSFADE_FRAMES :
#	#	crossfade_blank_clip = blank_clip[0]*objSettings.DURATION_CROSSFADE_FRAMES
#	#else 
#	#	crossfade_blank_clip = blank_clip
#	crossfade_blank_clip = blank_clip[0]*objSettings.DURATION_CROSSFADE_FRAMES
#	prior_clip_for_crossfade = crossfade_blank_clip
#	if A_DEBUG_IS_ON: print_DEBUG(f'objSettings.DURATION_CROSSFADE_FRAMES ({objSettings.DURATION_CROSSFADE_FRAMES}) > 0 ... crossfade_blank_clip={crossfade_blank_clip}')
#else:
#	prior_clip_for_crossfade = blank_clip
#	if A_DEBUG_IS_ON: print_DEBUG(f'objSettings.DURATION_CROSSFADE_FRAMES ({objSettings.DURATION_CROSSFADE_FRAMES}) <= 0 ... no crossfade_blank_clipcreated')
#
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++


CURRENT_CHUNK_FILENAME = UTIL.fully_qualified_filename(objSettings.SETTINGS_DICT['CURRENT_CHUNK_FILENAME'])
if not os.path.exists(CURRENT_CHUNK_FILENAME):
	raise ValueError(f'ERROR: Incoming current chunk JSON-file "{CURRENT_CHUNK_FILENAME}" not found !')

try:
	with open(CURRENT_CHUNK_FILENAME, 'r') as fp:
		individual_chunk_dict = json.load(fp)
except Exception as e:
	raise ValueError(f'ERROR: loading incoming current chunk JSON file: "{CURRENT_CHUNK_FILENAME}" from controller !')
print_NORMAL(f'ENCODER (legacy): Loaded incoming current chunk JSON file: "{CURRENT_CHUNK_FILENAME}" from controller.')

# OK we have retrieved a chunk dict, telling us what to encode.  It has this format:
#	{	
#		'chunk_id': chunk_id,
#		'chunk_fixed_json_filename' :				UTIL.fully_qualified_filename(SETTINGS_DICT['CURRENT_CHUNK_FILENAME']),		# always the same fixed filename
#		'proposed_ffv1_mkv_filename' :				UTIL.fully_qualified_filename(SETTINGS_DICT['CHUNK_ENCODED_FFV1_FILENAME_BASE'] + str(chunk_id).zfill(5) + r'.mkv'),	# filename related to chunk_id
#		'num_frames_in_chunk' :						0,	# initialize to 0, filled in by encoder
#		'start_frame_num_in_chunk':					0,	# initialize to 0, filled in by encoder
#		'end_frame_num_in_chunk':					0,	# initialize to 0, filled in by encoder
#		'start_frame_num_of_chunk_in_final_video':	0,	# initialize to 0, # calculated AFTER encoder finished completely
#		'end_frame_num_of_chunk_in_final_video': 	0,	# initialize to 0, # calculated AFTER encoder finished completely
#		'num_files': 								0,	# initialized but filled in by this loop, number of files in file_list
#		'file_list':	 							[],	# each item is a fully qualified filename of a source file for this chunk
#		'num_snippets': 							0,	# # initialize to 0, number of files in file_list, filled in by encoder
#		'snippet_list': 							[], # an empty dict to be be filled in by encoder, it looks like this:
#		# snippet_list:	[								# each snippet list item is a dict which looks like the below:
#		#					{	
#		#						'start_frame_of_snippet_in_chunk': 0,				# filled in by encoder
#		#						'end_frame_of_snippet_in_chunk': XXX, 				# filled in by encoder
#		#						'start_frame_of_snippet_in_final_video': AAA,  		# AFTER all encoding completed, calculated and filled in by controller
#		#						'end_frame_of_snippet_in_final_video': XXX, 		# AFTER all encoding completed, calculated and filled in by controller
#		#						'snippet_num_frames': YYY,							# filled in by encoder
#		#						'snippet_source_video_filename': '\a\b\c\ZZZ1.3GP'	# filled in by encoder
#		#					},
#		#				]
#	}
#
# These fields in a chunk dict NEED to be UPDATED BY THE ENCODER:
#	'num_frames_in_chunk'
#	'start_frame_num_in_chunk'
#	'end_frame_num_in_chunk'
#	'num_snippets': 							0,	# # initialize to 0, number of files in file_list, filled in by encoder
#		'snippet_list'
#			'start_frame_of_snippet_in_chunk': 0,				# filled in by encoder
#			'end_frame_of_snippet_in_chunk': XXX, 				# filled in by encoder
#			'snippet_num_frames': YYY,							# filled in by encoder
#			'snippet_source_video_filename': '\a\b\c\ZZZ1.3GP'	# filled in by encoder
#		

ct = objSettings.CROSSFADE_TYPE if objSettings.DURATION_CROSSFADE_FRAMES>0 else None
cd = objSettings.CROSSFADE_DIRECTION if objSettings.DURATION_CROSSFADE_FRAMES>0 else None

Count_of_files = 0
clips = prior_clip_for_crossfade	# initialize the accumulated clips with a starting small blank clip
Count_of_snippets = 0

num_files = individual_chunk_dict['num_files']
print_NORMAL(f'ENCODER (legacy): Start processing {num_files} image/video files, crossfade="{ct}/{cd}" RECURSIVE={objSettings.RECURSIVE} DEBUG_MODE={objSettings.DEBUG_MODE}" \n      with Extensions={objPrettyPrint.pformat(objSettings.EXTENSIONS)}')
for i in range(0,num_files):	# base 0; 0..(num_files - 1)
	file_to_process = individual_chunk_dict['file_list'][i]
	path = Path(UTIL.fully_qualified_filename(file_to_process))
	
	if A_DEBUG_IS_ON: print_DEBUG(f'********************************************************************************************************************************************************************************************************************************************************')
	Count_of_files = Count_of_files + 1
	print_NORMAL(f'Processing {Count_of_files} {str(path)}')
	this_clip = get_clip_2(path)
	if this_clip is None:	# ignore clips which had an issue with being opened
		raise ValueError(f'Unable to process {Count_of_files} {str(path)} even through open-checked by the controller.')
	else:
		if objSettings.DURATION_CROSSFADE_FRAMES > 0:		# and objSettings.CROSSFADE_TYPE.lower() != "none".lower():
			if A_DEBUG_IS_ON: print_DEBUG(f'Performing crossfade_merge in while loop')
			clips, snippet_video_frame_number, snippet_num_frames = crossfade_merge(a=clips, b=this_clip, crossfade_duration_frames=objSettings.DURATION_CROSSFADE_FRAMES, crossfade_type=objSettings.CROSSFADE_TYPE, crossfade_direction=objSettings.CROSSFADE_DIRECTION) 
			if path.suffix.lower() in objSettings.VID_EXTENSIONS:
				# Save snippet info back into the LIST 'snippet_list'
				Count_of_snippets = Count_of_snippets + 1
				individual_chunk_dict['snippet_list'].append(	{	
																'start_frame_of_snippet_in_chunk':			snippet_video_frame_number,
																'end_frame_of_snippet_in_chunk':			snippet_video_frame_number + snippet_num_frames - 1,
																'start_frame_of_snippet_in_final_video':	0,
																'end_frame_of_snippet_in_final_video':		0,
																'snippet_num_frames':						snippet_num_frames,
																'snippet_source_video_filename':			str(path)
																}
															)
	del this_clip
	#num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
	###if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: in-Directory-loop end of processing a single file, number of unreachable objects found={num_unreachable_objects}')
	if A_DEBUG_IS_ON: print_DEBUG(f'********************************************************************************************************************************************************************************************************************************************************')
#end for
#------
# perhaps a finishing crossfade to black ?
if objSettings.DURATION_CROSSFADE_FRAMES > 0 and objSettings.CROSSFADE_TYPE.lower() != "none".lower():	
	if A_DEBUG_IS_ON: print_DEBUG(f'Performing final crossfade_merge after while loop')
	clips, snippet_video_frame_number, snippet_num_frames = crossfade_merge(a=clips, b=prior_clip_for_crossfade, crossfade_duration_frames=objSettings.DURATION_CROSSFADE_FRAMES, crossfade_type=objSettings.CROSSFADE_TYPE, crossfade_direction=objSettings.CROSSFADE_DIRECTION) 
else:
	if A_DEBUG_IS_ON: print_DEBUG(f'Performing NO final crossfade_merge after while loop')
	clips = clips + prior_clip_for_crossfade	# add a small blank clip to the end
clips = clips.std.AssumeFPS(fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)

# Final updates to chunk info
clips_first_frame_num = 0
clips_last_frame_num = clips.num_frames - 1
individual_chunk_dict['num_snippets'] = Count_of_snippets
individual_chunk_dict['num_frames_in_chunk'] = clips.num_frames
individual_chunk_dict['start_frame_num_in_chunk'] = clips_first_frame_num
individual_chunk_dict['end_frame_num_in_chunk'] = clips_last_frame_num

# now dump the updated individual_chunk_dict back to disk again so it can be re-read by the controller
chunk_json_filename = UTIL.fully_qualified_filename(individual_chunk_dict['chunk_fixed_json_filename'])					# always the same fixed filename
if A_DEBUG_IS_ON:	print_DEBUG(f"DEBUG: ENCODER: attempting to create updated chunk_json_filename='{chunk_json_filename}' for controller to consume.")
try:
	with open(chunk_json_filename, 'w') as fp:
		json.dump(individual_chunk_dict, fp, indent=4)
except Exception as e:
	raise ValueError(f"ERROR: ENCODER: error dumping current chunk JSON file: '{chunk_json_filename}' individual_chunk_dict=\n{objPrettyPrint.pformat(individual_chunk_dict)}\n{str(e)}")
if A_DEBUG_IS_ON:	print_DEBUG(f"DEBUG: ENCODER: Created fixed-filename chunk file for controller to consume: '{chunk_json_filename}' listing {individual_chunk_dict['num_files']} files, individual_chunk_dict=\n{objPrettyPrint.pformat(individual_chunk_dict)}")


#++++++++++++++++++++
print_NORMAL(f'ENCODER: Finished processing {Count_of_files} image/video files, num_frames={len(clips)} crossfade="{ct}/{cd}" RECURSIVE={objSettings.RECURSIVE} DEBUG_MODE={objSettings.DEBUG_MODE}" \n      with Extensions={objPrettyPrint.pformat(objSettings.EXTENSIONS)}')
#++++++++++++++++++++

#++++++++++++++++++++
# Convert from ["WORKING_PIXEL_FORMAT"] vs.YUV444P8 to  ["WORKING_PIXEL_FORMAT"] vs.YUV420P8 for output
clips = clips.resize.Point(format=objSettings.TARGET_PIXEL_FORMAT)
#++++++++++++++++++++

#++++++++++++++++++++
# Cleanup any temporary .ffindex files created by ffms2
# THE .FFINDEX ARE CREATED in the temporary folder
print_NORMAL(f'ENCODER: Start removing temporary *.ffindex files from directory "{objSettings.TEMP_DIRECTORY_LIST[0]}" with recursive="{objSettings.RECURSIVE}" ...')
ff_glob_var="**/*.ffindex"		# for .ffindex file deletion recursive
#ff_glob_var="*.ffindex"		# for .ffindex file deletion non-recursive
pp = objSettings.TEMP_DIRECTORY_LIST[0] + "/" + ff_glob_var
ffindex_files = glob.glob(pp, recursive=objSettings.RECURSIVE)
#num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
###if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: post-Directory-loop and pre-Delete-ffindex-files-loop, number of unreachable objects found={num_unreachable_objects}')
Count_of_files_removed = 0
for ff in ffindex_files:
	if ff.lower()[-len(objSettings.DOT_FFINDEX):] == objSettings.DOT_FFINDEX:	# double check the file really does have ext .ffindex
		try:
			Count_of_files_removed = Count_of_files_removed + 1
			if A_DEBUG_IS_ON: print_DEBUG(f'removing {Count_of_files_removed} {ff}')
			os.remove(ff)
		except OSError as ee:
			print_NORMAL(f'ERROR:  error during removal of ffindex file: {ff} :{ee} : {ee.strerror}')
			raise ValueError(f'ERROR: error during removal of ffindex file: {ff} :{ee} : {ee.strerror}')
print_NORMAL(f'Finished removing {Count_of_files_removed} temporary .ffindex files with recursive="{objSettings.RECURSIVE}"')
num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: post-Delete-ffindex-files-loop, number of unreachable objects found={num_unreachable_objects}')
clips.set_output()

#++++++++++++++++++++
output_clip_specs = get_clip_specs(clips, path=None, ext=".mp4", mediainfo_specs=None)
if A_DEBUG_IS_ON: print_DEBUG(f'OUTPUT VIDEO: clip and frame properties: w={clips.width} h={clips.height} specs=\n{objPrettyPrint.pformat(output_clip_specs)}')
print_NORMAL(f'Done. ENCODER completed.')
#++++++++++++++++++++


#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++

# OLD LEGACY CODE IS COMMENTED OUT
# OLD LEGACY CODE IS COMMENTED OUT
# OLD LEGACY CODE IS COMMENTED OUT

#
#if objSettings.RECURSIVE:
#	glob_var="**/*.*"			# recursive
#	ff_glob_var="**/*.ffindex"	# for .ffindex file deletion recursive
#else:
#	glob_var="*.*"				# non-recursive
#	ff_glob_var="*.ffindex"		# for .ffindex file deletion non-recursive
# glob : with DIRECTORY not having a trailing slash !!!
#num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
#if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: post blank_clip creation and pre-Directory-loop, number of unreachable objects found={num_unreachable_objects}')
#Count_of_files = 0
#clips = prior_clip_for_crossfade	# initialize the accumulated clips with a starting small blank clip
#
## Open the snippet data file in write mode, overwriting an existing file
#snippet_data_file_object = open(objSettings.SNIPPETS_FILENAME_PATH_LIST[0] , "w")
#
#for Directory in objSettings.DIRECTORY_LIST:
#	current_Directory = UTIL.fully_qualified_directory_no_trailing_backslash(Directory)
#	ct = objSettings.CROSSFADE_TYPE if objSettings.DURATION_CROSSFADE_FRAMES>0 else None
#	cd = objSettings.CROSSFADE_DIRECTION if objSettings.DURATION_CROSSFADE_FRAMES>0 else None
#	print_NORMAL(f'Start processing image/video files in "{current_Directory}" crossfade="{ct}/{cd}" RECURSIVE={objSettings.RECURSIVE} DEBUG_MODE={objSettings.DEBUG_MODE} glob_var="{glob_var}" \n      with Extensions={objPrettyPrint.pformat(objSettings.EXTENSIONS)}')
#	# NOTE: current_Directory MUST NOT have a trailing backslash ... remove during ini setup
#	paths = Path(current_Directory).glob(glob_var) # generator of all paths in a directory, files starting with . won't be matched by default
#	path = get_path(paths)	#pre-fetch first path
#	if path is None:
#		raise ValueError(f'ERROR: File Extensions:\n{objSettings.EXTENSIONS}\nnot found in "{current_Directory}"')
#	#------
#	while not (path is None):	# first clip already pre-retrieved ready for this while loop
#		if A_DEBUG_IS_ON: print_DEBUG(f'********************************************************************************************************************************************************************************************************************************************************')
#		Count_of_files = Count_of_files + 1
#		print_NORMAL(f'processing {Count_of_files} {str(path)}')
#		this_clip = get_clip_2(path)
#		if this_clip is None:	# ignore clips which had an issue with being opened
#			print_NORMAL(f'Unable to process {Count_of_files} {str(path)} ... ignoring it ')
#		else:
#			if objSettings.DURATION_CROSSFADE_FRAMES > 0:		# and objSettings.CROSSFADE_TYPE.lower() != "none".lower():
#				#if A_DEBUG_IS_ON: print_DEBUG(f'Performing crossfade_merge in while loop')
#				clips, snippet_video_frame_number, snippet_num_frames = crossfade_merge(a=clips, b=this_clip, crossfade_duration_frames=objSettings.DURATION_CROSSFADE_FRAMES, crossfade_type=objSettings.CROSSFADE_TYPE, crossfade_direction=objSettings.CROSSFADE_DIRECTION) 
#				if path.suffix.lower() in objSettings.VID_EXTENSIONS:
#					# Save snippet info so we can find and use the file's audio later and put it in the right place in the slideshow being created by this script
#					fully_qualified_path_string = UTIL.fully_qualified_filename(path)
#					snippet_data_file_object.write(f"{snippet_video_frame_number} {snippet_num_frames} {repr(fully_qualified_path_string)}\n")
#					snippet_data_file_object.flush()
#		path = get_path(paths)		# get next path to process in this while loop
#		#num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
#		###if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: in-Directory-loop end of processing a single file, number of unreachable objects found={num_unreachable_objects}')
#		if A_DEBUG_IS_ON: print_DEBUG(f'********************************************************************************************************************************************************************************************************************************************************')
#	#------
#	# perhaps a finishing crossfade to black ?
#	if objSettings.DURATION_CROSSFADE_FRAMES > 0 and objSettings.CROSSFADE_TYPE.lower() != "none".lower():	
#		if A_DEBUG_IS_ON: print_DEBUG(f'Performing final crossfade_merge after while loop')
#		clips, snippet_video_frame_number, snippet_num_frames = crossfade_merge(a=clips, b=prior_clip_for_crossfade, crossfade_duration_frames=objSettings.DURATION_CROSSFADE_FRAMES, crossfade_type=objSettings.CROSSFADE_TYPE, crossfade_direction=objSettings.CROSSFADE_DIRECTION) 
#	else:
#		if A_DEBUG_IS_ON: print_DEBUG(f'Performing NO final crossfade_merge after while loop')
#		clips = clips + prior_clip_for_crossfade	# add a small blank clip to the end
#clips = clips.std.AssumeFPS(fpsnum=objSettings.TARGET_FPSNUM, fpsden=objSettings.TARGET_FPSDEN)
##
## Write the last line to the snippet data file and close it.
## remember:
##	using line format: start_frame_number_in_clip, last_frame_number_in_clip, filename of this slideshow in mp4 in single-quotes
##	eg 0, 2999, 'd:\slideshow_file'
##	where num_frames would be 3000
#clips_first_frame_num = 0
#clips_last_frame_num = clips.num_frames - 1
#snippet_data_file_object.write(f"{clips_first_frame_num} {clips_last_frame_num} {repr(objSettings.OUTPUT_MKV_FILENAME_PATH_LIST[0])}\n")
#snippet_data_file_object.flush()
#snippet_data_file_object.close()
##
#del this_clip
#++++++++++++++++++++
#++++++++++++++++++++
#print_NORMAL(f'Finished processing {Count_of_files} image/video files in "{current_Directory}" num_frames={len(clips)} crossfade="{ct}/{cd}" RECURSIVE={objSettings.RECURSIVE} DEBUG_MODE={objSettings.DEBUG_MODE} glob_var="{glob_var}" \n      with Extensions={objPrettyPrint.pformat(objSettings.EXTENSIONS)}')
#++++++++++++++++++++
#++++++++++++++++++++
## Convert from ["WORKING_PIXEL_FORMAT"] vs.YUV444P8 to  ["WORKING_PIXEL_FORMAT"] vs.YUV420P8 for output
#clips = clips.resize.Point(format=objSettings.TARGET_PIXEL_FORMAT)
#++++++++++++++++++++
#++++++++++++++++++++
## Cleanup any temporary .ffindex files created by ffms2
## THE .FFINDEX ARE CREATED in the temporary folder
#print_NORMAL(f'Start removing temporary *.ffindex files from directory "{current_Directory}" with recursive="{objSettings.RECURSIVE}" ...')
#ff_glob_var="**/*.ffindex"		# for .ffindex file deletion recursive
##ff_glob_var="*.ffindex"		# for .ffindex file deletion non-recursive
#pp = objSettings.TEMP_DIRECTORY_LIST[0] + "/" + ff_glob_var
#ffindex_files = glob.glob(pp, recursive=objSettings.RECURSIVE)
##num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
####if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: post-Directory-loop and pre-Delete-ffindex-files-loop, number of unreachable objects found={num_unreachable_objects}')
#Count_of_files_removed = 0
#for ff in ffindex_files:
#	if ff.lower()[-len(objSettings.DOT_FFINDEX):] == objSettings.DOT_FFINDEX:	# double check the file really does have ext .ffindex
#		try:
#			Count_of_files_removed = Count_of_files_removed + 1
#			if A_DEBUG_IS_ON: print_DEBUG(f'removing {Count_of_files_removed} {ff}')
#			os.remove(ff)
#		except OSError as ee:
#			print_NORMAL(f'ERROR:  error during removal of ffindex file: {ff} :{ee} : {ee.strerror}')
#			raise ValueError(f'ERROR: error during removal of ffindex file: {ff} :{ee} : {ee.strerror}')
#print_NORMAL(f'Finished removing {Count_of_files_removed} temporary .ffindex files with recursive="{objSettings.RECURSIVE}"')
#num_unreachable_objects = gc.collect()	# With no arguments, run a full garbage collection. # The number of unreachable objects found is returned
#if A_DEBUG_IS_ON: print_DEBUG(f'*** GARBAGE_COLLECTION: post-Delete-ffindex-files-loop, number of unreachable objects found={num_unreachable_objects}')
#clips.set_output()
#++++++++++++++++++++
#++++++++++++++++++++
#print_NORMAL(f'Done.')
#output_clip_specs = get_clip_specs(clips, path=None, ext=".mp4", mediainfo_specs=None)
#if A_DEBUG_IS_ON: print_DEBUG(f'OUTPUT VIDEO: clip and frame properties: w={clips.width} h={clips.height} specs=\n{objPrettyPrint.pformat(output_clip_specs)}')
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++
#++++++++++++++++++++

#++++++++++++++++++++
### FOR EMERGENCY DEBUG ONLY
if IS_DEBUG_SYSTEM_OVERRIDE:
	vpy_log = []
	if A_DEBUG_IS_ON: print_DEBUG('Post set_output: Consistency Check: loading all frames ...')
	num_frames = len(clips)
	baddies = 0
	for n in range(num_frames):
		try:
			clips.get_frame(n)
		except Exception as e:
			baddies = baddies + 1
			vpy_log.append(f'Post set_output: Consistency Check: FAILED to get_frame at frame {n} (base 0) of {num_frames-1} (base 0): {e}')
	if len(vpy_log) > 0:
		for n in range(len(vpy_log)):
			print_NORMAL(vpy_log[n])
		raise ValueError(f'Post set_output: Consistency Check: FAILED to get_frame {baddies} of {num_frames} frames')
	else:
		if A_DEBUG_IS_ON: print_DEBUG(f'Post set_output: Consistency Check: passed, {num_frames} frames successfully retrieved')
		pass
