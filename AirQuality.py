#! /usr/bin/env python3

# MQTT example code author: Tony DiCola

import random
import sys
import time
import board
import busio
import adafruit_scd30
import adafruit_dotstar as dotstar
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from Adafruit_IO import MQTTClient
from adafruit_ht16k33.segments import BigSeg7x4


#initialize Dotstar strip
numLEDs = 144
dots = dotstar.DotStar(board.SCK, board.MOSI, numLEDs, brightness=0.05)


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

COLOR1 = (9, 0, 103)
COLOR2 = (0, 29, 135)
COLOR3 = (0, 99, 148)
COLOR4 = (0, 159, 182)
COLOR5 = (0, 212, 207)
COLOR6 = (0, 240, 240)
BLACK = (0, 0, 0)


slice_color(0.05)


# Set Adafruit IO key and username. DO NOT PUBLISH
ADAFRUIT_IO_KEY = 'f6ae06ffa71542e7819045fc5e2ea08f'
ADAFRUIT_IO_USERNAME = 'aalbert'


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO.  Listening for DemoFeed changes...')
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe('DemoFeed')

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO.')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

reset_pin = None
# If you have a GPIO, its not a bad idea to connect it to the RESET pin
# reset_pin = DigitalInOut(board.G0)
# reset_pin.direction = Direction.OUTPUT
# reset_pin.value = False

# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# Create library object, use 'slow' 100KHz frequency!
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
time.sleep(1)  # wait to avoid I/O error by letting i2c settle

#7 segment display test
display = BigSeg7x4(i2c)
display.fill(0)
display.print("C02")
time.sleep(3)
display.fill(0)



# Connect to PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)
print("Found PM2.5 sensor, reading data...")
scd = adafruit_scd30.SCD30(i2c)

# Now the program needs to use a client loop function to ensure messages are
# sent and received.  There are a few options for driving the message loop,
# depending on what your program needs to do.

# The first option is to run a thread in the background so you can continue
# doing things in your program.
#client.loop_background()
# Now send new values every 10 seconds.

while True:
    time.sleep(10)

    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
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
        print("Data Available!")
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
    client.publish('PM25', aqdata["pm25 standard"])
    client.publish('Temperature', scd.temperature)
    client.publish('Humidity', scd.relative_humidity)
    client.publish('CO2', scd.CO2)



client.loop_blocking()



# Another option is to pump the message loop yourself by periodically calling
# the client loop function.  Notice how the loop below changes to call loop
# continuously while still sending a new message every 10 seconds.  This is a
# good option if you don't want to or can't have a thread pumping the message
# loop in the background.
#last = 0
#print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
#while True:
#   # Explicitly pump the message loop.
#   client.loop()
#   # Send a new message every 10 seconds.
#   if (time.time() - last) >= 10.0:
#       value = random.randint(0, 100)
#       print('Publishing {0} to DemoFeed.'.format(value))
#       client.publish('DemoFeed', value)
#       last = time.time()

# The last option is to just call loop_blocking.  This will run a message loop
# forever, so your program will not get past the loop_blocking call.  This is
# good for simple programs which only listen to events.  For more complex programs
# you probably need to have a background thread loop or explicit message loop like
# the two previous examples above.
#client.loop_blocking()
