# import RPi.GPIO as GPIO
# import time
# import json
# import state_manager as sm

# SENSOR_PIN = 12
 
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(SENSOR_PIN, GPIO.IN)


# def my_callback(channel):
    
#     # If the user's already entered the pod, don't do anything
#     if sm.get_motion_entering_pod():
#         return
    
#     else:
#         sm.set_motion_entering_pod(True)

#         # If the user's already exited the pod, don't do anything
#         if sm.get_motion_exiting_pod():
#             return
        
#         else:
#             sm.set_motion_exiting_pod(True)
    
# try:
#     GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=my_callback)
    
# except KeyboardInterrupt:
#     print ("Finish")
    
    
## Revised Code
import RPi.GPIO as GPIO
import time
import threading
import state_manager as sm

SENSOR_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)

def motion_handler(channel):
        # Detect motion once the user enters the pod the first time
        if sm.get_access_granted() and sm.get_door_unlocked() and not sm.get_motion_entering_pod():
                sm.set_motion_entering_pod(True)
                print("Motion detected: User entering pod")

        # If the user is already in the pod, don't do anything
        

        # DEMO: If the user interrupted their nap, pause for a few seconds to allow the door to be closed
        if sm.get_nap_interrupted():
                time.sleep(5)

        # Detect motion once the user exits the pod the first time
        if sm.get_nap_completed() and sm.get_access_granted() and sm.get_door_unlocked() and not sm.get_motion_exiting_pod():
                sm.set_motion_exiting_pod(True)
                print("Motion detected: User exiting pod")
        
        # If the user is already out of the pod, don't do anything
        
def start_motion_monitor():
        GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_handler)
