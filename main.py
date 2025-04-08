# Libraries
import urllib.request
import csv
from io import StringIO
from datetime import datetime

# Files
import read_database


allBookings = read_database.read_clean_csv()
for slot in allBookings:
        print(slot.start_time)
        