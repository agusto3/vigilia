#!/bin/sh
# openCV_launcher.sh
# activate the cv enviroment

cd /home/pi
source 'which virtualenvwrapper.sh'
workon $1
deactivate