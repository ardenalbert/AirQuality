#! /usr/bin/env python3

# Google Docs example code author: Tony DiCola

import random
import sys
import time
import datetime
import board
import busio
import adafruit_scd30
import adafruit_dotstar
import gspread
import digitalio
from oauth2client.service_account import ServiceAccountCredentials
from adafruit_pm25.i2c import PM25_I2C
from adafruit_ht16k33.segments import BigSeg7x4

LOCATION = 'NONE'

#google docs spreadsheet name and oauth json file (place oauth file in same directory as this python script)
GDOCS_OAUTH_JSON = '/home/pi/diy-ai-169402-7d9989ca811a.json'
GDOCS_SPREADSHEET_NAME = 'AirQuality1'

FREQUENCY_SECONDS = 60

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
# reset_pin = DigitalInOut(board.G0)
# reset_pin.direction = Direction.OUTPUT
# reset_pin.value = False

#initialize Dotstar strip
num_pixels = 24
pixels = adafruit_dotstar.DotStar(board.SCK, board.MOSI, num_pixels, brightness=0.1, auto_write=False)
CO2_normal_color = (10, 240, 240)
CO2_warn_color = (230, 150, 0)
CO2_high_color = (255, 0, 0)
black = (0, 0, 0)
CO2ledMin = 400
CO2ledMax = 1600
#blank any LEDs that may be still on
pixels.fill(black)
pixels.show()

def CO2_gauge(CO2):
    #determine the color of the LEDS based on the CO2 concentration
    if CO2  < 800:
        CO2_color = CO2_normal_color
    elif CO2 < 1200:
        CO2_color = CO2_warn_color
    else:
        CO2_color = CO2_high_color
    #calculate the number of LEDs to show based on the CO2 concentration
    CO2_leds = min(num_pixels, int((CO2 - CO2ledMin) * num_pixels / (CO2ledMax - CO2ledMin)))
    for i in range(num_pixels):
        if i < CO2_leds:
            pixels[i] = CO2_color
        else:
            pixels[i] = black
    pixels.show()
    print("Dots to display: %d" % CO2_leds)

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

#SDC30 Forced Outdoor Calibration (NOTE: Unit must be outside when performing this!)
#print("Calibrating SDC30 Sensor at 400ppm...")
#time.sleep(300)
#scd.forced_recalibration_reference = 400
#print("Calibration Complete")

#main - To do: look into using background processes for sending data etc
#time.sleep(10)
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
        #display CO2 on LED strip
        CO2_gauge(scd.CO2)

    #display selected measurement on 7 segment display
    display.fill(0)
    if not(swDisplayCO2.value):  #check if CO2 is selected
        print("Display Mode = CO2")
        display.print(min(int(scd.CO2), 9999))   #ensure value to display can't be more than the maximum value the 7 segment LED can display
    elif not(swDisplayPM25.value):   #check if PM2.5 is selected
        print("Display Mode = PM2.5")
        display.print(min(int(aqdata["pm25 standard"]), 9999))
    elif not(swDisplayOFF.value):   #check if OFF is selected
        print("Display Mode = OFF")
        display.fill(0)
    else:
        print("Display Mode = ERROR")
        display.print("ERR")

    #get room selection from switch
    if not(swRoomKITCHEN.value):
        print("Room = Kitchen")
        LOCATION = "KITCHEN"
    elif not(swRoomOFFICE.value):
        print("Room = Office")
        LOCATION = "OFFICE"
    elif not(swRoomBEDROOM1.value):
        print("Room = Bedroom 1")
        LOCATION = "BEDROOM1"
    elif not(swRoomBEDROOM2.value):
        print("Room = Bedroom 2")
        LOCATION = "BEDROOM2"
    elif not(swRoomBEDROOM3.value):
        print("Room = Bedroom 3")
        LOCATION = "BEDROOM3"
    elif not(swRoomOUTSIDE.value):
        print("Room = Outside")
        LOCATION = "OUTSIDE"
    else:
        print("Room = ERROR")
        LOCATION = "ERROR"

    #append the data in the spreadsheet, including a timestamp
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
