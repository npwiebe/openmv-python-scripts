

import sensor, image, time


thresholds = (150, 300)
#thresholds = (255, 88)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.VGA)
sensor.set_windowing(320,320)
sensor.skip_frames(time = 5000)
sensor.set_auto_gain(True) # must be turned off for color tracking
sensor.set_auto_whitebal(True) # must be turned off for color tracking
sensor.set_auto_exposure(True)
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot()
    blob_list = img.find_blobs([thresholds], pixels_threshold=200, area_threshold=200, merge=False)
    for blob in blob_list:
        if blob.area()<25000:
            print(blob.area())
            img.draw_rectangle(blob.rect())
            img.draw_cross(blob.cx(), blob.cy())

    img.draw_string(1,1,str(len(blob_list)),scale=3)
    #img.draw_string(0, 0, "FPS:%.2f"%(clock.fps()))
    #print(clock.fps())
