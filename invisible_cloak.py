import cv2
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)

def create_background(cap, num_frames=30):
    logger.info("Capturing background. Please move out of frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            logger.warning(f"Could not read frame {i+1}/{num_frames}")
        time.sleep(0.1)
    if backgrounds:
        return np.median(backgrounds, axis=0).astype(np.uint8)
    else:
        return None

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
        self.camera_index = camera_index
        self.capture = None
        self.background = None

    def initialize(self):
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                logger.error(f"Could not open camera with index {self.camera_index}")
                return False
            
            logger.info(f"Camera opened successfully. Width: {self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)}, Height: {self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            ret, frame = self.capture.read()
            if not ret:
                logger.error("Could not read a frame from the camera")
                return False
            
            logger.info(f"Successfully read a test frame. Shape: {frame.shape}")
            return True
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            return False

    def capture_background(self):
        if self.capture is None or not self.capture.isOpened():
            logger.error("Camera is not initialized")
            return None
        
        background = create_background(self.capture)
        if background is None:
            logger.error("Could not capture background")
        return background

    def process_frame(self):
        if self.capture is None or not self.capture.isOpened():
            logger.error("Camera is not initialized")
            return None

        ret, frame = self.capture.read()
        if not ret:
            logger.error("Error: Could not read frame.")
            return None

        if self.background is None:
            return frame

        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask = create_mask(frame, lower_blue, upper_blue)
        return apply_cloak_effect(frame, mask, self.background)

    def reset(self):
        self.background = None

    def release(self):
        if self.capture is not None:
            self.capture.release()
        cv2.destroyAllWindows()