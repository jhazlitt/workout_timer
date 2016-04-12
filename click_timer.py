import math
import os
import time

count = 0
with open('click_timer_score.txt') as f:
	lines = f.readlines()

#print 'Score to beat: ' + str(lines[0])

while True:
	#os.system('clear')
	highScore = lines[0]
	print 'Score to beat: ' + str(highScore)
	print str(count) + ' done. 1 minute timer (enter to begin, q to quit)'
	userInput = raw_input()
	if (userInput == ''):
		count = count + 1
		if (count > highScore) or (count == 60):
			os.system('mpg123 tada.mp3')
		os.system('mpg123 party_horn.mp3')
		startTime = time.time()

		os.system('clear')
		print ('60 second timer running')
		while True:
			if (time.time() - startTime >= 60):
				os.system('aplay doorbell.wav')
				break
	elif (userInput == 'q'):
		with open('click_timer_score.txt','w') as f:
			f.write(str(count))
		break
	os.system('clear')
