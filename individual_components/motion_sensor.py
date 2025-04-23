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
    
    
# ## Revised Code
# import RPi.GPIO as GPIO
# import time
# import threading
# import state_manager as sm

# SENSOR_PIN = 12

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(SENSOR_PIN, GPIO.IN)

# motion_phase = "idle"  # shared state

# def motion_handler(channel):
#     global motion_phase
#     if motion_phase == "idle":
#         print("User entering pod")
#         sm.set_motion_entering_pod(True)
#         sm.set_motion_exiting_pod(False)
#         motion_phase = "entered"

# def monitor_for_exit():
#     global motion_phase
#     while True:
#         if motion_phase == "entered" and GPIO.input(SENSOR_PIN) == GPIO.LOW:
#             print("User exiting pod")
#             sm.set_motion_exiting_pod(True)
#             sm.set_motion_entering_pod(False)
#             motion_phase = "idle"
#         time.sleep(0.5)

# def start_motion_monitor():
#     GPIO.add_event_detect(SENSOR_PIN, GPIO.RISING, callback=motion_handler)
#     threading.Thread(target=monitor_for_exit, daemon=True).start()

