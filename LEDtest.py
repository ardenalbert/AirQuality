#! /usr/bin/env python3

import time
import adafruit_dotstar
import board

num_pixels = 24
pixels = adafruit_dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.2, auto_write=False)
co2_normal_color = (10, 240, 240)
co2_warn_color = (230, 150, 0)
co2_high_color = (255, 0, 0)
black = (0, 0, 0)
CO2ledMin = 400
CO2ledMax = 1600

def co2_gauge(co2):
    #determine the color of the leds based on the CO2 concentration
    if co2 < 800:
        co2_color = co2_normal_color
    elif co2 <1000:
        co2_color = co2_warn_color
    else:
        co2_color = co2_high_color
    #calculate the number of leds to show based on the CO2 concentration
    co2_leds = min(num_pixels, int((co2 - CO2ledMin) * num_pixels / (CO2ledMax - CO2ledMin)))
    for i in range(num_pixels):
        if i < co2_leds:
            pixels[i] = co2_color
        else:
            pixels[i] = black
    pixels.show()
    print("Dots to display: %d" % co2_leds)

#clear leds
pixels.fill(black)
pixels.show()
time.sleep(1.0)

co2_gauge(500)
