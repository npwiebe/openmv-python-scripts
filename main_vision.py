# UART Control
#
# This example shows how to use the serial port on your OpenMV Cam. Attach pin
# P4 to the serial input of a serial LCD screen to see "Hello World!" printed
# on the serial LCD display.

import time,sensor, image, struct, tf
from pyb import UART
import binascii


# Load the built-in person detection network (the network is in your OpenMV Cam's firmware).
net = tf.load('person_detection')
labels = ['no person','person','unsure']

def camera_setup(framesize=sensor.QVGA, pixformat = sensor.GRAYSCALE):
    # Reset sensor
    sensor.reset()
    sensor.set_framesize(framesize)
    sensor.set_pixformat(pixformat)
    # Skip a few frames to allow the sensor settle down
    sensor.skip_frames(time = 1000)

camera_setup(framesize=sensor.HQVGA)

BAUDRATE = 2400

# Always pass UART 3 for the UART number for your OpenMV Cam.
# The second argument is the UART baud rate. For a more advanced UART control
# example see the BLE-Shield driver.
uart = UART(3,BAUDRATE)
uart.init(BAUDRATE, bits=8, parity=None, stop=1, timeout=1000, read_buf_len=64, flow = UART.RTS)
clock = time.clock()


def send_img(img,compression):
    img_compressed = img.compress(quality=compression)
    uart.write(str(img_compressed.size()))
    print(str(img_compressed.size()))
    time.sleep(0.1)
    uart.write(img_compressed)
    print(binascii.hexlify(img_compressed))

def send_occupancy(img):
    uart.write("O:2")

def detect_occupancy(img):
    for obj in net.classify(img,min_scale=0.25, scale_mul=0.2, x_overlap=0.0, y_overlap=0.0):
        #print("**********\nDetections at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
        #for i in range(len(obj.output())):
            #print("%s = %f" % (labels[i], obj.output()[i]))
        if (obj.output().index(max(obj.output())) == 1):
            img.draw_rectangle(obj.rect())
            img.draw_string(obj.x()+3, obj.y()-1, labels[obj.output().index(max(obj.output()))], mono_space = False)
            return True
        return False

def find_object(img,threshholds):
    blob_list = img.find_blobs(thresholds, x_stride =2,y_stride =2,pixels_threshold=200, area_threshold=200, merge=False, margin = 1)
    for blob in blob_list:
        detect_occupancy(img,blob.rect())

RUN = True
while (RUN):
        clock.tick()
        img = sensor.snapshot()
        if (detect_occupancy(img)):
            send_img(img,50)
            RUN = False

        #print(clock.fps(), "fps")
#main()
