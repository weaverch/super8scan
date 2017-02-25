###################################################################
# This file is a modification of the file "camera.py" from the    #
#  RPi Telecine project.  I've included that project's header and #
#  copyright below.                                               #  
###################################################################
# RPi Telecine Camera Control
#
# Code to encapsulate the operation of the camera.
#        
# Basically this isolates the fixed settings we use during the
# taking process. Images returned are bgr format Numpy arrays
# that can be used by openCV.
#        
# Prerequisites:
# Uses Python-picamera by Dave Hughes from: 
# https://pypi.python.org/pypi/picamera/
# or use sudo apt-get install python-picamera on your Pi.
#        
# Uses array API of Picamera 1.5+ to return a Numpy array
#
# As of May 2014, it seems to be necessary to set the memory split
# in raspi-config to at least 192M, otherwise we seem to get MMAL 
# out-of-memory errors.
# 
# 
# Copyright (c) 2015, Jason Lane
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation and/or 
# other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors 
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR 
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import picamera
from picamera import PiCamera
#import time

# Subclass of PiCamera

class s8sCamera( PiCamera ):
    
    def __init__(self):
        super().__init__(sensor_mode=2)
 
    def setup_cam(self,confDictCam):

        self.shutter_speed =         confDictCam["shutter_speed"]  
        self.resolution =            (confDictCam["resolution_w"], confDictCam["resolution_h"])
        self.iso =                   confDictCam["iso"]
        self.awb_gains =             (confDictCam["awb_red_gain"], confDictCam["awb_blue_gain"])
        self.awb_mode =              confDictCam["awb_modes"]
        self.sharpness =             confDictCam["sharpness"]
        self.brightness =            confDictCam["brightness"]
        self.exposure_modes =        confDictCam["exposure_modes"] 
        self.exposure_compensation = confDictCam["exposure_compensation"] 
        self.drc_strength =          confDictCam["drc_strength"] 
        self.raw_formats =           confDictCam["raw_formats"]
        self.image_denoise =         confDictCam["image_denoise"]  
        self.framerate =             15
        
    #def take_bracket_pictures(self):
        #""" 
        #Returns two images in a list
        #One with normal exposure, and one with 2 stop longer exposure 
        #The aim to to get detail out of shadows/underexposed film
        #Resulting images can be combined on a PC with Hugin's enfuse utility
        #"""
        #old_shutter = self.shutter_speed
        #imgs = []
        #with picamera.array.PiRGBArray(self) as output:
            #self.capture(output, format='bgr')
            #imgs.append( output.array )
            #self.shutter_speed = old_shutter*4
            #output.truncate(0)
            #self.capture(output, format='bgr')
            #imgs.append( output.array )
        #self.shutter_speed = old_shutter
        #return imgs
        
