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
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            st.error("Could not open camera")
            return False
        return True

    def capture_background(self):
        if self.camera is None:
            if not self.initialize_camera():
                return None
        
        backgrounds = []
        for i in range(30):
            ret, frame = self.camera.read()
            if ret:
                backgrounds.append(frame)
            time.sleep(15/30)
        
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

        if st.session_state.stage == 'init':
            step.info("Step 1: Move out of the camera frame")
            if capture_button.button("I'm out of the frame"):
                st.session_state.stage = 'capture'

        if st.session_state.stage == 'capture':
            step.info("Step 2: Capturing background")
            with st.spinner("Capturing background..."):
                cloak.background = cloak.capture_background()
            if cloak.background is not None:
                st.success("Background captured successfully!")
                st.session_state.stage = 'ready'
            else:
                st.error("Failed to capture background. Please try again.")
                st.session_state.stage = 'init'

        if st.session_state.stage == 'ready':
            step.info("Step 3: Put on a blue cloth and stand in front of the camera")
            if capture_button.button("Reset"):
                st.session_state.stage = 'init'
                cloak.background = None

    with col1:
        video_placeholder = st.empty()

    while True:
        frame = cloak.get_frame()
        if frame is not None:
            if st.session_state.stage == 'ready':
                processed_frame = cloak.process_frame(frame)
            else:
                processed_frame = frame
            video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)
        else:
            break

    cloak.release()

if __name__ == "__main__":
    main()