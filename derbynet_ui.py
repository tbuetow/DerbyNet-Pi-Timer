#!/usr/bin/env python3

import subprocess
import signal
import os
from gpiozero import Button, LED
import logging
import time
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)8s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Derbnet_Hardware_UI")

@dataclass(frozen=True)
class HardwareConfig:
    timer_button_pin: int = 18   # header pin 12
    led_running_pin: int = 24    # header pin 18
    led_stopped_pin: int = 23    # header pin 16
    track_timer_type: str = "NewBold"
    track_lanes: int = 4    

@dataclass(frozen=True)
class ServerConfig:
    timer_executable_path = "/home/thomas/DerbyNet/derby-timer.jar"
    timer_log_directory = "/home/thomas/DerbyNet/timerlogs"
    server_url = "https://derbynet.buetowfamily.net/"
    server_username = "Timer"
    server_password = os.getenv("PASSWORD") or None
    simulation = True
    

class Derbynet_Hardware_UI:
    def __init__(self,server_config=ServerConfig(), hardware_config=HardwareConfig()):
        self.server_config = server_config
        self.hardware_config = hardware_config

        self.button = Button(self.hardware_config.timer_button_pin,pull_up=True,bounce_time=0.1)
        self.led_running = LED(self.hardware_config.led_running_pin)
        self.led_stopped = LED(self.hardware_config.led_stopped_pin)
        self.process = None
        if not os.path.isfile(self.server_config.timer_executable_path):
            self.server_config.timer_executable_path = None
            logger.error(f'script path "{self.server_config.timer_executable_path}" not a file')
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
                    for line in self.process.stdout:
                        logging.debug(line.decode().strip())
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
            command = [
                        "java",
                        "-jar", self.server_config.timer_executable_path,
                        "-logdir", self.server_config.timer_log_directory,
                        "-u", self.server_config.server_username,
                        "-p", self.server_config.server_password,
                        "-d", self.hardware_config.track_timer_type,
                        "-lanes", str(self.hardware_config.track_lanes),
                        "-x",
                    ]
            if self.server_config.simulation:
                command.append("-simulate-timer")
            command.append(self.server_config.server_url)

            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.debug(f'Started process with PID {self.process.pid}')
        except Exception as e:
            self.led_running.off()
            logger.error(f'Failted to start timer: {e}')
            logger.exception(e)
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
    ui = Derbynet_Hardware_UI()
    ui.run()

