------------------
super8scan Project
------------------

Introduction
------------

A hobbyist's (retired accountant) effort to assemble inexpensive processors and camera, assorted small motors, several 3D printed parts and scrap wood into something capable of digitizing a small collection of Super8mm films from the early 70's.  Films have been in a box in the closet unseen for over 35 years, but appear to be in excellent physical condition.

While this is a comparatively low budget effort, sending the reels off to BigBoxStore etc would yield DVDs for substantially less time and $$.  My justification for taking this path is simply to tinker with 3D modelling and printing, lenses & cameras, gears, microcomputers / processors and python.

The result works, but is inefficient and sloppy, containing a number of abandoned paths from past versions.  It is also very "bare bones", with no setup script, no rewind etc.  Not an issue for me given small inventory of film, but definitely an issue for someone needing more throughput.

Mechanically, my choices clearly suffer from Maslow's hammer ("if all you have is a hammer, everything looks like a nail"), except in my case the hammer is a 3d printer.  

I've studied the following similar-ish efforts closely and taken ideas from them all:

- https://github.com/jas8mm/rpitelecine
- https://github.com/jphfilm/rpi-film-capture/wiki
- http://kinograph.cc/
- http://www.sabulo.com/sb/8mm-film/
- https://therobotfish.com/projects/digital-telecine/
- http://www.mets-telecinesystem.co.uk/

Overview
--------

The capture device is freestanding and limited functionally to capturing raw bayer data images of each frame.  Images are saved to the Pi3's microSD system card (128G).  Python code is single threaded at this stage and system runs at a little over 2 seconds / frame.  Film is advanced by a stepper motor's drive wheel with 2mm O-rings set into it and an opposing pinch wheel.  Film tension is maintained by gravity via two arms mounted on potentiometers that ride up/down as film advances. The changing voltage is read by the Arduino to trigger motors connected to the feed and takeup reels.

Stepping to advance film is calculated on the Pi by grabbing the greyscale bayer data image, threshholding (via OpenCV) a small vertical roi where the sprocket hole should in general be found and grabbing the average Y value of the white pixels.  Stepping info sent to Arduino over serial connection to trigger next frame.  This only works on film with black around the sprockets, but that's all I have.  Calculated steps keep each frame's center within 50 pixels or so above /below image center.  

Once capture is complete, microSD card goes via sneakernet to my desktop booted into Arch Linux.  Images copy to desktop's hard drive at approximately 20MBytes / sec which is considerably faster than my wifi network's transfer rate.

Once on the desktop in NTFS partitions, I batch process the raw image sequences into demoisaiced RGB tiff sequences using dcraw.  These images in turn pass through a python script which locates the sprocket hole again and crops relative to the hole's location, saving a 2066x1550 tiff.

I'm currently using DaVinci Resolve (freebie for non-com use version 12.5) in Windows 10 to cut and paste image sequences into video segments and do all color correction, including I hope masking out the purple fringe that's very noticeable against certain backgrounds.  Resolve also has an incredible tracker that makes stabilization dead simple.  From Resolve I output color corrected / stabilized DPX image sequences which are then encoded with ffmpeg.

Gear Used
--------
Freestanding Capture Thing:
- Raspberry Pi 3 with Arducam 5MP OV5647 cam (M12 mount)
- M12 lens; 12mm focal length mounted separately in a threaded tube for magnification and focusing
- Arduino Uno with Adafruit Motor Shield V2 - drives stepper and two DC motors - serial connection / power via Rpi3 USB
- Stepper motor - 12v / 200 steps connected to homemade 16x reduction gear box (awful...buy geared stepper or figure out microstepping on this driver)
- Light source is an 8x2 diy matrix of 5mm clear white leds powered by 4 to 5 volts dc from an adjustable power supply; adjusting voltage allows rough brightness control; diffusion currently from reflected light in something of a leaky integrating sphere

3D Models:
- Freecad; can be a bit fussy.  I'll be using Fusion360 on future projects.
- 3D printing on owned Original Prusa i3 mk2 acquired as kit from Prusa in Prague. 

Results
-------
Image quality varies between dreadful and barely acceptable yet I enjoy seeing the people and places from long ago immensely.  

Samples housed on Youtube:
-------------------------
Scanning underway  https://youtu.be/BP9WV82NFkA
Sample output      https://youtu.be/8DqxQMjq3eE


Acknowledgements
----------------
Thanks to authors of all the projects listed above.  I've tried to acknowledge authors and their copyrights in source files.  If I've missed anything please advise and I will modify immediately.
