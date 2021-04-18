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

    def perform_actions(self, actionNumber=0):
        """
        actionNumber is the option number on the screen 
        performs default actions when changed to a page
        this method may be overriden in subclasses
        """
        self.display_features()

class PlaySomething(Page):
    FEATURES = ["Radio 1", "Playlist 1", "More"]

    def __init__(self):

        super().__init__(self.FEATURES)
        self.radio_number = 0 # radio number on screen - 1
        self.playlist_number = 0 # playlist number on screen - 1
        self.number_of_playlists = 4
        self.number_of_stations = 4

    @staticmethod
    def increment_index(inc, maxIndex):
        inc += 1
        if inc == maxIndex:
            inc = 0
        return inc

    def next_option(self):
        """
        present next set of options available for radio and playlist
        """
        self.playlist_number = self.increment_index(
                                                    self.playlist_number,
                                                    self.number_of_playlists
        )
        self.radio_number = self.increment_index(
                                                 self.radio_number,
                                                 self.number_of_stations
        )
        self.FEATURES[0] = "Radio " + str(self.radio_number + 1)
        self.FEATURES[1] = "Playlist " + str(self.playlist_number + 1)

    def perform_actions(self, actionNumber=0):
        if actionNumber == 3:
            self.next_option()
        self.display_features()

class HomePage(Page):
    FEATURES = ["Play Something", "Change User", "Setup"]

    def __init__(self):

        super().__init__(self.FEATURES)

class Book:
    """Book holds the pages displayed and controls current page"""

    def __init__(self):

        self.playSomething = PlaySomething()
        self.home = HomePage()
        self.home.perform_actions()
        self.pageIdentifier = {
                               "hp": {
                                      1: (self.playSomething, "playSomething") # button 1 -> radio
                                     },
                               "playSomething": {
                                                 1: (self.home, "hp"),
                                                 2: (self.home, "hp"),
                                                 3: (self.playSomething, "playSomething")
                              }
        }

        self.currPageName = "hp"

    def input(self, pin):

        output = None
        buttonNumber = None
        if pin == BUTTON[1]:
            if 1 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][1]
                buttonNumber = 1

        if pin == BUTTON[2]:
            if 2 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][2]
                buttonNumber = 2

        if pin == BUTTON[3]:
            if 3 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][3]
                buttonNumber = 3

        if pin == BUTTON[4]:
            if 4 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][4]
                buttonNumber = 4

        if pin == BUTTON[5]:
            if 5 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][5]
                buttonNumber = 5

        if output is not None:
            currPage, self.currPageName = output
            currPage.perform_actions(buttonNumber)

curr = Book()


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):

    output = curr.input(channel)
    return

GPIO.add_event_detect(BUTTON[1], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[2], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[3], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[4], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[5], GPIO.FALLING,
            callback=button_pressed_callback, bouncetime=200)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()

