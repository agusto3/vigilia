#!/bin/bash

### BEGIN INIT INFO
# Provides:          example
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       	This file should be used to construct scripts to be
#				placed in /etc/init.d. this example start a
#				single forking daemon capable of writing a pid
#				file. To get other behavoirs, implement
#				do_start(), do_stop() or other functions to
#				override the defaults in /lib/init/init-d-script.
### END INIT INFO

source ~/.profile
workon cv3
ping 193.168.6.1>/dev/null &
cd /home/pi/Proyectos_OpenCv/Motion\ detection/Vigilancia/
python pi_surveillance.py --conf conf.json --picamera 1

exit