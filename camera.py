import cv2
import time


class Camera:
    def __init__(self, camera_index=0):
        # Force DirectShow (IMPORTANT for Windows)
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Warm-up delay (CRITICAL)
        time.sleep(1)

    def get_frame(self):
        if not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        return frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
