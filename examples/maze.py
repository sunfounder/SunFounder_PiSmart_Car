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
from orion import Orion, Motor, TTS, Speech_Recognition, LED
import numpy
import time

o = Orion()
tts = TTS()
sr = Speech_Recognition('command', dictionary_update=False)
led = LED(LED.BLUE)

o.motor_switch(1)
o.servo_switch(1)
o.speaker_switch(1)

left_motor = Motor('Motor B', forward=0)
right_motor = Motor('Motor A', forward=1)
left_motor.stop()
right_motor.stop()

o.power_type = '2S'
o.volume = 100
tts.engine = 'pico'

lt_tolerate = 100

forward_speed = 40
turning_speed = 40

WHITE_REFERENCES = [588, 577, 564, 534, 591]
BLACK_REFERENCES = [784, 753, 764, 708, 768]

def debug(info):
	print info
	#for i in info.split(' '):
	#	time.sleep(0.2)

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
	trick_count = 0
	check_turning_count = 0
	check_turning_time = 0.5

	turning_point = [0,0,0]     # Possible Turning way
	#cali()
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
		lt_status = read_status()
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
		# Turning 
		elif lt_status == [0,0,0,0,0]:
			left_motor.forward(forward_speed)
			right_motor.forward(forward_speed)
			time.sleep(check_turning_time)
			lt_status = read_status()
			if lt_status == [0,0,0,0,0]:
				print 'dead end'
				left_motor.forward(turning_speed)
				right_motor.backward(turning_speed)
				tts.say('Dead end')
				if not found_line(3):
					Finished = True
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
			lt_status = read_status()
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
				tts.say('Thank you.')
				if   direction == 1:
					left_motor.backward(turning_speed)
					right_motor.forward(turning_speed)
				elif direction == 2:
					left_motor.forward(turning_speed)
					right_motor.backward(turning_speed)
				elif direction == 3:
					left_motor.forward(forward_speed)
					right_motor.forward(forward_speed)
				#time.sleep(0.5)
				if found_line(1):
					if direction != 3:
						wait_for_turning_done()
				else:
					Finished = True
			turning_point = [0,0,0]

def speed_limit(speed):
	if speed > 100:
		speed = 100
	elif speed < 0:
		speed = 0
	return speed

def found_line(timeout):
	print 'Finding line...',
	time_start = time.time()
	time_during = 0
	while time_during < timeout:
		lt_status = read_status()
		result = 0
		for lt in lt_status:
			result = result or lt
		if result == 1:
			print 'Done!'
			return True
		time_now = time.time()
		time_during = time_now - time_start
	print 'Fail!'
	return False

def wait_for_turning_done():
	print 'Waiting for turning done...',
	while True:
		lt_status = read_status()
		if lt_status == [0,0,1,0,0]:
			print 'Done!'
			break

def read_sensor():
	lt0 = o.read_analog(0)
	lt1 = o.read_analog(1)
	lt2 = o.read_analog(2)
	lt3 = o.read_analog(3)
	lt4 = o.read_analog(4)
	return lt0, lt1, lt2, lt3, lt4

def read_status():
	lt = read_sensor()
	status_list = []
	for i in range(0, 5):
		if lt[i] < lt_tolerate + WHITE_REFERENCES[i]:
			status_list.append(0)
		elif lt[i] > lt_tolerate - BLACK_REFERENCES[i]:
			status_list.append(1)
		else:
			status_list.append(-1)
			debug('Channel %d detect error, error value: %d. white: %d, black: %d'%(i,lt[i], WHITE_REFERENCES[i], BLACK_REFERENCES[i]))
	return status_list

def cali():
	mount = 100
	global WHITE_REFERENCES, BLACK_REFERENCES
	tts.say('Take me to the white.')
	time.sleep(2)
	led.brightness = 60
	tts.say('Measuring')
	lt0_list = []
	lt1_list = []
	lt2_list = []
	lt3_list = []
	lt4_list = []
	for i in range(0, mount):
		lt0, lt1, lt2, lt3, lt4 = read_sensor()
		lt0_list.append(lt0)
		lt1_list.append(lt1)
		lt2_list.append(lt2)
		lt3_list.append(lt3)
		lt4_list.append(lt4)
	lt0 = int(numpy.mean(lt0_list))
	lt1 = int(numpy.mean(lt1_list))
	lt2 = int(numpy.mean(lt2_list))
	lt3 = int(numpy.mean(lt3_list))
	lt4 = int(numpy.mean(lt4_list))
	WHITE_REFERENCES = [lt0, lt1, lt2, lt3, lt4]
	tts.say('Done')
	led.off()
	print 'White references =', WHITE_REFERENCES
	time.sleep(1)

	tts.say('Now, take me to the black.')
	time.sleep(2)
	led.brightness = 60
	tts.say('Measuring')
	lt0_list = []
	lt1_list = []
	lt2_list = []
	lt3_list = []
	lt4_list = []
	for i in range(0, mount):
		lt0, lt1, lt2, lt3, lt4 = read_sensor()
		lt0_list.append(lt0)
		lt1_list.append(lt1)
		lt2_list.append(lt2)
		lt3_list.append(lt3)
		lt4_list.append(lt4)
	lt0 = int(numpy.mean(lt0_list))
	lt1 = int(numpy.mean(lt1_list))
	lt2 = int(numpy.mean(lt2_list))
	lt3 = int(numpy.mean(lt3_list))
	lt4 = int(numpy.mean(lt4_list))
	BLACK_REFERENCES = [lt0, lt1, lt2, lt3, lt4]

	tts.say("Done.")
	led.off()
	print "Black references =", BLACK_REFERENCES
	time.sleep(1)

def destroy():
	o.motor_switch(0)
	o.servo_switch(0)
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
