import os,time
# Initilize LED
os.system("echo none >/sys/class/leds/led0/trigger")

# set onboard LED off and on
for i in range(10):
    os.system("echo 0 >/sys/class/leds/led0/brightness")
    time.sleep(0.5)
    os.system("echo 1 >/sys/class/leds/led0/brightness")
    time.sleep(0.5)

# Set LED back to default function
os.system("echo mmc0 >/sys/class/leds/led0/trigger")

# reference https://forums.raspberrypi.com/viewtopic.php?t=12530