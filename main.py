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
from individual_components.fan import set_fan_speed # Fan file
from individual_components.led import set_led_color # LED file
from individual_components.alarm import play_alarm # Alarm file
from gpiozero import Button

# Security Access boolean in json
import json
import state_manager as sm

############################################################################
# Main Code #
############################################################################

def unlock_door():
    # Unlock the door (with a servo)
    set_angle(90)  # Unlock the door
    
    # Set LED to green
    set_led_color('green')
        
    # Change the json variable that the door's unlocked
    sm.set_door_unlocked(True)
    print("Door Unlocked")

def lock_door():
    # Unlock the door (with a servo)
    set_angle(180)  # Unlock the door
    
    # Set LED to red
    set_led_color('red')
    
    # Change the json variable that the door's unlocked
    sm.set_door_unlocked(False)
    print("Door Locked")

def change_door_state():
    print("Button Pressed!")
    # Change the door state
    if sm.get_door_unlocked():
        lock_door()
    else:
        unlock_door()
        
        # If the user is interupting their nap, display a message
        if sm.get_nap_in_progress():
            print("User is interupting their nap. Please wait for the user to exit the pod.")
            sm.set_nap_in_progress(False)

def turn_off_alarm():
    # Turn off the alarm
    sm.set_snooze_alarm(True)

def manage_button_hold():
    # Change the door state
    change_door_state()

    # If the alarm is sounding, turn it off
    if sm.get_alarm_sounding():
        turn_off_alarm()

def end_of_nap():
    # Set nap in progress to false
    sm.set_nap_in_progress(False)
    sm.set_nap_completed(True)

    # Play an alarm to wake up user
    play_alarm()

    # Unlock the door
    unlock_door()

    # Turn off the fan
    set_fan_speed(0)

    # Set access granted to false for the next user
    sm.set_access_granted(False)

    # Once the user exits, lock the door
    time.sleep(5)
    print("User has exited the pod. Locking the door...")
    lock_door()

def reset():
    # Reset the json variables
    sm.set_door_unlocked(False)
    sm.set_motion_detected(False)
    sm.set_nap_in_progress(False)
    sm.set_motion_entering_pod(False)
    sm.set_motion_exiting_pod(False)
    sm.set_nap_completed(False)
    sm.set_alarm_sounding(False)
    sm.set_snooze_alarm(False)

    # Set LED to red
    set_led_color('red')

    # Lock the door
    lock_door()

    time.sleep(5)
    print("System Reset - Ready to Run!")

# Open GUI
# if __name__ == "__main__":
#     app = App()
#     app.mainloop()

# # Once Access is Granted!!
# while (not get_access_granted()):
#     time.sleep(0.1)

# Reset the json variables
reset()

# Declare button
doorButton = Button(25)
# When the button is pushed, the door locks
doorButton.when_held = manage_button_hold

# Start the motion sensor
# motion_sensor.start_motion_monitor()


while True:

    # Wait for access to be granted
    if (sm.get_access_granted()):

        # Unlock the door (with a servo) and turn LED to green
        unlock_door()
        
        # Hard coding motion sensor for debugging
        print("Waiting for user to enter the pod...")
        time.sleep(3)

        # Wait for user to open the door and enter the pod
        # while (not sm.get_motion_entering_pod()):
        #     time.sleep(0.1)
        
        # Turn the fan on
        set_fan_speed(0.50)

        # Once the button is pressed, the door locks
        print("Waiting for user to lock the door...")
        
        while (sm.get_door_unlocked()):
            time.sleep(0.1)

        # Once the user's locked the door, their nap is in progress
        sm.set_nap_in_progress(True)

        # State the time for the nap has started
        print("User has locked the door. Starting nap timer...")
        print("The user has 20 minutes to take a nap.")

        # Once the nap ends, alarm plays and door unlocks. Reset for next user
        end_of_nap()


# TODO:
'''
- Make GUI usable while main.py runs
    - Add GUI to show nap timer
- Add nap timer
- Add in motion sensor
'''
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