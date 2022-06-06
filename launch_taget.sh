#!/bin/sh
# launch.sh

cd /home/pi/rpi-resc
while true
do
    sudo python Target_test.py >> /home/pi/log/log
    sleep 5
done