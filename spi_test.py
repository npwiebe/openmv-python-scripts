import sensor, image, time, pyb
from pyb import Pin, SPI

cs = Pin("P3", Pin.OUT_PP)
cs.high()

# The hardware SPI bus for your OpenMV Cam is always SPI bus 2.
spi = SPI(2, SPI.MASTER, baudrate=9600, polarity=0, phase=0)
i = 0
while(i<5):
    i = i +1
    cs.low()
    spi.send(b'1234')
    cs.high()
    print("sent")
    time.sleep_ms(1000)
