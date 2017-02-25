#!/usr/bin/env python

###################################################################
# This file is a modification of the file "tc-run.py" from the    #
#  RPi Telecine project.  I've included that project's header and #
#  copyright below.                                               #  
###################################################################
#
# RPi Telecine - Run the telecine job
#
# Usage: python tc-run job_name -s|--start [start_frame] -e|--end[end_frame] 
#
# Command line options:
# -s, --start           Start frame counter
# -e, --end             End counter
#
# Writing the images is done in a concurrent thread to the picture taking and
# film transport. 
#
# This script runs in command line only, so can be run in a Screen session, allowing
# it to run autonomously.
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


from __future__ import division

import argparse
import os
import time
import cv2
import io
import numpy as np
from s8s_common import *

reel_name       = ''
ini_name        = '/mnt/Terabytes/Projects/super8scan/PostProc/postproc.ini'
source_dir_path = '/mnt/Terabytes/Projects/Media8mm/Captures/'
source_dir_full = ''
dest_dir_path   = '/mnt/Terabytes/Projects/Media8mm/CroppedTiffs/'
dest_dir_full   = ''

step_num = 0
wh_pixels = 0
socket_midY = 0
count_reads = 0
count_writes = 0
count_pxlwhitelow = 0
count_pxlwhitehigh = 0
count_cntrlow = 0
count_cntrhigh = 0
   
def parse_commandline():
    # Command line arguments
    global reel_name

    parser = argparse.ArgumentParser()
    parser.add_argument('reelname', help='Name of the tiff cropping job')
    args = parser.parse_args()    
    reel_name = args.reelname
    
def getBayer(jpeg_name):     
    """ 
    Returns an openCV compatible 10 bit greyscale image
    """ 
    
    # offset is used to grab the 1952 x 3264 bytes of file - the bayer data
    offset = 6371328
    ver = 1
    
    data = np.fromfile(open(jpeg_name, 'rb'), np.dtype(np.uint8))
    data = data[-offset:]
    
    # For the V1 module, the data consists of 1952 rows of 3264 bytes of data.
    # The last 8 rows of data are unused (they only exist because the maximum
    # resolution of 1944 rows is rounded up to the nearest 16).
    #
    # For the V2 module, the data consists of 2480 rows of 4128 bytes of data.
    # There's actually 2464 rows of data, but the sensor's raw size is 2466
    # rows, rounded up to the nearest multiple of 16: 2480.
    #
    # Likewise, the last few bytes of each row are unused (why?). Here we
    # reshape the data and strip off the unused bytes.
    
    reshape, crop = {
        1: ((1952, 3264), (1944, 3240)),
        2: ((2480, 4128), (2464, 4100)),
        }[ver]
    data = data.reshape(reshape)[:crop[0], :crop[1]]
    
    # Horizontally, each row consists of 10-bit values. Every four bytes are
    # the high 8-bits of four values, and the 5th byte contains the packed low
    # 2-bits of the preceding four values. In other words, the bits of the
    # values A, B, C, D and arranged like so:
    #
    #  byte 1   byte 2   byte 3   byte 4   byte 5
    # AAAAAAAA BBBBBBBB CCCCCCCC DDDDDDDD AABBCCDD
    #
    # Here, we convert our data into a 16-bit array, shift all values left by
    # 2-bits and unpack the low-order bits from every 5th byte in each row,
    # then remove the columns containing the packed bits
    
    data = data.astype(np.uint16) << 2
    for byte in range(4):
        data[:, byte::5] |= ((data[:, 4::5] >> ((4 - byte) * 2)) & 0b11)
    data = np.delete(data, np.s_[4::5], 1)
    
    return data

def crop_image(img_name):
    # Reads one demosaiced img tiff previously created by dcraw
    #   and the original raw capture.  Relocates perf in capture and uses
    #   center of socket on greyscale raw to crop the demosaiced tiff
    
    global cnf, pf, source_dir_full, dest_dir_full
    global count_reads, count_writes, count_pxlwhitehigh, count_pxlwhitelow, count_cntrhigh, count_cntrlow
    
    tiff_name = os.path.join(source_dir_full, img_name)
    jpeg_name = tiff_name
    jpeg_name = jpeg_name.replace("tiff", "jpeg")
    mod_img_name = 'Crop-' + img_name
    outfile_name = os.path.join(dest_dir_full, mod_img_name)
    
    tiff_img = cv2.imread(tiff_name) 
    count_reads = count_reads + 1
    
    bayerdata = getBayer(jpeg_name)
    
    step_num, socket_midY, wh_pixels  = pf.perf_analyze(bayerdata)
    
    # If perf_analyze function couldn't find valid perf skip crop & save
    if step_num > 6000:
        print(os.path.basename(outfile_name),',', socket_midY, ',', wh_pixels, ',', step_num, 'Skipped')
        if step_num == 9999:
            count_pxlwhitelow = count_pxlwhitelow + 1
        elif step_num == 8888:
            count_pxlwhitelhigh = count_pxlwhitehigh + 1
        elif step_num == 7777:
            count_cntrlow = count_cntrlow + 1
        elif step_num == 6666:
            count_cntrhigh = count_cntrhigh + 1 
        return
        
    cropped_img = pf.perf_cropper(tiff_img)
    cv2.imwrite(outfile_name, cropped_img)
    count_writes = count_writes + 1
    print(os.path.basename(outfile_name),',', socket_midY, ',', wh_pixels, ',', step_num)
    
def nothing(x):
    pass
    
def check_crop(testing_image):
    tiff_name = os.path.join(source_dir_full, testimg_name)
    jpeg_name = tiff_name
    jpeg_name = jpeg_name.replace("tiff", "jpeg")
    
    tiff_img = cv2.imread(tiff_name)     
    bayerdata = getBayer(jpeg_name)    
    step_num, socket_midY, wh_pixels  = pf.perf_analyze(bayerdata)
    
    scale_img = cv2.resize(tiff_img,(960, 720), interpolation = cv2.INTER_AREA)
    working_scale_img = scale_img.copy()
    
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('CX','image',128,255,nothing)
    cv2.createTrackbar('CY','image',128,255,nothing)
    cv2.createTrackbar('RX','image',128,255,nothing)
    cv2.createTrackbar('RY','image',128,255,nothing)
    # create switch for ON/OFF functionality
    switch = '0 : HALT \n1 : RUN'
    cv2.createTrackbar(switch, 'image',0,1,nothing)

    while(1):
        cv2.imshow('image', working_scale_img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            if go_flag == 0:
                break
            else:
                pf.cropXOrigin = pf.cropXOrigin + (cx_delta-128)
                pf.perf_shift  = pf.perf_shift - (cy_delta - 128)
                pf.westXROI    = pf.westXROI  + (rx_delta-128)
                pf.eastXROI    = pf.westXROI + pf.incrXROI
                pf.northYROI   = pf.northYROI - (ry_delta-128)
                pf.southYROI   = pf.northYROI + pf.incrYROI
                break
    
        # get current positions of trackbars
        cx_delta = cv2.getTrackbarPos('CX','image')
        cy_delta = cv2.getTrackbarPos('CY','image')
        rx_delta = cv2.getTrackbarPos('RX','image')
        ry_delta = cv2.getTrackbarPos('RY','image')
        s = cv2.getTrackbarPos(switch,'image')
        
        CrectX1 = cnf.confDictPerfCrop["cropxorigin"] + (cx_delta - 128)
        CrectX2 = CrectX1 + cnf.confDictPerfCrop["cropxwidth"]
        CYband  = cnf.confDictPerfCrop["cropyband"]
        CrectY1 = socket_midY - CYband - pf.perf_shift + (cy_delta - 128)
        CrectY2 = socket_midY + CYband - pf.perf_shift + (cy_delta - 128)
        CrectX1 = int(round(CrectX1 / 2.7))
        CrectX2 = int(round(CrectX2 / 2.7))
        CrectY1 = int(round(CrectY1 / 2.7))
        CrectY2 = int(round(CrectY2 / 2.7))
        
        RrectX1 = cnf.confDictPerfCrop["westxroi"] + (rx_delta - 128)
        RrectX2 = RrectX1 + cnf.confDictPerfCrop["incrxroi"]
        RrectY1 = cnf.confDictPerfCrop["northyroi"] + (ry_delta - 128)
        RrectY2 = RrectY1 + cnf.confDictPerfCrop["incryroi"]
        RrectX1 = int(round(RrectX1 / 2.7))
        RrectX2 = int(round(RrectX2 / 2.7))
        RrectY1 = int(round(RrectY1 / 2.7))
        RrectY2 = int(round(RrectY2 / 2.7))

        working_scale_img = scale_img.copy()
        cv2.rectangle(working_scale_img,(CrectX1, CrectY1),(CrectX2, CrectY2),(0,0,255),2)
        cv2.rectangle(working_scale_img,(RrectX1, RrectY1),(RrectX2, RrectY2),(0,0,255),2)
     
        if s == 0:
            go_flag = 0
        else:
            go_flag = 1

    cv2.destroyAllWindows()
     
    return(go_flag)
     
if __name__ == '__main__':
    
    parse_commandline()
    cnf.read_configfile(ini_name)    
    pf.setup_perf(cnf.confDictPerfCrop)
    
    source_dir_full = os.path.join(source_dir_path, reel_name)
    dest_dir_full  = os.path.join(dest_dir_path, reel_name)
    
    # Create directory for cropped tiffs if it doesn't already exist

    if not os.path.exists(dest_dir_full):
        try:
            os.mkdir(dest_dir_full)
        except:
            print('Error creating cropped-tiff directory: %s'%dest_dir_full)
            quit()
    if not os.path.isdir(dest_dir_full):
        print('%s is a file not a directory'%dest_dir_full)
        quit()
        
    # Read in first image and display with crop borders for review
        
    for testimg_name in os.listdir(source_dir_full):
        if testimg_name.endswith(".tiff"):
            go_flag = check_crop(testimg_name)
            if go_flag == 0:
                exit()
            else:
                break

    # Iterate through all tiffs in directory and...     
    for img_name in os.listdir(source_dir_full):
        if img_name.endswith(".tiff"):
            crop_image(img_name)


    print('##################')
    print('Images Read:      ', count_reads)
    print('Images Written:   ', count_writes)
    print('------------------')
    print('Pixel Count Low:  ', count_pxlwhitelow)
    print('Pixel Count High: ', count_pxlwhitehigh)
    print('Socket Low:       ' , count_cntrlow)
    print('Socket High:      ', count_cntrhigh)
    
