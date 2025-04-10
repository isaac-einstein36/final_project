# Libraries
import urllib.request
import csv
from io import StringIO
from datetime import datetime

# Individual Components
from individual_components.servo import set_angle

# Security Access boolean in json
import json

# Read the boolean to see if access is granted
def get_access_granted():
    with open("shared_state.json", "r") as f:
        state = json.load(f)
    return state.get("access_granted", False)

# Files
# import read_bookings.read_database as read_database

# allBookings = read_database.read_csv()

# for slot in allBookings:
#         print(slot)

print(get_access_granted())

# Once Access is Granted!!

# Unlock the servo



# Check motion sensor (wait for user to enter the pod)
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