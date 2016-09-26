# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import RequestContext
from orion import Orion, Motor, TTS

o = Orion()
tts = TTS()
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
speed = 100
turning_rate = 0.7

MOTOR_ACTIONS = ['forward', 'left', 'right', 'backward', 'stop']

def forward():
	left_motor.forward(speed)
	right_motor.forward(speed)

def stop():
	left_motor.stop()
	right_motor.stop()

def backward():
	left_motor.backward(speed)
	right_motor.backward(speed)

def left():
	left_motor.backward(int(speed*turning_rate))
	right_motor.forward(int(speed*turning_rate))

def right():
	left_motor.forward(int(speed*turning_rate))
	right_motor.backward(int(speed*turning_rate))

def home(request):
    return render_to_response("base.html", request)

def run(request):
	words = ''
	if 'words' in request.GET:
		words = request.GET['words']
		tts.say(words)
	if 'action' in request.GET:
		exec('%s()'%request.GET['action'])
	return render_to_response("run.html", {'last_words': words})
