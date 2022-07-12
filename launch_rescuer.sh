#!/usr/bin/env bash
# launch.sh

cd /home/pi/rpi-resc
while true
do
        python3 Rescuer.py >> /home/pi/log/log
        sleep 5
done