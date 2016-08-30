from orion import Motor, Orion, TTS
import RPi.GPIO as GPIO
from time import sleep
import random

o = Orion()
tts = TTS()

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

def backward():
	print 'backward'
	left_motor.backward(speed)
	right_motor.backward(speed)

def turn_right():
	print 'turn right'
	left_motor.forward(speed)
	right_motor.backward(speed + 10)

def turn_left():
	print 'turn left'
	left_motor.backward(speed + 10)
	right_motor.forward(speed)

def random_direction():
	direction = random.randint(0, 1)
	if direction == 0:
		turn_left()
		tts.say('And, turn left')
	if direction == 1:
		turn_right()
		tts.say('And, turn right')

def stop():
	left_motor.stop()
	right_motor.stop()

def main():
	last_status = -1
	while True:
		left_value = GPIO.input(Avoid_left)
		right_value = GPIO.input(Avoid_right)
		status = (left_value << 1) + right_value

		if status != last_status:
			print 'status: 0x%2x' % status
			if status == 0:		# Both blocked
				backward()
				tts.say('Some in my way, backing off.')
				sleep(left_right_delay)
				random_direction()
				sleep(left_right_delay)
			if status == 1:		# Left blocked
				turn_right()
				tts.say('Turning right')
				sleep(left_right_delay)
			if status == 2:		# Right blocked
				turn_left()
				tts.say('Turning left')
				sleep(left_right_delay)
			if status == 3:		# Not blocked
				forward()
			last_status = status

def destroy():
	stop()
	o.motor_switch(0)

if __name__ == '__main__':
	try:
		setup()
		main()
	except Exception, e:
		print e
		destroy()
	except KeyboardInterrupt:
		destroy()