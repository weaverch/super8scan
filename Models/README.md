Please read the WARNING.txt first !!


Notes re models:
----------------

Software used:

- FreeCAD     http://www.freecadweb.org
- OpenSCAD    http://www.openscad.org


Most models were developed using FreeCAD, an open source 3d CAD parametric modelling program.  I was able to do what I needed with primitives and booleans and a very few sketches.  Threaded pieces in FreeCAD require the Fasteners workbench, which has to be added after installation.  It is great, easy to install, and located at http://theseger.com/projects/2015/06/fasteners-workbench-for-freecad/

Lens extension / focusing tubes use other folks' parametric OpenSCAD scripts.  Install OpenSCAD, open the *.scad files and see the developers' notes.

General Observations:
--------------------
There are vestiges of initial design uncertainty in some models that could be removed now.  For example the camera slider is far longer than necessary due to the fact that earlier camera designs had lenses a few centimeters from the camera sensor.  The elaborate dc motor mounts for the film reels are there because I wasn't certain how I would connect motors to shafts.  Could be simpler.

I've included the gear setup for the stepper.  The gears are there because I needed greater resolution and I was / am too cheap to buy another (geared) stepper.  The gears are awful; I would not take that route from a fresh start.


Model Sets:
-----------

Camera
------
- cameraSledV3.FCStd				                Very tight fit; too long
- camera-m12-slider-mount.FCStd		        Connects cam to sled
- camera-m12.FCStd				                  Arducam 5mp specific

Lenses
------
- FocusFemaleThreadedTube-LongWide.scad
- FocusMaleThreadedTube-LongWide.scad
- m12Internal.FCStd				                Holds lens in MaleTube


Motors Gears Pulleys
--------------------
- dcMount.fcstd					                  Specific to motor used
- dcMotorSlider.FCStd				              Adjust belt tension
- roundbeltpulleyMotor.FCStd			          For 2mm urethane belt
- roundbeltpulleySpool.FCStd			          For 2mm urethane belt

- gear-1.55shaft.FCStd				              Bad idea
- gear-32x8-drive.FCStd				            Bad idea
- gear-8-stepper.FCStd				              For 5mm D shaft
- gearframe.FCStd					                Ignore dummy gears
- gearboxshaft.FCStd
- shaftboardguide.FCStd				            Stabilize driveshaft
- gearedOringRoller.FCStd			            For 2x20mm O rings

- Stepper mount			                      http://www.thingiverse.com/thing:1866886

All Other
---------
- SpoolMount.FCStd				                  Adjust board thickness
- pinchSwingArm.FCStd
- pinchfilmguide.FCStd
- crossbrace.FCStd				                  Brace base & vert panel
- filmsideguide.FCStd				              Threads not used
- filmspoolAdapterSmaller.FCStd		        Holds reels onto shafts
- gate3-top.fcstd					                Mod of RPitelecine
- gate3-bottom.fcstd				                Mod of RPitelecine
- takeupArm.FCStd
- takeupArmBase.FCStd				              Check dimensions of pot
- takeupArmBaseShort.FCStd			            Short version
- potArmspacer.FCStd				                Big 8mm ID washer / guide

- Take-up reel			                        http://www.thingiverse.com/thing:390502
