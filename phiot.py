#!/usr/bin/env python

from RPi import GPIO
import time


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


LEDS = [23,24,25]

map(lambda led: GPIO.setup(led, GPIO.OUT), LEDS)


def foo(mask):
    map(lambda i: GPIO.output(LEDS[i], mask & pow(2,i) == pow(2,i)), range(len(LEDS)))

def RCtime(RCpin):
    reading = 0
    GPIO.setup(RCpin, GPIO.OUT)
    GPIO.output(RCpin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(RCpin, GPIO.IN)

    while (GPIO.input(RCpin) == GPIO.LOW):
	reading += 1

    return reading



if __name__ == '__main__':
    foo(0)

    while True:
	reading = RCtime(18)

	if reading < 300:
	    foo(4) #green (most light)

	elif reading < 900:
	    foo(2) #blue (medium light)

	else:
	    foo(1) #red (low light)

	#print RCtime(18)

	#bar = raw_input("Enter r|b|g|x|0:")

	#blah = {'r' : 1, 'b' : 2, 'g' : 4, 'x' : 7, '0' : 0}

	#foo(blah[bar])

