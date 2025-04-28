##########################################
import time
import pickle
import cv2
import face_recognition
from picamera2 import Picamera2
import threading

# Declare stop_event as a global variable
stop_event = threading.Event()

def start_face_recognition(update_name_callback):
    global stop_event
    stop_event.clear()

    # Initialize 'currentname' to trigger only when a new person is identified
    currentname = "Dr.Metzler"
    encodingsP = "face_id/encodings.pickle"  # Path to your encodings file
    cascade = "face_id/haarcascade_frontalface_default.xml"  # Path to your cascade file

    # Load the known faces and embeddings along with OpenCV's Haar
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open(encodingsP, "rb").read())
    detector = cv2.CascadeClassifier(cascade)

    # Initialize the Raspberry Pi camera using Picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    time.sleep(2.0)  # Allow the camera to warm up

    try:
        # Loop over frames from the video stream
        while not stop_event.is_set():        # Capture the frame from the Raspberry Pi camera
            frame = picam2.capture_array()

            # Convert the frame to grayscale for face detection and RGB for face recognition
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces in the grayscale frame
            rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                                            minNeighbors=5, minSize=(30, 30),
                                            flags=cv2.CASCADE_SCALE_IMAGE)

            # Convert bounding boxes from (x, y, w, h) to (top, right, bottom, left)
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # Compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # Loop over the facial embeddings
            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"  # Default to "Unknown" if no match is found

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)

                    if currentname != name:
                        currentname = name
                        print(currentname)
                        update_name_callback(name)  # Call the update function to update the GUI


                names.append(name)

            # Draw bounding boxes around faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 0, 0), 2)

            # Display the frame to the screen
            cv2.imshow("Facial Recognition", frame)

            # Exit the loop if 'q' is pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
                stop_event.set()
                    # recognition_running = False

    finally:
        print("Cleaning up camera...")
        cv2.destroyAllWindows()
        picam2.stop()
        picam2.close()  # <<< This is crucial to release /dev/video0
        stop_event.set()
        time.sleep(1)

###########################################
# ## CHAT'S ATTEMPT USING KIVY
# import time
# import pickle
# import threading
# import cv2
# import face_recognition
# import numpy as np
# from picamera2 import Picamera2

# from kivy.app import App
# from kivy.uix.image import Image
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.clock import Clock
# from kivy.graphics.texture import Texture

# class FaceRecognitionApp(App):
#     def build(self):
#         self.encodingsP = "face_id/encodings.pickle"
#         self.cascade = "face_id/haarcascade_frontalface_default.xml"
#         self.stop_event = threading.Event()
#         self.frame_lock = threading.Lock()
#         self.current_frame = None
#         self.recognition_thread = None

#         layout = BoxLayout(orientation='vertical')
#         self.img_widget = Image()
#         self.button = Button(text="Start Recognition")
#         self.button.bind(on_press=self.toggle_recognition)

#         layout.add_widget(self.img_widget)
#         layout.add_widget(self.button)
#         return layout

#     def toggle_recognition(self, instance):
#         if self.recognition_thread and self.recognition_thread.is_alive():
#             self.stop_event.set()
#             self.button.text = "Start Recognition"
#         else:
#             self.stop_event.clear()
#             self.recognition_thread = threading.Thread(target=self.face_recognition_loop)
#             self.recognition_thread.start()
#             Clock.schedule_interval(self.update_kivy_image, 1.0 / 30.0)
#             self.button.text = "Stop Recognition"

#     def update_kivy_image(self, dt):
#         if self.stop_event.is_set():
#             Clock.unschedule(self.update_kivy_image)
#             return
#         with self.frame_lock:
#             if self.current_frame is not None:
#                 buf = cv2.flip(self.current_frame, 0).tobytes()
                
#                 texture = Texture.create(size=(self.current_frame.shape[1], self.current_frame.shape[0]), colorfmt='rgb')
#                 texture.blit_buffer(self.current_frame.flatten(), colorfmt='rgb', bufferfmt='ubyte')

#                 # texture = Texture.create(size=(self.current_frame.shape[1], self.current_frame.shape[0]), colorfmt='bgr')
#                 # texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
#                 self.img_widget.texture = texture

#     def face_recognition_loop(self):
#         data = pickle.loads(open(self.encodingsP, "rb").read())
#         print(f"[DEBUG] Known faces: {set(data['names'])}")

#         detector = cv2.CascadeClassifier(self.cascade)
#         currentname = "unknown"

#         picam2 = Picamera2()
#         picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
#         picam2.start()
#         time.sleep(2.0)

#         try:
#             while not self.stop_event.is_set():

#                 frame = picam2.capture_array()
#                 frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 frame = cv2.rotate(frame, cv2.ROTATE_180)
                
#                 gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#                 rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#                 rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
#                                                   flags=cv2.CASCADE_SCALE_IMAGE)
#                 boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
#                 encodings = face_recognition.face_encodings(rgb, boxes)
#                 names = []

#                 for encoding in encodings:
#                     matches = face_recognition.compare_faces(data["encodings"], encoding)
#                     name = "Unknown"
#                     if True in matches:
#                         matchedIdxs = [i for (i, b) in enumerate(matches) if b]
#                         counts = {}
#                         for i in matchedIdxs:
#                             name = data["names"][i]
#                             counts[name] = counts.get(name, 0) + 1
#                         name = max(counts, key=counts.get)

#                     if currentname != name:
#                         currentname = name
#                         print(currentname)

#                     names.append(name)

#                 for ((top, right, bottom, left), name) in zip(boxes, names):
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                     y = top - 15 if top - 15 > 15 else top + 15
#                     cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (255, 0, 0), 2)

#                 with self.frame_lock:
#                     self.current_frame = frame.copy()
#         finally:
#             print("Cleaning up camera...")
#             picam2.stop()
#             picam2.close()
#             self.stop_event.set()

# if __name__ == "__main__":
#     FaceRecognitionApp().run()

