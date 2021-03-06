# import the necessary packages
from pyimagesearch.tempimage import TempImage
#from dropbox.client import DropboxOAuth2FlowNoRedirect
#from dropbox.client import DropboxClient
import dropbox

#from pyimagesearch.gmailScript import gmail

#from picamera.array import PiRGBArray
from imutils.video import VideoStream
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
 
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

#s = gmail()

#s.SendMessage("tonypacheco333@gmail.com", "agustinleira1@hotmail.com", "Inicio de sistema", "Inicio", "Se ha establecido inicio de sistema")
#s.main()

if conf["use_dropbox"]:
	# connect to dropbox and start the session authorization process
	#flow = DropboxOAuth2FlowNoRedirect(conf["dropbox_key"], conf["dropbox_secret"])
	#print "[INFO] Authorize this application: {}".format(flow.start())
	#authCode = raw_input("Enter auth code here: ").strip()
 
	# finish the authorization and grab the Dropbox client
	#(accessToken, userID) = flow.finish(authCode)
	#client = DropboxClient(accessToken)
	#print "[SUCCESS] dropbox account linked"
	client = dropbox.Dropbox(conf["access_token"])
	
	print client.users_get_current_account()

# initialize the video stream and allow the cammera sensor to warmup
vs = VideoStream(usePiCamera=args["picamera"] > 0).start()
time.sleep(2.0)
	
	# initialize the camera and grab a reference to the raw camera capture
#camera = PiCamera()
#camera.resolution = tuple(conf["resolution"])
#camera.framerate = conf["fps"]
#rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
 
# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

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
	 
		# if the average frame is None, initialize it
		if avg is None:
			print "[INFO] starting background model..."
			avg = gray.copy().astype("float")
			#rawCapture.truncate(0)
			continue
	 
		# accumulate the weighted average between the current frame and
		# previous frames, then compute the difference between the current
		# frame and running average
		cv2.accumulateWeighted(gray, avg, 0.5)
		frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
		
		# threshold the delta image, dilate the thresholded image to fill
		# in holes, then find contours on thresholded image
		thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
			cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
	 
		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < conf["min_area"]:
				continue
	 
			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			text = "Occupied"
	 
		# draw the text and timestamp on the frame
		ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
		cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.35, (0, 0, 255), 1)
			
			# check to see if the room is occupied
		if text == "Occupied":
			# check to see if enough time has passed between uploads
			if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
				# increment the motion counter
				motionCounter += 1
	 
				# check to see if the number of frames with consistent motion is
				# high enough
				if motionCounter >= conf["min_motion_frames"]:
					# check to see if dropbox sohuld be used
					if conf["use_dropbox"]:
						# write the image to temporary file
						t = TempImage()
						cv2.imwrite(t.path, frame)
	 					now = datetime.datetime.now()
						nts = str(now.year) + '_' +( '0' + str(now.month)  if now.month < 10 else str(now.month) ) + '_' +( '0' + str(now.day) if now.day < 10 else str(now.day)) + '_' +( '0' + str(now.hour) if now.hour < 10 else str(now.hour) )  + '_' +( '0' + str(now.minute) if now.minute < 10 else str(now.minute) ) + '_' +( '0' + str(now.second) if now.second < 10 else str(now.second) ) + '_' +str(now.microsecond)
						# upload the image to Dropbox and cleanup the tempory image
						print "[UPLOAD] {}".format(ts)
						print nts
						path = "/{base_path}/{timestamp}.jpg".format(
							base_path=conf["dropbox_base_path"], timestamp=nts)
						#client.put_file(path, open(t.path, "rb"))
						client.files_upload(open(t.path, "rb"),path)
						t.cleanup()
	 
					# update the last uploaded timestamp and reset the motion
					# counter
					lastUploaded = timestamp
					motionCounter = 0
	 
		# otherwise, the room is not occupied
		else:
			motionCounter = 0
			
		# check to see if the frames should be displayed to screen
		if conf["show_video"]:
			# display the security feed
			cv2.imshow("Security Feed", frame)
			key = cv2.waitKey(1) & 0xFF
			# if the `q` key is pressed, break from the lop
			if key == ord("q"):
				break
	
		# clear the stream in preparation for the next frame
		#rawCapture.truncate(0)
	except Exception as value:	
		print('An error occured.',value)
	
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()