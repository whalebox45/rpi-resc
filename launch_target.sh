#!/usr/bin/env bash
# launch.sh

cd /home/pi/rpi-resc
while true
do
        python3 Target_test.py >> /home/pi/log/log
        sleep 5
done