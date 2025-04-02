import requests
import csv
from io import StringIO
from datetime import datetime

# Replace with your generated direct download link
onedrive_direct_link = "https://buckeyemailosu-my.sharepoint.com/personal/einstein_15_buckeyemail_osu_edu/_layouts/15/download.aspx?sourceurl=/personal/einstein_15_buckeyemail_osu_edu/EXc3W4K5srVErQPhOtlQo-oBITUgMcGDUfpfI_tTTLs81g"

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

    def __str__(self):
        return f"TimeSlot({self.customer_name}, {self.start_time}, {self.service_name})"

# Function to clean and standardize StartTime
def clean_and_standardize_time(time_str):
    """Attempts to parse various date formats and convert to a standard format."""
    time_formats = [
        "%m/%d/%y %H:%M",         # Example: 4/2/25 13:00
        "%m/%d/%Y %I:%M:%S %p",   # Example: 4/2/2025 3:00:00 PM
        "%m/%d/%Y %H:%M",         # Example: 4/2/2025 15:00
    ]
    
    for fmt in time_formats:
        try:
            # Attempt to parse the time string with the current format
            # Using strptime to parse the date and then format it to the desired output
            return datetime.strptime(time_str, fmt).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return time_str  # Return original if no format matches

# Function to download CSV from OneDrive
def download_csv_from_onedrive(url):
    response = requests.get(url)
    if response.status_code == 200:
        csv_data = response.text
        return csv_data
    else:
        raise Exception(f"Failed to download file, status code: {response.status_code}")


# Read and process CSV file
def read_clean_csv():
        # Declare a list to hold cleaned TimeSlot objects
        clean_time_slots = []

        # Download and read CSV
        csv_text = download_csv_from_onedrive(onedrive_direct_link)
        csv_file = StringIO(csv_text)
        reader = csv.DictReader(csv_file)

        # Loop through each row
        for row in reader:
                # Ensure required fields are not blank
                if row["CustomerID"] and row["StartTime"]:  
                        standardized_time = clean_and_standardize_time(row["StartTime"])
                        
                time_slot = TimeSlot(
                        row["CustomerID"],
                        row["CustomerEmail"],
                        row["CustomerPhone"],
                        row["CustomerName"],
                        standardized_time,
                        row["ServiceName"],
                        row["Password"]
                        )
                clean_time_slots.append(time_slot)

        return clean_time_slots

clean_time_slots = read_clean_csv()

# Print first few entries to verify
for slot in clean_time_slots[:5]:
    print(slot)
