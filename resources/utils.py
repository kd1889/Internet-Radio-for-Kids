# GPIO TO LCD MAPPING
LCD_MAP = {
    "LCD_RS": 5,
    "LCD_E": 13,
#    "LCD_RW": 6,  # LCD_RW line is not used and permanently grounded in hardware
    "LCD_D4": 23,
    "LCD_D5": 22,
    "LCD_D6": 27,
    "LCD_D7": 17,
}

# IMPORTANT COMMANDS FOR 4BIT
LCD_COMMAND = {
    "LCD_CLEAR": [0,0,0,0,0,0,0,1],
    "LCD_D_OFF": [0,0,0,0,1,0,0,0],
    "LCD_4BIT1": [0,0,1,1,0,0,1,1],
    "LCD_4BIT2": [0,0,1,1,0,0,1,0],
    "LCD_ON_NC": [0,0,0,0,1,1,0,0],
    "LCD_ENTRY": [0,0,0,0,0,1,1,0],
}

# TIMING CONSTANTS
TIMING = {
    "E_PULSE": 0.0005,
    "E_DELAY": 0.0005,
}

# GPIO TO BUTTON MAPPING
BUTTON = {
    "UP": 12,
    "DOWN": 16,
    "LEFT": 20,
    "RIGHT": 7,
    "SELECT": 8,
}
