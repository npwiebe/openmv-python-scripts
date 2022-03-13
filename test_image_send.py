# UART Control
#
# This example shows how to use the serial port on your OpenMV Cam. Attach pin
# P4 to the serial input of a serial LCD screen to see "Hello World!" printed
# on the serial LCD display.

import time,sensor, image, struct
from pyb import UART
import binascii

# Reset sensor
sensor.reset()
sensor.set_framesize(sensor.QQQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
# Skip a few frames to allow the sensor settle down
sensor.skip_frames(time = 2000)


# Always pass UART 3 for the UART number for your OpenMV Cam.
uart = UART(3,9600)
uart.init(9600, bits=8, parity=None, stop=1, timeout=1000, read_buf_len=64)
clock = time.clock()
img = sensor.snapshot().compress(quality=40)


print(img.size()) #prints image size
print(str(binascii.hexlify(img))) #print image hex data to terminal


uart.write(str(img.size()))
time.sleep(0.1)
uart.write(img)

#print(clock.fps())
