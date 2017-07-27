#!/usr/bin/env python
'''
**********************************************************************
* Filename    : Ultrasonic_Avoidance.py
* Description : A module for SunFounder Ultrasonic Avoidance
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-26    New release
**********************************************************************
'''
import time
import RPi.GPIO as GPIO

class Ultrasonic_Avoidance(object):
	timeout = 0.05

	def __init__(self, channel):
		self.channel = channel
		GPIO.setmode(GPIO.BCM)

	def distance(self):
		pulse_end = 0
		pulse_start = 0
		GPIO.setup(self.channel,GPIO.OUT)
		GPIO.output(self.channel, False)
		time.sleep(0.01)
		GPIO.output(self.channel, True)
		time.sleep(0.00001)
		GPIO.output(self.channel, False)
		GPIO.setup(self.channel,GPIO.IN)
		
		timeout_start = time.time()
		while GPIO.input(self.channel)==0:
			pulse_start = time.time()
			if pulse_start - timeout_start > self.timeout:
				return -1 
		while GPIO.input(self.channel)==1:
			pulse_end = time.time()
			if pulse_start - timeout_start > self.timeout:
				return -1 

		if pulse_start != 0 and pulse_end != 0:
			pulse_duration = pulse_end - pulse_start
			distance = pulse_duration * 100 * 343.0 /2
			distance = int(distance)
			#print 'start = %s'%pulse_start,
			#print 'end = %s'%pulse_end
			if distance >= 0:
				return distance
			else:
				return -1
		else :
			#print 'start = %s'%pulse_start,
			#print 'end = %s'%pulse_end
			return -1

	def get_distance(self, mount = 5):
		sum = 0
		for i in range(mount):
			a = self.distance()
			#print '    %s' % a
			sum += a
		return int(sum/mount)			
	def less_than(self, alarm_gate):
		dis = self.get_distance()
		status = 0
		if dis >=0 and dis <= alarm_gate:
			status = 1
		elif dis > alarm_gate:
			status = 0
		else:
			status = -1
		#print 'distance =',dis
		#print 'status =',status
		return status

if __name__ == '__main__':
	UA = Ultrasonic_Avoidance(17)
	threshold = 10
	while True:
		distance = UA.get_distance()
		status = UA.less_than(threshold)
		if distance != -1:
			print 'distance', distance, 'cm'
			time.sleep(0.2)
		else:
			print False
		if status == 1:
			print "Less than %d" % threshold
		elif status == 0:
			print "Over %d" % threshold
		else:
			print "Read distance error."
