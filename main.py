# Libraries
import urllib.request
import csv
from io import StringIO
from datetime import datetime
import time

# Importing Files
# import read_bookings.read_database as read_database
from gui.main_gui import App
from individual_components.servo import set_angle       # Servo file
import individual_components.motion_sensor as motion_sensor # Motion Sensor file

# Security Access boolean in json
import json

############################################################################
# Main Code #
############################################################################

# Read the access boolean to see if access is granted (FaceID and Password entered)
def get_access_granted():
    with open("shared_state.json", "r") as f:
        state = json.load(f)
    return state.get("access_granted", False)

def get_door_unlocked():
    with open("shared_state.json", "r") as f:
        state = json.load(f)
    return state.get("door_unlocked", False)

def get_motion_detected():
    with open("shared_state.json", "r") as f:
        state = json.load(f)
    return state.get("motion_detected", False)

def set_door_unlocked(value):
    try:
        with open("shared_state.json", "r") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    state["door_unlocked"] = value

    with open("shared_state.json", "w") as f:
        json.dump(state, f, indent=4)

def set_motion_detected(value):
    try:
        with open("shared_state.json", "r") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    state["motion_detected"] = value

    with open("shared_state.json", "w") as f:
        json.dump(state, f, indent=4)

def unlock_door():
    # Unlock the door (with a servo)
    set_angle(90)  # Unlock the door
    
    # Change the json variable that the door's unlocked
    set_door_unlocked(True)
    print("Door Unlocked")

def lock_door():
    # Unlock the door (with a servo)
    set_angle(180)  # Unlock the door
    
    # Change the json variable that the door's unlocked
    set_door_unlocked(False)
    print("Door Locked")

# Open GUI
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()

# # Once Access is Granted!!
# while (not get_access_granted()):
#     time.sleep(0.1)

# Unlock the door (with a servo)
unlock_door()

# Wait for user to enter the pod
# Check motion sensor (wait for user to enter the pod)
while(get_door_unlocked()):
    while (not get_motion_detected()):
        time.sleep(0.1)
        
    if get_motion_detected():
        print("User Entered!")
        set_motion_detected(False)

        # Turn the fan on
        # Turn the LED on

# User pushes button to lock 

# GUI starts counting down

# Timer Ends
        # Alarm sounds
        # Door Unlocks
        # LED changes color to alert user
        
# Wait for motion sensor again (Wait for user to exit the pod)
# Have user click on GUI that they exited
        # Turn off fan
        # Turn off LED
        # Lock the door with the servo