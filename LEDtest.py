#! /usr/bin/env python3
# Example of using the MQTT client class to subscribe to and publish feed values.
# Author: Tony DiCola

# Import standard python modules.
#import time
#import board
#import busio
#import adafruit_dotstar as dotstar

#num_pixels = 144
#dots = dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.2)
#dots.fill((247, 2, 64))

"""CircuitPython Essentials DotStar example"""
import time
from rainbowio import colorwheel
import adafruit_dotstar
import board

num_pixels = 144
pixels = adafruit_dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.1, auto_write=False)


def color_fill(color, wait):
    pixels.fill(color)
    pixels.show()
    time.sleep(wait)


def slice_alternating(wait):
    pixels[::2] = [RED] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[1::2] = [ORANGE] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[::2] = [YELLOW] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[1::2] = [GREEN] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[::2] = [TEAL] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[1::2] = [CYAN] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[::2] = [BLUE] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[1::2] = [PURPLE] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[::2] = [MAGENTA] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)
    pixels[1::2] = [WHITE] * (num_pixels // 2)
    pixels.show()
    time.sleep(wait)


def slice_rainbow(wait):
    pixels[::6] = [RED] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[1::6] = [ORANGE] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[2::6] = [YELLOW] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[3::6] = [GREEN] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[4::6] = [BLUE] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[5::6] = [PURPLE] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[5::6] = [BLACK] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[4::6] = [BLACK] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[3::6] = [BLACK] * (num_pixels //6)
    pixels.show()
    time.sleep(wait)
    pixels[2::6] = [BLACK] * (num_pixels // 6)
    pixels.show()
    time.sleep(wait)
    pixels[1::6] = [BLACK] * (num_pixels //6)
    pixels.show()
    time.sleep(wait)
    pixels[::6] = [BLACK] * (num_pixels //6)
    pixels.show()
    time.sleep(wait)

def rainbow_cycle(wait):
    for i in range(num_pixels):
        rc_index = ((i * 120 // num_pixels) + 150)
        pixels[i] = colorwheel(rc_index & 255)
    pixels.show()
    time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
ORANGE = (255, 40, 0)
GREEN = (0, 255, 0)
TEAL = (0, 255, 120)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 20)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

while True:
    # Change this number to change how long it stays on each solid color.
#    color_fill(RED, 0.5)
#    color_fill(YELLOW, 0.5)
#    color_fill(ORANGE, 0.5)
#    color_fill(GREEN, 0.5)
#    color_fill(TEAL, 0.5)
#    color_fill(CYAN, 0.5)
#    color_fill(BLUE, 0.5)
#    color_fill(PURPLE, 0.5)
#    color_fill(MAGENTA, 0.5)
#    color_fill(WHITE, 0.5)

    # Increase or decrease this to speed up or slow down the animation.
#    slice_alternating(0.1)

#    color_fill(WHITE, 0.5)

    # Increase or decrease this to speed up or slow down the animation.
#    slice_rainbow(0.05)
#    color_fill(BLACK, 0.5)

#    time.sleep(0.5)

    # Increase this number to slow down the rainbow animation.
    rainbow_cycle(0)

