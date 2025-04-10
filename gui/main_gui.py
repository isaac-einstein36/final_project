# Libraries
import tkinter as tk    # GUI Library
from tkinter import ttk
from datetime import datetime
import threading
import json

# Global stop_event to control when to stop the face recognition
stop_event = threading.Event()

# Global Security booleans
pass_face_recognition = False
pass_password = False

# Global upcoming booking name
upcoming_booking_name = "No Future Bookings"  # This would come from your booking system

# Global upcoming booking password
correct_password = "No Future Bookings"  # This would come from your booking system

# Project Files
import read_bookings.read_database as read_database
from face_id.face_rec import start_face_recognition  # Import the function

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
    def __init__(self):
        super().__init__()
        self.title("Smart Nap Pod Booking System")
        self.geometry("400x300")

        # Container to hold all screens
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # Add all screens here
        for F in (StartScreen, AllBookingsScreen, CheckInScreen, PasswordPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

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

# Screen to show the upcoming booking and future bookings
class StartScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        showHomeButton(self,controller)
        
        label = tk.Label(self, text="Home Screen")
        label.pack(pady=10)
        
        btn = tk.Button(self, text="See All Bookings",
                        command=lambda: controller.show_frame(AllBookingsScreen))
        btn.pack()
        
        btn = tk.Button(self, text="Check-In for Appointment",
                        command=lambda: controller.show_frame(CheckInScreen))
        btn.pack()

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
            
            booking_label = tk.Label(self, text=f"Upcoming Booking: {upcoming_booking}")
            booking_label.pack(pady=10)
            
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

    def on_show(self):
        """This function starts the face recognition when the screen is shown."""
        # self.recognized_name_var.set(f"Expecting: {self.upcoming_booking_name}")

        if self.face_recognition_thread is None or not self.face_recognition_thread.is_alive():
            self.start_face_recognition_thread()

    def start_face_recognition_thread(self):
        """This function starts the face recognition in a background thread."""
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
            self.recognized_name_var.set(f"Recognized: {name} - Welcome {name}!")
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

    def set_access_granted(self,value):
        with open("shared_state.json", "w") as f:
            json.dump({"access_granted": value}, f)

    def check_password(self):
        entered_password = self.password_entry.get()
        global correct_password
        correct_password = "1234"
        if entered_password == correct_password:
            self.set_access_granted(True)
            self.result_label.config(text="You may enter the pod!", fg="green")
            global pass_password
            pass_password = True

        else:
            self.set_access_granted(False)
            self.result_label.config(text="Access Denied", fg="red")

if __name__ == "__main__":
    app = App()
    app.mainloop()
