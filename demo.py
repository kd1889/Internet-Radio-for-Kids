import radio
import time;
from resources.utils import BUTTON
import yaml

radio.setup_pins()
file = open("./webui/radio.yaml", 'r');
radioDict = yaml.safe_load(file);
radio.setup_station(radio.create_stations(radioDict)[0]); 

print("Testing is_led_on");

print(radio.is_led_on(0));

print("Testing is_button_pressed");

print(radio.is_button_pressed(BUTTON[1]));

print("Testing send_data_to_screen")
radio.setup_LCD();
time.sleep(0.005);
radio.send_data_to_screen("kd1889")

print("Testing toggle display with both inputs");
radio.toggle_display(0);
time.sleep(1);
radio.toggle_display(1);
time.sleep(1);

print("Testing play_sound");
radio.setup_pygame_player();
radio.play_sound("HiTomSamp.mp3");
radio.play_sound("bensound-epic.mp3");
#count = 10000;
#while (count != 0):
#    if (radio.check_player() == 1):
#        print("Playing");
radio.send_data_to_screen("Now playing 'Epic'");
time.sleep(1);
#radio.play_radio();
time.sleep(15);
radio.shutdown_radio();
