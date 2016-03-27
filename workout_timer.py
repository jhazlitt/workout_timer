# Commands to move the camera
#PTZ_STOP=1
#TILT_UP=0
#TILT_UP_STOP=1
#TILT_DOWN=2
#TILT_DOWN_STOP=3
#PAN_LEFT=4
#PAN_LEFT_STOP=5
#PAN_RIGHT=6
#PAN_RIGHT_STOP=7
#PTZ_LEFT_UP=90
#PTZ_RIGHT_UP=91
#PTZ_LEFT_DOWN=92
#PTZ_RIGHT_DOWN=93
#PTZ_CENTER=25
#PTZ_VPATROL=26
#PTZ_VPATROL_STOP=27
#PTZ_HPATROL=28
#PTZ_HPATROL_STOP=29

import numpy as np
import cv2
import sqlite3
import urllib
import time
import os
#from Tkinter import *

def runCamera(cameraName):
	# Get camera values from database
	ip = retrieveFromDatabase("ip", cameraName)
	port = retrieveFromDatabase("port", cameraName)
	password = retrieveFromDatabase("password", cameraName)

	# Create camera url
	mpegURL = "http://" + ip + ":" + port + "/videostream.asf?user=admin&pwd=" + password + "&resolution=32&rate=0&.mpg"

	# Specify the video to be captured
	cap = cv2.VideoCapture(mpegURL)

	fourcc = cv2.cv.CV_FOURCC(*'XVID')

	fgbg = cv2.BackgroundSubtractorMOG()

	motionDetectedFrameCount = 0
	# While the camera is recording
	while(True):
		# Check for any keys that were pressed
		k = cv2.waitKey(30) & 0xff

		if k == ord('q') or k == 27:
			break
		elif k == ord('k'):
			# Generate a new background
			fgbg = cv2.BackgroundSubtractorMOG()
		elif k == ord('m'):
			mute = not mute 
		elif k == ord('w'):
			# Move camera up
			moveCamera(password, ip, port, 0)
		elif k == ord('a'):
			# Move camera left
			moveCamera(password, ip, port, 4)
		elif k == ord('s'):
			# Move camera down
			moveCamera(password, ip, port, 2)
		elif k == ord('d'):
			# Move camera right	
			moveCamera(password, ip, port, 6)
		# Stop any camera movement
		moveCamera(password, ip, port, 1)

		# Read the current frame from the camera
		ret, frame = cap.read()

		# If there has been motion detected for more than a specified number of frames, generate a new mask
		if motionDetectedFrameCount > 1:
			fgbg = cv2.BackgroundSubtractorMOG()
			motionDetectedFrameCount = 0

		# Apply the mask to the frame
		fgmask = fgbg.apply(frame)
		kernel = np.ones((5,5),np.uint8)	
		fgmask = cv2.erode(fgmask,kernel,iterations = 1)
		fgmask = cv2.dilate(fgmask,kernel,iterations = 5)
		
		# Find differences between the mask and frame, if any.  These are called contours
		contours, hierarchy = cv2.findContours(fgmask,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

		# If there are no contours an error will be thrown.  If there are contours:
		if len(contours) != 0:
			motionDetectedFrameCount += 1
			#motionDetected = True
			cnt = contours[0]
			x,y,w,h = cv2.boundingRect(cnt)
			minX = x
			minY = y
			maxX = x + w
			maxY = y + h
			for contour in contours:
				x,y,w,h = cv2.boundingRect(contour)
				if x < minX:
					minX = x
				elif y < minY:
					minY = y
				elif (x + w) > maxX:
					maxX = (x + w)
				elif (y + h) > maxY:
					maxY = (y + h)
			# Draw a target around the motion detected
			centerX = (minX + maxX) / 2
			centerY = (minY + maxY) / 2
			cv2.rectangle(frame,(centerX,centerY),(centerX,centerY),(255,000,255),2)
			cv2.rectangle(frame,(minX,minY),(maxX,maxY),(255,000,255),2)
		cv2.rectangle(fgmask,(5,5),(50,50),(255,000,255),2)
			# Play a sound to alert the user of motion detected
			#if not mute:
			#	os.system("aplay beep.wav")

			# Record movement time of occurrence in log
			#if (motionDetectedTimestamp != time.asctime(time.localtime())):
			#	motionDetectedTimestamp = time.asctime(time.localtime())
			#	logTimestamp()
	
		# Put text over video frame
		# Put a timestamp on the video frame
		#font = cv2.FONT_HERSHEY_SIMPLEX
		#cv2.putText(frame,str(time.asctime(time.localtime())),(0,25), font, 1, (0,0,0), 7)
		#cv2.putText(frame,str(time.asctime(time.localtime())),(0,25), font, 1, (255,255,255), 2)
		# Add MUTE text if the program is muted
		#if mute:
		#	cv2.putText(frame,"MUTE",(555,475), font, 1, (0,0,255), 4)

		# Show the frame, and write it to the .avi file
		cv2.imshow('Video',fgmask)
		#out.write(frame)

		# Find how long the routine has been running for
		#endTime = time.time() 
		#elapsedTime = endTime - startTime

		# Save the video after a specified number of seconds
		#if elapsedTime >= 60:
		#	out.release()
			
			# If there was motion detected during the recording, move on to the next video number.  Otherwise write over this video
			# If there are more than a specified number of videos, the count is set back to 1 so they can all be written over
		#	if (videoNumber == 150) and (motionDetected == True):
		#		motionDetected = False
		#		videoNumber = 1
		#	elif motionDetected == True:
		#		motionDetected = False
		#		videoNumber += 1

	#		out = getOutputFile(fileSaveDirectory, videoNumber, fourcc); 
	#		startTime = time.time()
	cap.release()
	#out.release()
	cv2.destroyWindow('Video')

def getOutputFile(fileSaveDirectory, videoNumber, fourcc):
	outputFile = cv2.VideoWriter(str(fileSaveDirectory) + str(videoNumber) + '.avi',fourcc, 12, (640,480))
	return outputFile

def logTimestamp():
	queryText = 'INSERT INTO log (timestamp) VALUES ("' + time.asctime(time.localtime()) + '");'
	c.execute(queryText)
	conn.commit()

def retrieveFromDatabase(value, camera):
	# Get value from database
	queryText = 'SELECT ' + value + ' FROM cameras WHERE name = "' + camera + '";'
	result = c.execute(queryText)
	# Strip extra characters from the query result
	for value in result:
		value = str(value)
		value = value[3:len(value)-3]
	return value

def retrieveDirectoryFromDB():
	# Get value from database
	queryText = 'SELECT directory FROM save_directory;'
	result = c.execute(queryText)
	# Strip extra characters from the query result
	for value in result:
		value = str(value)
		value = value[3:len(value)-3]
	return value
	
def moveCamera(password, ip, port, direction):
	direction = str(direction)
	moveURL = "http://admin:" + password + "@" + ip + ":" + port + "/decoder_control.cgi?command=" + direction + ""
	urllib.urlopen(moveURL)

# Connect to database
conn = sqlite3.connect('/home/john/opencv_database.db')
c = conn.cursor()

runCamera('camera1')
