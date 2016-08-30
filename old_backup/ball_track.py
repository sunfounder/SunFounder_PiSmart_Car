from orion import Orion, Servo, Motor
from time import sleep
import SimpleCV

o = Orion()
pan_servo = Servo(0)
tilt_servo = Servo(1)
left_motor = Motor('Motor B', forward=1)
right_motor = Motor('Motor A')

o.servo_switch(1)
o.motor_switch(1)
o.power_type = '2S'

cam = SimpleCV.Camera()
#display = SimpleCV.Display()

pan_servo.offset = -55
tilt_servo.offset = -20

ball_size = 40

def main():
	x = 400				# x initial in the middle
	y = 300				# y initial in the middle
	r = 0				# ball radius initial to 0(no balls if r < ball_size)

	pan_angle = 90			# initial angle for pan
	tilt_angle = 10			# initial angle for tilt
	camera_step = 1			# Step to move camera when it find ball
	cam_tolerate = 50		# camera tolerate for the ball almost in the middle 

	'''
	scan_direction = True	# scan for balls True means left
	scan_step = 20			# scan step (angle)
	max_angle = 135			# max scan angle
	min_angle = 45			# min scan angle
	'''
	#scan_angles = [45, 60, 75, 90, 105, 120, 135, 120, 105, 90, 75, 60]
	scan_angles = [30, 60, 90, 120, 150, 120, 90, 60]
	angle_count = 0
	scan_count = 0
	scan_max_count = 5

	default_speed = 45
	high_speed = default_speed + 5		# initial speed for left motor
	low_speed = default_speed - 5		# initial speed for right motor
	motor_tolerate = 5					# motor tolerate for the servo almost in the middle 

	while True:
		img = cam.getImage()
		dist = img - img.colorDistance(SimpleCV.Color.RED).dilate(4)
		blobs = dist.findBlobs()
		if blobs:
			circles = blobs.filter([b.isCircle(0.2) for b in blobs])
			if circles:
				#img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.BLUE,1)
				x = circles[-1].x
				y = circles[-1].y
				r = circles[-1].radius()
			if r > ball_size:
				print 'Ball Detect!!  x: %d, y: %d, r: %d' % (x, y, r)
			else:
				print 'No Ball'
				r = 0
		#dist.show()
		if r > ball_size:
			if x - 400 < -cam_tolerate:			# Ball is on left
				pan_angle += camera_step
				if pan_angle > 180:
					pan_angle = 180
			if x - 400 > cam_tolerate:			# Ball is on right
				pan_angle -= camera_step
				if pan_angle < 0:
					pan_angle = 0
			if y - 300 < -cam_tolerate:			# Ball is on top
				tilt_angle += camera_step
				if tilt_angle > 180:
					tilt_angle = 180
			if y - 300 > cam_tolerate:			# Ball is on bottom
				tilt_angle -= camera_step
				if tilt_angle < 0:
					tilt_angle = 0
			pan_servo.turn(pan_angle)
			tilt_servo.turn(tilt_angle)
		else:
			#sleep(3)
			tilt_angle = 5
			if scan_count > scan_max_count:
				pan_angle = scan_angles[angle_count]
				pan_servo.turn(pan_angle)
				tilt_servo.turn(tilt_angle)
				angle_count += 1
				if angle_count == len(scan_angles):
					angle_count = 0
				scan_count = 0
			else:
				scan_count += 1
		if r > ball_size and r < 120:
			if pan_angle - 90 < -5:			# Ball is on left
				left_speed = low_speed
				right_speed = high_speed
			elif pan_angle - 90 > 5:			# Ball is on right
				left_speed = high_speed
				right_speed = low_speed
			else:
				left_speed = default_speed
				right_speed = default_speed
			left_motor.forward(left_speed)
			right_motor.forward(right_speed)
		else:
			left_motor.stop()
			right_motor.stop()

def destroy():
	o.servo_switch(0)
	o.motor_switch(0)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		destroy()
