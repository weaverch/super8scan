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
import numpy as np
import serial
import io
import csv

from s8s_common import *

job_name = ''
start_frame = 0
end_frame = 0
frames_count = 0
current_frame = 0
capture_ext = 'jpeg'
fileSaveParams = []
step_num = 0
wh_pixels = 0
socket_midY = 0
csv_file = ''
csv_columns = ["Frame", "Steps", "Line", "Wh Pixs"]
data_list = []
data_list_row = []
s8s_cfgfile = "s8sconfig.ini" 

    
def motors_off():
    ser.write(b"X0E")   
    
def frame_advance(numsteps):
    frame_advance_string = 'S{}E'.format(numsteps)
    ser.write(frame_advance_string.encode())
        
def frame_reverse():
    pass
    
def parse_commandline():
    # Command line arguments
    global job_name, start_frame, end_frame, frames_count
    global current_frame, capture_direction, capture_ext, reverse#, brackets
    parser = argparse.ArgumentParser()
    parser.add_argument('jobname', help='Name of the telecine job')
    parser.add_argument('-s','--start', type=int, help='Start frame number')
    parser.add_argument('-e','--end', type=int, help='End frame number')

    args = parser.parse_args()
    
    job_name = args.jobname

    start_frame = args.start if args.start else 0
    end_frame = args.end if args.end else 0
    frames_count = abs(end_frame - start_frame)+1
    if frames_count==0:
        print('Job needs to know how many frames')
        quit()
    current_frame = start_frame

job_finished = False
still_writing = True

failed_frames = 0

taking_time = Stopwatch()
taking_times = []

def take_picture(fname):     
    """ 
    This function is taken from the Picamera module documentation
    Returns an openCV compatible 10 bit greyscale image 
    """
    stream = io.BytesIO()

    # Capture the image, including the Bayer data
    cam.capture(stream, format='jpeg', bayer=True)
    ver = {
        'RP_ov5647': 1,
        'RP_imx219': 2,
        }[cam.exif_tags['IFD0.Model']]
    
    # Extract the raw Bayer data from the end of the stream, check the
    # header and strip if off before converting the data into a numpy array
    
    capturedata = stream.getvalue()
    capturedatanp = np.fromstring(capturedata, dtype=np.uint8)
    
    # Save the entire jpeg capture with bayer data
    
    with open(fname, 'wb') as fcapt:
        capturedatanp.tofile(fcapt)
    
    # Pull out the greyscale bayer data to do perf analysis
    
    offset = {
        1: 6404096,
        2: 10270208,
        }[ver]
        
    data = stream.getvalue()[-offset:]
    assert data[:4] == b'BRCM'
    data = data[32768:]
    data = np.fromstring(data, dtype=np.uint8)
    
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

def single_picture(current_frame):
    # Takes one picture and sends it look for perforation
    # If there is problem with perf step_num variable will return
    #   set to high value and job will stop
    # Image is saved to disk in take_picture so nothing left to do
    global cnf, capture_ext,fpath,failed_frames, job_name
    global taking_time, taking_times
    fname = job_name + '-{:05d}.{}'.format(current_frame,capture_ext)
    fname = os.path.join(fpath,fname)
    taking_time.start()
    
    #img is our 16 bit grayscale bayer data
    
    img = take_picture(fname)
    t = taking_time.stop()
    taking_times.append(t)
    
    step_num, wh_pixels, socket_midY = pf.perf_analyze(img)
    print('Frame ', current_frame, " step_info: ", step_num, wh_pixels, socket_midY)
    data_list_row = [current_frame, step_num, wh_pixels, socket_midY]
    data_list.append(data_list_row)
    
    if step_num > 6000:
        failed_frames = 6
        return


    write_time = Stopwatch()
    write_time.start()
    tprint=write_time.stop()
    
    frame_advance(step_num)
    
    #  Wait for Arduino to signal that stepper advance is done
    while True:
        if(ser.inWaiting() == 0):
            pass
        else:
            time.sleep(1.0)
            break       
                
def WriteListToCSV(csv_file,csv_columns,data_list):
    #global csv_file, csv_columns, data_list

    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(csv_columns)
        for data in data_list:
            writer.writerow(data)

    
        
def run_job():
    global q, job_finished
    global cnf,job_name
    global fpath, step_num
    global pf, cam
    global failed_frames
    global current_frame, start_frame, end_frame
    global csv_file, csv_columns, data_list
    
    max_fails = 5 # Maximum number of adjacent failed perforation detections
    
    job_time = Stopwatch()
    job_time.start()
    job_finished = False

    try:
        time.sleep(2)
        cam.setup_cam(cnf.confDictCam)
        pf.setup_perf(cnf.confDictPerfCrop)
        frame_time = Stopwatch()
        frame_times = []
        
        for current_frame in range(start_frame,end_frame):
            frame_time.start() # Start timing
            taking_time.start()

            single_picture(current_frame)

            if failed_frames >= max_fails:
                print('Perf or Crop Error: ', step_num)
                break

            tprint = frame_time.stop()
            frame_times.append(tprint)
    finally:
        motors_off()
        cam.close()
        WriteListToCSV(csv_file,csv_columns,data_list)
        job_finished = True        

    jt = job_time.stop()
    minutes = jt // 60
    seconds = jt % 60
    job_finished = True                
    ave_per_frame = sum(frame_times) / len(frame_times)
    ave_camera_time = sum(taking_times) / len(taking_times)
    # Some stats
    print(" ")
    print('%d frames'%(len(frame_times)))
    print('Elapsed time {:.0f} mins {:.1f} secs'.format(minutes,seconds))
    print('Average time per frame: {:.2f} secs'.format(ave_per_frame))
    print('Fastest frame: {:.2f} secs'.format(min(frame_times)))
    print('Slowest frame: {:.2f} secs'.format(max(frame_times)))
    print('Average camera time per frame: {:.2f} secs'.format(ave_camera_time))
    print('Fastest frame: {:.2f} secs'.format(min(taking_times)))
    print('Slowest frame: {:.2f} secs'.format(max(taking_times)))
    
  
if __name__ == '__main__':
    
    ser = serial.Serial('/dev/ttyACM0', 115200)
    parse_commandline()
    cnf.read_configfile(s8s_cfgfile)
    
    csv_file = os.path.join('.',job_name, job_name + '.csv')
    
    # Create capture directory if it doesn't already exist
    fpath = os.path.join('.',job_name)
    if not os.path.exists(fpath):
        try:
            os.mkdir(fpath)
        except:
            print('Error creating capture directory: %s'%fpath)
            quit()
    if not os.path.isdir(fpath):
        print('%s is a file not a directory'%fpath)
        quit()

    run_job()
    
    
