import radio
import time;

print("Testing is_led_on");

print(radio.is_led_on(0));

print("Testing is_button_pressed");
print(radio.is_button_pressed(0));

print("Testing send_data_to_screen")
radio.setup_LCD();
time.sleep(0.005);
radio.send_data_to_screen("kd1889")

print("Testing toggle display with both inputs");
radio.toggle_display(0);
time.sleep(1);
radio.toggle_display(1);
time.sleep(0);

print("Testing play_sound");
radio.play_sound("'Hello' by Lionel Richie")

