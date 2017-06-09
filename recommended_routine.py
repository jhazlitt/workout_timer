import os
import time

def timer(waitTime):
	while (waitTime > 0):
		os.system('clear')
		print waitTime
		waitTime -= 1
		time.sleep(1)

secondWait = 90

lines = open('workout_list.txt')

for line in lines:
	print line
	userInput = raw_input('Continue?')
	#os.system('mpg123 party_horn.mp3')
	os.system('clear')
	timer(secondWait)	
	os.system('aplay doorbell.wav')
	os.system('clear')

os.system('mpg123 tada.mp3')
os.system('clear')
print('Workout complete!')
