#!/usr/bin/python3
# capture-noir.py - Records a sequence of images and stores them to:
#   ../data/recording/image<i>.jpg

import picamera
import time
import os

dirname = 'recording'
os.mkdir(dirname)
with picamera.PiCamera() as camera:
    camera.start_preview()
    time.sleep(2) # time for camera to warm up
    print('recording ... be still')
    camera.capture_sequence([
        '%s/image%d.jpg' % (dirname,i,)
        for i in range(600)],
	use_video_port=True # use video port to capture images
	)
    camera.stop_preview()

# send the recording
os.system('scp -r /home/pi/recording marko@192.168.178.33:/home/marko/Documents/general/repos/ppg-based-estimation/data/')
os.system('rm -r /home/pi/recording')
