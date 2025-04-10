# Libraries
import tkinter as tk    # GUI Library
from datetime import datetime

# Project Files
import read_bookings.read_database as read_database

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
        for F in (StartScreen, AllBookingsScreen, CheckInScreen):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartScreen)

    def show_frame(self, screen_class):
        frame = self.frames[screen_class]
        frame.tkraise()

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

        showHomeButton(self,controller)

        
        label = tk.Label(self, text="Check-In For Appointment")
        label.pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
