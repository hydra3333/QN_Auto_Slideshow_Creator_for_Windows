# Public Domain software: vs_transitions
#		https://github.com/OrangeChannel/vs-transitions
# vs-transitions SOURCE CODE:
#		https://raw.githubusercontent.com/OrangeChannel/vs-transitions/master/vs_transitions/__init__.py
# vs-transitions DOCUMENTATION:
#		https://vapoursynth-transitions.readthedocs.io/en/latest/api.html
#
"""Powerpoint-like transitions implemented in VapourSynth."""
##################################################################################################################################################################################################################################################################################################
import sys
from datetime import datetime, date, time, timezone
import enum
import math
from fractions import Fraction
from typing import Callable, Optional, Tuple, TYPE_CHECKING
import gc	# for inbuilt garbage collection
import vapoursynth as vs
#from vapoursynth import core
core = vs.core
#core.num_threads=1
##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
class Direction(str, enum.Enum):
	"""Direction enumeration.
	Members can be simply referenced by their names,
	i.e. ``vs_transitions.LEFT`` instead of ``vs_transitions.Direction.LEFT``.
	"""
	LEFT = "left"
	RIGHT = "right"
	UP = "up"
	DOWN = "down"
	HORIZONTAL = "horizontal"
	VERTICAL = "vertical"

class MiscConstants(str, enum.Enum):
	"""Miscellanious enumeration for some functions.

	Members can be simply referenced by their names,
	i.e. ``vs_transitions.SLIDE`` instead of ``vs_transitions.MiscConstants.SLIDE``.
	"""

	SLIDE = "slide"
	SQUEEZE = "squeeze"
	EXPAND = "expand"
##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
IS_DEBUG = False
##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
try:
	from ._metadata import __author__, __date__, __version__  # type: ignore
except (ImportError, ModuleNotFoundError):
	__author__ = __date__ = __version__ = "unknown (portable version)"  # type: ignore

ID = 0	# removed from al lcalls/defs 2023.03.28 
__all__ = [
	"cover",
	"cube_rotate",
	"curtain_cover",
	"curtain_reveal",
	"fade",
	"fade_from_black",
	"fade_to_black",
	"linear_boundary",
	"poly_fade",
	"push",
	"reveal",
	"slide_expand",
	"squeeze_expand",
	"squeeze_slide",
	"wipe",
]
LEFT = Direction.LEFT
RIGHT = Direction.RIGHT
UP = Direction.UP
DOWN = Direction.DOWN
HORIZONTAL = Direction.HORIZONTAL
VERTICAL = Direction.VERTICAL
__all__ += list(Direction.__members__)
SLIDE = MiscConstants.SLIDE
SQUEEZE = MiscConstants.SQUEEZE
EXPAND = MiscConstants.EXPAND
__all__ += list(MiscConstants.__members__)
##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
def print_DEBUG(*args, **kwargs):	# PRINT TO stderr
	# per https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
	if IS_DEBUG:
		right_now = datetime.now().strftime('%Y-%m-%d.%H:%M:%S.%f')
		print(f'{right_now} DEBUG:', *args, **kwargs, file=sys.stderr, flush=True)
	return
def print_NORMAL(*args, **kwargs):	# PRINT TO stderr
	# per https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
	right_now = datetime.now().strftime('%Y-%m-%d.%H:%M:%S.%f')
	print(f'{right_now}', *args, **kwargs, file=sys.stderr, flush=True)
	return
##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
def raise_ValueError_wrapper(reason:str):	# print the error as well as raising the error.  yes I know it duplicates but I'm having trouble with vspipe error messages disappearing and want to see if this works
	#print_DEBUG(f'vs_transitions: Entered raise_ValueError_wrapper')	### THIS IS FOR ONLY DURING DEVELOPMENT
	#print_NORMAL(reason)												### THIS IS FOR ONLY DURING DEVELOPMENT
	#raise ValueError('raise_ValueError_wrapper: ' + reason)			### THIS IS FOR ONLY DURING DEVELOPMENT
	raise ValueError(reason)			### THIS IS FOR ONLY DURING DEVELOPMENT
	sys.exit(1)	# force exception handling cleanup and exit if raise ValueError does not abort ...

def garbage_collect():
	#print_DEBUG(f'vs_transitions: ---------- Entered garbage_collect')
	try:
		num_unreachable_objects = gc.collect()
		if num_unreachable_objects > 0:
			#print_DEBUG(f'vs_transitions: garbage_collect: *** GARBAGE_COLLECTION: number of unreachable objects found={num_unreachable_objects}')
			pass
		del num_unreachable_objects
		return
	except Exception as e:
		raise ValueError(f'vs_transitions: garbage_collect: ERROR: unknown error occurred at high level try/except:\n{e}\n{type(e)}\n{str(e)}')

def check_clips_preStack_and_abort(list_of_clips:list, abort=False):
	#print_DEBUG(f'vs_transitions: Entered check_clips_preStack_and_abort')
	try:
		# a few calls to vs_transitions are returning errors
		# apparently from inconsistent clips sizes given to StackHorizontal and StackVertical
		length_list_of_clips = len(list_of_clips)
		if length_list_of_clips <= 1:
			return
		W0 = list_of_clips[0].width
		H0 = list_of_clips[0].height
		F0 = list_of_clips[0].format
		L0 = len(list_of_clips[0])
		for i in range(1,length_list_of_clips):	# base 0, so 1 starts at second list entry
			if list_of_clips[i].width != W0 or list_of_clips[0].height != H0:
				if abort:
					print_NORMAL(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: unmatched clip dimensions clip[0] width/height={W0}/{H0} clip[{i}] width/height={list_of_clips[i].width}/{list_of_clips[i].height}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
					raise ValueError(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: unmatched clip dimensions clip[0] width/height={W0}/{H0} clip[{i}] width/height={list_of_clips[i].width}/{list_of_clips[i].height}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
				else:
					print_DEBUG(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: NOTE: unmatched clip dimensions clip[0] width/height={W0}/{H0} clip[{i}] width/height={list_of_clips[i].width}/{list_of_clips[i].height}')
					pass
			if list_of_clips[i].format != F0:
				if abort:
					print_NORMAL(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: inconsistent clip formats clip[0] format={F0} clip[{i}] format={list_of_clips[i].format}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
					raise ValueError(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: inconsistent clip formats clip[0] format={F0} clip[{i}] format={list_of_clips[i].format}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
				else:
					print_DEBUG(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: WARNING: inconsistent clip formats clip[0] format={F0} clip[{i}] format={list_of_clips[i].format}')
					pass
			if len(list_of_clips[i]) != L0:
				if abort:
					print_NORMAL(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: inconsistent clip lengths clip[0] length={L0} clip[{i}] length={len(list_of_clips[i])}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
					raise ValueError(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: inconsistent clip lengths clip[0] length={L0} clip[{i}] length={len(list_of_clips[i])}\nclip[0]={list_of_clips[0]}\nclip[{i}={list_of_clips[i]}')
				else:
					print_DEBUG(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: WARNING: inconsistent clip lengths clip[0] length={L0} clip[{i}] length={len(list_of_clips[i])}')
					pass
		return
	except Exception as e:
		print_NORMAL(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: unknown error occurred at high level try/except:\n{e}\n{type(e)}\n{str(e)}')
		raise ValueError(f'vs_transitions: check_clips_preStack_and_abort: ID={ID}: ERROR: unknown error occurred at high level try/except:\n{e}\n{type(e)}\n{str(e)}')

def print_stack_clips_list_properties(caller: Callable, list_of_clips:list, debug=False):
	e = f'vs_transitions: Entered print_stack_clips_list_properties -  ID={ID} - USUALLY TO DUMP A LIST OF CLIPS AFTER AN ERROR WAS DETECTED BY "{caller.__name__}"'
	if debug:
		print_DEBUG(e)
	else:
		print_NORMAL(e)
	length_list_of_clips = len(list_of_clips)
	if length_list_of_clips <= 0:
		return
	for i in range(0,length_list_of_clips):
		try:
			clip_properties = f'vs_transitions: print_stack_clips_list_properties {caller.__name__}: ID={ID}: clip[{i}] of {length_list_of_clips-1} (base 0) format="{list_of_clips[i].format.name}" WxH={list_of_clips[i].width}x{list_of_clips[i].height} num_frames={list_of_clips[i].num_frames} fps={list_of_clips[i].fps}'	#  \n{list_of_clips[i]}'
			if debug:
				print_DEBUG(clip_properties)
			else:
				print_NORMAL(clip_properties)
		except Exception as e:
			print_NORMAL(f'vs_transitions: print_stack_clips_list_properties: EXCEPTION: {caller.__name__}: ID={ID}: ERROR: failed to find/print characteristics clip[{i}] of {length_list_of_clips-1} (base 0)')
			raise ValueError(f'vs_transitions: print_stack_clips_list_properties: EXCEPTION: {caller.__name__}: ID={ID}: ERROR: failed to find/print characteristics clip[{i}] of {length_list_of_clips-1} (base 0) \n{e}\n{type(e)}\n{str(e)}')
	return

def StackHorizontal_wrapper(list_of_clips:list) -> vs.VideoNode:
	#print_DEBUG(f'vs_transitions: *** Entered StackHorizontal_wrapper ID={ID}')
	c = core.std.StackHorizontal(list_of_clips)	# the real StackHorizontal
	return c
	### THIS IS FOR ONLY DURING DEVELOPMENT
	###try:
	###	check_clips_preStack_and_abort(list_of_clips, abort=False)	### THIS IS FOR ONLY DURING DEVELOPMENT
	###	try:
	###		c = core.std.core.std.StackHorizontal(list_of_clips)	# the real StackHorizontal
	###	except Exception as e:
	###		print_stack_clips_list_properties(StackHorizontal_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackHorizontal_wrapper: ERROR: StackHorizontal_wrapper ID={ID} error:\n{e}\n{type(e)}\n{str(e)}')
	###	if not isinstance(c, vs.VideoNode):
	###		print_stack_clips_list_properties(StackHorizontal_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackHorizontal_wrapper: ERROR: StackHorizontal_wrapper ID={ID} did not return a type vs.VideoNode video clip')
	###	elif len(c) <= 0:
	###		print_stack_clips_list_properties(StackHorizontal_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackHorizontal_wrapper: ERROR: StackHorizontal_wrapper ID={ID} returned a zero length video clip')
	###	return c
	###except Exception as e:
	###	print_stack_clips_list_properties(StackHorizontal_wrapper, list_of_clips, debug=False)
	###	raise ValueError(f'vs_transitions: StackHorizontal_wrapper: ID={ID} ERROR: unknown error occurred at high level try/except:\n{e}\n{type(e)}\n{str(e)}')
	
def StackVertical_wrapper(list_of_clips:list) -> vs.VideoNode:
	#print_DEBUG(f'vs_transitions: *** Entered StackVertical_wrapper ID={ID}')
	c = core.std.StackVertical(list_of_clips)	# the real StackVertical
	return c
	### THIS IS FOR ONLY DURING DEVELOPMENT
	###try:
	###	check_clips_preStack_and_abort(list_of_clips, abort=False)	### THIS IS FOR ONLY DURING DEVELOPMENT
	###	try:
	###		c = core.std.core.std.StackVertical(list_of_clips)	# the real StackVertical
	###	except Exception as e:
	###		print_stack_clips_list_properties(StackVertical_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackVertical_wrapper: ERROR: StackVertical_wrapper ID={ID} error:\n{e}\n{type(e)}\n{str(e)}')
	###	if not isinstance(c, vs.VideoNode):
	###		print_stack_clips_list_properties(StackVertical_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackVertical_wrapper: ERROR: StackVertical_wrapper ID={ID} did not return a type vs.VideoNode video clip')
	###	elif len(c) <= 0:
	###		print_stack_clips_list_properties(StackVertical_wrapper, list_of_clips, debug=False)
	###		raise ValueError(f'vs_transitions: StackVertical_wrapper: ERROR: StackVertical_wrapper ID={ID} returned a zero length video clip')
	###	return c
	###except Exception as e:
	###	print_stack_clips_list_properties(StackVertical_wrapper, list_of_clips, debug=False)
	###	raise ValueError(f'vs_transitions: StackVertical_wrapper: ID={ID} ERROR: unknown error occurred at high level try/except:\n{e}\n{type(e)}\n{str(e)}')

##################################################################################################################################################################################################################################################################################################

##################################################################################################################################################################################################################################################################################################
def _check_clips(frames: int, caller: Callable, *clips: vs.VideoNode, **kwargs) -> None:
	"""General checker for clip formats, resolutions, length, and other keywords.

	Possible kwargs:
		'subsampling': checks that all clips have 444 subsampling for resize purposes
	"""
	#print_DEBUG(f'vs_transitions: Entered _check_clips ID={ID}')
	if frames <= 0:
		raise ValueError(f"{caller.__name__}: ID={ID} `frames` cannot be less than 1")
	same_check = set()
	for clip in clips:
		if clip.format is None:
			raise ValueError(f"{caller.__name__}: ID={ID} all clips must be constant-format")
		if 0 in (clip.width, clip.height):
			raise ValueError(f"{caller.__name__}: ID={ID} all clips must be constant-resolution")
		if clip.num_frames < frames:
			raise ValueError(f"{caller.__name__}: ID={ID} all clips must have at least {frames} frames")
		same_check.add((clip.format.id, clip.width, clip.height))

		if kwargs:
			if ("subsampling" in kwargs) and kwargs["subsampling"]:
				if clip.format.subsampling_w != 0 or clip.format.subsampling_h != 0:
					raise ValueError(
						f"{caller.__name__}: ID={ID} all clips must have 444 chroma subsampling for a non-mod2 resize"
					)

	if len(same_check) > 1:
		raise ValueError(f"{caller.__name__}: ID={ID} all clips must be same format and resolution")
		pass


def _return_combo(
	clip1: Optional[vs.VideoNode],
	clip_middle: vs.VideoNode,
	clip2: Optional[vs.VideoNode],
) -> vs.VideoNode:
	"""Prevents splicing empty clips.

	:param clip1:		optional start clip
	:param clip_middle:  mandatory middle clip
	:param clip2:		optional ending clip
	:return: splice of existing clips in order
	"""
	#print_DEBUG(f'vs_transitions: Entered _return_combo ID={ID}: ')
	if clip1 is not None and clip2 is not None:
		return clip1 + clip_middle + clip2
	elif clip1 is not None and clip2 is None:
		return clip1 + clip_middle
	elif clip1 is None and clip2 is not None:
		return clip_middle + clip2
	elif clip1 is None and clip2 is None:
		return clip_middle


def _transition_clips(
	clip1: vs.VideoNode, clip2: vs.VideoNode, frames: int
) -> Tuple[Optional[vs.VideoNode], Optional[vs.VideoNode], vs.VideoNode, vs.VideoNode]:
	"""Returns clean (non-transition) and transition sections of the given clips based on frames."""
	#print_DEBUG(f'vs_transitions: Entered _transition_clips ID={ID}: ')
	if clip1.num_frames == frames:
		clip1_t_zone = clip1
		clip1_clean = None
	else:
		clip1_t_zone = clip1[-frames:]
		clip1_clean = clip1[:-frames]

	if clip2.num_frames == frames:
		clip2_t_zone = clip2
		clip2_clean = None
	else:
		clip2_t_zone = clip2[:frames]
		clip2_clean = clip2[frames:]

	return clip1_clean, clip2_clean, clip1_t_zone, clip2_t_zone


def add_together(clipa: vs.VideoNode, clipb: vs.VideoNode) -> vs.VideoNode:
	"""Just add clips together.
		Result will be twice as long as with merged clips
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered add_together ID={ID}')
	frames_ = min(1, clipa.num_frames, clipb.num_frames)
	_check_clips(frames_, add_together, clipa, clipb)
	return clipa + clipb


def fade(clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None) -> vs.VideoNode:
	"""Cross-fade clips."""
	#print_DEBUG(f'vs_transitions: ---------- Entered fade ID={ID}')
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, fade, clipa, clipb)
	clipa_clean, clipb_clean, clipa_fade_zone, clipb_fade_zone = _transition_clips(clipa, clipb, frames_)

	def _fade(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _fade ID={ID}')
		progress = Fraction(n, frames_ - 1)
		if progress == 0:
			return clipa_fade_zone
		elif progress == 1:
			return clipb_fade_zone
		else:
			return core.std.Merge(
				clipa_fade_zone,
				clipb_fade_zone,
				weight=[float(progress)],
			)

	faded = core.std.FrameEval(clipa_fade_zone, _fade)

	return _return_combo(clipa_clean, faded, clipb_clean)


def poly_fade(
	clipa: vs.VideoNode,
	clipb: vs.VideoNode,
	frames: Optional[int] = None,
	exponent: int = 1,
) -> vs.VideoNode:
	"""Cross-fade clips according to a curve.

	:param exponent: An integer in the range from 1-5 (inclusive)
		where 1 represents a parabolic curve, 2 represents a quartic curve,
		and higher powers more resembling an tight ease-in-out function with constant speed for most of the transition.

		An `exponent` of ``1`` is probably most useful,
		as higher exponents tend towards a constant speed and therefore are
		almost indistinguishable from a normal :func:`fade`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered poly_fade ID={ID}')
	if not (1 <= exponent <= 5):
		raise ValueError("poly_fade: exponent must be an int between 1 and 5 (inclusive)")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, fade, clipa, clipb)
	clipa_clean, clipb_clean, clipa_fade_zone, clipb_fade_zone = _transition_clips(clipa, clipb, frames_)

	def get_pos(x: Fraction) -> Fraction:
		#print_DEBUG(f'vs_transitions: Entered get_pos ID={ID}')
		"""Returns position as a fractions.Fraction, based on a input percentage fractions.Fraction"""

		def _curve(y: Fraction) -> Fraction:
			#print_DEBUG(f'vs_transitions: Entered _curve ID={ID}')
			return -(((2 * y - 1) ** (2 * exponent + 1)) / (4 * exponent + 2)) + y - Fraction(1, 2)

		return ((_curve(Fraction(1, 1)) - _curve(Fraction())) ** -1) * (_curve(x) - _curve(Fraction()))

	def _fade(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _fade ID={ID}')
		progress = Fraction(n, frames_ - 1)
		if progress == 0:
			return clipa_fade_zone
		elif progress == 1:
			return clipb_fade_zone
		else:
			return core.std.Merge(clipa_fade_zone, clipb_fade_zone, weight=[float(get_pos(progress))])

	faded = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _fade)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, faded, clipb_clean)


def fade_to_black(src_clip: vs.VideoNode, frames: Optional[int] = None) -> vs.VideoNode:
	"""Simple convenience function to :func:`fade` a clip to black.

	`frames` will be the number of frames consumed from the end of the `src_clip` during the transition.
	The first frame of the transition will be the first frame of the `src_clip`,
	while the last frame of the transition will be a pure black frame.

	If `frames` is not given, will fade to black over the entire duration of the `src_clip`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered fade_to_black ID={ID}')
	if src_clip.format is None:
		raise ValueError("fade_to_black: `src_clip` must be a constant format VideoNode")
	black_clip = core.std.BlankClip(clip=clip, format=vs.GRAY8, length=frames, color=[0])	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly
	if TYPE_CHECKING:
		assert black_clip.format is not None
		assert src_clip.format is not None
	black_clip_resized = black_clip.resize.Point(
		width=src_clip.width,
		height=src_clip.height,
		format=black_clip.format.replace(
			color_family=src_clip.format.color_family,
			sample_type=src_clip.format.sample_type,
			bits_per_sample=src_clip.format.bits_per_sample,
			subsampling_w=src_clip.format.subsampling_w,
			subsampling_h=src_clip.format.subsampling_h,
		).id,
	)
	return fade(src_clip, black_clip_resized, frames)


def fade_from_black(src_clip: vs.VideoNode, frames: Optional[int] = None) -> vs.VideoNode:
	"""Simple convenience function to :func:`fade` a clip into view from black.

	`frames` will be the number of frames consumed from the start of the `src_clip` during the transition.
	The first frame of the transition will be a pure black frame,
	while the last frame of the transition will be the last frame of the `src_clip`.

	If `frames` is not given, will fade in over the entire duration of the `src_clip`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered fade_from_black ID={ID}')
	if src_clip.format is None:
		raise ValueError("fade_to_black: `src_clip` must be a constant format VideoNode")
	black_clip = core.std.BlankClip(clip=clip, format=vs.GRAY8, length=frames, color=[0])	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly
	if TYPE_CHECKING:
		assert black_clip.format is not None
		assert src_clip.format is not None
	black_clip_resized = black_clip.resize.Point(
		width=src_clip.width,
		height=src_clip.height,
		format=black_clip.format.replace(
			color_family=src_clip.format.color_family,
			sample_type=src_clip.format.sample_type,
			bits_per_sample=src_clip.format.bits_per_sample,
			subsampling_w=src_clip.format.subsampling_w,
			subsampling_h=src_clip.format.subsampling_h,
		).id,
	)
	return fade(black_clip_resized, src_clip, frames)


def wipe(
	clipa: vs.VideoNode,
	clipb: vs.VideoNode,
	frames: Optional[int] = None,
	direction: Direction = Direction.LEFT,
) -> vs.VideoNode:
	"""A moving directional fade.

	Similar to a :func:`fade`, but with a moving mask.
	The `direction` will be the direction the fade progresses towards.
	(i.e. the second clip begins fading in from the **opposite** given direction,
	and the first clip begins fading out starting from the **opposite** given direction,
	progressing towards `direction`)

	Uses a pure white to black gradient for the fade.
	If possible, uses `numpy <https://pypi.org/project/numpy/>`_ to generate the mask.
	If the numpy module is not found, falls back to a slower
	and possibly less accurate approach using lists
	and the ``ctypes`` module for writing to a VapourSynth frame.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered wipe ID={ID} direction={direction}')
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("wipe: give a proper direction")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, wipe, clipa, clipb)
	clipa_clean, clipb_clean, clipa_wipe_zone, clipb_wipe_zone = _transition_clips(clipa, clipb, frames_)

	blank_clip = core.std.BlankClip(clip=clipa, width=1 << 16, height=1, format=vs.GRAYS, color=[0.0], length=1)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly
	write_frame = blank_clip.get_frame(0).copy()
	try:
		import numpy as np

		def frame_writer(n, f):
			#print_DEBUG(f'vs_transitions: Entered frame_writer ID={ID} direction={direction}')
			if n is not None:
				pass
			fout = f.copy()
			#ptr = np.asarray(fout.get_write_array(0))
			ptr = np.asarray(fout[0]) # for vs VAPv4
			ptr[0] = np.linspace(0, 1, 1 << 16)
			return fout

		mask = blank_clip.std.ModifyFrame([blank_clip], frame_writer)

	except (ImportError, ModuleNotFoundError):
		###warn("wipe: numpy module not found, falling back to slower less accurate method", Warning)
		import ctypes

		ptr_type = ctypes.c_float * (1 << 16)
		vs_ptr = ctypes.cast(write_frame.get_write_ptr(0), ctypes.POINTER(ptr_type))
		float_lin_array = [i / ((1 << 16) - 1) for i in list(range(1 << 16))]
		float_Arr_ptr = ctypes.pointer(ptr_type(*float_lin_array))
		vs_ptr[0] = float_Arr_ptr[0]
		mask = blank_clip.std.ModifyFrame([blank_clip], lambda n, f: write_frame)

	mask = mask.grain.Add()
	if TYPE_CHECKING:
		assert mask.format is not None
		assert clipa.format is not None
	mask_horiz = mask.resize.Spline64(
		clipa.width,
		clipa.height,
		dither_type="error_diffusion",
		format=mask.format.replace(
			bits_per_sample=clipa.format.bits_per_sample, color_family=vs.GRAY, sample_type=clipa.format.sample_type
		).id,
		matrix_in_s="rgb",
	)
	mask_vert = core.std.Transpose(mask).resize.Spline64(
		clipa.width,
		clipa.height,
		dither_type="error_diffusion",
		format=mask.format.replace(
			bits_per_sample=clipa.format.bits_per_sample, color_family=vs.GRAY, sample_type=clipa.format.sample_type
		).id,
		matrix_in_s="rgb",
	)
	black_clip = core.std.BlankClip(clip=mask_horiz, length=1, color=[0])										# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly
	white_clip = core.std.BlankClip(clip=mask_horiz, length=1, color=[(1 << clipa.format.bits_per_sample) - 1])	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	if direction in [Direction.LEFT, Direction.RIGHT]:
		stack = core.std.StackHorizontal([black_clip, mask_horiz, white_clip])
		w = mask_horiz.width

		if direction == Direction.LEFT:

			def _wipe(n: int) -> vs.VideoNode:
				#print_DEBUG(f'vs_transitions: Entered _wipe 1 ID={ID} direction={direction}')
				stack_ = stack.resize.Spline36(
					width=w,
					src_left=2 * w * n / (frames_ - 1),
					src_width=w,
				)
				return core.std.MaskedMerge(clipa_wipe_zone, clipb_wipe_zone, stack_)

		elif direction == Direction.RIGHT:
			stack = core.std.FlipHorizontal(stack)

			def _wipe(n: int) -> vs.VideoNode:
				#print_DEBUG(f'vs_transitions: Entered _wipe 2 ID={ID} direction={direction}')
				stack_ = stack.resize.Spline36(
					width=w,
					src_left=(2 * w) * (1 - n / (frames_ - 1)),
					src_width=w,
				)
				return core.std.MaskedMerge(clipa_wipe_zone, clipb_wipe_zone, stack_)

	elif direction in [Direction.UP, Direction.DOWN]:
		stack = core.std.StackVertical([black_clip, mask_vert, white_clip])
		h = mask_vert.height

		if direction == Direction.UP:

			def _wipe(n: int) -> vs.VideoNode:
				#print_DEBUG(f'vs_transitions: Entered _wipe 3 ID={ID} direction={direction}')
				stack_ = stack.resize.Spline36(
					height=h,
					src_top=2 * h * n / (frames_ - 1),
					src_height=h,
				)
				return core.std.MaskedMerge(clipa_wipe_zone, clipb_wipe_zone, stack_)

		elif direction == Direction.DOWN:
			stack = core.std.FlipVertical(stack)

			def _wipe(n: int) -> vs.VideoNode:
				#print_DEBUG(f'vs_transitions: Entered _wipe 4 ID={ID} direction={direction}')
				stack_ = stack.resize.Spline36(
					height=h,
					src_top=(2 * h) * (1 - n / (frames_ - 1)),
					src_height=h,
				)
				return core.std.MaskedMerge(clipa_wipe_zone, clipb_wipe_zone, stack_)

	wiped = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _wipe)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, wiped, clipb_clean)


def cube_rotate(
	clipa: vs.VideoNode,
	clipb: vs.VideoNode,
	frames: Optional[int] = None,
	direction: Direction = Direction.LEFT,
	exaggeration: int = 0,
) -> vs.VideoNode:
	"""Mimics a cube face rotation by adjusting the speed at which the :func:`squeeze_expand` boundary moves.

	Cube face containing `clipa` rotates away from the viewer in projected 3-D space towards `direction`.

	:param exaggeration: An integer between 0 and 100 (inclusive)
		representing how much the effect of the cosine wave should be exaggerated.
		`0` corresponds to a mathematically correct projection of a 90 degree rotation offset by 45 degrees.
		`100` corresponds to a fitted cosine wave.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered cube_rotate ID={ID} direction={direction}')
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("cube_rotate: give a proper direction")
	if not (0 <= exaggeration <= 100):
		raise ValueError(f"cube_rotate: exaggeration {exaggeration} not between 0 and 100")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, cube_rotate, clipa, clipb)
	clipa_clean, clipb_clean, clipa_squeeze_zone, clipb_squeeze_zone = _transition_clips(clipa, clipb, frames_)

	def rotation(percentage: float) -> float:
		"""Return a radian rotation based on `percentage` ranging from -pi/4 at 0% to -3pi/4 at 100%"""
		#print_DEBUG(f'vs_transitions: Entered rotation ID={ID} direction={direction}')
		return (-math.pi / 2) * percentage - math.pi / 4

	def position(percentage: float, bias: int) -> float:
		"""
		Return position of a rotated edge as a percentage
		0% at 0%, 23% at 25%, 50% at 50%, 77% at 75%, 100% at 100%
		"""
		#print_DEBUG(f'vs_transitions: Entered position ID={ID} direction={direction}')

		def _projection(x: float):
			"""mathmatically correct projection"""
			#print_DEBUG(f'vs_transitions: Entered _projection ID={ID}')
			return (-math.cos(rotation(x)) + (math.sqrt(2) / 2)) / math.sqrt(2)

		def _fitted(x: float):
			"""fitted cosine wave to exaggerate the effects"""
			#print_DEBUG(f'vs_transitions: Entered _fitted ID={ID} direction={direction}')
			return -0.5 * math.cos(2 * rotation(x) + math.pi / 2) + 0.5

		if bias == 0:
			return round(_projection(percentage), 9)
		elif bias == 100:
			return round(_fitted(percentage), 9)
		else:
			fitted = (bias / 100) * _fitted(percentage)
			projection = ((100 - bias) / 100) * _projection(percentage)
			return round(fitted + projection, 9)

	if direction in [Direction.LEFT, Direction.RIGHT]:

		def _rotate(n: int):
			#print_DEBUG(f'vs_transitions: Entered _rotate 1 ID={ID} direction={direction}')
			w_inc = math.floor(clipa.width * position(n / (frames_ - 1), exaggeration))
			w_dec = clipa.width - w_inc

			if w_dec == clipa.width:
				return clipa_squeeze_zone
			elif w_inc == clipa.width:
				return clipb_squeeze_zone
			else:
				clipa_squeezed = clipa_squeeze_zone.resize.Spline36(width=w_dec)
				clipb_squeezed = clipb_squeeze_zone.resize.Spline36(width=w_inc)
				if direction == Direction.LEFT:
					return core.std.StackHorizontal([clipa_squeezed, clipb_squeezed])
				elif direction == Direction.RIGHT:
					return core.std.StackHorizontal([clipb_squeezed, clipa_squeezed])

	elif direction in [Direction.UP, Direction.DOWN]:

		def _rotate(n: int):
			#print_DEBUG(f'vs_transitions: Entered _rotate 2 ID={ID} direction={direction}')
			h_inc = math.floor(clipa.height * position(n / (frames_ - 1), exaggeration))
			h_dec = clipa.height - h_inc

			if h_dec == clipa.height:
				return clipa_squeeze_zone
			elif h_inc == clipa.height:
				return clipb_squeeze_zone
			else:
				clipa_squeezed = clipa_squeeze_zone.resize.Spline36(height=h_dec)
				clipb_squeezed = clipb_squeeze_zone.resize.Spline36(height=h_inc)
				if direction == Direction.UP:
					return core.std.StackVertical([clipa_squeezed, clipb_squeezed])
				elif direction == Direction.DOWN:
					return core.std.StackVertical([clipb_squeezed, clipa_squeezed])

	rotated = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _rotate)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, rotated, clipb_clean)


def linear_boundary(
	clipa: vs.VideoNode,
	clipb: vs.VideoNode,
	clipa_movement: MiscConstants,
	clipb_movement: MiscConstants,
	frames: Optional[int] = None,
	direction: Direction = Direction.LEFT,
) -> vs.VideoNode:
	"""Generalized boundary moving function for a linear transition between two stacked clips.

	`clipa` can either slide out of view (having its size unchanged) or be squeezed to nothing from its original size.
	`clipb` can either slide into view (having its size unchanged) or be expanded from nothing to its full size.
	The boundary between the two clips moves towards `direction`.

	The parameter `clipa_movement` can be :attr:`MiscConstants.SLIDE` or :attr:`MiscConstants.SQUEEZE`.
	The parameter `clipb_movement` can be :attr:`MiscConstants.SLIDE` or :attr:`MiscConstants.EXPAND`.

	See :func:`push`, :func:`slide_expand`, :func:`squeeze_slide`, or :func:`squeeze_expand`
	for simpler aliases in the same form as most other linear, directional transitions.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered linear_boundary ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
	if clipa_movement not in [MiscConstants.SLIDE, MiscConstants.SQUEEZE]:
		raise ValueError("linear_boundary: clipa_movement must be either a slide or a squeeze")
	if clipb_movement not in [MiscConstants.SLIDE, MiscConstants.EXPAND]:
		raise ValueError("linear_boundary: clipb_movement must be either a slide or an expand")
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("linear_boundary: give a proper direction")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	check_for_subsampling = not (
		clipa_movement == clipb_movement == MiscConstants.SLIDE
	)  # only need subsampling check if resizing
	_check_clips(frames_, linear_boundary, clipa, clipb, subsampling=check_for_subsampling)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	if clipa_movement == clipb_movement == MiscConstants.SLIDE:
		w, h = clipa.width, clipa.height

		def _stack(clipa_: vs.VideoNode, clipb_: vs.VideoNode) -> vs.VideoNode:
			#print_DEBUG(f'vs_transitions: linear_boundary: Entered _stack ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
			if direction == Direction.LEFT:
				return core.std.StackHorizontal([clipa_, clipb_])
			elif direction == Direction.RIGHT:
				return core.std.StackHorizontal([clipb_, clipa_])
			elif direction == Direction.UP:
				return core.std.StackVertical([clipa_, clipb_])
			elif direction == Direction.DOWN:
				return core.std.StackVertical([clipb_, clipa_])

		stack = _stack(clipa_t_zone, clipb_t_zone)

		def _push(n: int) -> vs.VideoNode:
			#print_DEBUG(f'vs_transitions: linear_boundary: Entered _push ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
			if direction == Direction.LEFT:
				return stack.resize.Spline36(width=w, src_left=w * n / (frames_ - 1), src_width=w)
			elif direction == Direction.RIGHT:
				return stack.resize.Spline36(width=w, src_left=w * (1 - n / (frames_ - 1)), src_width=w)
			elif direction == Direction.UP:
				return stack.resize.Spline36(height=h, src_top=h * n / (frames_ - 1), src_height=h)
			elif direction == Direction.DOWN:
				return stack.resize.Spline36(height=h, src_top=h * (1 - n / (frames_ - 1)), src_height=h)

		pushed = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _push)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

		return _return_combo(clipa_clean, pushed, clipb_clean)

	elif clipa_movement == MiscConstants.SLIDE and clipb_movement == MiscConstants.EXPAND:

		def _slide_expand(n: int):
			#print_DEBUG(f'vs_transitions: linear_boundary: Entered _slide_expand ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
			scale = Fraction(n, frames_ - 1)

			if scale == 0:
				return clipa_t_zone
			elif scale == 1:
				return clipb_t_zone

			if direction in [Direction.LEFT, Direction.RIGHT]:
				w = math.floor(scale * clipa.width)

				if w == 0:
					return clipa_t_zone

				if direction == Direction.LEFT:
					stack = core.std.StackHorizontal([clipa_t_zone, clipb_t_zone.resize.Spline36(width=w)])
					return stack.std.Crop(left=w)
				elif direction == Direction.RIGHT:
					stack = core.std.StackHorizontal([clipb_t_zone.resize.Spline36(width=w), clipa_t_zone])
					return stack.std.Crop(right=w)

			elif direction in [Direction.UP, Direction.DOWN]:
				h = math.floor(scale * clipa.height)

				if h == 0:
					return clipa_t_zone

				if direction == Direction.UP:
					stack = core.std.StackVertical([clipa_t_zone, clipb_t_zone.resize.Spline36(height=h)])
					return stack.std.Crop(top=h)
				elif direction == Direction.DOWN:
					stack = core.std.StackVertical([clipb_t_zone.resize.Spline36(height=h), clipa_t_zone])
					return stack.std.Crop(bottom=h)

		slide_expanded = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _slide_expand)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

		return _return_combo(clipa_clean, slide_expanded, clipb_clean)

	elif clipa_movement == MiscConstants.SQUEEZE and clipb_movement == MiscConstants.SLIDE:

		def _squeeze_slide(n: int):
			#print_DEBUG(f'vs_transitions: linear_boundary: Entered _squeeze_slide ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
			scale = 1 - Fraction(n, frames_ - 1)

			if scale == 1:
				return clipa_t_zone
			elif scale == 0:
				return clipb_t_zone

			if direction in [Direction.LEFT, Direction.RIGHT]:
				w = math.floor(scale * clipa.width)

				if w == 0:
					return clipb_t_zone

				if direction == Direction.LEFT:
					stack = core.std.StackHorizontal([clipa_t_zone.resize.Spline36(width=w), clipb_t_zone])
					return stack.std.Crop(right=w)
				elif direction == Direction.RIGHT:
					stack = core.std.StackHorizontal([clipb_t_zone, clipa_t_zone.resize.Spline36(width=w)])
					return stack.std.Crop(left=w)

			elif direction in [Direction.UP, Direction.DOWN]:
				h = math.floor(scale * clipa.height)

				if h == 0:
					return clipb_t_zone

				if direction == Direction.UP:
					stack = core.std.StackVertical([clipa_t_zone.resize.Spline36(height=h), clipb_t_zone])
					return stack.std.Crop(bottom=h)

				elif direction == Direction.DOWN:
					stack = core.std.StackVertical([clipb_t_zone, clipa_t_zone.resize.Spline36(height=h)])
					return stack.std.Crop(top=h)

		squeeze_slided = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _squeeze_slide)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

		return _return_combo(clipa_clean, squeeze_slided, clipb_clean)

	elif clipa_movement == MiscConstants.SQUEEZE and clipb_movement == MiscConstants.EXPAND:

		def _squeeze_expand(n: int) -> vs.VideoNode:
			#print_DEBUG(f'vs_transitions: linear_boundary: Entered _squeeze_expand ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}')
			scale = Fraction(n, frames_ - 1)

			if scale == 0:
				return clipa_t_zone
			elif scale == 1:
				return clipb_t_zone

			if direction in [Direction.LEFT, Direction.RIGHT]:
				w_inc = math.floor(scale * clipa.width)
				w_dec = clipa.width - w_inc

				if w_inc == 0:
					return clipa_t_zone

				if direction == Direction.LEFT:
					return core.std.StackHorizontal(
						[clipa_t_zone.resize.Spline36(width=w_dec), clipb_t_zone.resize.Spline36(width=w_inc)]
					)
				elif direction == Direction.RIGHT:
					return core.std.StackHorizontal(
						[clipb_t_zone.resize.Spline36(width=w_inc), clipa_t_zone.resize.Spline36(width=w_dec)]
					)

			elif direction in [Direction.UP, Direction.DOWN]:
				h_inc = math.floor(scale * clipa.height)
				h_dec = clipa.height - h_inc

				if h_inc == 0:
					return clipa_t_zone

				if direction == Direction.UP:
					#print_DEBUG(f'vs_transitions: linear_boundary: Entered _squeeze_expand ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}(=UP) clipA.resized.height={h_dec} clipB.resized.height={h_inc}')
					return core.std.StackVertical(
						[clipa_t_zone.resize.Spline36(height=h_dec), clipb_t_zone.resize.Spline36(height=h_inc)]
					)
				elif direction == Direction.DOWN:
					#print_DEBUG(f'vs_transitions: linear_boundary: Entered _squeeze_expand ID={ID} clipa_movement={clipa_movement} clipb_movement={clipb_movement} direction={direction}(=DOWN) clipB.resized.height={h_inc} clipA.resized.height={h_dec}')
					return core.std.StackVertical(
						[clipb_t_zone.resize.Spline36(height=h_inc), clipa_t_zone.resize.Spline36(height=h_dec)]
					)

		squeeze_expanded = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _squeeze_expand)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

		return _return_combo(clipa_clean, squeeze_expanded, clipb_clean)


def push(clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT):
	"""Second clip pushes first clip off of the screen.

	The first clip moves off of the screen moving towards the given `direction`.

	Alias for :func:`linear_boundary` with ``clipa_movement=SLIDE`` and ``clipb_movement=SLIDE``.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered push ID={ID} direction={direction}')
	return linear_boundary(clipa, clipb, MiscConstants.SLIDE, MiscConstants.SLIDE, frames=frames, direction=direction)


def slide_expand(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
):
	"""First clip slides out of view, while second clip expands into view from nothing.

	`clipa` slides off of the screen towards `direction`.
	`clipb` expands into view from the opposite side of the given direction.

	Alias for :func:`linear_boundary` with ``clipa_movement=SLIDE`` and ``clipb_movement=EXPAND``.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered slide_expand ID={ID} direction={direction}')
	return linear_boundary(clipa, clipb, MiscConstants.SLIDE, MiscConstants.EXPAND, frames=frames, direction=direction)


def squeeze_slide(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
):
	"""First clip squeezes into nothing, while second clip slides into view.

	`clipa` gets compressed off of the screen towards `direction`.
	`clipb` slides into view from the opposite side of the given direction.

	Alias for :func:`linear_boundary` with ``clipa_movement=SQUEEZE`` and ``clipb_movement=SLIDE``.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered squeeze_slide ID={ID} direction={direction}')
	return linear_boundary(clipa, clipb, MiscConstants.SQUEEZE, MiscConstants.SLIDE, frames=frames, direction=direction)


def squeeze_expand(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
):
	"""First clip squeezes into nothing, while second clip expands into view from nothing.

	`clipa` gets compressed off of the screen towards `direction`.
	`clipb` expands into view from the opposite side of the given direction.

	Alias for :func:`linear_boundary` with ``clipa_movement=SQUEEZE`` and ``clipb_movement=EXPAND``.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered squeeze_expand ID={ID} direction={direction}')
	return linear_boundary(
		clipa, clipb, MiscConstants.SQUEEZE, MiscConstants.EXPAND, frames=frames, direction=direction
	)


def cover(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
) -> vs.VideoNode:
	"""Second clip slides in and covers the first clip which stays in place.

	`clipb` slides into frame towards `direction` covering `clipa`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered cover ID={ID} direction={direction}')
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("cover: give a proper direction")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, cover, clipa, clipb)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _cover(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _cover ID={ID} direction={direction}')
		progress = Fraction(n, frames_ - 1)
		w = math.floor(progress * clipa.width)
		h = math.floor(progress * clipa.height)

		if progress == 0:
			return clipa_t_zone
		elif progress == 1:
			return clipb_t_zone

		if direction in [Direction.LEFT, Direction.RIGHT]:
			if w == 0:
				return clipa_t_zone
		elif direction in [Direction.UP, Direction.DOWN]:
			if h == 0:
				return clipa_t_zone

		if direction == Direction.LEFT:
			cropped_a = clipa_t_zone.std.Crop(right=w)
			stack = core.std.StackHorizontal([cropped_a, clipb_t_zone])
			return stack.resize.Spline36(width=clipa.width, src_width=clipa.width)
		elif direction == Direction.RIGHT:
			cropped_a = clipa_t_zone.std.Crop(left=w)
			stack = core.std.StackHorizontal([clipb_t_zone, cropped_a])
			return stack.resize.Spline36(width=clipa.width, src_left=clipa.width - w, src_width=clipa.width)
		elif direction == Direction.UP:
			cropped_a = clipa_t_zone.std.Crop(bottom=h)
			stack = core.std.StackVertical([cropped_a, clipb_t_zone])
			return stack.resize.Spline36(height=clipa.height, src_height=clipa.height)
		elif direction == Direction.DOWN:
			cropped_a = clipa_t_zone.std.Crop(top=h)
			stack = core.std.StackVertical([clipb_t_zone, cropped_a])
			return stack.resize.Spline36(height=clipa.height, src_top=clipa.height - h, src_height=clipa.height)

	covered = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _cover)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, covered, clipb_clean)


def reveal(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
) -> vs.VideoNode:
	"""First clip slides out of view exposing second clip that stays in place.

	`clipa` slides out of frame towards `direction` revealing `clipb`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered reveal ID={ID} direction={direction}')
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("reveal: give a proper direction")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, reveal, clipa, clipb)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _reveal(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _reveal ID={ID} direction={direction}')
		progress = 1 - Fraction(n, frames_ - 1)
		w = math.floor(progress * clipa.width)
		h = math.floor(progress * clipa.height)

		if progress == 1:
			return clipa_t_zone
		elif progress == 0:
			return clipb_t_zone

		if direction in [Direction.LEFT, Direction.RIGHT]:
			if w == 0:
				return clipb_t_zone
		elif direction in [Direction.UP, Direction.DOWN]:
			if h == 0:
				return clipb_t_zone

		if direction == Direction.LEFT:
			cropped_b = clipb_t_zone.std.Crop(left=w)
			stack = core.std.StackHorizontal([clipa_t_zone, cropped_b])
			return stack.resize.Spline36(width=clipa.width, src_width=clipa.width, src_left=clipa.width - w)
		elif direction == Direction.RIGHT:
			cropped_b = clipb_t_zone.std.Crop(right=w)
			stack = core.std.StackHorizontal([cropped_b, clipa_t_zone])
			return stack.resize.Spline36(width=clipa.width, src_width=clipa.width)
		elif direction == Direction.UP:
			cropped_b = clipb_t_zone.std.Crop(top=h)
			stack = core.std.StackVertical([clipa_t_zone, cropped_b])
			return stack.resize.Spline36(height=clipa.height, src_height=clipa.height, src_top=clipa.height - h)
		elif direction == Direction.DOWN:
			cropped_b = clipb_t_zone.std.Crop(bottom=h)
			stack = core.std.StackVertical([cropped_b, clipa_t_zone])
			return stack.resize.Spline36(height=clipa.height, src_height=clipa.height)

	covered = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _reveal)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, covered, clipb_clean)


def curtain_cover(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, axis: Direction = Direction.HORIZONTAL
) -> vs.VideoNode:
	"""Second clip comes into view from both directions split along the given axis covering the first clip in place.

	`clipb` splits and moves inwards along the given `axis`.

	If `axis` is given as :attr:`Direction.HORIZONTAL`, the clips must have an even integer width.
	If `axis` is given as :attr:`Direction.VERTICAL`, the clips must have an even integer height.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered curtain_cover ID={ID} axis={axis}')
	if axis not in [Direction.HORIZONTAL, Direction.VERTICAL]:
		raise ValueError("curtain_cover: give a proper axis")
	if axis == Direction.HORIZONTAL and clipa.width % 2:
		raise ValueError("curtain_cover: for horizontal reveal, input clips must have an even width")
	elif axis == Direction.VERTICAL and clipa.height % 2:
		raise ValueError("curtain_cover: for vertical reveal, input clips must have an even height")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, curtain_cover, clipa, clipb)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _curtain_cover(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _curtain_cover ID={ID} axis={axis}')
		progress = Fraction(n, frames_ - 1)

		if progress == 0:
			return clipa_t_zone
		elif progress == 1:
			return clipb_t_zone

		if axis == Direction.HORIZONTAL:
			w = round(float(clipa.width * progress / 2)) * 2

			if w == 0:
				return clipa_t_zone
			elif w == clipa.width:
				return clipb_t_zone

			clipb_left = clipb_t_zone.std.Crop(right=clipa.width // 2)
			clipb_right = clipb_t_zone.std.Crop(left=clipa.width // 2)

			clipb_left = clipb_left.std.Crop(left=clipb_left.width - w // 2)
			clipb_right = clipb_right.std.Crop(right=clipb_right.width - w // 2)

			clipa_cropped = clipa_t_zone.std.Crop(left=clipb_left.width, right=clipb_right.width)
			return core.std.StackHorizontal([clipb_left, clipa_cropped, clipb_right])

		elif axis == Direction.VERTICAL:
			h = round(float(clipa.height * progress / 2)) * 2

			if h == 0:
				return clipa_t_zone
			elif h == clipa.height:
				return clipb_t_zone

			clipb_top = clipb_t_zone.std.Crop(bottom=clipa.height // 2)
			clipb_bottom = clipb_t_zone.std.Crop(top=clipa.height // 2)

			clipb_top = clipb_top.std.Crop(top=clipb_top.height - h // 2)
			clipb_bottom = clipb_bottom.std.Crop(bottom=clipb_bottom.height - h // 2)

			clipa_cropped = clipa_t_zone.std.Crop(top=clipb_top.height, bottom=clipb_bottom.height)
			return core.std.StackVertical([clipb_top, clipa_cropped, clipb_bottom])

	curtain_covered = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _curtain_cover)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, curtain_covered, clipb_clean)


def curtain_reveal(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, axis: Direction = Direction.HORIZONTAL
) -> vs.VideoNode:
	"""First clip splits apart to reveal the second clip in place.

	`clipa` splits and moves apart along the given `axis`.

	If `axis` is given as :attr:`Direction.HORIZONTAL`, the clips must have an even integer width.
	If `axis` is given as :attr:`Direction.VERTICAL`, the clips must have an even integer height.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered curtain_reveal ID={ID} axis={axis}')
	if axis not in [Direction.HORIZONTAL, Direction.VERTICAL]:
		raise ValueError("curtain_reveal: give a proper axis")
	if axis == Direction.HORIZONTAL and clipa.width % 2:
		raise ValueError("curtain_reveal: for horizontal reveal, input clips must have an even width")
	elif axis == Direction.VERTICAL and clipa.height % 2:
		raise ValueError("curtain_reveal: for vertical reveal, input clips must have an even height")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, curtain_reveal, clipa, clipb)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _curtain_reveal(n: int) -> vs.VideoNode:
		#print_DEBUG(f'vs_transitions: Entered _curtain_reveal ID={ID} axis={axis}')
		progress = Fraction(n, frames_ - 1)

		if progress == 0:
			return clipa_t_zone
		elif progress == 1:
			return clipb_t_zone

		if axis == Direction.HORIZONTAL:
			w = round(float(clipa.width * progress / 2)) * 2

			if w == 0:
				return clipa_t_zone
			elif w == clipa.width:
				return clipb_t_zone

			clipa_left = clipa_t_zone.std.Crop(right=clipa.width // 2)
			clipa_right = clipa_t_zone.std.Crop(left=clipa.width // 2)

			clipa_left = clipa_left.std.Crop(left=w // 2)
			clipa_right = clipa_right.std.Crop(right=w // 2)

			clipb_cropped = clipb_t_zone.std.Crop(left=clipa_left.width, right=clipa_right.width)
			return core.std.StackHorizontal([clipa_left, clipb_cropped, clipa_right])

		elif axis == Direction.VERTICAL:
			h = round(float(clipa.height * progress / 2)) * 2

			if h == 0:
				return clipa_t_zone
			elif h == clipa.height:
				return clipb_t_zone

			clipa_top = clipa_t_zone.std.Crop(bottom=clipa.height // 2)
			clipa_bottom = clipa_t_zone.std.Crop(top=clipa.height // 2)

			clipa_top = clipa_top.std.Crop(top=h // 2)
			clipa_bottom = clipa_bottom.std.Crop(bottom=h // 2)

			clipb_cropped = clipb_t_zone.std.Crop(top=clipa_top.height, bottom=clipa_bottom.height)
			return core.std.StackVertical([clipa_top, clipb_cropped, clipa_bottom])

	curtain_revealed = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _curtain_reveal)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, curtain_revealed, clipb_clean)


def pixellate(
	clipa: vs.VideoNode,
	clipb: vs.VideoNode,
	frames: Optional[int] = None,
	lowest_target_w: Optional[int] = 2,
	lowest_target_h: Optional[int] = 2,
) -> vs.VideoNode:
	"""Pixellate using rescales and aggressively fade at the center.

	For large clips (width `x` height), the effect might not be too noticeable
	until the transition is near the middle point.
	This is due to bicubic downscales and point re-upscales
	at very high percentages of the original dimensions
	not being noticeably different.

	Due to the way pixellation progress is calculated,
	the transition `must` be at least 4 frames long.

	Longer transitions paired with larger target dimensions
	will cause the pixellation effect to appear to pause towards the center of the transition.

	:param lowest_target_w: An integer that determines the minimum width target to downscale to.
		By specifying ``None``, or by specifying the width of the source clips, the clips will not be scaled in the
		`x` or width direction, making this only pixellate vertically.

	:param lowest_target_h: An integer that determines the minimum height target to downscale to.
		By specifying ``None``, or by specifying the height of the source clips, the clips will not be scaled in the
		`y` or height direction, making this only pixellate horizontally.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered pixellate ID={ID}')
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if frames_ < 4:
		raise ValueError("pixellate: transition must be at least 4 frames long")

	if lowest_target_w is None:
		lowest_target_w = clipa.width
	if lowest_target_h is None:
		lowest_target_h = clipa.height
	if lowest_target_w < 1 or lowest_target_w > clipa.width:
		raise ValueError("pixellate: `lowest_target_w` must be at least one and at most the width of the source clips")
	if lowest_target_h < 1 or lowest_target_h > clipa.height:
		raise ValueError("pixellate: `lowest_target_h` must be at least one and at most the height of the source clips")
	if lowest_target_w == clipa.width and lowest_target_h == clipa.height:
		raise ValueError("pixellate: at least one target dimension must be lower than the source dimensions")
	lowest_target_w_ = lowest_target_w
	lowest_target_h_ = lowest_target_h

	if TYPE_CHECKING:
		assert isinstance(frames_, int)
		assert isinstance(lowest_target_w_, int)
		assert isinstance(lowest_target_h_, int)
	_check_clips(frames_, pixellate, clipa, clipb)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _pixellate(n: int):
		#print_DEBUG(f'vs_transitions: Entered _pixellate ID={ID}')
		if iseven(frames_):
			center = (frames_ - 1) / 2
			if n < center:
				progress_a = Fraction(math.floor(center) - n, math.floor(center)) ** 2

				target_w_a = max([lowest_target_w_, math.floor(progress_a * clipa.width)])
				target_h_a = max([lowest_target_h_, math.floor(progress_a * clipa.height)])

				target_w_b = lowest_target_w_
				target_h_b = lowest_target_h_

				clipa_small = clipa_t_zone.resize.Bicubic(target_w_a, target_h_a)
				clipb_small = clipb_t_zone.resize.Bicubic(target_w_b, target_h_b)

				clipa_pixellated = clipa_small.resize.Point(clipa.width, clipa.height)
				clipb_pixellated = clipb_small.resize.Point(clipa.width, clipa.height)

				if n == math.floor(center):
					return core.std.Merge(clipa_pixellated, clipb_pixellated, [1 / 3])
				else:
					return clipa_pixellated

			else:
				progress_b = Fraction(n - math.ceil(center), math.floor(center)) ** 2

				target_w_b = max([lowest_target_w_, math.floor(progress_b * clipa.width)])
				target_h_b = max([lowest_target_h_, math.floor(progress_b * clipa.height)])

				target_w_a = lowest_target_w_
				target_h_a = lowest_target_h_

				clipa_small = clipa_t_zone.resize.Bicubic(target_w_a, target_h_a)
				clipb_small = clipb_t_zone.resize.Bicubic(target_w_b, target_h_b)

				clipa_pixellated = clipa_small.resize.Point(clipa.width, clipa.height)
				clipb_pixellated = clipb_small.resize.Point(clipa.width, clipa.height)

				if n == math.ceil(center):
					return core.std.Merge(clipa_pixellated, clipb_pixellated, [2 / 3])
				else:
					return clipb_pixellated
		else:
			center = (frames_ - 1) // 2
			if n < center:
				progress_a = Fraction(center - n, center) ** 2

				target_w_a = max([lowest_target_w_, math.floor(progress_a * clipa.width)])
				target_h_a = max([lowest_target_h_, math.floor(progress_a * clipa.height)])

				target_w_b = lowest_target_w_
				target_h_b = lowest_target_h_

				clipa_small = clipa_t_zone.resize.Bicubic(target_w_a, target_h_a)
				clipb_small = clipb_t_zone.resize.Bicubic(target_w_b, target_h_b)

				clipa_pixellated = clipa_small.resize.Point(clipa.width, clipa.height)
				clipb_pixellated = clipb_small.resize.Point(clipa.width, clipa.height)

				if n == center - 1:
					return core.std.Merge(clipa_pixellated, clipb_pixellated, [1 / 4])
				else:
					return clipa_pixellated

			elif n == center:
				target_w_a = target_w_b = lowest_target_w_
				target_h_a = target_h_b = lowest_target_h_
				clipa_small = clipa_t_zone.resize.Bicubic(target_w_a, target_h_a)
				clipb_small = clipb_t_zone.resize.Bicubic(target_w_b, target_h_b)

				clipa_pixellated = clipa_small.resize.Point(clipa.width, clipa.height)
				clipb_pixellated = clipb_small.resize.Point(clipa.width, clipa.height)

				return core.std.Merge(clipa_pixellated, clipb_pixellated, [1 / 2])

			else:
				progress_b = Fraction(n - center, center) ** 2

				target_w_b = max([lowest_target_w_, math.floor(progress_b * clipa.width)])
				target_h_b = max([lowest_target_h_, math.floor(progress_b * clipa.height)])

				target_w_a = lowest_target_w_
				target_h_a = lowest_target_h_

				clipa_small = clipa_t_zone.resize.Bicubic(target_w_a, target_h_a)
				clipb_small = clipb_t_zone.resize.Bicubic(target_w_b, target_h_b)

				clipa_pixellated = clipa_small.resize.Point(clipa.width, clipa.height)
				clipb_pixellated = clipb_small.resize.Point(clipa.width, clipa.height)

				if n == center + 1:
					return core.std.Merge(clipa_pixellated, clipb_pixellated, [3 / 4])
				else:
					return clipb_pixellated

	pixellated = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _pixellate)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, pixellated, clipb_clean)


def peel(
	clipa: vs.VideoNode, clipb: vs.VideoNode, frames: Optional[int] = None, direction: Direction = Direction.LEFT
) -> vs.VideoNode:
	"""First clip peels away revealing the second clip beneath.

	Both clips remain in place during the transition. The boundary between clips moves towards `direction`.
	"""
	#print_DEBUG(f'vs_transitions: ---------- Entered peel ID={ID} direction={direction}')
	if direction not in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
		raise ValueError("peel: give a proper direction")
	frames_ = frames or min(clipa.num_frames, clipb.num_frames)
	if TYPE_CHECKING:
		assert isinstance(frames_, int)
	_check_clips(frames_, peel, clipa, clipb, subsampling=True)
	clipa_clean, clipb_clean, clipa_t_zone, clipb_t_zone = _transition_clips(clipa, clipb, frames_)

	def _peel(n: int):
		#print_DEBUG(f'vs_transitions: Entered _peel ID={ID} direction={direction}')
		progress = Fraction(n, frames_ - 1)
		if progress == 0:
			return clipa_t_zone
		elif progress == 1:
			return clipb_t_zone
		else:
			if direction in [Direction.LEFT, Direction.RIGHT]:
				clipb_w = math.floor(clipa.width * progress)
				clipa_w = clipa.width - clipb_w

				if clipb_w == 0:
					return clipa_t_zone
				elif clipb_w == clipa.width:
					return clipb_t_zone
				else:
					if direction == Direction.LEFT:
						clipa_cropped = clipa_t_zone.std.Crop(right=clipb_w)
						clipb_cropped = clipb_t_zone.std.Crop(left=clipa_w)
						return core.std.StackHorizontal([clipa_cropped, clipb_cropped])
					elif direction == Direction.RIGHT:
						clipa_cropped = clipa_t_zone.std.Crop(left=clipb_w)
						clipb_cropped = clipb_t_zone.std.Crop(right=clipa_w)
						return core.std.StackHorizontal([clipb_cropped, clipa_cropped])
			elif direction in [Direction.UP, Direction.DOWN]:
				clipb_h = math.floor(clipa.height * progress)
				clipa_h = clipa.height - clipb_h

				if clipb_h == 0:
					return clipa_t_zone
				elif clipb_h == clipa.width:
					return clipb_t_zone
				else:
					if direction == Direction.UP:
						clipa_cropped = clipa_t_zone.std.Crop(bottom=clipb_h)
						clipb_cropped = clipb_t_zone.std.Crop(top=clipa_h)
						return core.std.StackVertical([clipa_cropped, clipb_cropped])
					elif direction == Direction.DOWN:
						clipa_cropped = clipa_t_zone.std.Crop(top=clipb_h)
						clipb_cropped = clipb_t_zone.std.Crop(bottom=clipa_h)
						return core.std.StackVertical([clipb_cropped, clipa_cropped])

	peeled = core.std.FrameEval(core.std.BlankClip(clip=clipa, length=frames_), _peel)	# hopefully makes a blankclip like clipa with format/width/height/fps, but overridden by parameters specified explicitly

	return _return_combo(clipa_clean, peeled, clipb_clean)


def round_to(f: Fraction, n: int) -> int:
	"""Rounds a fractional value to the nearest `n`, rounding half up and never returning less than `n`"""
	#print_DEBUG(f'vs_transitions: ---------- Entered round_to')
	if n < 1:
		raise ValueError("round_to: `n` must be an integer greater than 0")
	if n == 1:
		return max(1, round(float(f)))
	else:
		return max(n, round(float(f / n)) * n)


def isodd(value: int) -> bool:
	return bool(value % 2)


def iseven(value: int) -> bool:
	return not bool(value % 2)
