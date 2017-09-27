# import the necessary packages
from pyimagesearch.tempimage import TempImage

from imutils.video import VideoStream
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import socket
import sys
import curses
from array import array

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="path to the JSON configuration file")
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())
 
# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")
conf = json.load(open(args["conf"]))
client = None

# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)
	
 
# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)

# loop over the frames from the video stream
while True:
	# grab the raw NumPy array representing the image and initialize
	# the timestamp and occupied/unoccupied text
	try:
		frame = vs.read()
		timestamp = datetime.datetime.now()
		text = "Unoccupied"
	 
		# resize the frame, convert it to grayscale, and blur it
		frame = imutils.resize(frame, width=500)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)
	 
		
		#sock.sendto(bytearray(str(frame)), (MCAST_GRP, MCAST_PORT))
		sock.sendto(str(frame), (MCAST_GRP, MCAST_PORT))
		print('sending image')
		
		now = datetime.datetime.now()

		print str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
		
		
	
		# check to see if the frames should be displayed to screen
		if conf["show_video"]:
			# display the security feed
			cv2.imshow("Security Feed", frame)
			key = cv2.waitKey(1) & 0xFF

	except:	
		e = sys.exc_info()[0]
		print( "<p>Error: %s</p>" % e )	
		vs.stop()
		break	

	
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
sock.close()
#curses.endwin()