import radio
print("Testing is_led_on");

print(radio.is_led_on(0));

print("Testing is_button_pressed");
print(radio.is_button_pressed(0));

print("Testing toggle_display with both possible inputs");
radio.toggle_display(0)
radio.toggle_display(1)

print("Testing send_data_to_screen")
radio.send_data_to_screen("My name is Kunj")

print("Testing play_sound");
radio.play_sound("'Hello' by Lionel Richie")


