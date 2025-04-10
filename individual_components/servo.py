import RPi.GPIO as GPIO
import time

# Set up the GPIO mode and the servo pin
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
servo_pin = 16          # GPIO pin connected to the servo signal wire

# Set up the pin as an output
GPIO.setup(servo_pin, GPIO.OUT)

# Set up PWM on the pin, with a frequency of 50Hz (standard for servos)
pwm = GPIO.PWM(servo_pin, 50)

# Start PWM with a duty cycle of 0 (servo won't move yet)
pwm.start(0)

def set_angle(angle):
    # Convert angle to duty cycle (Servo typically works between 0° and 180°)
    duty_cycle = (angle / 18) + 2
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)

# try:
#     while True:
#         # Move the servo to different angles
#         set_angle(0)      # Move to 0 degrees
#         time.sleep(2)
#         set_angle(90)     # Move to 90 degrees
#         time.sleep(2)
#         set_angle(180)    # Move to 180 degrees
#         time.sleep(2)

# except KeyboardInterrupt:
#     print("Program interrupted")
# finally:
#     pwm.stop()         # Stop PWM
#     GPIO.cleanup()     # Clean up the GPIO settings