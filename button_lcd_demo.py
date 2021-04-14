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

    def display_features(self):

        radio.write_arr_4bits(LCD_COMMAND["LCD_CLEAR"], LCD_CMD)
        for i in range(len(self.features)):
            radio.lcd_go_to_XY(i, 0)
            radio.send_data_to_screen(str(i + 1) + " " + self.features[i])

class Radio(Page):
    FEATURES = ["Something Else", "Change User", "Back"]

    def __init__(self):

        super().__init__(self.FEATURES)

class HomePage(Page):
    FEATURES = ["Radio", "Downloaded Content", "Settings"]

    def __init__(self):

        super().__init__(self.FEATURES)
        self.display_features()

class Book:
    """Book holds the pages displayed and controls current page"""

    def __init__(self):

        self.radio = Radio()
        self.home = HomePage()
        self.pageIdentifier = {
                               "hp": {1: (self.radio, "radio")}, # button 1 -> radio
                               "radio": {3: (self.home, "hp")}
        }

        self.currPageName = "hp"

    def input(self, pin):

        output = None
        if pin == BUTTON[1]:
            if 1 in self.pageIdentifier[self.currPageName]:
                currPage, self.currPageName = self.pageIdentifier[self.currPageName][1]
                currPage.display_features()
        if pin == BUTTON[3]:
            if 3 in self.pageIdentifier[self.currPageName]:
                currPage, self.currPageName = self.pageIdentifier[self.currPageName][3]
                currPage.display_features()

curr = Book()


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):

    output = curr.input(channel)
    return

GPIO.add_event_detect(BUTTON[1], GPIO.FALLING, 
            callback=button_pressed_callback, bouncetime=100)
GPIO.add_event_detect(BUTTON[3], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=100)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()

