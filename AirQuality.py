#! /usr/bin/env python3

import random
import sys
import time
import datetime
import board
import busio
import adafruit_scd30
import adafruit_dotstar
import digitalio
import paho.mqtt.client as mqtt
import json
from adafruit_pm25.i2c import PM25_I2C
from adafruit_ht16k33.segments import BigSeg7x4

LOCATION = 'NONE'

FREQUENCY_SECONDS = 10

# ----------------- MQTT CONFIG -----------------
MQTT_BROKER = "192.168.86.16"   # <-- Change to your HA broker IP
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"         # <-- Change to your HA MQTT user
MQTT_PASSWORD = "mqtt_password" # <-- Change to your HA MQTT password
MQTT_TOPIC_PREFIX = "home/airquality"

# Connect to MQTT broker
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print(f"Connected to MQTT broker at {MQTT_BROKER}")
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")

# ------------------------------------------------

reset_pin = None

#initialize Dotstar strip
num_pixels = 24
pixels = adafruit_dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.1, auto_write=False)
CO2_normal_color = (10, 240, 240)
CO2_warn_color = (230, 150, 0)
CO2_high_color = (255, 0, 0)
black = (0, 0, 0)
CO2ledMin = 400
CO2ledMax = 1600
pixels.fill(black)
pixels.show()

def CO2_gauge(CO2):
    if CO2 < 800:
        CO2_color = CO2_normal_color
    elif CO2 < 1200:
        CO2_color = CO2_warn_color
    else:
        CO2_color = CO2_high_color
    CO2_leds = min(num_pixels, int((CO2 - CO2ledMin) * num_pixels / (CO2ledMax - CO2ledMin)))
    for i in range(num_pixels):
        pixels[i] = CO2_color if i < CO2_leds else black
    pixels.show()
    print("Dots to display: %d" % CO2_leds)

#initialize display select switch inputs
swDisplayCO2 = digitalio.DigitalInOut(board.D5)
swDisplayCO2.direction = digitalio.Direction.INPUT
swDisplayPM25 = digitalio.DigitalInOut(board.D6)
swDisplayPM25.direction = digitalio.Direction.INPUT
swDisplayOFF = digitalio.DigitalInOut(board.D7)
swDisplayOFF.direction = digitalio.Direction.INPUT

#initialize room select switch inputs
swRoomKITCHEN = digitalio.DigitalInOut(board.D12)
swRoomKITCHEN.direction = digitalio.Direction.INPUT
swRoomOFFICE = digitalio.DigitalInOut(board.D13)
swRoomOFFICE.direction = digitalio.Direction.INPUT
swRoomBEDROOM1 = digitalio.DigitalInOut(board.D14)
swRoomBEDROOM1.direction = digitalio.Direction.INPUT
swRoomBEDROOM2 = digitalio.DigitalInOut(board.D15)
swRoomBEDROOM2.direction = digitalio.Direction.INPUT
swRoomBEDROOM3 = digitalio.DigitalInOut(board.D16)
swRoomBEDROOM3.direction = digitalio.Direction.INPUT
swRoomOUTSIDE = digitalio.DigitalInOut(board.D17)
swRoomOUTSIDE.direction = digitalio.Direction.INPUT

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
time.sleep(1)

# 7-segment display test
display = BigSeg7x4(i2c)
display.fill(0)
display.print("8888")
time.sleep(3)
display.fill(0)

# Connect sensors
pm25 = PM25_I2C(i2c, reset_pin)
print("Found PM2.5 sensor")
scd = adafruit_scd30.SCD30(i2c)
print("Found SCD30 sensor")
#Set temperature offset to compensate for sensor heating
scd.temperature_offset = 3.1
#--- Display current temperature reading offset ---
current_offset = scd.temperature_offset
print(f"Current temperature offset: {current_offset} degrees C")
print('Press Ctrl-C to quit.')
while True:
    try:
        aqdata = pm25.read()
    except RuntimeError:
        print("Unable to read from PM2.5 sensor, retrying...")
        continue

    print("\nPM 1.0: %d\tPM2.5: %d\tPM10: %d" %
          (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]))

    if scd.data_available:
        print("SCD30 Data Available")
        co2 = scd.CO2
        temperature = scd.temperature
        humidity = scd.relative_humidity
        pm25_value = aqdata["pm25 standard"]

        print(f"CO2: {co2:.0f} PPM | Temp: {temperature:.2f}°C | Hum: {humidity:.2f}%")

        # Update LED gauge
        CO2_gauge(co2)

        # Publish to MQTT
        payload = {
            "location": LOCATION,
            "co2": round(co2, 2),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "pm25": pm25_value,
            "timestamp": datetime.datetime.now().isoformat()
        }
        mqtt_topic = f"{MQTT_TOPIC_PREFIX}/{LOCATION.lower()}"
        try:
            client.publish(mqtt_topic, json.dumps(payload))
            print(f"Published to MQTT: {mqtt_topic} -> {payload}")
        except Exception as e:
            print(f"MQTT publish failed: {e}")

    # Display data on 7-segment
    display.fill(0)
    if not swDisplayCO2.value:
        display.print(min(int(co2), 9999))
    elif not swDisplayPM25.value:
        display.print(min(int(pm25_value), 9999))
    elif not swDisplayOFF.value:
        display.fill(0)
    else:
        display.print("ERR")

    # Update LOCATION
    if not swRoomKITCHEN.value:
        LOCATION = "KITCHEN"
    elif not swRoomOFFICE.value:
        LOCATION = "OFFICE"
    elif not swRoomBEDROOM1.value:
        LOCATION = "BEDROOM1"
    elif not swRoomBEDROOM2.value:
        LOCATION = "BEDROOM2"
    elif not swRoomBEDROOM3.value:
        LOCATION = "BEDROOM3"
    elif not swRoomOUTSIDE.value:
        LOCATION = "OUTSIDE"
    else:
        LOCATION = "UNKNOWN"

    time.sleep(FREQUENCY_SECONDS)

