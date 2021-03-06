from mutagen.mp3 import MP3
import RPi.GPIO as GPIO
import time
import os
import sys
import pygame as pg
import yaml;
from resources.utils import (
    LCD_MAP,
    LCD_COMMAND,
    TIMING,
    BUTTON,
)

GPIO.setwarnings(False);
GPIO.setmode(GPIO.BCM);

#RS PIN STATES FOR CHARACTER AND COMMAND MODE
LCD_CHR = GPIO.HIGH;
LCD_CMD = GPIO.LOW;


def info():
    '''Prints a basic library description'''
    print("Software library for the stub project.")


def is_led_on(led_pin):
    """
    returns True if led at pin number led_pin is on
    else returns false
    """
    GPIO.setup(led_pin, GPIO.OUT) # remove once led pins have been assigned
    return bool(GPIO.input(led_pin))

def is_button_pressed(pin):
    """
    returns True if button at pin number pin is on
    else returns false
    """
    return bool(GPIO.input(pin))


def char_to_arr(c):
    return [int(b) for b in format(ord(c), '08b')];

def write_arr_4bits(bits, mode, debug=True):
    pins = [LCD_MAP["LCD_D7"], LCD_MAP["LCD_D6"], LCD_MAP["LCD_D5"], LCD_MAP["LCD_D4"]];
    GPIO.output(LCD_MAP["LCD_RS"], mode);

    for p, b in zip(pins, bits[:4]):
       GPIO.output(p,b);

    time.sleep(TIMING["E_DELAY"]);
    GPIO.output(LCD_MAP["LCD_E"], GPIO.HIGH);
    time.sleep(TIMING["E_PULSE"]);
    GPIO.output(LCD_MAP["LCD_E"], GPIO.LOW);
    time.sleep(TIMING["E_DELAY"]);

    for p, b in zip(pins, bits[4:]):
        GPIO.output(p, b);

    time.sleep(TIMING["E_DELAY"]);
    GPIO.output(LCD_MAP["LCD_E"], GPIO.HIGH);
    time.sleep(TIMING["E_PULSE"]);
    GPIO.output(LCD_MAP["LCD_E"], GPIO.LOW);
    time.sleep(TIMING["E_DELAY"]);

    for p in pins:
        GPIO.output(p, GPIO.LOW);


def toggle_display(state):
    if (state == 0):
        write_arr_4bits(LCD_COMMAND["LCD_D_OFF"], LCD_CMD);
        state_str = "OFF"
    else:
        write_arr_4bits(LCD_COMMAND["LCD_ON_NC"], LCD_CMD);
        state_str = "ON";
    print("LCD has been toggled " + state_str);


def setup_LCD():

    for p in LCD_MAP.values():
        GPIO.setup(p, GPIO.OUT);

    write_arr_4bits(LCD_COMMAND["LCD_4BIT1"], LCD_CMD);
    write_arr_4bits(LCD_COMMAND["LCD_4BIT2"], LCD_CMD);
    write_arr_4bits(LCD_COMMAND["LCD_ON_NC"], LCD_CMD);
    write_arr_4bits(LCD_COMMAND["LCD_ENTRY"], LCD_CMD);
    write_arr_4bits(LCD_COMMAND["LCD_CLEAR"], LCD_CMD);


def send_data_to_screen(text):
    """
    Sends text to the LCD Screen
    """
    for char in text:
        write_arr_4bits(char_to_arr(char), LCD_CHR);
    print("The following has been sent to the screen:", text);

def lcd_go_to_XY(x, y):
    
    if not 0 <= x < 4 and 0 <= y < 20:
        raise Exception("x and y must be integers with  0 <= x <= 4 and 0 <= y <= 20")
    
    addr = 0
    
    if x == 0:
        addr = 0x00
    
    if x == 1:
        addr = 0x40
    
    if x == 2:
        addr = 0x14
    
    if x == 3:
        addr = 0x54
    
    addr += y
    
    addr = 0x80 | addr # extend to 8 bits
    
    cmd = [int(x) for x in list(bin(addr))[2:]]
    
    write_arr_4bits(cmd, 0) # move cursor to position x, y on screen

def setup_pygame_player(freq=44100, bitsize=-16, channels=2, buffer=2048):
    pg.mixer.init(freq, bitsize, channels, buffer);

def play_radio(station_num = 1):
    """
    From a created playlist of radio stations, play the first station
    """
    os.system("mpc play " + str(station_num));
def stop_radio():
    """
    Stop radio play, and reset playlist
    """
    os.system("mpc stop");
def setup_station(station_list):
    """
    Given a list, read from it different radio stations and fill the
    MPC playlist with the different stations
    """
    for url in station_list:
        if (url[1].strip()):
            os.system("mpc add " + url[1]);
def radio_reset():
    os.system("mpc clear");

def play_sound(sound_file):
    """
    Obtained from adafruit I2S decoder setup
    """
    sound_file = "./uploads/" + sound_file;
    clock = pg.time.Clock();
    try:
        pg.mixer.music.load(sound_file)
        print("Music file {} loaded!".format(sound_file))
    except:
        print("File {} not found! {}".format(music_file, pg.get_error()));
        return
    pg.mixer.music.play()
    print("Now playing:", sound_file);

    audio = MP3(sound_file)
    return audio.info.length
    #while pg.mixer.music.get_busy():
    #    clock.tick(30);
def stop_player():
    pg.mixer.music.stop();

def is_music_playing():
    return pg.mixer.music.get_busy()

def pause_music():
    pg.mixer.music.pause()

def unpause_music():
    pg.mixer.music.unpause()

def setup_buttons():

    for b in BUTTON.values():
        GPIO.setup(b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
def setup_pins():
    """
    Setup all pins required for radio operation. This function
    must be called before any operation on any GPIO pins
    """
    setup_buttons()
    setup_LCD()

def create_playlist(PLAYLIST_DICT, PLAYLIST_NUM):
    if PLAYLIST_NUM > int(PLAYLIST_DICT['num_playlist']):
        raise IndexError;
    else:
        return PLAYLIST_DICT['playlists'][PLAYLIST_NUM]['songs']

def create_stations(RADIO_DICT):
    stations = RADIO_DICT['stations'];
    num_stations =int(RADIO_DICT['num_stations']);
    res_stations = [];
    for i in range(num_stations):
        if stations[i]['state']:
            res_stations.append((stations[i]['name'], stations[i]['url']));
    return res_stations, len(res_stations);
    
