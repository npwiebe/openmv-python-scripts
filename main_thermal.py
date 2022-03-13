#capturing snapshot and sending to the flash memory while compressing
#getting image size in bytes and drawing blobs around objects using thermal camera
#finding number of blobs for occupancy tracking and displaying on image

import sensor, image, time, math, tf, struct
from pyb import UART

sensor.reset()                      # Reset and initialize the sensor.

#there is a bug in the new update, following two statements need a fake parameter at the end, 0 or 1
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_MODE, True,0)
sensor.ioctl(sensor.IOCTL_LEPTON_SET_MEASUREMENT_RANGE, 20, 32,0)

sensor.set_color_palette(sensor.PALETTE_IRONBOW)  #making colour palette cool

#sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
#sensor.set_framesize(sensor.QQVGA)   # Set frame size to QQVGA (160*120)
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.B128X128) # Set frame size to 64x64... (or 64x32)...
sensor.set_hmirror(1)               # I made changes, flip on y axis
sensor.skip_frames(time = 5000)     # Wait for settings take effect. I made changes, Needs more time to set

#initalize UART
uart = UART(3,9600)
uart.init(9600, bits=8, parity=None, stop=1, timeout=1000, read_buf_len=64)

clock = time.clock()                # Create a clock object to track the FPS.

# Load the built-in person detection network (the network is in your OpenMV Cam's firmware).
net = tf.load('person_detection')
labels = ['unsure', 'person', 'no_person']

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max),provided in examples of openMV
threshold_list = [(0, 100, 9, 127, -128, 127)]
#( 70, 100,  -30,   40,   20,  100)
occupancy = 0

#mock arming signal (to be recieved from hub)
armed = True
breach = False

#extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.RGB565)
#extra_fb.replace(sensor.snapshot())


while(True):
    clock.tick()
    img = sensor.snapshot()

    b_list = img.find_blobs(threshold_list, pixels_threshold=100, area_threshold=100, merge=True, margin=5)
    for blob in b_list:
        myROI = blob.rect()
        #img.draw_rectangle(myROI)
        #img.draw_cross(blob.cx(), blob.cy())
        #print("blob temp:"+str(get_blob_temp(img,threshold_list,blob)))
        xx = net.classify(img, myROI, min_scale=0.5, scale_mul=0.5, x_overlap=-1, y_overlap=-1)
            #for i in range(len(obj.output())):
               # print("%s = %f" % (labels[i], obj.output()[i]))
        if (labels[xx[0].output().index(max(xx[0].output()))]== 'person'):
            displacement = extra_fb.find_displacement(img)
            sub_pixel_x = int(displacement.x_translation() * 5) / 5.0
            img.draw_rectangle(xx[0].rect())
            img.draw_string(xx[0].x()+3, xx[0].y()-1, labels[xx[0].output().index(max(xx[0].output()))], mono_space = False)

            if(displacement.response() > 0.1): # Below 0.1 or so (YMMV) and the results are just noise.
                if (sub_pixel_x > 0):
                    breach = True
                    sensor.snapshot().compress(quality=90).save("OccupancyTrack.jpg")
                #elif (sub_pixel_x < -30):
                 #   occupancy = occupancy -1
            #print(breach)
            #uart.write(struct.pack(">l"), occupancy)
            #sending security alarm when armed
           #if (armed == True):
                # if(displacement.response() > 0.1): # Below 0.1 or so (YMMV) and the results are just noise.
                   # if (sub_pixel_x == -10):
                        #alarm the main hub
                       # uart.write(1)
                        #send image
                #print(uart.read())
            #uart.write(sensor.snapshot().compress(quality=60))
            #print(sensor.snapshot().compress(quality=60))

            #occupancy tracking



    #img.draw_string(1,1,"# of Obj.: "+ str(len(b_list)))

    # For this example we never update the old image to measure absolute change.


    # Offset results are noisy without filtering so we drop some accuracy.
    #sub_pixel_x = int(displacement.x_translation() * 5) / 5.0


    #if(displacement.response() > 0.1): # Below 0.1 or so (YMMV) and the results are just noise.
        #if (sub_pixel_x < 0):
         #   occupancy = occupancy +1
          #  print(occupancy)
#img.compress(quality=90) #compressing
#print(img.size()) #getting image size in bytes
#img.save("OccupancyTrack.jpg") #saving to drive D, flash memory
