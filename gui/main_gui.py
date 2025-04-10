# GUI Library
import tkinter as tk

# Project Files
import read_bookings.read_database as read_database

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Screen App")
        self.geometry("400x300")

        # Container to hold all screens
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # Add all screens here
        for F in (StartScreen, SecondScreen):
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
        label = tk.Label(self, text="Home Screen")
        label.pack(pady=10)
        btn = tk.Button(self, text="Go to Second Screen",
                        command=lambda: controller.show_frame(SecondScreen))
        btn.pack()

        # Read the available bookings
        allBookings = read_database.read_csv()

        # Delete past bookings from the array
        
        for slot in allBookings:
            booking_label = tk.Label(self, text=f"Booking: {slot}")
            booking_label.pack(pady=2)

class SecondScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Second Screen")
        label.pack(pady=10)
        btn = tk.Button(self, text="Back to Start",
                        command=lambda: controller.show_frame(StartScreen))
        btn.pack()

if __name__ == "__main__":
    app = App()
    app.mainloop()
