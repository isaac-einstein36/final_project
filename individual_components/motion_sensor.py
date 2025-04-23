import RPi.GPIO as GPIO
import time
import json
 
SENSOR_PIN = 12
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
 
def set_motion_detected(value):
    try:
        with open("shared_state.json", "r") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    state["motion_detected"] = value

    with open("shared_state.json", "w") as f:
        json.dump(state, f, indent=4)

def my_callback(channel):
    # Here, alternatively, an application / command etc. can be started.
    print('There was a movement!')

    set_motion_detected(True)
    
try:
    GPIO.add_event_detect(SENSOR_PIN , GPIO.RISING, callback=my_callback)
    set_motion_detected(False)
    # while True:
    #     time.sleep(100)
    #     set_door_unlocked(False)
except KeyboardInterrupt:
    print ("Finish")
    
    
