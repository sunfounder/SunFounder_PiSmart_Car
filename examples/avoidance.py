# -*- coding=utf-8 -*-
from pismart.pismart import PiSmart
from pismart.motor import Motor
from pismart.tts import TTS
from pismart.stt import STT
from pismart.led import LED

import RPi.GPIO as GPIO
import time

my_pismart = PiSmart()
tts = TTS()

my_pismart.motor_switch(1)
my_pismart.speaker_switch(1)

left_motor = Motor('MotorB', forward=1)
right_motor = Motor('MotorA', forward=0)
stt = STT('command', dictionary_update=False)
led = LED()

my_pismart.power_type = '2S'
my_pismart.speaker_volume = 30

US_Sig = 17

dead_line = 10
safe_line = 18

check_stop_max = 50
turn_point = 25
max_count = 10 * turn_point

or_so = 2.5
say_delay = 4

def setup():
	GPIO.setmode(GPIO.BCM)
	tts.say = "Hello, I can do ultra-sonic avoidance now"
	tts.say = "Do I need a calibration"
	led.brightness=60
	while True:
		stt.recognize()
		if stt.result == 'yes':
			calibrate = True
			break
		if stt.result == 'no':
			calibrate = False
			break
	led.off()
	if calibrate:
		tts.say = "Ok, Let's do the calibration"
		cali()
		tts.say = "Calibration is done, you can check the result on the terminal output."
	else:
		tts.say = "Ok"
	time.sleep(2)
	tts.say = "Now, Shall we get started?"
	led.brightness=60
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

def cali():
	tts.say = "So, This is how this work. I will do an action, and you tell me Yes, or No."
	tts.say = "Let's do this."
	left_motor.forward()
	time.sleep(1)
	left_motor.stop()
	tts.say = "Did I just turned right?"
	while True:
		led.brightness=60
		while True:
			stt.recognize()
			if stt.result == 'yes':
				calibrate = True
				break
			if stt.result == 'no':
				calibrate = False
				break
		led.off()
		left_motor.stop()
		if calibrate:
			tts.say = "Thank you"
			break
		else:
			tts.say = "Ok"
			left_motor.forward_direction = (left_motor.forward_direction + 1) & 1
			left_motor.forward()
			time.sleep(1)
			left_motor.stop()
			tts.say = "How about now."
	time.sleep(1)
	tts.say = "So"
	right_motor.forward()
	time.sleep(1)
	right_motor.stop()
	tts.say = "Did I just turned left?"
	while True:
		led.brightness=60
		while True:
			stt.recognize()
			if stt.result == 'yes':
				calibrate = True
				break
			if stt.result == 'no':
				calibrate = False
				break
		led.off()
		if calibrate:
			tts.say = "Thank you"
			break
		else:
			tts.say = "Ok"
			right_motor.forward_direction = (right_motor.forward_direction + 1) & 1
			right_motor.forward()
			time.sleep(1)
			right_motor.stop()
			tts.say = "How about now."
	tts.say = "So my left motor's forward direction is %d" % left_motor.forward_direction
	print "Left motor's forward direction is %d" % left_motor.forward_direction
	tts.say = "My right motor's forward direction is %d" % right_motor.forward_direction
	print "Right motor's forward direction is %d" % right_motor.forward_direction
	tts.say = "You should change the forward direction setting in the code at motor definations."

def read_distance():
	pulse_end = 0
	pulse_start = 0
	GPIO.setup(US_Sig,GPIO.OUT)
	GPIO.output(US_Sig, False)
	time.sleep(0.01)

	GPIO.output(US_Sig, True)
	time.sleep(0.00001)
	GPIO.output(US_Sig, False)

	GPIO.setup(US_Sig,GPIO.IN)
	while GPIO.input(US_Sig)==0:
		pulse_start = time.time()
	while GPIO.input(US_Sig)==1:
		pulse_end = time.time()

	pulse_duration = pulse_end - pulse_start
	distance = pulse_duration * 17150
	distance = round(distance, 3)
	
	return distance

def stop():
	left_motor.stop()
	right_motor.stop()

def left_right(direction): 
	if direction:
		left_motor.forward(70)
		right_motor.forward(0)
	else:
		left_motor.forward(0)
		right_motor.forward(70)

def backward():
	print 'backward'
	left_motor.backward(70)
	right_motor.backward(70)

def main():
	print 'Begin!'
	direction = True
	check_stop = []
	turning_time = 0.5
	last_dis = 0			# Remember the last distance
	last_say_time = 0			# Record the last say time, Do not Repeat the same speech rapidly
	last_turning_time = 0	# check time for shake
	while True:
		dis = read_distance()
		if dis > last_dis-or_so and dis < last_dis+or_so:    # count how many times no distance changed
			check_stop.append(dis)
		else:
			check_stop = []
		if len(check_stop) > check_stop_max:   # a few times car distance no change, stop and call for help
			stop()
			print check_stop
			time_now = time.time()
			if time_now - last_say_time > say_delay:
				tts.say = 'Help me!'
				last_say_time = time_now
		else:
			if dis < dead_line:     # too close, backward
				backward()
				time.sleep(0.5)
			elif dis > safe_line:   # 无障碍，小车左右摇摆前进。由direction来调节左右，turning_time摇摆节奏
				time_now = time.time()
				if time_now - last_turning_time > turning_time:
					direction = not direction
					last_turning_time = time_now
			else:                   # 检测到障碍后，由于不摇摆，所以将持续转向，以此避障
				time_now = time.time()
				print time_now, last_say_time
				if time_now - last_say_time > say_delay: 
					if direction:
						tts.say = 'Turn right'
					else:
						tts.say = 'Turn left'
					last_say_time = time_now
			left_right(direction)
		last_dis = dis

def destroy():
	GPIO.setup(US_Sig,GPIO.IN)
	stop()
	my_pismart.motor_switch(0)
	GPIO.cleanup()

if __name__ == '__main__':
	try:
		setup()
		main()
	except Exception, e:
		print e
		destroy()
	except KeyboardInterrupt:
		destroy()
