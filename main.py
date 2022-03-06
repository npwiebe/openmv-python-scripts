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

cascade = image.HaarCascade("frontalface", stages=25)

thresholds = []
th1 = (58, 2, 63, -60, 52, -1)
th2 = (55, 0, 127, -70, 127, 0)
th3 = (91, 0, 66, -44, 96, 8)
th4 = (91, 46, 22, -30, -23, 15) #watch
#thresholds.append(th1)
#thresholds.append(th2)
#thresholds.append(th2)
thresholds.append(th4)


# Always pass UART 3 for the UART number for your OpenMV Cam.
# The second argument is the UART baud rate. For a more advanced UART control
# example see the BLE-Shield driver.
uart = UART(3,2400)
uart.init(2400, bits=8, parity=None, stop=1, timeout=1000, read_buf_len=64, flow=UART.RTS)
clock = time.clock()


def send_img(img,compression):
    uart.write(img.compress(compression))

def send_occupancy(img):
    uart.write("O:2")

def detect_occupancy(img):
    for obj in net.classify(img, min_scale=1.0, scale_mul=0.5, x_overlap=0.0, y_overlap=0.0):
        #print("**********\nDetections at [x=%d,y=%d,w=%d,h=%d]" % obj.rect())
        #for i in range(len(obj.output())):
            #print("%s = %f" % (labels[i], obj.output()[i]))
        img.draw_rectangle(obj.rect())
        img.draw_string(obj.x()+3, obj.y()-1, labels[obj.output().index(max(obj.output()))], mono_space = False)
        if (obj.output().index(max(obj.output())) == 1):
            #send_img(img,40)
            return True
        return False


def camera_setup(framesize=sensor.QVGA,windowing = (640,480), pixformat = sensor.RGB565):
    # Reset sensor
    sensor.reset()
    sensor.set_framesize(framesize)
    sensor.set_windowing(windowing)
    sensor.set_pixformat(pixformat)
    # Skip a few frames to allow the sensor settle down
    sensor.skip_frames(time = 1000)

def find_persons(img,threshholds):
    blob_list = img.find_blobs(thresholds, x_stride =2,y_stride =2,pixels_threshold=1000, area_threshold=2300, merge=False, margin = 1)
    for blob in blob_list:
        if blob.area()<2800:
            print(blob.area())
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())

def find_persons_cascade(img,cascade):
    kpts1 = None
    print("test")
    while (kpts1 == None):
        img = sensor.snapshot()
        img.draw_string(0, 0, "Looking for a body...")
        objects = img.find_features(cascade, threshold=0.01, scale=1.1)
        if objects:
            person = (objects[0][0]-31, objects[0][1]-31,objects[0][2]+31*2, objects[0][3]+31*2)
            kpts1 = img.find_keypoints(threshold=10, scale_factor=1.1, max_keypoints=100, roi=person)
            img.draw_rectangle(objects[0])

camera_setup()
while (True):
        clock.tick()
        img = sensor.snapshot()
        if (detect_occupancy(img)):
            find_persons(img,thresholds)
            #find_persons_cascade(img,cascade)

        #print(clock.fps(), "fps")
main()
