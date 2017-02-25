###################################################################
# This file is a modification of the file "config.py" from the    #
#  RPi Telecine project.  I've included that project's header and #
#  copyright below.                                               #  
###################################################################
# RPi Telecine Configuration
#
# Config file handling for the telecine scripts 
# Provides for reading and writing the job's ini file
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

import os
import configparser


class s8sConfig():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.confDictCam = {}
        self.confDictPerfCrop = {}
         
    def read_configfile(self,cfg_name):
        self.configname = cfg_name
            
        # Read job config file - so we retain existing settings
        cnf_file = self.config.read([os.path.expanduser(self.configname)])
        
        section = 'Camera'        
        if section not in self.config.sections():
            self.config.add_section(section)
        options = self.config.options(section)
        
        if 'shutter_speed' in options:
            self.confDictCam["shutter_speed"] =         self.config.getint(section,  'shutter_speed')
        if 'resolution_w' in options:
            self.confDictCam["resolution_w"] =            self.config.getint(section,     'resolution_w')
        if 'resolution_h' in options:
            self.confDictCam["resolution_h"] =            self.config.getint(section,     'resolution_h')
        if 'iso' in options:
            self.confDictCam["iso"] =                   self.config.getint(section,  'iso')
        if 'awb_modes' in options:
            self.confDictCam["awb_modes"] =             self.config.get(section,     'awb_modes')      
        if 'awb_red_gain' in options:
            self.confDictCam["awb_red_gain"] =          self.config.getfloat(section,'awb_red_gain')
        if 'awb_blue_gain' in options:
            self.confDictCam["awb_blue_gain"] =         self.config.getfloat(section,'awb_blue_gain')
        if 'sharpness' in options:
            self.confDictCam["sharpness"] =             self.config.getint(section,  'sharpness')
        if 'brightness' in options:
            self.confDictCam["brightness"] =            self.config.getint(section,  'brightness')
        if 'exposure_modes' in options:
            self.confDictCam["exposure_modes"] =        self.config.get(section,     'exposure_modes')
        if 'exposure_compensation' in options:
            self.confDictCam["exposure_compensation"] = self.config.getint(section,  'exposure_compensation')
        if 'drc_strength' in options:
            self.confDictCam["drc_strength"] =          self.config.get(section,     'drc_strength')
        if 'raw_formats' in options:
            self.confDictCam["raw_formats"] =           self.config.get(section,     'raw_formats')
        if 'image_denoise' in options:
            self.confDictCam["image_denoise"] =         self.config.get(section,     'image_denoise') 
                              
        sectionP = 'PerfCrop'        
        if sectionP not in self.config.sections():
            self.config.add_section(sectionP)
        optionsP = self.config.options(sectionP)
        
        if 'westxroi' in optionsP:
            self.confDictPerfCrop["westxroi"] =    self.config.getint(sectionP,'westxroi')
        if 'incrxroi' in optionsP:
            self.confDictPerfCrop["incrxroi"] =    self.config.getint(sectionP,'incrxroi')
        if 'northyroi' in optionsP:
            self.confDictPerfCrop["northyroi"] =           self.config.getint(sectionP, 'northyroi')
        if 'incryroi' in optionsP:
            self.confDictPerfCrop["incryroi"] =           self.config.getint(sectionP, 'incryroi')
        if 'pixelsperstep' in optionsP:
            self.confDictPerfCrop["pixelsperstep"] =           self.config.getfloat(sectionP, 'pixelsperstep')
        if 'minwhitepixels' in optionsP:
            self.confDictPerfCrop["minwhitepixels"] =        self.config.getint(sectionP, 'minwhitepixels')
        if 'maxwhitepixels' in optionsP:
            self.confDictPerfCrop["maxwhitepixels"] =        self.config.getint(sectionP, 'maxwhitepixels')
        if 'sprocketcntrdist' in optionsP:
            self.confDictPerfCrop["sprocketcntrdist"] =      self.config.getint(sectionP, 'sprocketcntrdist')
        if 'cropxorigin' in optionsP:
            self.confDictPerfCrop["cropxorigin"] =        self.config.getint(sectionP, 'cropxorigin')
        if 'cropxwidth' in optionsP:
            self.confDictPerfCrop["cropxwidth"] =        self.config.getint(sectionP, 'cropxwidth')
        if 'cropyband' in optionsP:
            self.confDictPerfCrop["cropyband"] =      self.config.getint(sectionP, 'cropyband')
        

