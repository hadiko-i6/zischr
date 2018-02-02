#!/bin/bash

cd "$(dirname $0)"

export DISPLAY=:0.0
xsetroot -cursor blnk_ptr.xbm blnk_ptr.xbm

#DISPLAY=:0.0 inputattach -elo /dev/ttyS0 &
#sleep 0.4
CURSOR=`xinput list | grep 3M | awk -F "id=" '{ print $2 }' | awk '{ print $1 }'`

xinput set-prop ${CURSOR} "libinput Calibration Matrix" -1.4143646408839778, 0.0, 1.2244475138121547, 0.0, 1.5525606469002695, -0.27324797843665766, 0.0, 0.0, 1.0
#xinput set-prop ${CURSOR} "Evdev Axis Inversion" 0, 1

xset s off -dpms

exec python3 /zischr/frontend/frontend.py $@

