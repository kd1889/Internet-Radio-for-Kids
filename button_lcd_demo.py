import radio
import signal
import sys
import RPi.GPIO as GPIO
from resources.utils import BUTTON, LCD_COMMAND
import time
import threading
#import pygame as pg
GPIO.setmode(GPIO.BCM)
LCD_CMD = GPIO.LOW
radio.setup_pins()
exit_event = threading.Event() # exit_event for background musicPlayer
radio.setup_pygame_player();
#MUSIC_ENDED = pg.USEREVENT;
#pg.mixer.music.set_endevent(MUSIC_ENDED);

class MusicPlayer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.TIME_PLAYED = 0
        self.trackList = ["HiTomSamp.mp3","bensound-epic.mp3", "bensound-onceagain.mp3"]
        self.index = 0 # for track number in trackList
        self.isPlaying = False # attribute is set to true when track is playing
        self.changeTrack = False # set to true when changing track

       # threading to keep play running at all times in background
        thread = threading.Thread(target=self.play, args=())
        thread.daemon = True
        thread.start()

    def pause(self):
        radio.pause_music()
        self.isPlaying = False

    def unpause(self):
        radio.unpause_music()
        self.isPlaying = True

    def process(self):
        if self.changeTrack:
            self.changeTrack = False
            self.play_track(self.index)

        if not radio.is_music_playing():
            # if music was playing before but has now ended play next track; else it has been paused
            if self.isPlaying == True:
                self.play_next_track(self.index)

        time.sleep(1)

    def play(self):

        while True:
            if exit_event.is_set():
                break # kill background task play at the end when ctrl + c hit
            self.process()

    def play_track(self, trackNumber=0):
        """
        play track should be updated with actual code for playing station or
        track
        """
#        self.isPlaying = True;
#        for i in range(len(self.trackList)):
#            if not self.isPlaying:
#                break
#            print("Playing track: " + self.trackList[trackNumber])
#            time.sleep(1)
        self.TIME_PLAYED += radio.play_sound(self.trackList[trackNumber]);
        self.index = (self.index+1)%len(self.trackList) ;
        self.isPlaying = True;
        time.sleep(5)
#        self.isPlaying=False;
#        self.isPlaying = True

#        for i in range(5):
#            if not self.isPlaying:
#                break
#            print("playing track: " + self.trackList[trackNumber])
#            time.sleep(1)

#        self.isPlaying = False # done playing music

    def kill_music(self):
        radio.stop_player();
        radio.stop_radio();
        self.isPlaying = False

    def play_next_track(self, trackNumber):
        #self.kill_music()
        # sleep time here must be greater than that in play to ensure effect
        # of kill_music and change track
        # time.sleep(1.1)
        self.index = trackNumber;
        self.changeTrack = True

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

    def exit_actions(self, actionNumber=0):
        """
        actionNumber is the option number on the screen
        performs default actions when page is being exited
        this method may be overriden in subclasses
        """
        return

class PlaySomething(Page):
    FEATURES = ["Radio 1", "Playlist 1", "More"]

    def __init__(self):

        super().__init__(self.FEATURES)
        self.isLocked = False # parental lock
        self.isRadioPlaying = False
        self.isMusicOnly = True
        self.radio_number = 0 # radio number on screen - 1
        self.playlist_number = 0 # playlist number on screen - 1
        self.number_of_playlists = 1
        self.number_of_stations = 3

        self.musicPlayer = MusicPlayer()
        #radio.stop_player();
        #radio.play_radio(1);
       # self.play_track()

    def get_time_played(self):
        return self.musicPlayer.TIME_PLAYED

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

    def is_radio_playing(self):
        return self.isRadioPlaying

    def stop_radio(self):
        radio.stop_radio()
        radio.stop_player()
        self.isRadioPlaying = False

    def play_radio(self):
        radio.play_radio(self.radio_number)
        self.isRadioPlaying = True

    def perform_actions(self, actionNumber=0):
        if actionNumber == 3:
            self.next_option()

        self.display_features()

    def exit_actions(self, actionNumber=0):
        if self.is_locked():
            print("Cannot play anything if locked")
            return # do not perform any action below

        if actionNumber == 1: #playing radio
            self.isMusicOnly = False
            self.stop_radio()
            radio.play_radio(self.radio_number);

        if actionNumber == 2: # playing playlist
            self.isMusicOnly = True
            self.stop_radio()
            self.play_track();
            #self.play();

    def is_playing(self):
        return self.musicPlayer.isPlaying

    def is_locked(self):
        return self.isLocked

    def lock(self):
        self.isLocked = True

    def unlock(self):
        self.isLocked = False

    def pause(self):
        self.musicPlayer.pause()

    def unpause(self):
        self.musicPlayer.unpause()

    def play_track(self, trackNumber=0):

        self.musicPlayer.play_next_track(trackNumber)

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
        self.isPausedOrMuted = False
        self.hasReachedMax = False # based on parental control
        self.pageIdentifier = {
                               "hp": {
                                      1: (self.playSomething, "playSomething") # button 1 -> radio
                                     },
                               "playSomething": {
                                                 1: (self.home, "hp"),
                                                 2: (self.home, "hp"),
                                                 3: (self.playSomething, "playSomething"),
                                                 5: (self.home, "hp") # back button
                              }
        }

        self.currPageName = "hp"
        self.currPage = self.home
        self.MAX_TIME = 0.5

        # threading to keep checking whether daily max has been reached
        thread = threading.Thread(target=self.p_control, args=())
        thread.daemon = True
        thread.start()

    def p_control(self):

        while True:
            if exit_event.is_set():
                break # kill background task play at the end when ctrl + c hit

            if self.playSomething.get_time_played() > self.MAX_TIME:

                if not self.playSomething.is_locked():
                    if self.playSomething.is_playing():
                        self.playSomething.pause()
                        print("Lock has paused music")

                    self.playSomething.stop_radio()
                    self.playSomething.lock()
            else:
                if self.playSomething.is_locked():
                    self.playSomething.unlock()
            time.sleep(1)

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

            else: # mute or pause actions
                if self.playSomething.is_locked():
                    print("Cannot pause/mute if locked")
                    return
                if self.isPausedOrMuted is not None:
                    if not self.isPausedOrMuted:

                        if not self.playSomething.isMusicOnly: # if currently playing music

                            if self.playSomething.is_radio_playing():
                                self.playSomething.stop_radio()
                                print("radio muted")

                        else:

                            if self.playSomething.is_playing():
                                self.playSomething.pause()
                                print("Music paused")
                        self.isPausedOrMuted = True
                    else:

                        if not self.playSomething.isMusicOnly: # if currently radio and not playing music

                            if not self.playSomething.is_radio_playing():
                                self.playSomething.play_radio()
                                print("radio unmuted")
                        else:

                            if not self.playSomething.is_playing():
                                self.playSomething.unpause()
                                print("Music unpaused")
                        self.isPausedOrMuted = False

        if pin == BUTTON[5]:
            if 5 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][5]
                buttonNumber = 5

        if output is not None:
            self.currPage.exit_actions(buttonNumber)
            self.currPage, self.currPageName = output
            self.currPage.perform_actions(buttonNumber)
            print("Output is not None");
curr = Book()


def signal_handler(sig, frame):
    radio.stop_player();
    radio.stop_radio();
    exit_event.set()
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):

    output = curr.input(channel)
    return

GPIO.add_event_detect(BUTTON[1], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[2], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[3], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[4], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200) # mute or pause
GPIO.add_event_detect(BUTTON[5], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200) # back button

signal.signal(signal.SIGINT, signal_handler)
signal.pause()

