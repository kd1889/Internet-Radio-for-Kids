import RPi.GPIO as GPIO
import time
import sys
GPIO.setwarnings(False);
GPIO.setmode(GPIO.BCM);
#GPIO TO LCD MAPPING
LCD_RS = 5;
LCD_E = 13
LCD_RW = 6;
LCD_D4 = 23;
LCD_D5 = 22;
LCD_D6 = 27;
LCD_D7 = 17;

#RS PIN STATES FOR CHARACTER AND COMMAND MODE
LCD_CHR = GPIO.HIGH;
LCD_CMD = GPIO.LOW;

#IMPORTANT COMMANDS FOR 4BIT
LCD_CLEAR = [0,0,0,0,0,0,0,1];
LCD_D_OFF = [0,0,0,0,1,0,0,0];
LCD_4BIT1 = [0,0,1,1,0,0,1,1];
LCD_4BIT2 = [0,0,1,1,0,0,1,0];
LCD_ON_NC = [0,0,0,0,1,1,0,0];
LCD_ENTRY = [0,0,0,0,0,1,1,0];

#TIMING CONSTANTS
E_PULSE = 0.0005;
E_DELAY = 0.0005;

def info():
    '''Prints a basic library description'''
    print("Software library for the stub project.")


def is_led_on(led_pin):
    """
    returns True if led at pin number led_pin is on 
    else returns false
    """

    return True

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
    pins = [LCD_D7, LCD_D6, LCD_D5, LCD_D4];
    GPIO.setup(LCD_RS, GPIO.OUT); 
    GPIO.output(LCD_RS, mode);

    for p, b in zip(pins, bits[:4]):
       GPIO.setup(p, GPIO.OUT);
       GPIO.output(p,b);
    
    time.sleep(E_DELAY);
    GPIO.output(LCD_E, GPIO.HIGH);
    time.sleep(E_PULSE);
    GPIO.output(LCD_E, GPIO.LOW);
    time.sleep(E_DELAY);

    for p, b in zip(pins, bits[4:]):
        GPIO.setup(p, GPIO.OUT);
        GPIO.output(p, b);
    
    time.sleep(E_DELAY);
    GPIO.output(LCD_E, GPIO.HIGH);
    time.sleep(E_PULSE);
    GPIO.output(LCD_E, GPIO.LOW);
    time.sleep(E_DELAY);

    for p in pins:
        GPIO.output(p, GPIO.LOW);
def toggle_display(state):
    if (state == 0):
        write_arr_4bits(LCD_D_OFF, LCD_CMD);
        state_str = "OFF"
    else:
        write_arr_4bits(LCD_ON_NC, LCD_CMD);
        state_str = "ON";
    print("LCD has been toggled " + state_str);

def setup_LCD():
    LCD_PINS = [LCD_RS, LCD_RW, LCD_E, LCD_D7, LCD_D6, LCD_D5, LCD_D4];
    for p in LCD_PINS:
        GPIO.setup(p, GPIO.OUT);
    GPIO.output(LCD_RW, GPIO.LOW);

    write_arr_4bits(LCD_4BIT1, LCD_CMD);
    write_arr_4bits(LCD_4BIT2, LCD_CMD);
    write_arr_4bits(LCD_ON_NC, LCD_CMD);
    write_arr_4bits(LCD_ENTRY, LCD_CMD);
    write_arr_4bits(LCD_CLEAR, LCD_CMD);
   
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

