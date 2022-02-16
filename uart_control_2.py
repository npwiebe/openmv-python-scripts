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
sensor.set_contrast(3)
sensor.set_gainceiling(16)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((640, 480))
sensor.set_pixformat(sensor.GRAYSCALE)
# Skip a few frames to allow the sensor settle down
sensor.skip_frames(time = 2000)


# Always pass UART 3 for the UART number for your OpenMV Cam.
# The second argument is the UART baud rate. For a more advanced UART control
# example see the BLE-Shield driver.
uart = UART(3,9600)
uart.init(9600, bits=8, parity=None, stop=1, timeout=1000, read_buf_len=64)
clock = time.clock()
byte_array = bytearray([0xFF,0xFF,0xFF,0xFF])
while (True):
    clock.tick()
    img = sensor.snapshot().compress(quality=60)
    #print(img.size())
    #uart.write(struct.pack(">l", img.size()))
    uart.write(img)
    uart.write(byte_array)
    print(clock.fps())

