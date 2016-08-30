from orion import Motor, Orion, TTS, Speech_Recognition, LED
import RPi.GPIO as GPIO
from time import sleep
import random
import sys

o = Orion()
tts = TTS()
sr = Speech_Recognition('command', dictionary_update=False)
red = LED(LED.RED)

o.motor_switch(1)
o.servo_switch(1)
o.speaker_switch(1)

left_motor = Motor('Motor B', forward=1)
right_motor = Motor('Motor A')

o.power_type = '2S'
o.volume = 100

Avoid_left = 18
Avoid_right = 17

speed = 60

a = 20.0
left_right_delay = float(a) / speed
backward_delay = ( a * 3 ) / speed

tts.engine = 'pico'

def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(Avoid_left, GPIO.IN)
	GPIO.setup(Avoid_right, GPIO.IN)

def forward():
	print 'forward'
	left_motor.forward(speed)
	right_motor.forward(speed)

def turn_right():
	print 'turn right'
	left_motor.forward(speed)
	right_motor.backward(speed + 10)

def turn_left():
	print 'turn left'
	left_motor.backward(speed + 10)
	right_motor.forward(speed)

def stop():
	left_motor.stop()
	right_motor.stop()

def blink(color, times, delay):
	for i in range(0, times):
		color.brightness = color.RUNING
		sleep(delay)
		color.off()
		sleep(delay)
	color.brightness = color.RUNING

def main():
	direction = 0
	while True:
		forward()
		sleep(0.2)
		left_value = GPIO.input(Avoid_left)
		right_value = GPIO.input(Avoid_right)
		value = left_value + right_value
		if value < 2:
			stop()
			tts.say('Which way should I go?')
			sleep(2)
			blink(red, 2, 0.1)
			sr.recognize()
			while True:
				if sr.result == 'left':
					direction = 1
					break
				if sr.result == 'right':
					direction = 2
					break
				if sr.result == 'back':
					direction = 3
					break
			red.off()
			tts.say('Okey.')
			if direction == 1:
				turn_left()
				sleep(left_right_delay)
			if direction == 2:
				turn_right()
				sleep(left_right_delay)
			if direction == 3:
				turn_right()
				sleep(backward_delay)

def destroy():
	o.motor_switch(0)
	red.off()

if __name__ == '__main__':
	try:
		setup()
		main()
	except Exception, e:
		print e
		destroy()
	except KeyboardInterrupt:
		destroy()