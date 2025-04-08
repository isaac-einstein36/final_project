import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and button pin
GPIO.setmode(GPIO.BCM)  # Using BCM numbering
button_pin = 25        # GPIO pin number where the button is connected

# Set up the button pin as an input with an internal pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Check if button is pressed (GPIO pin is low when pressed)
        if GPIO.input(button_pin) == GPIO.LOW:
            print("Button Pressed!")
        else:
            print("Button Released!")
        
        time.sleep(0.1)  # Small delay to avoid excessive CPU usage

except KeyboardInterrupt:
    print("Program terminated")
finally:
    GPIO.cleanup()  # Clean up the GPIO settings when done