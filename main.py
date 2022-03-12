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


def camera_setup(framesize=sensor.QVGA, pixformat = sensor.GRAYSCALE):
    # Reset sensor
    sensor.reset()
    sensor.set_framesize(framesize)
    sensor.set_pixformat(pixformat)
    # Skip a few frames to allow the sensor settle down
    sensor.skip_frames(time = 1000)

camera_setup(framesize=sensor.HQVGA)

extra_fb = sensor.alloc_extra_fb(sensor.width(),sensor.height(),sensor.RGB565)
extra_fb.replace(sensor.snapshot())

thresholds = []
th1 = (58, 2, 63, -60, 52, -1)
th2 = (55, 0, 127, -70, 127, 0)
th3 = (91, 0, 66, -44, 96, 8)
th4 = (100, 85, +22, -20, -20, +20) #watch
th5 = (30, 53, -128, 39, -128, 63)

BAUDRATE = 2400

#thresholds.append(th1)
#thresholds.append(th2)
#thresholds.append(th2)
thresholds.append(th5)


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

RUN = True
while (RUN):
        clock.tick()
        img = sensor.snapshot()
        #find_persons_cascade(img,cascade)
        if (detect_occupancy(img)):
            send_img(img,50)
            RUN = False

        #print(clock.fps(), "fps")
#main()
