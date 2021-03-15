import RPi.GPIO as GPIO
import time
import sys
from resources.utils import (
    LCD_MAP,
    LCD_COMMAND,
    TIMING,
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
    GPIO.setup(led_pin, GPIO.OUT)
    return bool(GPIO.input(led_pin))

def is_button_pressed(pin):
    """
    returns True if button at pin number pin is on
    else returns false
    """
    GPIO.setup(pin, GPIO.IN)
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


def play_sound(sound_file):
    """
    Plays the sound file
    """
    print("Now playing:", sound_file);

