import streamlit as st
import cv2
import numpy as np
import time
from invisible_cloak import create_mask, apply_cloak_effect

class StreamlitInvisibleCloak:
    def __init__(self):
        self.camera = None
        self.background = None

    def initialize_camera(self):
        index = 0
        while index < 10:
            self.camera = cv2.VideoCapture(index)
            if self.camera.isOpened():
                st.success(f"Camera {index} opened successfully.")
                return True
            else:
                self.camera.release()
            index += 1
        
        st.error("Could not open any camera.")
        return False

    def capture_background(self):
        if self.camera is None:
            if not self.initialize_camera():
                return None
        
        backgrounds = []
        for i in range(30):
            ret, frame = self.camera.read()
            if ret:
                backgrounds.append(frame)
            time.sleep(0.5)  # Reduced sleep time to 0.5 seconds
        
        if backgrounds:
            return np.median(backgrounds, axis=0).astype(np.uint8)
        else:
            st.error("Could not capture background")
            return None

    def process_frame(self, frame):
        if self.background is None:
            return frame
        
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask = create_mask(frame, lower_blue, upper_blue)
        return apply_cloak_effect(frame, mask, self.background)

    def get_frame(self):
        if self.camera is None:
            if not self.initialize_camera():
                return None
        
        ret, frame = self.camera.read()
        if not ret:
            st.error("Could not read frame from camera")
            return None
        
        return frame

    def release(self):
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()

def main():
    st.set_page_config(page_title="Invisible Cloak", page_icon="🧙‍♂️", layout="wide")
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.title("🧙‍♂️ Harry Potter's Invisible Cloak")
    st.write("Definitely not a child-action movie. Sorry :)")

    cloak = StreamlitInvisibleCloak()

    col1, col2 = st.columns([2, 1])

    with col2:
        st.subheader("Controls")
        step = st.empty()
        capture_button = st.empty()

        if 'stage' not in st.session_state:
            st.session_state.stage = 'init'
        
        if 'camera_initialized' not in st.session_state:
            st.session_state.camera_initialized = False

        if st.session_state.stage == 'init':
            step.info("Step 1: Move out of the camera frame")
            if capture_button.button("I'm out of the frame"):
                st.session_state.stage = 'capture'

        if st.session_state.stage == 'capture':
            step.info("Step 2: Capturing background")
            if not st.session_state.camera_initialized:
                st.session_state.camera_initialized = cloak.initialize_camera()
            
            if st.session_state.camera_initialized:
                with st.spinner("Capturing background..."):
                    cloak.background = cloak.capture_background()
                if cloak.background is not None:
                    st.success("Background captured successfully!")
                    st.session_state.stage = 'ready'
                else:
                    st.error("Failed to capture background. Please try again.")
                    st.session_state.stage = 'init'
            else:
                st.error("Failed to initialize camera. Please check your camera and try again.")
                st.session_state.stage = 'init'

        if st.session_state.stage == 'ready':
            step.info("Step 3: Put on a blue cloth and stand in front of the camera")
            if capture_button.button("Reset"):
                st.session_state.stage = 'init'
                st.session_state.camera_initialized = False
                cloak.background = None

    with col1:
        video_placeholder = st.empty()

    # Display video stream
    while True:
        frame = cloak.get_frame()
        if frame is not None:
            if st.session_state.stage == 'ready':
                processed_frame = cloak.process_frame(frame)
            else:
                processed_frame = frame
            video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)
        else:
            st.warning("Lost connection to camera. Trying to reconnect...")
            cloak.release()
            st.session_state.camera_initialized = False
            if cloak.initialize_camera():
                st.session_state.stage = 'capture'
            else:
                st.error("Could not reconnect to camera. Please check your camera and try again.")
                break

    cloak.release()

if __name__ == "__main__":
    main()