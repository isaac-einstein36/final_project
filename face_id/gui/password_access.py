import tkinter as tk
import json

def set_access_granted(value):
    with open("shared_state.json", "w") as f:
        json.dump({"access_granted": value}, f)


# Set up the main window
root = tk.Tk()
root.title("Pod Access")
root.geometry("300x150")

# Variables
correct_password = "openSesame"  # You can change this

# Functions
def check_password():
    entered_password = password_entry.get()
    if entered_password == correct_password:
        set_access_granted(True)
        result_label.config(text="You may enter the pod!", fg="green")
    else:
        set_access_granted(False)
        result_label.config(text="Access Denied", fg="red")

# GUI Elements
prompt_label = tk.Label(root, text="Enter Password:")
prompt_label.pack(pady=5)

password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

submit_button = tk.Button(root, text="Submit", command=check_password)
submit_button.pack(pady=5)

result_label = tk.Label(root, text="")
result_label.pack(pady=10)

# Run the GUI loop
root.mainloop()
