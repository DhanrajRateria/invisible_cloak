import cv2
import numpy as np
import time

def create_background(cap, num_frames=30):
    print("Capturing background. Please move out of frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            print(f"Warning: Could not read frame {i+1}/{num_frames}")
        time.sleep(0.1)
    if backgrounds:
        return np.median(backgrounds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Could not capture any frames for background")

def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)
    return mask

def apply_cloak_effect(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

class InvisibleCloak:
    def __init__(self, camera_index=0):
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            raise ValueError(f"Could not open camera with index {camera_index}")
        
        print(f"Camera opened successfully. Width: {self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)}, Height: {self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        
        try:
            self.background = create_background(self.capture)
        except ValueError as e:
            print(f"Error: {e}")
            self.capture.release()
            raise

    def process_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            print("Error: Could not read frame.")
            time.sleep(1)
            return None
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask = create_mask(frame, lower_blue, upper_blue)
        return apply_cloak_effect(frame, mask, self.background)

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()