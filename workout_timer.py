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
			contourCount = len(contours)
			motionDetectedFrameCount += 1
			cnt = contours[0]
			x,y,w,h = cv2.boundingRect(cnt)
			minX = x
			minY = y
			maxX = x + w
			maxY = y + h
			totalX = 0
			totalY = 0
			for contour in contours:
				x,y,w,h = cv2.boundingRect(contour)
				totalX = totalX + x
				totalY = totalY + y
				if x < minX:
					minX = x
				elif y < minY:
					minY = y
				elif (x + w) > maxX:
					maxX = (x + w)
				elif (y + h) > maxY:
					maxY = (y + h)
			# Find the average X and Y coordinates of all contours
			averageX = (totalX / contourCount)
			averageY = (totalY / contourCount)
			# Find the center of the bounding rectangle of the contours
			centerX = (minX + maxX) / 2
			centerY = (minY + maxY) / 2
			# Find the area of the bounding rectangle
			area = (maxX - minX) * (maxY - minY)
			# When the camera moves, the motion may be picked up.  In that case the motion should be ignored.  Usually this causes a large bounding rectangle with an area > 100000 pixels
			if (area < 100000):
#				if (centerX < 213):
#					if (centerY < 160):
#						moveCamera(password, ip, port, 90)
#					elif ((centerY >= 160) and (centerY < 320)):
#						moveCamera(password, ip, port, 4)
#					elif ((centerY >= 320) and (centerY <= 480)):
#						moveCamera(password, ip, port, 92)
#				elif ((centerX >= 213) and (centerX < 426)):
#					if (centerY < 160):
#						moveCamera(password, ip, port, 0)
#					elif ((centerY >= 320) and (centerY <= 480)):
#						moveCamera(password, ip, port, 2)
#				elif ((centerX >= 426) and (centerX <= 640)):
#					if (centerY < 160):
#						moveCamera(password, ip, port, 91)
#					elif ((centerY >= 160) and (centerY < 320)):
#						moveCamera(password, ip, port, 6)
#					elif ((centerY >= 320) and (centerY <= 480)):
#						moveCamera(password, ip, port, 93)
				if (averageX < 213):
					if (averageY < 160):
						moveCamera(password, ip, port, 90)
					elif ((averageY >= 160) and (averageY < 320)):
						moveCamera(password, ip, port, 4)
					elif ((averageY >= 320) and (averageY <= 480)):
						moveCamera(password, ip, port, 92)
				elif ((averageX >= 213) and (averageX < 426)):
					if (averageY < 160):
						moveCamera(password, ip, port, 0)
					elif ((averageY >= 320) and (averageY <= 480)):
						moveCamera(password, ip, port, 2)
				elif ((averageX >= 426) and (averageX <= 640)):
					if (averageY < 160):
						moveCamera(password, ip, port, 91)
					elif ((averageY >= 160) and (averageY < 320)):
						moveCamera(password, ip, port, 6)
					elif ((averageY >= 320) and (averageY <= 480)):
						moveCamera(password, ip, port, 93)
				# Stop any camera movement
				moveCamera(password, ip, port, 1)

			# Draw the average of the contours in yellow
			cv2.rectangle(frame,(averageX,averageY),(averageX,averageY),(000,255,255),10)
			# Draw the center of the bounding rectangle 
			cv2.rectangle(frame,(centerX,centerY),(centerX,centerY),(255,000,255),2)
			# Draw the bounding rectangle
			cv2.rectangle(frame,(minX,minY),(maxX,maxY),(255,000,255),2)
			# Play a sound to alert the user of motion detected
			#if not mute:
			#	os.system("aplay beep.wav")

		#cv2.rectangle(fgmask,(5,5),(50,50),(255,000,255),2)
		cv2.imshow('Video',frame)
	cap.release()
	cv2.destroyWindow('Video')

def retrieveFromDatabase(value, camera):
	# Get value from database
	queryText = 'SELECT ' + value + ' FROM cameras WHERE name = "' + camera + '";'
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
