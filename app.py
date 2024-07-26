from flask import Flask, render_template, Response, jsonify, request
from invisible_cloak import InvisibleCloak
import cv2
import numpy as np
import logging

app = Flask(__name__)
cloak = InvisibleCloak()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        try:
            frame = cloak.process_frame()
            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera not available", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logger.error(f"Error in gen(): {str(e)}")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/initialize_camera', methods=['POST'])
def initialize_camera():
    try:
        success = cloak.initialize()
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Error initializing camera: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/capture_background', methods=['POST'])
def capture_background():
    try:
        cloak.background = cloak.capture_background()
        return jsonify({"success": cloak.background is not None})
    except Exception as e:
        logger.error(f"Error capturing background: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/reset', methods=['POST'])
def reset():
    try:
        cloak.reset()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error resetting: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)