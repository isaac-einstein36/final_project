import urllib.request
import csv
from io import StringIO
from datetime import datetime
# from git import Repo

# Define the TimeSlot class
class TimeSlot:
    def __init__(self, customer_id, customer_email, customer_phone, customer_name, start_time, service_name, password):
        # Initialize the TimeSlot object with provided parameters
        self.customer_id = customer_id
        self.customer_email = customer_email
        self.customer_phone = customer_phone
        self.customer_name = customer_name
        self.start_time = start_time
        self.service_name = service_name
        self.password = password

        self.formattedTime = formatted_time = self.start_time.strftime("%I:%M %p %m/%d/%y")

    def __str__(self):
        # return f"TimeSlot({self.customer_name}, {self.formattedTime}, {self.service_name})"
        return f"{self.service_name} – {self.customer_name} | {self.formattedTime}"

# Function to pull the latest changes from the Git repository
# def pull_latest_repo():
#     # Path to your local Git repo
#     # repo_path = "~/Library/CloudStorage/OneDrive-TheOhioStateUniversity/Ohio State/Classes/SP2025/5194 - Smart Products/Github/final_project"
#     # repo_path = repo_path.replace("~", "/Users/sierrabasic")
#     repo_path = "~/Documents/5194_Code_Repo/final_project"

#     # Open the repo
#     repo = Repo(repo_path)

#     # Make sure it's not in a detached HEAD state
#     assert not repo.bare

#     # Pull the latest changes from origin (default remote)
#     origin = repo.remotes.origin
#     origin.pull()

#     print("Repository updated with latest changes.")

# Read and process CSV file
def read_csv():
        # Declare a list to hold cleaned TimeSlot objects
        time_slots = []

        # Download and read CSV
        # Open and read the CSV file
        csv_file = "MasterBookings.csv"
        with open(csv_file, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)

            # Loop through each row
            for row in reader:
                    # Ensure required fields are not blank
                    if row["CustomerID"] and row["StartTime"]:  
                            
                        time_slot = TimeSlot(
                                row["CustomerID"],
                                row["CustomerEmail"],
                                row["CustomerPhone"],
                                row["CustomerName"],
                                # row["StartTime"],
                                datetime.strptime(row["StartTime"], "%Y-%m-%dT%H:%M:%S"),
                                row["ServiceName"],
                                row["Password"]
                                )
                        time_slots.append(time_slot)

        # Sort by start time
        time_slots = sorted(time_slots, key=lambda slot: slot.start_time)   
        # time_slots.sort(key=lambda slot: time_slot.start_time.strip())

        return time_slots

# pull_latest_repo()
