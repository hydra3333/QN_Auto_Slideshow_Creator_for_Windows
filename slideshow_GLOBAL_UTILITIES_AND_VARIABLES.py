# We could use this module slideshow_GLOBAL_UTILITIES_AND_VARIABLES to store global variables.
# EVERYONE (EXCEPT ITSELF) must import slideshow_GLOBAL_UTILITIES_AND_VARIABLES 
# Then global variables can be stored and shared acorss modules
# by defining/initializing those global variables here at the module level
# (or omitting them and setting them externally, which is not good practice)
# Thus every main program and module which needs to share the globalvariables
#
# We can use this like:
#
#	import slideshow_GLOBAL_UTILITIES_AND_VARIABLES as UTIL
#	#if not hasattr(UTIL, "DEBUG"):
#	#	UTIL.DEBUG = False
#	DEBUG = UTIL.DEBUG
#
# or even just assume the variable is always defined/initialized
# by slideshow_GLOBAL_UTILITIES_AND_VARIABLES itself which is good practice.

# JUST A NOTE AND NOT USED HERE,
# if we wanted to use a dynamic memory based module for storing global variables
# we could do this in every module including this one:
#	import types
#	local_config = types.ModuleType("local_config")
# Then later do stuff like:
#	if not hasattr(local_config, "DEBUG"):
#		local_config.DEBUG = False
#	DEBUG = local_config.DEBUG

# ---------- START COMMON IMPORT BLOCK USED EVERYWHERE ----------
# ---------- START COMMON IMPORT BLOCK USED EVERYWHERE ----------
# ---------- START COMMON IMPORT BLOCK USED EVERYWHERE ----------

# 1.	Modifying the sys.path list in a module DOES NOT not affect the sys.path of other modules or the main program.
# 2.	Modifying the sys.path list in the MAIN PROGRAM WILL affect the search path for	all modules imported by that program.
# Ensure we can import modules from ".\" by adding the current default folder to the python path.
# (tried using just PYTHONPATH environment variable but it was unreliable)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#import slideshow_GLOBAL_UTILITIES_AND_VARIABLES as UTIL	# define utilities and make global variables available to everyone ... DO NOT IMPORT ITSELF

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

from PIL import Image, ExifTags, UnidentifiedImageError
from PIL.ExifTags import TAGS

import pydub
from pydub import AudioSegment

CDLL(r'MediaInfo.dll')				# note the hard-coded folder	# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
from MediaInfoDLL3 import MediaInfo, Stream, Info, InfoOption		# per https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio#post2678372
#from MediaInfoDLL3 import *											# per https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py

# ---------- END COMMON IMPORT BLOCK USED EVERYWHERE ----------
# ---------- END COMMON IMPORT BLOCK USED EVERYWHERE ----------
# ---------- END COMMON IMPORT BLOCK USED EVERYWHERE ----------

# ---------- START GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- START GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- START GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------

# Global Variables 

DEBUG = False
SETTINGS_DICT = {}
NUM_CORES = multiprocessing.cpu_count()
NUM_THREADS_FOR_FFMPEG_DIVISOR = 3	 																# for calculating number of threads ffmpeg is allowed 
NUM_THREADS_FOR_FFMPEG = min(8, max(1, int(NUM_CORES // NUM_THREADS_FOR_FFMPEG_DIVISOR)))			# of physical+hyperthreading cores (limit: 1 to 8 cores)

NUM_THREADS_FOR_FFMPEG_DECODER = min(8, max(1, int(NUM_THREADS_FOR_FFMPEG // 4)))					# 1/4 of cores for ffmpeg go to decoder
NUM_THREADS_FOR_FFMPEG_ENCODER = max(1, (NUM_THREADS_FOR_FFMPEG - NUM_THREADS_FOR_FFMPEG_DECODER))	# 3/4 or cores for ffmpeg go to encoder

FFMPEG_EXE	= 'FFMPEG_EXE_HAS_NOT_BEEN_SET_INTO_slideshow_GLOBAL_UTILITIES'				# assume set globally before calling this, so intiialize to failing value
FFPROBE_EXE	= 'FFPROBE_EXE_HAS_NOT_BEEN_SET_INTO_slideshow_GLOBAL_UTILITIES'			# assume set globally before calling this, so intiialize to failing value
VSPIPE_EXE	= 'VSPIPE_EXE_HAS_NOT_BEEN_SET_INTO_slideshow_GLOBAL_UTILITIES'				# assume set globally before calling this, so intiialize to failing value

# Global external Functions with associated variables

TERMINAL_WIDTH = 250
objPrettyPrint = pprint.PrettyPrinter(width=TERMINAL_WIDTH, compact=False, sort_dicts=False)	# facilitates formatting and 

MI = MediaInfo()
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
	'Rotation',                                      # : Rotation as a real number eg 180.00
	'FrameRate',                                     # : Frames per second
	'FrameRate_Num',                                 # : Frames per second, numerator
	'FrameRate_Den',                                 # : Frames per second, denominator
	'FrameCount',                                    # : Number of frames
	#
	'Recorded_Date',								 # : Time/date/year that the recording began ... this can be None so use Encoded_Date instead. this can be None so use Encoded_Date instead. date_recorded = datetime.strptime(mi_dict["Recorded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	'Encoded_Date',									 # : Time/date/year that the encoding of this content was completed. date_encoded = datetime.strptime(mi_dict["Encoded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	#
	'FrameRate_Mode',								 # : Frame rate mode (CFR, VFR)
	'FrameRate_Minimum',							 # : Minimum Frames per second
	'FrameRate_Nominal',							 # : Nominal Frames per second
	'FrameRate_Maximum',							 # : Maximum Frames per second
	'FrameRate_Real',								 # : Real (capture) frames per second
	'ScanType',
	'ScanOrder',
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
# ---------- END GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- END GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- END GLOBAL VARIABLED WHICH CAN BE SHARED ACROSS MODULES ----------

# ---------- START UTILITY FUNCTIONS WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- START UTILITY FUNCTIONS WHICH CAN BE SHARED ACROSS MODULES ----------
# ---------- START UTILITY FUNCTIONS WHICH CAN BE SHARED ACROSS MODULES ----------

#
def normalize_path(path):
	#if UTIL.DEBUG:	print(f"DEBUG: normalize_path:  incoming path='{path}'",flush=True,file=sys.stderr)
	# Replace single backslashes with double backslashes
	path = path.rstrip(os.linesep).strip('\r').strip('\n').strip()
	r1 = r'\\'
	r2 = r1 + r1
	r4 = r2 + r2
	path = path.replace(r1, r4)
	# Add double backslashes before any single backslashes
	for i in range(0,20):
		path = path.replace(r2, r1)
	if DEBUG:	print(f"DEBUG: normalize_path: outgoing path='{path}'",flush=True,file=sys.stderr)
	return path

#
def fully_qualified_directory_no_trailing_backslash(directory_name):
	# make into a fully qualified directory string stripped and without a trailing backslash
	# also remove extraneous backslashes which get added by things like abspath
	new_directory_name = os.path.abspath(directory_name).rstrip(os.linesep).strip('\r').strip('\n').strip()
	if directory_name[-1:] == (r'\ '.strip()):		# r prefix means the string is treated as a raw string so all escape codes will be ignored. EXCEPT IF THE \ IS THE LAST CHARACTER IN THE STRING !
		new_directory_name = directory_name[:-1]	# remove any trailing backslash
	new_directory_name = normalize_path(new_directory_name)
	return new_directory_name

#
def fully_qualified_filename(file_name):
	# Make into a fully qualified filename string using double backslashes
	# to later print/write with double backslashes use eg
	#	converted_string = fully_qualified_filename('D:\\a\\b\\\\c\\\\\\d\\e\\f\\filename.txt')
	#	print(repr(converted_string),flush=True,file=sys.stderr)
	# yields 'D:\\a\\b\\c\\d\\e\\f\\filename.txt'
	new_file_name = os.path.abspath(file_name).rstrip(os.linesep).strip('\r').strip('\n').strip()
	if new_file_name.endswith('\\'):
		new_file_name = new_file_name[:-1]  # Remove trailing backslash
	new_file_name = normalize_path(new_file_name)
	return new_file_name

#
def reconstruct_full_directory_only(incoming, default):
	# default is assumed to be a directory, any text in it treated as that and not a filename
	if incoming:
		#outgoing = os.path.normpath(incoming + '\\' if not incoming.endswith('\\') else '')
		incoming_abspath = os.path.abspath(incoming) + '\\' if not incoming.endswith('\\') else ''
		outgoing = os.path.normpath(incoming_abspath)
	else:
		default_abs_path = os.path.abspath(default) + '\\' if not default.endswith('\\') else ''
		outgoing = os.path.normpath(default_abs_path)
	# CRIICAL NOTE:  file=sys.stderr MUST be used in slideshow_LOAD_SETTINGS and not in slideshow_CONTROLLER !!
	if DEBUG:	print(f"DEBUG: reconstruct_full_directory_only: incoming='{incoming}' default='{default}' outgoing='{outgoing}'",flush=True,file=sys.stderr)
	return outgoing

#
def reconstruct_full_directory_and_filename(incoming, default_path, default_filename):
	# default is assumed to be a filename, any text in it treated as that and not a directory unless ending in \ (repr='\\')
	default_directory = reconstruct_full_directory_only(default_path, default_path)
	#print(f"{20*'%'}  reconstruct_full_directory_and_filename: incoming='{incoming}' default_path='{default_path}' default_filename='{default_filename}' default_directory='{default_directory}' default_filename='{default_filename}'",flush=True,file=sys.stderr)
	default_filename, default_extension = os.path.splitext(default_filename)
	if incoming:
		incoming_directory, incoming_filename = os.path.split(incoming)
		if incoming_directory:
			incoming_directory = reconstruct_full_directory_only(incoming_directory, incoming_directory)
		incoming_filename, incoming_extension = os.path.splitext(incoming_filename)
		directory = incoming_directory or default_directory
		filename = incoming_filename or default_filename
		extension = incoming_extension or default_extension
		outgoing = os.path.normpath(os.path.join(directory, filename + extension))
	else:
		outgoing = os.path.normpath(default_abs_path)
	# CRIICAL NOTE:  file=sys.stderr MUST be used in slideshow_LOAD_SETTINGS and not in slideshow_CONTROLLER !!
	if DEBUG:	print(f"DEBUG: reconstruct_full_directory_and_filename: incoming='{incoming}' default_path='{default_path}' default_filename='{default_filename}' outgoing='{outgoing}'",flush=True,file=sys.stderr)
	return outgoing

#
def format_duration_ms_to_hh_mm_ss_hhh(milliseconds):
	duration = datetime.timedelta(milliseconds=milliseconds)
	hours = duration.seconds // 3600
	minutes = (duration.seconds // 60) % 60
	seconds = duration.seconds % 60
	milliseconds = duration.microseconds // 1000
	return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

#
def get_random_ffindex_filename(path):
	# use the filename component of the incoming path and create a random fully qualified path into the temp folder
	# there is a significant to 100% chance of home picture/video filenames in directory trees being non-unique
	# apparently uuid4 has a good chance of returning a unique string
	global SETTINGS_DICT	# not set, just flagging that slideshow_LOAD_SETTINGS would have poked it into UTIL by now
	f = fully_qualified_filename(os.path.join(SETTINGS_DICT['TEMP_FOLDER'], os.path.basename(path) + r'_' + str(uuid.uuid4()) + r'.ffindex'))
	return f


#********************************************************************************************************
#********************************************************************************************************

#--------------------------------------------------------------------------------------------------------
# OK, IN THIS BLOCK WE HAVE FUNCTIONS TO GET A LOT OF IMAGE AND VIDEO METADATA
#--------------------------------------------------------------------------------------------------------

# https://mediaarea.net/download/binary/libmediainfo0/
# https://mediaarea.net/en/MediaInfo/Download/Windows
# download 64bit DLL without installer, unzip, find Media
# put MediaInfoDLL3.py in your directory (portable setup) or site-packages directory

# use mediainfo functions below like this:
#
# 'Encoded_Date': '2013-09-01 03:46:29 UTC',#
#	video_metadata_dict = video_extract_metadata_via_MEDIAINFO(file_path)
#	Encoded_Date  = datetime.strptime(video_metadata_dict["Encoded_Date"], "%Y-%m-%d %H:%M:%S").strftime("%Y_%m_%d_%H_%M_%S_%f")
# or
#	MI.Open(file_path)
#	mi_dict = {}
#	for param in mi_video_params_1:
#		value = video_mediainfo_value_worker(Stream.Video, track=0, param=param, path=path)
#		video_mediainfo_value_worker
#		mi_dict[param] = value	# any of str, bool, int, float, etc
#	MI.Close()
#	print(f'\n====================mi_dict=\n{objPrettyPrint.pformat(mi_dict)}',flush=True)

def video_mediainfo_value_worker(stream:int, track:int, param:str, path: Union[Path,str]) -> Union[int,float,str]:
	# Assume MI.Open(str(path)) has already occurred
	#global MI	# use the global, since we re-use it across functions
	if not stream in range(0,8):
		raise ValueError(f'ERROR: video_mediainfo_value_worker: stream must be a Stream attribute: General, Video, Audio, Text, Other, Image, Menu, Max')
	if not isinstance(track, int) or track<0:
		raise ValueError(f'ERROR: video_mediainfo_value_worker: track must be a positive integer')
	if not isinstance(param, str):
		raise ValueError(f'ERROR: video_mediainfo_value_worker: param must be a string for particular stream, ion_Static("Info_Parameters")')
	if not isinstance(path, (Path, str)):
		raise ValueError(f'ERROR: video_mediainfo_value_worker: path must be Path or str class')    
	#MI.Open(str(path)) # CHANGED: open/close in calling routine, allowing this to be called mutiple times
	str_value = MI.Get(stream, track, param)
	info_option =  MI.Get(stream, track, param, InfoKind=Info.Options)
	#MI.Close() 		# CHANGED: open/close in calling routine, allowing this to be called mutiple times
	if not str_value:
		return None
	if info_option:
		#returning a proper value type, int, float or str for particular parameter
		type_ = info_option[InfoOption.TypeOfValue] #type_=info_option[3] #_type will be 'I', 'F', 'T', 'D' or 'B'
		try:	# sometimes mediainfo flags an INT or a FLOAT which cannou be ocnverted, so catch those
			val = {'I':int, 'F':float, 'T':str, 'D':str, 'B':str}[type_](str_value)
		except Exception as err:
			#print_NORMAL(f'CONVERSION EXCEPTION ON val =["I":int, "F":float, "T":str, "D":str, "B":str][type_](str_value) ... type_="{type_}" param="{param}" str_value="{str_value}" path={path}')
			#print_NORMAL(f"Unexpected Error {err=}, {type(err)=}")
			val = None
			#raise
			pass
		return val
	else:
		raise ValueError(f'ERROR: video_mediainfo_value_worker: wrong parameter: "{param}" for given stream: {stream}')
#
def video_mediainfo_value(stream:int, track:int, param:str, path: Union[Path,str]) -> Union[int,float,str]:
	# A wrapper for video_mediainfo_value_worker, which gets and returns a single parameter
	# it opens and closes MI, unlike video_mediainfo_value_worker
	# This function permits video_mediainfo_value_worker to be recycled elsewhere to be called mutiple times per one single MI.open
	#global MI	# use the global, since we re-use it across functions
	if not stream in range(0,8):
		raise ValueError(f'ERROR: video_mediainfo_value: stream must be a Stream attribute: General, Video, Audio, Text, Other, Image, Menu, Max')
	if not isinstance(track, int) or track<0:
		raise ValueError(f'ERROR: video_mediainfo_value: track must be a positive integer')
	if not isinstance(param, str):
		raise ValueError(f'ERROR: video_mediainfo_value: param must be a string for particular stream, ion_Static("Info_Parameters")')
	if not isinstance(path, (Path, str)):
		raise ValueError(f'ERROR: video_mediainfo_value: path must be Path or str class')   
	MI.Open(str(path))
	val = video_mediainfo_value_worker(stream, track, param, path)
	MI.Close()
	return val
#
def video_extract_metadata_via_MEDIAINFO(file_path):
	#global MI					# use the global, since we re-use it across functions
	#global mi_video_params		# use the global, since we re-use it across functions
	if DEBUG: print(f"DEBUG: video_extract_metadata_via_MEDIAINFO: entered with file_path='{file_path}'.",flush=True)
	# ALWAYS include Width, Height, Rotation, Encoded_Date

	mi_dict = {}
	try:
		MI.Open(str(file_path))
	except Exception as e:
		#print(f"video_extract_metadata_via_MEDIAINFO: MediaInfo: Unexpected error getting information from file: '{file_path}'\n{str(e)}",flush=True,file=sys.stderr)
		return mi_dict
	for param in mi_video_params:
		#value = mediainfo_value(Stream.Video, track=0, param=param, path=file_path)	# version: single-value retrieval and lots of open/close
		value = video_mediainfo_value_worker(Stream.Video, track=0, param=param, path=file_path)
		video_mediainfo_value_worker
		mi_dict[param] = value	# any of str, bool, int, float, etc
	MI.Close()
	if DEBUG: print(f"Extracted MediaInfo metadata for file_path='{file_path}'\n{objPrettyPrint.pformat(mi_dict)}",flush=True)
	
	# Example dates from mediainfo:	'Recorded_Date': None, 'Encoded_Date': '2016-10-22 02:46:59 UTC'
	try:
		date_recorded = datetime.strptime(mi_dict["Recorded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	except:
		date_recorded = datetime.strptime(datetime.fromtimestamp(pathlib.Path(file_path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") # chatgpt and https://pynative.com/python-file-creation-modification-datetime/
		#print(f"DEBUG video_extract_metadata_via_MEDIAINFO: FILE DATEMODIFIED USED FOR date_recorded='{date_recorded}'",flush=True)
	try:
		date_encoded = datetime.strptime(mi_dict["Encoded_Date"], "%Y-%m-%d %H:%M:%S UTC")
	except:
		date_encoded = datetime.strptime(datetime.fromtimestamp(pathlib.Path(file_path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") # chatgpt and https://pynative.com/python-file-creation-modification-datetime/
		#print(f"DEBUG video_extract_metadata_via_MEDIAINFO: FILE DATEMODIFIED USED FOR date_encoded='{date_recorded}'",flush=True)
	rotation_flipping_dict = video_calculate_rotation_flipping(int(float(mi_dict["Rotation"])))
	rotation_positive_degrees = rotation_flipping_dict["clockwise_rotation_degrees"]
	width_before_rotation = int(float(mi_dict["Width"]))
	height_before_rotation = int(float(mi_dict["Height"]))
	tolerance_degrees = 0.9
	if abs(rotation_positive_degrees % 90) <= tolerance_degrees:
		if abs(rotation_positive_degrees % 180) <= tolerance_degrees:
			# Handle 180-degree rotation (no change in width/height which are integers)
			width_after_rotation = width_before_rotation
			height_after_rotation = height_before_rotation
		else:
			# Handle 90-degree rotation (width/height which are integers)
			width_after_rotation = height_before_rotation
			height_after_rotation = width_before_rotation
	else:
		# Convert the rotation degrees to radians
		rotation_radians = math.radians(rotation_positive_degrees)
		# Calculate the new width and height after rotation (width/height which are integers)
		width_after_rotation = int(math.ceil(abs(width_before_rotation * math.cos(rotation_radians)) + abs(height_before_rotation * math.sin(rotation_radians))))
		height_after_rotation = int(math.ceil(abs(width_before_rotation * math.sin(rotation_radians)) + abs(height_before_rotation * math.cos(rotation_radians))))
	mi_dict["calc_data"] = {
			"Date_Recorded": date_recorded,						# sometimes this is None
			"Date_Encoded": date_encoded,						# use this one
			"Rotation_Flipping": rotation_flipping_dict,
			"width_before_rotation": width_before_rotation,
			"height_before_rotation": height_before_rotation,
			"width_after_rotation": width_after_rotation,
			"height_after_rotation": height_after_rotation
	}
	#print(f'\n====================mi_dict=\n{objPrettyPrint.pformat(mi_dict)}',flush=True)
	return mi_dict

def video_calculate_rotation_flipping(rotation_degrees):
	# return a dict containing rotation related information, similar to that in image_calculate_rotation_flipping
	# ffprobe and mediainfo yield clockwise rotation as degrees, there appears to be no flipping involved
	# assume the incoming rotation value has been converted from string-float to int by: int(float(video_metadata_dict["Rotation"]))
	# sometimes negative rotation degree values have been seen in the wild, so convert them to positive clockwise rotations.
	# I have only ever seen video rotations in increments of 90 degrees, however allow for others
	#
	# https://www.vapoursynth.com/doc/functions/video/transpose.html
	# https://www.vapoursynth.com/doc/functions/video/flipvertical_fliphorizontal.html
	#
	positive_rotation = (360 + rotation_degrees) % 360	# calculates the positive rotation value in degrees based on a given rotation in degrees.
	return {
				'orientation_value': rotation_degrees,
				'clockwise_rotation_degrees': positive_rotation,
				'vertical_flips': 0,
				'horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': (360 - positive_rotation) % 360,
				'reversal_clockwise_rotation_degrees': (360 - positive_rotation) % 360,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 0
			}

#********************************************************************************************************

# use ffprobe class like this:
#
#	obj_ffprobe = ffprobe(file_path)
#	print(f'{objPrettyPrint.pformat(obj_ffprobe.dict)}',flush=True)	# to print everything. take care to notice stream indexing to correctly find your video stream metadata
#	encoded_date = obj_ffprobe.format_dict.get("Encoded_Date")	# 'Encoded_Date': '2013-09-01 03:46:29 UTC'
#	duration = obj_ffprobe.format_dict.get("duration")
#	rotation = obj_ffprobe.first_video.get("rotation")
#	r_frame_rate = obj_ffprobe.first_video.get("r_frame_rate")

class ffprobe:
	# This is a beaut class.
	# It uses ffprobe to query a media file and fetch into a dict as much metadata as it can find
	# Given the complexities of ffprobe streams and stream IDs (which are unique across video/audio/data streams),
	# this class makes it easier to find by also storing values for first_video and first_audio.
	# The native ffprobe tag names go straight into the dict so they always align with ffprobe querying
	#
	# For your convenience, it has  found the first video stream for you, eg obj_ffprobe.first_video.get("rotation")
	#						it also found the first audio stream for you, in obj_ffprobe.first_audio
	#
	# Usage:
	#	obj_ffprobe = UTIL.ffprobe(file_path)
	#	print(f'{objPrettyPrint.pformat(obj_ffprobe.dict)}',flush=True)	# take care to notice STREAM INDEXING to correctly find your specific video stream's metadata
	#	duration = obj_ffprobe.format_dict.get("duration")
	#	rotation = obj_ffprobe.first_video.get("rotation")
	#	r_frame_rate = obj_ffprobe.first_video.get("r_frame_rate")
	# 
	import os
	import sys
	import subprocess
	from pathlib import Path
	from typing import NamedTuple
	import json
	#
	def __init__(self, file_path):
		# Assume ffprobe.exe is in the current folder and/or path
		self.dict = {}
		self.format_dict = {}
		self.streams_list = []
		self.return_code = 0
		self.error_code = 0
		self.error = ''
		self.num_streams = 0
		self.num_video_streams = 0
		self.num_audio_streams = 0
		self.indices_video = None
		self.first_video_stream_pair = None
		self.first_video_stream_index = None
		self.first_video_list_index = None
		self.indices_audio = None
		self.first_audio_stream_pair = None
		self.first_audio_stream_index = None
		self.first_audio_list_index = None
		self.first_video = {}
		self.first_audio = {}
		command_array =	[ FFPROBE_EXE, "-hide_banner", "-v", "quiet", "-print_format", "json", "-show_programs", "-show_format", "-show_streams", "-show_private_data", file_path ]
		#
		e = 0
		try:
			result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		except Exception as e:
			print(f"CONTROLLER: ffprobe.exe failed to run on '{file_path}', with error: '{result.stderr}'", file=sys.stderr, flush=True)
			self.return_code = result.returncode
			self.error_code = e
			self.error = result.stderr
			return
		#
		self.return_code = result.returncode
		self.error_code = e
		self.error = result.stderr
		try:
			self.dict = json.loads(result.stdout)
		except:
			print(f'CONTROLLER: ffprobe: ERROR: {file_path} loading ffprobe "json" data. json=\n{objPrettyPrint.pformat(self.streams_list)}', file=sys.stderr, flush=True)
			self.dict = {}
			pass
		self.format_dict = self.dict.get("format")
		if self.format_dict is None:
			print(f'CONTROLLER: ffprobe: ERROR: {file_path} contains no ffprobe "format" data. json=\n{objPrettyPrint.pformat(self.streams_list)}', file=sys.stderr, flush=True)
			self.format_dict = {}
			pass
		self.streams_list = self.dict.get("streams")
		if self.streams_list is None:
			print(f'CONTROLLER: ffprobe: ERROR: {file_path} contains no ffprobe "streams" data. json=\n{objPrettyPrint.pformat(self.streams_list)}', file=sys.stderr, flush=True)
			self.streams_list = []
			pass
		else:
			# determine the first video stream indexes
			self.indices_video  = [ {"list_index" : i, "stream_index" : _streams["index"] } for i, _streams in enumerate(self.streams_list) if _streams["codec_type"].lower() == "video".lower()]
			self.num_video_streams = len(self.indices_video)
			if self.num_video_streams > 0:
				self.first_video_stream_pair = min(self.indices_video, key=lambda x: x["stream_index"])
				self.first_video_list_index = self.first_video_stream_pair["list_index"]
				self.first_video_stream_index = self.first_video_stream_pair["stream_index"]
				self.streams_list[self.first_video_list_index]["color_matrix"] = self.streams_list[self.first_video_list_index].get("color_space")	# NOT LIKE MEDIAINFO !!! color_matrix is in ff field "color_space" (instances of it show bt2020nc which is a matrix name).
				self.first_video = self.streams_list[self.first_video_list_index]
				self.first_video["displaymatrix"] = None
				self.first_video["rotation"] = 0
				sdl = self.first_video.get("side_data_list")
				#	'side_data_list':	[
				#		{	'side_data_type': 'Display Matrix',
				#			'displaymatrix':	'00000000:            0       65536           0'
				#								'00000001:       -65536           0           0'
				#								'00000002:     31457280           0  1073741824',
				#			'rotation': -90
				#		}
				#						]
				if sdl is not None:
					for v in sdl:	# iterate the side data list if it exists; v is an item from the list which "should" be a dict for display matrix
						try:
							dm = v.get("displaymatrix")
							rot = v.get("rotation")
						except:
							dm = None
						if dm is not None:
							self.first_video["displaymatrix"] = dm.replace('\n',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').strip()
						if rot is not None:
							self.first_video["rotation"] = rot		# rot is the video rotation integer, which may be negative
			# determine the first audio stream indexes
			self.indices_audio = [ {"list_index" : i, "stream_index" : _streams["index"] } for i, _streams in enumerate(self.streams_list) if _streams["codec_type"].lower() == "audio".lower()]
			self.num_audio_streams = len(self.indices_audio)
			if self.num_audio_streams > 0:
				self.first_audio_stream_pair = min(self.indices_audio, key=lambda x: x["stream_index"])
				self.first_audio_list_index = self.first_audio_stream_pair["list_index"]
				self.first_audio_stream_index = self.first_audio_stream_pair["stream_index"]
				self.first_audio = self.streams_list[self.first_audio_list_index]
		self.num_streams = self.num_video_streams + self.num_audio_streams
		# return with the dict and codes filled in
		del command_array, e, result
		return

#********************************************************************************************************

def image_get_metadata_via_PIL(image_path):
	with Image.open(image_path) as image:
		exif_data = image._getexif()
		if exif_data is None:
			date_recorded = datetime.strptime(datetime.fromtimestamp(pathlib.Path(image_path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")	# chatgpt and https://pynative.com/python-file-creation-modification-datetime/
			#print(f"DEBUG image_get_metadata_via_PIL: no exif_data, FILE DATEMODIFIED WILL BE USED FOR date_recorded='{date_recorded}'",flush=True)
			return {
				"Date_Recorded": date_recorded,
				"Rotation_Flipping": {	'exif_orientation_value': 1,
										'exif_clockwise_rotation_degrees': 0,
										'exif_vertical_flips': 0,
										'exif_horizontal_flips': 0,
										'reversal_absolute_clockwise_rotation_degrees': 0,
										'reversal_clockwise_rotation_degrees': 0,
										'reversal_vertical_flips': 0,
										'reversal_horizontal_flips': 0
									},
				"width_before_rotation": image.width,
				"height_before_rotation": image.height,
				"width_after_rotation": image.width,
				"height_after_rotation": image.height
			}
		# fetch and calculate the exif data
		date_recorded = image_get_date_recorded_from_exif(image_path, exif_data)
		rotation_flipping_dict = image_calculate_rotation_flipping(exif_data)
		width_before_rotation = image.width
		height_before_rotation = image.height
		# Calculate width and Height_after_rotation (if rotation is applied)
		if rotation_flipping_dict["exif_clockwise_rotation_degrees"] == 90 or rotation_flipping_dict["exif_clockwise_rotation_degrees"] == 270:
			width_after_rotation = height_before_rotation
			height_after_rotation = width_before_rotation
		else:
			width_after_rotation = width_before_rotation
			height_after_rotation = height_before_rotation

		return {
			"Date_Recorded": date_recorded,
			"Rotation_Flipping": rotation_flipping_dict,
			"width_before_rotation": width_before_rotation,
			"height_before_rotation": height_before_rotation,
			"width_after_rotation": width_after_rotation,
			"height_after_rotation": height_after_rotation
		}

def image_get_date_recorded_from_exif(image_path, exif_data):
	date_tag = 36867  # Exif tag for DateTimeOriginal
	date_recorded = None
	if date_tag in exif_data:
		date_recorded = exif_data[date_tag]
		try:
			date_recorded = datetime.strptime(date_recorded, "%Y:%m:%d %H:%M:%S")	#.strftime("%Y_%m_%d_%H_%M_%S_%f")
		except:
			date_recorded = None
	if date_recorded == None:	# attempt to get the file date-modified
		# chatgpt and https://pynative.com/python-file-creation-modification-datetime/
		date_recorded = datetime.strptime(datetime.fromtimestamp(pathlib.Path(image_path).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S") # chatgpt and https://pynative.com/python-file-creation-modification-datetime/
		#print(f"DEBUG image_get_date_recorded_from_exif: FILE DATEMODIFIED USED FOR date_recorded='{date_recorded}'",flush=True)
	#print(f"DEBUG image_get_date_recorded_from_exif: date_recorded='{date_recorded}'",flush=True)
	return date_recorded

def image_calculate_rotation_flipping(exif_data):
	# https://www.vapoursynth.com/doc/functions/video/transpose.html
	# https://www.vapoursynth.com/doc/functions/video/flipvertical_fliphorizontal.html
	# https://sirv.com/help/articles/rotate-photos-to-be-upright/
	#	Exif Orientation values 1,3,6,8 have no flipping, 2,4,5,7 involve flipping as well as rotations.
	#	Orientation Value: 1
	#		Rotation Angle: 0 degrees (no rotation)
	#	Orientation Value: 2
	#		Rotation Angle: 0 degrees (no rotation) + Horizontal flip
	#	Orientation Value: 3
	#		Rotation Angle: 180 degrees clockwise rotation
	#	Orientation Value: 4
	#		Rotation Angle: 180 degrees clockwise rotation + Horizontal flip
	#	Orientation Value: 5
	#		Rotation Angle: 90 degrees clockwise rotation + Horizontal flip
	#	Orientation Value: 6
	#		Rotation Angle: 270 degrees clockwise rotation
	#	Orientation Value: 7
	#		Rotation Angle: 270 degrees clockwise rotation + Horizontal flip
	#	Orientation Value: 8
	#		Rotation Angle: 90 degrees clockwise rotation	
	#
	#	Therefore, the optimal REVERSAL rotation and flip values for each orientation are as follows:
	#	Orientation Value: 1
	#		Optimal Rotation: No rotation
	#		Optimal Flip: No flip
	#		ABSOLUTE REVERSAL ROTATION:  No rotation
	#	Orientation Value: 2
	#		Optimal Rotation: 0 degrees clockwise rotation
	#		Optimal Flip: Horizontal flip  ** MUST FLP
	#		ABSOLUTE REVERSAL ROTATION:  0
	#	Orientation Value: 3
	#		Optimal Rotation: 180 degrees clockwise rotation
	#		Optimal Flip: No flip
	#		ABSOLUTE REVERSAL ROTATION: 180 degrees clockwise rotation
	#	Orientation Value: 4
	#		Optimal Rotation: 0 degrees clockwise rotation
	#		Optimal Flip: Vertical flip	 ** MUST FLP
	#		ABSOLUTE REVERSAL ROTATION: 0
	#	Orientation Value: 5
	#		Optimal Rotation: 90 degrees clockwise rotation
	#		Optimal Flip: Horizontal flip  ** MUST FLIP
	#		ABSOLUTE REVERSAL ROTATION: 0
	#	Orientation Value: 6
	#		Optimal Rotation: 90 degrees clockwise rotation
	#		Optimal Flip: No flip
	#		ABSOLUTE REVERSAL ROTATION: 90 degrees clockwise rotation
	#	Orientation Value: 7
	#		Optimal Rotation: 90 degrees clockwise rotation
	#		Optimal Flip: Vertical flip  ** MUST FLP
	#		ABSOLUTE REVERSAL ROTATION: 0
	#	Orientation Value: 8
	#		Optimal Rotation: 270 degrees clockwise rotation
	#		Optimal Flip: No flip
	#		ABSOLUTE REVERSAL ROTATION: 270 degrees clockwise rotation
	#
	exif_orientation_value = 1
	if hasattr(exif_data, '__getitem__'):
		exif_orientation_value = exif_data.get(0x0112)
		if exif_orientation_value == 1:		# Rotation Angle: 0 degrees (no rotation). Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 0,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 0,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 0
			}
		elif exif_orientation_value == 2:	# Rotation Angle: 0 degrees (no rotation) + Horizontal flip. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 0,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 1,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 0,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 1
			}
		elif exif_orientation_value == 3:	# Rotation Angle: 180 degrees clockwise rotation. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 180,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': 180,
				'reversal_clockwise_rotation_degrees': 0,
				'reversal_vertical_flips': 1,
				'reversal_horizontal_flips': 1
			}
		elif exif_orientation_value == 4:	# Rotation Angle: 180 degrees clockwise rotation + Horizontal flip. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 180,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 1,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 0,
				'reversal_vertical_flips': 1,
				'reversal_horizontal_flips': 0
			}
		elif exif_orientation_value == 5:	# Rotation Angle: 90 degrees clockwise rotation + Horizontal flip. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 90,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 1,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 90,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 1
			}
		elif exif_orientation_value == 6:	# Rotation Angle: 270 degrees clockwise rotation. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 270,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': 90,
				'reversal_clockwise_rotation_degrees': 90,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 0
			}
		elif exif_orientation_value == 7:	# Rotation Angle: 270 degrees clockwise rotation + Horizontal flip. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 270,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 1,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 90,
				'reversal_vertical_flips': 1,
				'reversal_horizontal_flips': 0
			}
		elif exif_orientation_value == 8:	# Rotation Angle: 90 degrees clockwise rotation. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 90,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': 270,
				'reversal_clockwise_rotation_degrees': 270,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 0
			}
		else: # unknown exif value, assume no rotation and no flipping. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
			return {
				'exif_orientation_value': exif_orientation_value,
				'exif_clockwise_rotation_degrees': 0,
				'exif_vertical_flips': 0,
				'exif_horizontal_flips': 0,
				'reversal_absolute_clockwise_rotation_degrees': 0,
				'reversal_clockwise_rotation_degrees': 0,
				'reversal_vertical_flips': 0,
				'reversal_horizontal_flips': 0
			} 
	return {  # no exif data, assume no rotation and no flipping. Exif Orientation values 1,3,6,8 have no flipping, 2.4.5.7 involve flipping as well as rotations.
		'exif_orientation_value': 1,
		'exif_clockwise_rotation_degrees': 0,
		'exif_vertical_flips': 0,
		'exif_horizontal_flips': 0,
		'reversal_absolute_clockwise_rotation_degrees': 0,
		'reversal_clockwise_rotation_degrees': 0,
		'reversal_vertical_flips': 0,
		'reversal_horizontal_flips': 0
	}
