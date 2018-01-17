#!/usr/bin/env python
# -*- coding=utf-8 -*-
'''
**********************************************************************
* Filename		 : line_track.py
* Description	 : line track
* Author		 : Cavon
* Company		 : SunFounder
* E-mail		 : service@sunfounder.com
* Website		 : www.sunfounder.com
* Update		 : Cavon	2017-02-04
**********************************************************************
'''
from pismart.pismart import PiSmart
from pismart.motor import Motor
from pismart.tts import TTS
from pismart.stt import STT
from pismart.led import LED

import time
import line_follower_module

REFERENCES = [359, 352, 342, 316, 356]

forward_speed = 70
turning_speed = 60

max_off_track_count = 1    # off track count
max_trick_count = 1        # tolerant tricked count

my_pismart = PiSmart()
tts = TTS()
stt = STT('command', dictionary_update=True)
led = LED() 	
lf = line_follower_module.Line_Follower(references=REFERENCES)

my_pismart.motor_switch(1)
my_pismart.speaker_switch(1)

left_motor = Motor('MotorB', forward=0)
right_motor = Motor('MotorA', forward=1)
left_motor.stop()
right_motor.stop()

my_pismart.power_type = '2S'
my_pismart.speaker_volume = 3    
my_pismart.capture_volume = 100  

def setup():
	tts.say = "Hello, I can track black lines now, Do I need a calibration for the black and white colors?"
	
	led.brightness=60
	while True:   #  亮灯，开始接收指令。听到指令是yes和no时，分别给calibrate赋值True和False
		stt.recognize()
		if stt.result == 'yes':
			calibrate = True
			break
		if stt.result == 'no':
			calibrate = False
			break

	led.off()    # 接收完指令灯灭，根据calibrate来执行对应动作
	if calibrate:
		tts.say = "Ok, Let's do the calibration"
		cali()
		tts.say = "Calibration is done, you can check the result on the terminal output."
	else:
		tts.say = "Ok"
	tts.say = "Shall we get started?"
	
	led.brightness=60  #  亮灯，开始接收指令。
	while True:
		stt.recognize()
		if stt.result == 'yes':
			answer = True
			break
		if stt.result == 'no':
			answer = False
			break
	
	led.off()
	tts.say = "Ok"
	if not answer:
		destroy()

def main():
	global forward_speed, turning_speed
	trick_count = 0
	off_track_count = 0
	tts.say = 'Take me to the start point.'
	time.sleep(2)
	tts.say = "Let's roll!"
	left_speed = forward_speed
	right_speed = forward_speed
	a_step = 0.1
	b_step = 0.3
	c_step = 0.7
	d_step = 1
	while True:    # main loop
		lt_status = lf.read_digital()  
		print lt_status
		# Speed calculate
		if	lt_status == [0,0,1,0,0]:
			step = 0
		elif lt_status == [0,1,1,0,0] or lt_status == [0,0,1,1,0]:
			step = a_step
		elif lt_status == [0,1,0,0,0] or lt_status == [0,0,0,1,0]:
			step = b_step
		elif lt_status == [1,1,0,0,0] or lt_status == [0,0,0,1,1]:
			step = c_step
		elif lt_status == [1,0,0,0,0] or lt_status == [0,0,0,0,1]:
			step = d_step

		# Direction calculate
		if	lt_status == [0,0,1,0,0]:
			off_track_count = 0
			right_speed = forward_speed
			left_speed = forward_speed
		elif lt_status in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
			# turn right
			off_track_count = 0
			right_speed = int(turning_speed * (1+step))
			left_speed = int(turning_speed * (1-step))
		elif lt_status in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
			off_track_count = 0
			left_speed = int(turning_speed * (1+step))
			right_speed = int(turning_speed * (1-step))
		
		elif lt_status == [0,0,0,0,0]:    # no black line detected
			off_track_count += 1
			if off_track_count >= max_off_track_count: # is off track
				off_track_count = 0
				while True:
					left_motor.stop()
					right_motor.stop()
					tts.say = 'I think I am off track. Which way should I go?'
					turning_speed -= 2
					led.brightness=60
					while True:
						stt.recognize()
						if stt.result == 'left':
							direction = 1
							break
						if stt.result == 'right':
							direction = 2
							break
					led.off()
					tts.say = 'Ok, let me see.'
					if   direction == 1:
						left_motor.backward(turning_speed)
						right_motor.forward(turning_speed)
					elif direction == 2:
						left_motor.forward(turning_speed)
						right_motor.backward(turning_speed)
					if lf.found_line_in(0.5):
						left_motor.stop()
						right_motor.stop()
						tts.say = 'Here it is! Thank you!'
						break
					else:
						left_motor.stop()
						right_motor.stop()
						if trick_count < max_trick_count:
							tts.say = 'Are you kidding me?'
							trick_count += 1
							time.sleep(0.3)
							tts.say = 'Please help!'
							time.sleep(1)
						else:
							tts.say = 'Again?'
							time.sleep()
							tts.say = 'I do not believe you any more. Bye bye.'
							destroy()
		else:
			off_track_count = 0

		# speed limit
		if left_speed > 100:     
			left_speed = 100
		elif left_speed < 0:
			left_speed = 0
		if right_speed > 100:
			right_speed = 100
		elif right_speed < 0:
			right_speed = 0
		left_motor.forward(left_speed)
		right_motor.forward(right_speed)


def cali():
	mount = 100
	tts.say = 'Take me to the white.'
	time.sleep(2)
	led.brightness = 60
	tts.say = 'Measuring'
	white_references = lf.get_average(mount)  # get average value of white
	tts.say = 'Done'
	led.off()

	tts.say = 'Now, take me to the black.'
	time.sleep(2)
	led.brightness = 60
	tts.say = 'Measuring'
	black_references = lf.get_average(mount) # get average value of black
	tts.say = "Done."
	led.off()

	references = lf.references
	for i in range(0, 5):      # get all five middle value.
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references  
	print "Middle references =", references
	time.sleep(1)

def test():
	cali()
	while True:
		print lf.read_analog()
		print lf.read_digital()
		time.sleep(0.5)

def destroy():
	left_motor.stop()
	right_motor.stop()
	my_pismart.motor_switch(0)
	my_pismart.servo_switch(0)
	my_pismart.speaker_switch(0)
	tts.say = "Bye-bye."
	led.off()
	quit()

if __name__ == '__main__':
	try:
		setup()
		main()
		#test()
	except KeyboardInterrupt:
		destroy()
