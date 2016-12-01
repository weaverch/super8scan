------------------
super8scan Project
------------------

Introduction
------------

A hobbyist level (retired accountant) effort to cobble together inexpensive processors, an assortment of small motors, several 3D printed parts and scrap wood into something capable of digitizing a small collection of Super8mm family vacation and holiday films I took in the early 70's.  Films have been in a box in the closet unseen for over 35 years, but appear to be in excellent physical condition.

While this is a comparatively low budget effort, sending the reels off to BigBoxStore etc would get the job done for substantially less time and $$.  The justification for taking this path is full control over quality choices and a chance to tinker.

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

Processors:
- Raspberry Pi 3 with Camera Module V2
- Arduino Uno with Adafruit Motor Shield V2

Motors:
- Nema 17 stepper; 200 steps; 12V 
- DC gear motor; 10rpm; 12V

3d printing:
- Original Prusa i3 Mk2 using PLA

LED:
- Adafruit NeoPixel Jewel w/ 7 RGBW leds

Software:
- Pi3
	- Raspian (Debian linux) OS
	- Python3
	- PiCamera lib, OpenCV 3.1 Python wrapper, PyQt5
- Arduino
	- Adafruit MotorShield and NeoPixel Arduino libraries
- 3d modelling on Freecad 16 + Prusa version of Slic3r
- Blender for post-processing


The RPi3 with picamera attached is the "head" running a simple-ish python program "super8scan".  The Arduino Uno is attached to the RPi3 by USB serial connection.  RPi3's program captures an image and analyzes it using OpenCV functions to find perforations.  With the perf found the program crops and saves the frame image to the RPi3 SD card and adjusts the number of steps for the next frame advance if the perforation begins to run "high" or "low".

The RPi3 then sends a simple commmand string to the Arduino to advance the film # of steps.  The sketch running on the Arduino watches the serial port for characters and parses them.  

The Arduino handles all motor, LED and sensor functions.  The only sensor at present is a potentiometer to which an arm is mounted that rides up and down on the slack in front of the takeup spool.  When the arm drops below a certain level the motor runs until the arm reaches a prescribed height.


Results
-------

Samples housed on Youtube:

Acknowledgements
----------------

