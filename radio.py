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

    return True

def toggle_display(state):
    """
    Turns on the display if state is 1
    Turns off the display if state is 0
    """
    if (state):
        print("Screen is On")
    else:
        print("Screen is Off")

def send_data_to_screen(text):
    """
    Sends text to the LCD Screen
    """
    print("The following has been sent to the screen:", text);

