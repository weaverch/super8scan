#####################################################################
# Finds center Y value of perforation by thresholding thin vertical #
#  slice and averaging the Y value of white pixels.  Works on film  #
#  with black background probably not if translucent                #
#####################################################################

# Python 2/3 compatibility
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2

class s8sPerforation:
        
    def __init__(self):
        self.westXROI         = 0
        self.incrXROI         = 0
        self.eastXROI         = 0
        self.northYROI        = 0
        self.incrYROI         = 0
        self.southYROI        = 0
        
        self.meanYROI         = 0
        self.meanYImage       = 0

        self.pixelsPerStep    = 0  
        self.numsteps         = 0
        self.minWhitePixels   = 0
        self.maxWhitePixels   = 0
        self.sprocketCntrDist = 0
        
        self.cropXOrigin      = 0
        self.cropXWidth       = 0
        self.cropYBand        = 0
        
    def setup_perf(self,confDictPerfCrop):

        self.westXROI           = confDictPerfCrop["westxroi"]
        self.incrXROI           = confDictPerfCrop["incrxroi"]
        self.eastXROI           = self.westXROI + self.incrXROI
        self.northYROI          = confDictPerfCrop["northyroi"]
        self.incrYROI           = confDictPerfCrop["incryroi"]
        self.southYROI          = self.northYROI + self.incrYROI
        self.pixelsPerStep      = confDictPerfCrop["pixelsperstep"]
        self.minWhitePixels     = confDictPerfCrop["minwhitepixels"]
        self.maxWhitePixels     = confDictPerfCrop["maxwhitepixels"]
        self.sprocketCntrDist   = confDictPerfCrop["sprocketcntrdist"]
        self.cropXOrigin        = confDictPerfCrop["cropxorigin"]
        self.cropXWidth         = confDictPerfCrop["cropxwidth"]
        self.cropYBand          = confDictPerfCrop["cropyband"]
       
    def perf_analyze(self, img):
        # Set ROI for perforation search
        self.imgHeight = np.size(img, 0)
        self.halfHeight = int(round(self.imgHeight / 2))
        self.imgWidth = np.size(img, 1)
        myroi = img[self.northYROI:self.southYROI, self.westXROI:self.eastXROI]

        myroi8 = np.zeros([self.incrYROI, self.incrXROI], dtype=np.uint8)
        cv2.convertScaleAbs(myroi, myroi8)
        retval, myroiblurthresh = cv2.threshold(myroi8, 230, 255, cv2.THRESH_BINARY)
        pixelsWhite = np.where(myroiblurthresh == 255)
        if pixelsWhite[0].size > 0:
            self.meanYROI = int(np.mean(pixelsWhite[0]))
        else:
            self.meanYROI = 0
        self.meanYImage = self.meanYROI + self.northYROI
        
        if pixelsWhite[0].size < self.minWhitePixels:
            self.numsteps = 9999
            self.meanYImage = 9999
        elif pixelsWhite[0].size > self.maxWhitePixels:
            self.numsteps = 8888
            self.meanYImage = 8888
        elif (self.meanYImage - self.cropYBand) < 1:
            self.numsteps = 7777
            self.meanYImage = 7777
        elif (self.meanYImage + self.cropYBand) > self.imgHeight:
            self.numsteps = 6666
            self.meanYImage = 6666
        else:
            step_increment = int(round(((-self.halfHeight + self.meanYImage) \
            / self.pixelsPerStep)))
            self.numsteps = self.sprocketCntrDist + step_increment
        
        return self.numsteps, self.meanYImage, pixelsWhite[0].size
