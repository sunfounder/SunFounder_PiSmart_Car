#!/usr/bin/env python
'''
**********************************************************************
* Filename		 : voice_control_maze.py
* Description	 : voice control maze
* Author		 : Cavon
* Company		 : SunFounder
* E-mail		 : service@sunfounder.com
* Website		 : www.sunfounder.com
* Update		 : Cavon	2016-08-12
* Detail		 : New file
**********************************************************************
'''
from pirobot import PiRobot, Motor, TTS, Speech_Recognition, LED
import time
import line_follower_module

REFERENCES = [300, 300, 300, 300, 300]

FORWARD_SPEED = 40
TURNING_SPEED = 40

TURNING_DELAY = 0.68
REFLASH_DELAY = 0.01
CHECK_TURNING_TIMES = 20
CHECK_FORWARD_TIMES = 20

A_STEP = 0.1
B_STEP = 0.3
C_STEP = 0.5

p = PiRobot()
tts = TTS()
sr = Speech_Recognition('command', dictionary_update=False)
led = LED(LED.BLUE)
lf = line_follower_module.Line_Follower(references=REFERENCES)

p.motor_switch(1)
p.servo_switch(1)
p.speaker_switch(1)

left_motor = Motor('Motor B', forward=0)
right_motor = Motor('Motor A', forward=1)
left_motor.stop()
right_motor.stop()

p.power_type = '2S'
p.volume = 100
p.capture_volume = 100
tts.engine = 'pico'

LEFT_STATUS = (
	#[1,1,0,0,0],
	[1,1,1,0,0],
	[1,1,1,1,0],
	)
RIGHT_STATUS = (
	#[0,0,0,1,1],
	[0,0,1,1,1],
	[0,1,1,1,1],
	)
FORWARD_STATUS = (
	[1,1,0,0,0],
	[0,1,0,0,0],
	[0,1,1,0,0],
	[0,0,1,0,0],
	[0,0,1,1,0],
	[0,0,0,1,0],
	[0,0,0,1,1],
	)
FOLLOW_STATUS = (
	[1,1,0,0,0],
	[0,1,0,0,0],
	[0,1,1,0,0],
	[0,0,1,0,0],
	[0,0,1,1,0],
	[0,0,0,1,0],
	[0,0,0,1,1],
	)


STATUS = ['Finish', 'Line Follow', 'Turning Check', 'Wait Command', 'Turn']

def setup():
	tts.say("Hello, I can do walk through a maze with your help.")
	tts.say("First Do I need a calibration for the black and white colors?")
	led.brightness=60
	while True:
		sr.recognize()
		if sr.result == 'yes':
			calibrate = True
			break
		if sr.result == 'no':
			calibrate = False
			break
	led.off()
	if calibrate:
		tts.say("Ok, Let's do the calibration")
		cali()
		tts.say("Calibration is done, you can check the result on the terminal output.")
	else:
		tts.say("Ok")
	tts.say("Shall we get started?")
	led.brightness=60
	while True:
		sr.recognize()
		if sr.result == 'yes':
			answer = True
			break
		if sr.result == 'no':
			answer = False
			break
	led.off()
	tts.say("Ok")
	if not answer:
		destroy()

def main():
	global lf_status
	turning_point = [0,0,0]     # Possible Turning way: [left,forward,right]
	status = 1

	tts.say('Now, Take me to the start point.')
	time.sleep(3)
	tts.say("Let's roll!")
	left_speed = FORWARD_SPEED
	right_speed = FORWARD_SPEED
	lf_status = [0,0,0,0,0]
	turning_direction = 0

	while STATUS[status] != 'Finish':
		while STATUS[status] == 'Line Follow':
			print '\n---------------------------------'
			print 'Line Following'
			while True:
				reflash_lf_status()
				if  lf_status in FOLLOW_STATUS:
					if	lf_status == [0,0,1,0,0]:
						step = 0
					elif lf_status in ([0,1,1,0,0], [0,0,1,1,0]):
						step = A_STEP
					elif lf_status in ([0,1,0,0,0], [0,0,0,1,0]):
						step = B_STEP
					elif lf_status in ([1,1,0,0,0], [0,0,0,1,1]):
						step = C_STEP
	
					# Direction calculate
					if	lf_status == [0,0,1,0,0]:
						right_speed = FORWARD_SPEED
						left_speed = FORWARD_SPEED
					elif lf_status in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
						right_speed = int(TURNING_SPEED * (1+step))
						left_speed = int(TURNING_SPEED * (1-step))
					elif lf_status in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
						left_speed = int(TURNING_SPEED * (1+step))
						right_speed = int(TURNING_SPEED * (1-step))
	
					left_speed = speed_limit(left_speed)
					right_speed = speed_limit(right_speed)
					left_motor.forward(left_speed)
					right_motor.forward(right_speed)
				else:
					break
			if lf_status == [0, 0, 0, 0, 0]:
				turning_direction = 'back'
				status = 4
			if lf_status in LEFT_STATUS or lf_status in RIGHT_STATUS or lf_status == [1,1,1,1,1]:
				status = 2

		while STATUS[status] == 'Turning Check':
			print '\n------------------------------'
			print 'Turning Checking'
			left_speed = FORWARD_SPEED
			right_speed = FORWARD_SPEED
			turning_point = [0,0,0]     # Possible Turning way
			for i in range(CHECK_TURNING_TIMES):
				lf_status = lf.read_digital()
				print ' Check turning:', lf_status
				if lf_status in LEFT_STATUS:
					print '  Found left'
					turning_point[0] = 1
				elif lf_status in RIGHT_STATUS:
					print '  Found right'
					turning_point[2] = 1
				elif lf_status == [1,1,1,1,1]:
					print '  Found left and right'
					turning_point[0] = 1
					turning_point[2] = 1
			time.sleep(TURNING_DELAY/2)
			finished = False
			for i in range(CHECK_FORWARD_TIMES):
				lf_status = lf.read_digital()
				print ' Check forward', lf_status
				if lf_status in FORWARD_STATUS:
					print '  Found forward'
					turning_point[1] = 1
				elif turning_point == [1,0,1] and lf_status == [1,1,1,1,1]:
					finished = True
			if finished:	
				status = 0
				break
			time.sleep(TURNING_DELAY/2)
			if turning_point == [1,0,0]:
				turning_direction = 'left'
				status = 4
			elif turning_point == [0,1,0]:
				turning_direction = 'forward'
				status = 4
			elif turning_point == [0,0,1]:
				turning_direction = 'right'
				status = 4
			else:
				status = 3

		while STATUS[status] == 'Wait Command':
			print '\n-----------------------------'
			print 'Waiting for command'
			while True:
				left_motor.stop()
				right_motor.stop()
				print '  Directions:', turning_point
				if   turning_point == [1,1,0]:
					tts.say('Left, and forward')
				elif turning_point == [1,0,1]:
					tts.say('Left, and right')
				elif turning_point == [0,1,1]:
					tts.say('Forward, and right')
				elif turning_point == [1,1,1]:
					tts.say('Left, forward, and right')
				tts.say('Which way should I go?')
				led.brightness=60
				while True:
					sr.recognize()
					if sr.result == 'left':
						direction = 1
						break
					if sr.result == 'right':
						direction = 3
						break
					if sr.result == 'forward':
						direction = 2
						break
				led.off()
				if turning_point[direction-1] != 1:
					tts.say('Hah! You trick me!')
					tts.say('But, I really need your help here.')
				else:
					tts.say('Thank you.')
					if direction == 1:
						turning_direction = 'left'
					elif direction == 3:
						turning_direction = 'right'
					elif direction == 2:
						turning_direction = 'forward'
					status = 4
					break
			turning_point = [0,0,0]

		while STATUS[status] == 'Turn':
			print '\n-----------------------'
			print 'Turn'
			if turning_direction == 'left':
				print '  Turn left'
				left_motor.backward(TURNING_SPEED)
				right_motor.forward(TURNING_SPEED)
				lf.wait_tile_status([1,0,0,0,0])
				wait_for_turning_done()
			elif turning_direction == 'right':
				print '  Turn right'
				left_motor.forward(TURNING_SPEED)
				right_motor.backward(TURNING_SPEED)
				lf.wait_tile_status([0,0,0,0,1])
				wait_for_turning_done()
			elif turning_direction == 'forward':
				print '  Forward'
				left_motor.forward(TURNING_SPEED)
				right_motor.forward(TURNING_SPEED)
			elif turning_direction == 'back':
				print '  Dead end'
				left_motor.forward(FORWARD_SPEED)
				right_motor.forward(FORWARD_SPEED)
				time.sleep(TURNING_DELAY)
				left_motor.forward(TURNING_SPEED)
				right_motor.backward(TURNING_SPEED)
				lf.wait_tile_status([0,0,0,0,1])
				wait_for_turning_done()
			turning_point = [0,0,0]
			status =  1

def reflash_lf_status():
	global lf_status
	last_status = lf_status
	lf_status = lf.read_digital()
	if lf_status != last_status:
		time.sleep(REFLASH_DELAY)
		lf_status = lf.read_digital()
	#print lf_status

def speed_limit(speed):
	if speed > 100:
		speed = 100
	elif speed < 0:
		speed = 0
	return speed

def wait_for_turning_done():
	print '    Waiting for turning done...',
	lf.wait_tile_status([0,0,1,0,0])
	#time.sleep(0.2)
	print 'Done!'

def cali():
	references = [0,0,0,0,0]
	mount = 100
	tts.say('Take me to the white.')
	time.sleep(2)
	led.brightness = 60
	tts.say('Measuring')
	white_references = lf.get_average(mount)
	tts.say('Done')
	led.off()

	tts.say('Now, take me to the black.')
	time.sleep(2)
	led.brightness = 60
	tts.say('Measuring')
	black_references = lf.get_average(mount)
	tts.say("Done.")
	led.off()
	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print "Middle references =", references
	time.sleep(1)

def destroy():
	p.motor_switch(0)
	p.servo_switch(0)
	led.off()
	tts.say('finished')
	quit()

if __name__ == '__main__':
	try:
		#setup()
		main()
		destroy()
	except KeyboardInterrupt:
		destroy()
