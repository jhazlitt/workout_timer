import os
import time

def clearScreen():
	os.system('clear')
	
def playSound():
	os.system('aplay doorbell.wav')

def timer(waitTime):
	while (waitTime > 0):
		os.system('clear')
		print waitTime
		waitTime -= 1
		time.sleep(1)

secondWait = 90

# Pause for 90 seconds before beginning the workout
timer(secondWait)
playSound()
clearScreen()

lines = open('workout_list.txt')

for line in lines:
	print line
	userInput = raw_input('Continue?')
	if userInput == 'skip':
		os.system('clear')
		continue
	#os.system('mpg123 party_horn.mp3')
	os.system('clear')
	timer(secondWait)	
	playSound
	clearScreen()

os.system('mpg123 tada.mp3')
os.system('clear')
print('Workout complete!')
