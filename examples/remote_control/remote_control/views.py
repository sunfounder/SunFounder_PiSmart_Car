# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from pismart.pismart import PiSmart
from pismart.motor import Motor
from pismart.tts import TTS
import math

p = PiSmart()
tts = TTS()
p.motor_switch(1)
p.servo_switch(1)
p.speaker_switch(1)

MAXSPEED = 60

left_motor = Motor('MotorB', forward=0)
right_motor = Motor('MotorA', forward=1)

left_motor.stop()
right_motor.stop()

p.power_type = '2S'
p.speaker_volume = 100
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

def move_bak(value):
    values = value.split('_')
    x = int(values[0])
    y = int(values[1])
    print x, y
    r = math.sqrt(pow(x,2)+pow(y,2))
    theta = math.asin(abs(x)/r)/math.pi
    if x >= 0:
        if y >= 0:
            pass
        else:
            theta = 1-theta
    else:
        if y >= 0:
            theta = 2-theta
        else:
            theta = theta+1
    theta = int(100*theta)
    print "theta = %s" % theta
    print "r = %s" % r
    if theta < 50:
        left_speed = 100
        right_speed = p._map(theta, 0, 50, 100, -100)
    elif theta < 100:
        right_speed = -100
        left_speed = p._map(theta, 50, 100, 100, -100)
    elif theta < 150:
        left_speed = -100
        right_speed = p._map(theta, 100, 150, -100, 100)
    else:
        right_speed = 100
        left_speed = p._map(theta, 150, 200, -100, 100)
    left_speed *= r/100*MAXSPEED/100
    right_speed *= r/100*MAXSPEED/100
    print "(left, right) = (%s, %s)" % (left_speed, right_speed)
    left_motor.speed = int(left_speed)
    right_motor.speed = int(right_speed)

def move(value):
    values = value.split('_')
    mode = values[0]
    x = int(values[1])
    y = int(values[2])
    print x, y
    if mode == 'joystick':
        if x <= -20:
            left_speed = p._map(x, -20, -100, -40, -60)
            right_speed = p._map(x, -20, -100, 40, 60)
        elif x < 20:
            left_speed = y
            right_speed = y
        else:
            left_speed = p._map(x, 20, 100, 40, 60)
            right_speed = p._map(x, 20, 100, -40, -60)
    elif mode == 'bar':
        left_speed = x
        right_speed = y
    left_motor.speed = int(left_speed)
    right_motor.speed = int(right_speed)

def home(request):
    return render_to_response("base.html", request)

def run(request):
    words = ''
    if 'words' in request.GET:
        words = request.GET['words']
        tts.say = words
    if 'action' in request.GET:
        try:
            exec('%s()'%request.GET['action'])
        except:
            exec('move("%s")'%request.GET['action'])
    return render_to_response("run.html", {'last_words': words})

def test(request):
    return render_to_response("bars.html", request)
