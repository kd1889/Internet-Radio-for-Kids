import radio
import signal
import sys
import RPi.GPIO as GPIO
from resources.utils import BUTTON, LCD_COMMAND

GPIO.setmode(GPIO.BCM)
LCD_CMD = GPIO.LOW
radio.setup_pins()

class Page:

    def __init__(self, features):
        self.index = 0
        self.features = features

    def scroll(self, inc):
        self.index += inc
        if self.index == len(self.features):
            self.index = 0

        if self.index < 0:
            self.index = len(self.features) - 1

        return self.features[self.index]

    def down(self):
        return self.scroll(1)

    def up(self):
        return self.scroll(-1)

    def input(self, pin):

        output = None

        if pin == BUTTON[1]:
            output = self.up()
        if pin == BUTTON[2]:
            output = self.down()

        return output


class HomePage(Page):
    FEATURES = ["Radio", "Downloaded Content", "Settings"]

    def __init__(self):

        super().__init__(self.FEATURES)


curr = HomePage()


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):

    output = curr.input(channel)

    if output is not None:

        radio.write_arr_4bits(LCD_COMMAND["LCD_CLEAR"], LCD_CMD)
        radio.send_data_to_screen(output)

GPIO.add_event_detect(BUTTON[1], GPIO.FALLING, 
            callback=button_pressed_callback, bouncetime=100)


signal.signal(signal.SIGINT, signal_handler)
signal.pause()

