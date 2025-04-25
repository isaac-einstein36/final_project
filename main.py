# Libraries
import urllib.request
import csv
from io import StringIO
from datetime import datetime, timedelta
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
    print("\nDoor Unlocked")

def lock_door():
    # Unlock the door (with a servo)
    set_angle(180)  # Unlock the door
    
    # Set LED to red
    set_led_color('red')
    
    # Change the json variable that the door's unlocked
    sm.set_door_unlocked(False)
    print("\nDoor Locked")

def change_door_state():
    # Change the door state
    if sm.get_door_unlocked():
        lock_door()
    else:
        unlock_door()

def turn_off_alarm():
    # Turn off the alarm
    sm.set_snooze_alarm(True)

def check_nap_interupt():
    # If the user is interupting their nap, display a message
    if sm.get_nap_in_progress():
        print("User is interupting their nap. Please wait for the user to exit the pod.")
        sm.set_nap_in_progress(False)
        sm.set_nap_interrupted(True)

def manage_button_hold():
    # Change the door state
    change_door_state()

    # If the alarm is sounding, turn it off
    if sm.get_alarm_sounding():
        turn_off_alarm()

    # Check if the user is interupting their nap
    check_nap_interupt()

def end_of_nap():
    # Set nap in progress to false
    sm.set_nap_in_progress(False)
    sm.set_nap_completed(True)

    # Play an alarm to wake up user unless they interrupted the nap
    if not sm.get_nap_interrupted():
        play_alarm()

    # Unlock the door
    unlock_door()

    # Turn off the fan
    set_fan_speed(0)

    # Wait for the user to exit the pod
    print("\nWaiting for user to exit the pod...")
    while (not sm.get_motion_exiting_pod()):
        time.sleep(0.1)
    
    print("\nUser has exited the pod. Locking the door...")
    
    time.sleep(1)

    # Set access granted to false for the next user and lock the door
    sm.set_access_granted(False)

def reset():
    # Reset the json variables
    sm.set_door_unlocked(False)
    sm.set_nap_in_progress(False)
    sm.set_motion_entering_pod(False)
    sm.set_motion_exiting_pod(False)
    sm.set_nap_completed(False)
    sm.set_nap_interrupted(False)
    sm.set_alarm_sounding(False)
    sm.set_snooze_alarm(False)

    # Set LED to red
    set_led_color('red')

    # Lock the door
    lock_door()

    time.sleep(5)
    print("\nSystem Reset - Ready to Run!")
    print("Waiting for the next nap session")
    print("##########################")

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
motion_sensor.start_motion_monitor()

while True:

    # Wait for access to be granted
    if (sm.get_access_granted()):

        # Unlock the door (with a servo) and turn LED to green
        unlock_door()
        
        # Hard coding motion sensor for debugging
        print("\nWaiting for user to enter the pod...")
        
        # Wait for the user to enter the pod
        while (not sm.get_motion_entering_pod()):
            time.sleep(0.1)

        # Once the user enters the pod, turn fan on, etc.
        print("\nUser has opend the pod!")
            
        # Turn the fan on
        set_fan_speed(0.50)

        # Once the button is pressed, the door locks
        print("\nWaiting for user to lock the door...")
        
        # Wait for the user to lock the door
        while (sm.get_door_unlocked()):
            time.sleep(0.1)

        # Sleep for button debouncing
        time.sleep(1)

        # Once the user's locked the door, their nap is in progress
        sm.set_nap_in_progress(True)

        # State the time for the nap has started
        print("\nUser has locked the door. Starting nap timer...")
        print("The user has 20 minutes to take a nap.")
        ("##########################")

        
        # Calculate the end time of the nap
        start_time = datetime.now()
        nap_duration = .5 * 60
        end_time = start_time + timedelta(seconds=nap_duration)
        
        # Format and print nap end time
        print("\nNap will end at", end_time.strftime("%-I:%M %p"))  # e.g., 3:35 PM

        # Start the timer. Wait for nap duration to end or user to interrupt
        print("Nap in progress...")

        # Countdown loop
        while datetime.now() < end_time and not sm.get_nap_interrupted():
            remaining_time = end_time - datetime.now()
            remaining_seconds = int(remaining_time.total_seconds())

            mins, secs = divmod(remaining_seconds, 60)
            hrs, mins = divmod(mins, 60)
            print(f"Time remaining: {hrs:02}:{mins:02}:{secs:02}", end='\r')

            time.sleep(1)
        
        # Once the nap ends, alarm plays and door unlocks. Reset for next user
        end_of_nap()

        time.sleep(3)

        # State the system is reset
        reset()


# TODO:
'''
- Make GUI usable while main.py runs
    - Add GUI to show nap timer
- Add nap timer
- Add interrupting nap session
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