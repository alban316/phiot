#!/usr/bin/env python

from RPi import GPIO
import time


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED_ID = {'red':1, 'blue':2, 'green':4}
LED_PIN = [23,24,25]
PHOTO_PIN = 18


def init_leds():
    map(lambda led: GPIO.setup(led, GPIO.OUT), LED_PIN)
    set_leds(0)


def set_leds(mask):
    map(lambda i: GPIO.output(LED_PIN[i], mask & pow(2,i) == pow(2,i)), range(len(LED_PIN)))


def rc_time():
    reading = 0
    GPIO.setup(PHOTO_PIN, GPIO.OUT)
    GPIO.output(PHOTO_PIN, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(PHOTO_PIN, GPIO.IN)

    while (GPIO.input(PHOTO_PIN) == GPIO.LOW):
	reading += 1

    return reading


if __name__ == '__main__':
    init_leds()

    while True:
	reading = rc_time()

	if reading < 300:
	    set_leds(LED_ID['green'])

	elif reading < 900:
	    set_leds(LED_ID['blue'])

	else:
	    set_leds(LED_ID['red'])

	#print RCtime(18)

	#bar = raw_input("Enter r|b|g|x|0:")

	#blah = {'r' : 1, 'b' : 2, 'g' : 4, 'x' : 7, '0' : 0}

	#foo(blah[bar])

