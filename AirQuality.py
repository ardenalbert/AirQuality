#! /usr/bin/env python3

# Google Docs example code author: Tony DiCola

import random
import sys
import time
import datetime
import board
import busio
import adafruit_scd30
import adafruit_dotstar as dotstar
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from adafruit_ht16k33.segments import BigSeg7x4

LOCATION = 'KITCHEN'

#google docs spreadsheet name and oauth json file (place oauth file in same directory as this python script)
GDOCS_OAUTH_JSON = 'diy-ai-169402-7d9989ca811a.json'
GDOCS_SPREADSHEET_NAME = 'AirQuality1'

FREQUENCY_SECONDS = 60

#led strip colors
COLOR1 = (9, 0, 103)
COLOR2 = (0, 29, 135)
COLOR3 = (0, 99, 148)
COLOR4 = (0, 159, 182)
COLOR5 = (0, 212, 207)
COLOR6 = (0, 240, 240)
BLACK = (0, 0, 0)

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
# reset_pin = DigitalInOut(board.G0)
# reset_pin.direction = Direction.OUTPUT
# reset_pin.value = False


#initialize Dotstar strip
numLEDs = 144
dots = dotstar.DotStar(board.SCK, board.MOSI, numLEDs, brightness=0.05)

def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1 # pylint: disable=redefined-outer-name
        return worksheet
    except Exception as ex: # pylint: disable=bare-except, broad-except
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, \
        and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)

#startup LED animation
def slice_color(wait):
    dots[::6] = [COLOR1] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[1::6] = [COLOR2] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[2::6] = [COLOR3] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[3::6] = [COLOR4] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[4::6] = [COLOR5] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[5::6] = [COLOR6] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[5::6] = [BLACK] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[4::6] = [BLACK] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[3::6] = [BLACK] * (numLEDs //6)
    dots.show()
    time.sleep(wait)
    dots[2::6] = [BLACK] * (numLEDs // 6)
    dots.show()
    time.sleep(wait)
    dots[1::6] = [BLACK] * (numLEDs //6)
    dots.show()
    time.sleep(wait)
    dots[::6] = [BLACK] * (numLEDs //6)
    dots.show()
    time.sleep(wait)



# I2C - Create library object, use 'slow' 100KHz frequency!
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
time.sleep(1)  # let i2c settle to avoid I/O error

#7 segment display test
display = BigSeg7x4(i2c)
display.fill(0)
display.print("8888")
time.sleep(3)
display.fill(0)

# Connect to PM2.5 and SCD30 sensors over I2C
pm25 = PM25_I2C(i2c, reset_pin)
print("Found PM2.5 sensor")
scd = adafruit_scd30.SCD30(i2c)  #to do: Look into reset pin
print("Found SCD30 sensor")

#main - To do: look into using background processes for sending data etc
slice_color(0.05)
time.sleep(10)
print('Logging sensor measurements to\ {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
worksheet = None
while True:
    #login if necessary
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from PM2.5 sensor, retrying...")
        continue

    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")
    
    if scd.data_available:
        print("SCD30 Data Available")
        print("CO2: %d PPM" % scd.CO2)
        print("Temperature: %0.2f degrees C" % scd.temperature)
        print("Humidity: %0.2f %% rH" % scd.relative_humidity)
        print("")
        print("Waiting for new data...")
        print("")
        #display CO2 on LED bar (replace  max scaling with a variable)
        #make this a function call
        #calculate number of LEDs to light up for CO2 and ensure it isn't larger than numLEDs
        CO2LEDs = min(numLEDs, int(scd.CO2 * numLEDs / 2000))
        print("dots to display: %d " % CO2LEDs)
        dots.fill((0, 0, 0))
        for dot in range(CO2LEDs):
            dots[dot] = (0, 200, 200)
        #display CO2 on 7 segment display
        CO2seg = min(int(scd.CO2), 9999)
        display.fill(0)
        display.print(CO2seg)
    #append the data in the spreadsheet, including a timestamp
    '''test append with temp values
    tempco2 = 5.5
    temppm25 = 10.1
    temptemp = 24.6
    temphumidity = 88.32'''
    try:
        worksheet.append_row((datetime.datetime.now().isoformat(), LOCATION, scd.CO2, aqdata["pm25 standard"], scd.temperature, scd.relative_humidity))
    except: # pylint: disable=bare-except, broad-except
        #Error appending data, most likely because credentials are stale.
        #Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue
    #Wait before continuing
    print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)
    #To Do: create a variable for each measurement with desired precision that all processes can use (CO2, Temp, Humidity, etc instead of using scd.* everywhere)


client.loop_blocking()
