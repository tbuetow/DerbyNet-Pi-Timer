#!/usr/bin/env python3

import subprocess
import signal
import os
from gpiozero import Button, LED
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)8s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Derbnet_Hardware_UI")

class Derbynet_Hardware_UI:
    def __init__(self,button_pin:int,led_running_pin:int,led_stopped_pin:int,script_path:os.PathLike):
        self.button = Button(button_pin,pull_up=True,bounce_time=.1)
        self.led_running = LED(led_running_pin)
        self.led_stopped = LED(led_stopped_pin)
        self.process = None
        if os.path.isfile(script_path):
            self.script_path = script_path
        else:
            self.script_path = None
            logger.error(f'script path "{script_path}" not a file')
            raise ValueError("Provided script path is not a valid file")
        self._init_leds()

        self.button.when_pressed = self._toggle_timer

        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info('Timer UI initialized')
    
    def _init_leds(self):
        self.led_running.off()
        self.led_stopped.off()
        for i in range(3):
            self.led_running.toggle()
            self.led_stopped.toggle()
            time.sleep(0.25)
        self.led_running.off()
        self.led_stopped.on()

    def run(self):
        logger.info("Monitoring for button presses")
        while True:
            if self.process:
                if self.process.poll() is None:
                    logging.debug("Process is alive")
                else:
                    logging.warning("Process has terminated.")
                    self.stop_timer()
            time.sleep(.5)
            
        # signal.pause() #Elegant but doesn't let me poll process
    
    def _toggle_timer(self):
        if self.process:
            self.stop_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.stop_timer()
        logger.info('Starting Timer')
        self.led_running.on()
        try:
            self.process = subprocess.Popen([self.script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug(f'Started process with PID {self.process.pid}')
        except Exception as e:
            self.led_running.off()
            logger.error(f'Failted to start timer: {e}')
        finally:
            self.led_stopped.off()


    def stop_timer(self):
        if self.process:
            logger.info('Stopping timer')
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning('Process did not terminate in time, murdering...')
                self.process.kill()
            self.process = None
        self.led_running.off()
        self.led_stopped.on()


    def _handle_shutdown(self, signum, frame):
        logger.info('Shutting down like a good boy')
        self.stop_timer()
        exit(0)
        

if __name__ == "__main__":
    button_pin = 18         # header pin 12
    led_running_pin = 23    # header pin 16
    led_stopped_pin = 24    # header pin 18
                            # 5V on pins 2,4
                            # GND on pins 6,14,20
    script_path = "/home/thomas/DerbyNet/run_timer.sh"

    ui = Derbynet_Hardware_UI(button_pin,led_running_pin,led_stopped_pin,script_path)

    ui.run()

