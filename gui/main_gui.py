# Libraries
import tkinter as tk    # GUI Library
from tkinter import ttk
from datetime import datetime
import threading
import json
import queue

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from tkinter import messagebox

# Global stop_event to control when to stop the face recognition
stop_event = threading.Event()

# Global Security booleans
pass_face_recognition = False
pass_password = False
shown_face_recognition_once = False

# Global upcoming booking name
upcoming_booking_name = "No Future Bookings"  # This would come from your booking system
upcoming_booking_start = datetime.now()  # This would come from your booking system

# Global upcoming booking password
correct_password = "No Future Bookings"  # This would come from your booking system

# Project Files
import read_bookings.read_database as read_database
from face_id.face_rec import start_face_recognition  # Import the function

def get_access_granted():
    with open("shared_state.json", "r") as f:
        state = json.load(f)
    return state.get("access_granted", False)

# Global function to show a home button throughout
def showHomeButton(screen, controller):
    # Load PNG image using tk.PhotoImage
    house_icon = tk.PhotoImage(file="gui/house.png")

    # Resize the image to a smaller size (proportional)
    house_icon = house_icon.subsample(10, 10)  # Resizing by a factor of 10 (adjust as needed)

    # Home button with icon only (no text)
    home_button = tk.Button(
        screen,
        image=house_icon,
        command=lambda: controller.show_frame(StartScreen),
        borderwidth=0  # Optional: makes the button cleaner
    )
    house_icon.image = house_icon  # Keep a reference to avoid garbage collection
    home_button.place(x=10, y=10)  # Position at the top-left corner

class App(tk.Tk):
    def __init__(self, message_queue):
        super().__init__()
        
        self.message_queue = message_queue
        
        self.title("Smart Nap Pod Booking System")
        self.geometry("400x300")

        # Container to hold all screens
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # Add all screens here
        for F in (StartScreen, AllBookingsScreen, CheckInScreen, SkipFacePage, PasswordPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Screens that DO need the queue
        enter_pod = EnterPodPage(parent=container, controller=self, message_queue=message_queue)
        self.frames[EnterPodPage] = enter_pod
        enter_pod.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartScreen)

    def show_frame(self, screen_class):
        """Ensure that face recognition stops before switching screens."""
        if isinstance(self.frames.get(CheckInScreen), CheckInScreen):
            self.frames[CheckInScreen].on_exit()  # Stop the face recognition when leaving the CheckInScreen

        frame = self.frames[screen_class]
        frame.tkraise()

        # Start face recognition again when switching to CheckInScreen
        if isinstance(frame, CheckInScreen):
            frame.on_show()  # Start face recognition when CheckInScreen is shown

        if hasattr(frame, "on_show"):
            frame.on_show()

        if not hasattr(frame, 'home_button'):
            showHomeButton(frame, self)

# Screen to show the upcoming booking and future bookings
class StartScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        showHomeButton(self,controller)

        self.controller = controller
        
        label = tk.Label(self, text="Home Screen")
        label.pack(pady=10)
        
        btn = tk.Button(self, text="See All Bookings",
                        command=lambda: controller.show_frame(AllBookingsScreen))
        btn.pack()

        self.checkin_button = tk.Button(self, text="Check-In for Appointment")
        self.checkin_button.pack(pady=10)

        self.enter_pod_btn = tk.Button(self, text="Enter Pod", state="disabled",
                                       command=lambda: controller.show_frame(EnterPodPage))
        self.enter_pod_btn.pack(pady=10)

        # Check if the user has logged in properly to their nap session
        if get_access_granted():
            self.enter_pod_btn.config(state="normal")

        # Read the available bookings
        allBookings = read_database.read_csv()

        # Delete past bookings from the array
        now = datetime.now()

        # Create a new list to only include future bookings
        futureBookings = [entry for entry in allBookings if entry.start_time > now]

        # Show the upcoming booking
        if futureBookings:
            upcoming_booking = futureBookings[0]
            
            # Save upcoming name and password globally
            global upcoming_booking_name, correct_password
            upcoming_booking_name = upcoming_booking.customer_name
            correct_password = upcoming_booking.password
            
            booking_label = tk.Label(self, text=f"Upcoming Booking:\n {upcoming_booking}")
            booking_label.pack(pady=10)

            # Calculate time remaining until next appointment
            global upcoming_booking_start
            upcoming_booking_start = upcoming_booking.start_time
            time_diff = upcoming_booking_start - now
            total_seconds = int(time_diff.total_seconds())

            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60

            formatted_time = f"Time Until Appointment: {days} days, {hours} hours, {minutes} minutes"
            
            time_remaining_label = tk.Label(self,text=formatted_time)
            time_remaining_label.pack(pady=10)
            # self.time_remaining_label = time_remaining_label

            # List all other bookings
            tk.Label(self, text="Future Bookings:").pack(pady=5)
            counter = 1
            for slot in futureBookings[1:]:
                booking_label = tk.Label(self, text=f"{counter}. {slot}")
                booking_label.pack(pady=2)
                counter+=1
        
        # If there aren't any future bookings
        else:
            no_booking_label = tk.Label(self, text="No Upcoming Bookings")
            no_booking_label.pack(pady=10)

    def on_show(self):
        global shown_face_recognition_once
        global upcoming_booking_start

        if shown_face_recognition_once:
            self.checkin_button.config(
                text="Check-In for Appointment (Email Verification)",
                command=lambda: self.controller.show_frame(SkipFacePage)
            )
        else:
            self.checkin_button.config(
                text="Check-In for Appointment (Face ID)",
                command=lambda: self.controller.show_frame(CheckInScreen)
            )

        # See if the user has logged in properly to their nap session
        if get_access_granted():
            self.enter_pod_btn.config(state="normal")

        # Update time remaining label
        global upcoming_booking_start
        time_diff = upcoming_booking_start - datetime.now()
        total_seconds = int(time_diff.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        new_formatted_time = f"Time Until Appointment: {days} days, {hours} hours, {minutes} minutes"
        # self.time_remaining_label.config = tk.Label(text=new_formatted_time)

# Screen to see all bookings
class AllBookingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        showHomeButton(self,controller)

        label = tk.Label(self, text="All Bookings").pack(pady=20)
        
        # Read the available bookings
        allBookings = read_database.read_csv()
        
        # List all bookings
        counter = 1
        for slot in allBookings:
            booking_label = tk.Label(self, text=f"{counter}. {slot}")
            booking_label.pack(pady=2)
            counter+=1

# Screen to check in for appointment
class CheckInScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        showHomeButton(self, controller)

        label = tk.Label(self, text="Check-In For Appointment")
        label.pack(pady=10)

        # Store the upcoming booking name for comparison (for now, hardcoded)
        global upcoming_booking_name
        global upcoming_booking_start
        self.upcoming_booking_name = upcoming_booking_name  # This would come from your booking system
        # self.upcoming_booking_name = "Isaac" # For testing purposes

        # StringVar to hold the recognized name
        self.recognized_name_var = tk.StringVar()
        self.recognized_name_var.set("Waiting for face recognition...")  # Initial text
        self.recognized_name_label = tk.Label(self, textvariable=self.recognized_name_var)
        self.recognized_name_label.pack(pady=10)

        # StringVar for displaying the expected name
        self.expected_name_var = tk.StringVar()
        self.expected_name_var.set(f"Expecting: {self.upcoming_booking_name}")  # Default to upcoming booking
        self.expected_name_label = tk.Label(self, textvariable=self.expected_name_var)
        self.expected_name_label.pack(pady=10)

        # StringVar for instructions
        self.exit_instructions_var = tk.StringVar()
        self.exit_instructions_var.set("Please Press 'q' to Exit")
        self.exit_instructions_label = tk.Label(self, textvariable=self.exit_instructions_var)
        self.exit_instructions_label.pack(pady=10)

        self.face_recognition_thread = None

        # Add the button for password page (initially hidden)
        self.password_button = tk.Button(self, text="Go to Password Page", 
                                         command=lambda: controller.show_frame(PasswordPage))  # Adjust this to your password page screen class
        self.password_button.pack(pady=10)
        self.password_button.pack_forget()  # Hide the button initially

        # Button to skip FaceID
        self.skip_face_recognition_button = tk.Button(self, text="Skip Face Recognition",
                                                      command=lambda: controller.show_frame(SkipFacePage), fg="red")
        self.skip_face_recognition_button.pack(pady=5)

    def on_show(self):
        """This function starts the face recognition when the screen is shown."""
        # self.recognized_name_var.set(f"Expecting: {self.upcoming_booking_name}")

        if self.face_recognition_thread is None or not self.face_recognition_thread.is_alive():
            self.start_face_recognition_thread()

    def start_face_recognition_thread(self):
        """This function starts the face recognition in a background thread."""
        # Set shownFaceRecognitionOnce to True
        global shown_face_recognition_once
        shown_face_recognition_once = True
        
        # Reset the stop_event before starting the face recognition
        stop_event.clear()

        # Start the face recognition in a new thread
        self.face_recognition_thread = threading.Thread(target=start_face_recognition, 
                                                        args=(self.update_recognized_name,), daemon=True)
        self.face_recognition_thread.start()

    def update_recognized_name(self, name):
        """This function is used as a callback to update the recognized name in the GUI."""
        self.recognized_name_var.set(f"Recognized: {name}")
        
        # Show the welcome message if the recognized name matches the expected name
        if name == self.upcoming_booking_name:
            print(f"Welcome {name}, you're expected!")
            self.recognized_name_var.set(f"\nRecognized: {name} - Welcome {name}!")
            # Remove the expecting label after successful recognition
            self.expected_name_label.pack_forget()

            global pass_face_recognition
            pass_face_recognition = True

            if pass_face_recognition:
                # Show the password button once the person is recognized
                self.password_button.pack(pady=10)  # Make the button visible now
        else:
            print(f"Unexpected person: {name}")

    def on_exit(self):
        stop_event.set()
        if self.face_recognition_thread and self.face_recognition_thread.is_alive():
            self.face_recognition_thread.join()  # Wait for the thread to clean up properly

# Function to send a verification email
def send_verification_email(receiver_email):
    # Email account credentials
    sender_email = "smartproductsfinalproject2025@gmail.com"
    sender_password = "alsu yvfg mnvi ovnx"  # Use App Password if you have 2FA enabled

    # Generate a random 6-digit verification code
    verification_code = random.randint(100000, 999999)

    # Create the email content
    subject = "Your Verification Code"
    body = f"Your verification code is: {verification_code}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email via Gmail's SMTP server
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print(f"Verification email sent to {receiver_email}")
        return verification_code
    except Exception as e:
        print(f"Error sending email: {e}")
        return None


# Tkinter GUI page to skip face recognition and send verification email
class SkipFacePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        showHomeButton(self,controller)

        self.controller = controller

        # Label to show what the page is about
        label = tk.Label(self, text="")
        label.pack(pady=20)

        # Label to show what the page is about
        label = tk.Label(self, text="Enter Email to Receive Verification Code")
        label.pack(pady=20)

        # Email entry field
        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(pady=10)

        # Button to send verification email
        send_btn = tk.Button(self, text="Send Code", command=self.send_code)
        send_btn.pack(pady=10)

        # Label to show the verification status
        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack(pady=10)

        # Code entry field to verify the code
        self.code_entry = tk.Entry(self, width=30)
        self.code_entry.pack(pady=10)

        # Button to verify the code
        verify_btn = tk.Button(self, text="Verify Code", command=self.verify_code)
        verify_btn.pack(pady=10)

        # Button to go to password page after verification
        self.password_btn = tk.Button(self, text="Go to Password Page", state="disabled",
                                      command=lambda: controller.show_frame(PasswordPage))
        self.password_btn.pack(pady=20)

    def send_code(self):
        # Get the email from the entry field
        email = self.email_entry.get()

        if email:
            # Send the verification email and get the code
            self.verification_code = send_verification_email(email)

            if self.verification_code:
                self.status_label.config(text=f"Code sent to {email}")
                self.status_label.config(fg="green")
            else:
                self.status_label.config(text="Failed to send code. Try again.")
                self.status_label.config(fg="red")
        else:
            self.status_label.config(text="Please enter a valid email.")
            self.status_label.config(fg="red")

    def verify_code(self):
        # Get the entered code
        entered_code = self.code_entry.get()

        if entered_code == str(self.verification_code):
            self.status_label.config(text="Verification successful!", fg="green")
            self.password_btn.config(state="normal")  # Enable the password button
        else:
            self.status_label.config(text="Incorrect code. Try again.", fg="red")


# Password Page for entering password
class PasswordPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        showHomeButton(self, controller)

        label = tk.Label(self, text="Enter your password")
        label.pack(pady=20)

        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=10)

        self.result_label = tk.Label(self, text="", fg="red")
        self.result_label.pack(pady=10)

        submit_button = tk.Button(self, text="Submit", command=self.check_password)
        submit_button.pack(pady=10)

        # Button to go to "Enter Pod" page after verification
        self.enter_pod_btn = tk.Button(self, text="Click to Enter Pod!", state="disabled",
                                      command=lambda: controller.show_frame(EnterPodPage))
        self.enter_pod_btn.pack(pady=10)

    def set_access_granted(self,value):
        try:
            with open("shared_state.json", "r") as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}

        state["access_granted"] = value

        with open("shared_state.json", "w") as f:
            json.dump(state, f, indent=4)

    def check_password(self):
        entered_password = self.password_entry.get()
        global correct_password
        correct_password = "1234"
        if entered_password == correct_password:
            self.set_access_granted(True)
            self.result_label.config(text="You may enter the pod!", fg="green")
            global pass_password
            pass_password = True
            self.enter_pod_btn.config(state="normal")  # Enable the enter pod button

        else:
            self.set_access_granted(False)
            self.result_label.config(text="Access Denied", fg="red")
            self.enter_pod_btn.config(state="disabled")

class EnterPodPage(tk.Frame):
    def __init__(self, parent, controller, message_queue):
        super().__init__(parent)

        self.message_queue = message_queue

        showHomeButton(self, controller)

        label = tk.Label(self, text="\n\nWelcome to Your Nap Session!")
        label.pack(pady=20)

        self.timer_label = tk.Label(self, text="Time remaining: --:--:--", font=("Helvetica", 12))
        self.timer_label.pack(pady=(10, 5))
        
        # Create textbox for displaying messages
        self.textbox = tk.Text(
            self,
            height=15,
            width=60,
            state='disabled',
            wrap='word',
            bg=self.cget("bg"),           # Match frame background
            relief='flat',                # Remove 3D border
            bd=0,                         # No border
            font=("Helvetica", 11),       # Clean readable font
            highlightthickness=0,        # No border highlight
            cursor="arrow"               # No typing cursor
        )
        self.textbox.pack(pady=(10, 5), padx=10)

        # Add a clear textbox button
        clear_button = tk.Button(
            self,
            text="Clear Messages",
            command=self.clear_textbox,
            font=("Helvetica", 10),
            relief='ridge',
            bg="#e0e0e0"
        )
        clear_button.pack(pady=(0, 10))

        # Add a scrollbar to the textbox
        scrollbar = tk.Scrollbar(self, command=self.textbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.textbox.config(yscrollcommand=scrollbar.set)

        # Start checking the queue for updates
        self.after(100, self.check_queue)

    def clear_textbox(self):
        self.textbox.config(state='normal')
        self.textbox.delete(1.0, tk.END)
        self.textbox.config(state='disabled')

    def check_queue(self):
        try:
            while True:
                msg = self.message_queue.get_nowait()

                # Handle timer updates differently
                if isinstance(msg, dict) and msg.get("type") == "timer":
                    self.timer_label.config(text=f"Time remaining: {msg['text']}")
                else:
                    self.textbox.config(state='normal')
                    self.textbox.insert(tk.END, msg + "\n")
                    self.textbox.see(tk.END)
                    self.textbox.config(state='disabled')

        except queue.Empty:
            pass

        self.after(200, self.check_queue)  # Keep checking

if __name__ == "__main__":
    app = App()
    app.mainloop()
