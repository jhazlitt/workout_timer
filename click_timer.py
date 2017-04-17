import math
import os
import time

beginningTime = time.time()

count = 0 
with open('click_timer_score.txt') as f:
	lines = f.readlines()

while True:
	highScore = lines[0]
	print 'Score to beat: ' + str(highScore)
	print str(count) + ' done. 1 minute timer (enter to begin, q to quit)'
	userInput = raw_input()
	if (userInput == ''):
		count = count + 1
		if (int(count) > int(highScore)) or (int(count) == 30):
			os.system('mpg123 tada.mp3')
		os.system('mpg123 party_horn.mp3')
		startTime = time.time()

		os.system('clear')
		seconds = 90
		print ('' + str(seconds) + ' second timer running')
		while True:
			if (time.time() - startTime >= seconds):
				os.system('aplay doorbell.wav')
				break
	elif (userInput == 'q'):
		with open('click_timer_score.txt','w') as f:
			f.write(str(count))
		break
	os.system('clear')

totalTime = round((time.time() - beginningTime) / 60, 2)
print 'Total time: ' + str(totalTime) + ' minutes.'
