#!/bin/sh
# Just calls Raspistill to show the camera preview
# Useful for setting focus
raspistill -w 2592 -h 1944 -p 50,700,400,300 -awb auto -k  -ss 10000 -ex off -t 9000
