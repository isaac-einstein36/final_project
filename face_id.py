from picamera2 import Picamera2
import time

# Initialize the camera
picam2 = Picamera2()

# Configure the camera
picam2.configure(picam2.create_preview_configuration())

# Start the camera
picam2.start()
time.sleep(2)  # Allow time for auto-exposure and auto-focus to adjust

# Capture an image
image_path = "test_image.jpg"

picam2.capture_file(image_path)
print(f"Image captured and saved to {image_path}")

# Stop the camera
picam2.stop()