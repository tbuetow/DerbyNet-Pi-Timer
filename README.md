# DerbyNet Timer on a Raspberry Pi
The excellent [DerbyNet software](https://derbynet.org/) contains a Java based timer used to control the hardware timers commonly used for clocking Pinewood Derby races. I wanted a simple way to run it headless on a Raspberry Pi.

## Python service
A simple python script runs as a service to control the java timer. It can start and stop the java timer, and monitors the process to indicate if it is still alive.

## Hardware control
- 2 LEDs to indicate if the timer is running or stopped for any reason
- Pushbutton to start the timer from stopped

## Setup and Installation
1. You need a java runtime, python 3.11 or newer, and a few python modules found in the requirements.txt
1. copy the .envExample to .env, put the timer roll password for derbyNet in there.
1. Symlink the derbynet-timer.service into systemd `sudo ln -s /path/to/this/repo/derbynet-timer.service /etc/systemd/system/derbynet-timer.service`
1. Do the systemd new service incantation:
    - `sudo systemctl daemon-reload`
    - `sudo systemctl enable derbynet-timer.service`
    - `sudo systemctl start derbynet-timer.service`

## Hardware
I built a simple proto-board that grab 5V (pins 2,4), GND (pins 6,14), and some IO (pins 12,16,18). I'm using NPN transistors to power the LEDs, but you could power them directly from the Pi as long as you use the 3.3V supply and keep their current under ~10mA or so.

Circuit diagram TBD