# Libraries
import urllib.request
import csv
from io import StringIO
from datetime import datetime, timedelta
import time
import threading
from queue import Queue

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
def gui_print(msg):
    print(msg)
    gui_message_queue.put(msg)

def unlock_door():
    # Unlock the door (with a servo)
    set_angle(90)  # Unlock the door
    
    # Set LED to green
    set_led_color('green')
        
    # Change the json variable that the door's unlocked
    sm.set_door_unlocked(True)
    gui_print("\nDoor Unlocked")

def lock_door():
    # Unlock the door (with a servo)
    set_angle(180)  # Unlock the door
    
    # Set LED to red
    set_led_color('red')
    
    # Change the json variable that the door's unlocked
    sm.set_door_unlocked(False)
    gui_print("\nDoor Locked")

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
        gui_print("User is interupting their nap. Please wait for the user to exit the pod.")

        # Update the time remaining on the GUI
        hrs = 0
        mins = 0
        secs = 0
        gui_print({"type": "timer", "text": f"{hrs:02}:{mins:02}:{secs:02}"})

        # Update the json variable that the user is interupting their nap
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
    gui_print("\nNap is over!")

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
    gui_print("\nWaiting for user to exit the pod...")
    
    while (not sm.get_motion_exiting_pod()):
        time.sleep(0.1)
    
    gui_print("\nUser has exited the pod. Locking the door...")
    
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
    gui_print("\nSystem Reset - Ready to Run!")
    gui_print("Waiting for the next nap session")
    gui_print("________________________________________")

# Enable Queue for communication between threads
gui_message_queue = Queue()

# Open GUI
def launch_gui():
    app = App(gui_message_queue)
    app.mainloop()

# Run GUI in a separate thread
gui_thread = threading.Thread(target=launch_gui, daemon=True)
gui_thread.start()

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
        msg = "\nWaiting for user to enter the pod..."
        gui_print(msg)
        
        # Wait for the user to enter the pod
        while (not sm.get_motion_entering_pod()):
            time.sleep(0.1)

        # Once the user enters the pod, turn fan on, etc.
        msg = "\nUser has opened the pod!"
        gui_print(msg)
            
        # Turn the fan on
        set_fan_speed(0.50)

        # Once the button is pressed, the door locks
        msg = "\nWaiting for user to lock the door..."
        gui_print(msg)
        
        # Wait for the user to lock the door
        while (sm.get_door_unlocked()):
            time.sleep(0.1)

        # Sleep for button debouncing
        time.sleep(1)

        # Once the user's locked the door, their nap is in progress
        sm.set_nap_in_progress(True)

        gui_print("\nUser has locked the door. Starting nap timer...\nThe user has 30 minutes to take a nap.")

        # Calculate the end time of the nap
        start_time = datetime.now()
        nap_duration = 1 * 60
        end_time = start_time + timedelta(seconds=nap_duration)
        
        # Format and print nap end time
        msg = f"\nNap will end at {end_time.strftime('%-I:%M %p')}"  # e.g., 3:35 PM
        gui_print(msg)

        # Start the timer. Wait for nap duration to end or user to interrupt
        msg = "\nNap in progress..."
        print(msg)
        gui_print(msg)

        # Countdown loop
        while datetime.now() < end_time and not sm.get_nap_interrupted():
            remaining_time = end_time - datetime.now()
            remaining_seconds = int(remaining_time.total_seconds())

            mins, secs = divmod(remaining_seconds, 60)
            hrs, mins = divmod(mins, 60)
            # print(f"Time remaining: {hrs:02}:{mins:02}:{secs:02}", end='\r')
            gui_print({"type": "timer", "text": f"{hrs:02}:{mins:02}:{secs:02}"})

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
'''
