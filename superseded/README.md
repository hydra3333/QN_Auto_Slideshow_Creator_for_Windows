# ReSize images with irfanview and encode with ffmpeg
### to produce an .mp4 slideshow and a DVD .mpg

It works, after a fashion.  As an example only.    

I will say the images as resized by irfanview (up and down to fit into a 1920x1080 box), whilst beautifully maintaining aspect ratio, were particularly pretty.

It partially got around this:   
The exercise failed miserably with native ffmpeg "-f concat" using the "scale" and "pad" filters ... 
as soon as it saw an odd dimension then the image was stretched either horizontally or vertically 
no matter what options I tried ... and I tried a lot.   
It also was less than forgiving by delivering bt470gb colorspace etc and inconsistent "range" (TV or PC) 
perhaps depending on the first image it encountered.   

Plenty of advice around on the net with basically the same ffmpeg options, however the authors must not have tried 
a range of old and new and odd-dimensioned images nor examined things like colorspaces and output ranges.   
To be fair, some aspect ratio issues would have been hard to spot if the sources were "close" in dimensions and less eclectic than my lot.   

See https://forum.videohelp.com/threads/408230-ffmpeg-avc-from-jpgs-of-arbitrary-dimensions-maintaining-aspect-ratio/page2#post2682862    

Issues:
- It is less than forgiving by delivering bt470gb colorspace etc and inconsistent "range" (TV or PC) 
perhaps depending on the first image it encountered.  
- No possibility of addressing video clips.
