from gpiozero import PWMOutputDevice
import time

motor_pin = PWMOutputDevice(26)

def set_fan_speed(speed):
    if speed > 1:
        speed = 1
    elif speed < 0:
        speed = 0
    motor_pin.value = speed

# try:
#     set_motor_speed(0.5)
#     time.sleep(5)

#     set_motor_speed(1.0)
#     time.sleep(5)

#     set_motor_speed(0)
#     time.sleep(5)
    
# finally:
#     motor_pin.off()
