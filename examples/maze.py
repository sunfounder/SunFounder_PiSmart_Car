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
import numpy
import time
import line_follower_module

REFERENCES = [359, 352, 342, 316, 356]

forward_speed = 40
turning_speed = 40

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


def debug(info):
	print info

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
	check_turning_time = 0.5

	turning_point = [0,0,0]     # Possible Turning way

	tts.say('Now, Take me to the start point.')
	time.sleep(3)
	tts.say("Let's roll!")
	left_speed = forward_speed
	right_speed = forward_speed
	a_step = 0.1
	b_step = 0.3
	c_step = 0.7
	d_step = 1

	Finished = False

	while not Finished:
		lt_status = lf.read_digital()
		print lt_status
		# Line Follow:
		if  lt_status not in ([0,0,0,0,0], [1,1,1,0,0], [1,1,1,1,0], [1,1,1,1,1], [0,0,1,1,1], [0,1,1,1,1]):
			#print 'Line Follow'
			if	lt_status == [0,0,1,0,0]:
				step = 0
			elif lt_status in ([0,1,1,0,0], [0,0,1,1,0]):
				step = a_step
			elif lt_status in ([0,1,0,0,0], [0,0,0,1,0]):
				step = b_step
			elif lt_status in ([1,1,0,0,0], [0,0,0,1,1]):
				step = c_step
			elif lt_status in ([1,0,0,0,0], [0,0,0,0,1]):
				step = d_step

			# Direction calculate
			if	lt_status == [0,0,1,0,0]:
				right_speed = forward_speed
				left_speed = forward_speed
			elif lt_status in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
				# turn right
				#print 'right'
				right_speed = int(turning_speed * (1+step))
				left_speed = int(turning_speed * (1-step))
			elif lt_status in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
				#print 'left'
				left_speed = int(turning_speed * (1+step))
				right_speed = int(turning_speed * (1-step))

			left_speed = speed_limit(left_speed)
			right_speed = speed_limit(right_speed)
			left_motor.forward(left_speed)
			right_motor.forward(right_speed)
		# Dead End
		elif lt_status == [0,0,0,0,0]:
			left_motor.forward(forward_speed)
			right_motor.forward(forward_speed)
			time.sleep(check_turning_time)
			lt_status = lf.read_digital()
			if lt_status == [0,0,0,0,0]:
				print 'dead end'
				left_motor.forward(turning_speed)
				right_motor.backward(turning_speed)
				tts.say('Dead end')
				if not found_line(3):
					Finished = True
		# Turning 
		else:
			print ' Turning Point!'
			left_speed = forward_speed
			right_speed = forward_speed
			if lt_status[0:3] == [1,1,1]:
				debug('Found left')
				turning_point[0] = 1
			if lt_status[2:] == [1,1,1]:
				debug('Found right')
				turning_point[2] = 1
			time.sleep(check_turning_time)
			lt_status = lf.read_digital()
			debug('lt status: %s' % lt_status)
			if lt_status == [1,1,1,1,1]:
				break
			elif lt_status[2] == 1:
				debug('Found forward')
				turning_point[1] = 1

			debug('Turning point check finished! Turning point is %s' % turning_point)
			# Turn left:
			if turning_point == [1,0,0]:
				debug('Turn left')
				left_motor.backward(turning_speed)
				#left_motor.stop()
				right_motor.forward(turning_speed)
				if not found_line(2):
					Finished = True
				wait_for_turning_done()
			# Turn right:
			elif turning_point == [0,0,1]:
				debug('Turn right')
				left_motor.forward(turning_speed)
				#right_motor.stop()
				right_motor.backward(turning_speed)
				if not found_line(2):
					Finished = True
				wait_for_turning_done()
			else:
				while True:
					debug('waiting for command')
					left_motor.stop()
					right_motor.stop()
					tts.say('Which way should I go?')
					led.brightness=60
					while True:
						sr.recognize()
						if sr.result == 'left':
							direction = 1
							break
						if sr.result == 'right':
							direction = 2
							break
						if sr.result == 'forward':
							direction = 3
							break
					led.off()
					if turning_point[direction-1] != 1:
						tts.say('Hah! You trick me!')
						tts.say('But, I really need your help here.')
					else:
						tts.say('Thank you.')
						if   direction == 1:
							left_motor.backward(turning_speed)
							right_motor.forward(turning_speed)
							lf.wait_tile_status([1,0,0,0,0])
							wait_for_turning_done()
						elif direction == 2:
							left_motor.forward(turning_speed)
							right_motor.backward(turning_speed)
							lf.wait_tile_status([0,0,0,0,1])
							wait_for_turning_done()
						elif direction == 3:
							left_motor.forward(forward_speed)
							right_motor.forward(forward_speed)
							break
			turning_point = [0,0,0]

def speed_limit(speed):
	if speed > 100:
		speed = 100
	elif speed < 0:
		speed = 0
	return speed

def wait_for_turning_done():
	print 'Waiting for turning done...',
	lf.wait_tile_status([0,0,1,0,0]):
	print 'Done!'

def cali():
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
		setup()
		main()
	except KeyboardInterrupt:
		destroy()
	finally:
		destroy()
