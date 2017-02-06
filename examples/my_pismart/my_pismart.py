from pismart.amateur import PiSmart
from time import sleep

def setup():
    global my_pismart
    my_pismart = PiSmart()
    # If one of the motor is reversed, change its False to True
    my_pismart.MotorA_reversed = True
    my_pismart.MotorB_reversed = False

def end():
    my_pismart.end()

def loop():
    my_pismart.LED = 80              # turn on led
    my_pismart.listen
    if my_pismart.heard:
        my_pismart.LED = 0           # turn off led
        if my_pismart.result == "forward":
            # PiSmart Car move forward
            my_pismart.MotorA = 60
            my_pismart.MotorB = 60
            my_pismart.Say = "I go forward!"
            sleep(3)

        if my_pismart.result == "backward":
            # PiSmart Car backward
            my_pismart.MotorA = -60
            my_pismart.MotorB = -60
            my_pismart.Say = "I go backward!"
            sleep(3)

        if my_pismart.result == "left":
            # PiSmart Car turn left
            my_pismart.MotorA = 60
            my_pismart.MotorB = 20
            my_pismart.Say = "I turn left!"
            sleep(3)

        if my_pismart.result == "right":
            # PiSmart Car turn right
            my_pismart.MotorA = 20
            my_pismart.MotorB = 60
            my_pismart.Say = "I turn right!"
            sleep(3)
        my_pismart.MotorA = 0
        my_pismart.MotorB = 0
        sleep(0.5)


if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        end()

