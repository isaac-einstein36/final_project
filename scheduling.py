import urllib.request
import csv
from io import StringIO
from datetime import datetime

# Replace with your generated direct download link
onedrive_direct_link = "https://buckeyemailosu-my.sharepoint.com/personal/einstein_15_buckeyemail_osu_edu/_layouts/15/download.aspx?sourceurl=/personal/einstein_15_buckeyemail_osu_edu/EXc3W4K5srVErQPhOtlQo-oBITUgMcGDUfpfI_tTTLs81g"

# Add the User-Agent header to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to download CSV from OneDrive using urllib and a User-Agent header
def download_csv_from_onedrive(url):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request) as response:
        csv_data = response.read().decode('utf-8')
        return csv_data

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

# # Function to download CSV from OneDrive using urllib
# def download_csv_from_onedrive(url):
#     with urllib.request.urlopen(url) as response:
#         csv_data = response.read().decode('utf-8')
#         return csv_data

# Read and process CSV file
def read_clean_csv():
        # Declare a list to hold cleaned TimeSlot objects
        clean_time_slots = []

        # Download and read CSV
        csv_text = download_csv_from_onedrive(onedrive_direct_link)
        csv_file = StringIO(csv_text)
        reader = csv.DictReader(csv_file)

        # Print the raw CSV text to inspect
        print("CSV Text (first 500 characters):", csv_text[:500])

        # Print the header to check the column names
        print("CSV Headers:", reader.fieldnames)

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
