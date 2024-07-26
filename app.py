from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
from invisible_cloak import InvisibleCloak

app = Flask(__name__)
cloak = InvisibleCloak()

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        frame = cloak.process_frame()
        if frame is None:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "Camera not available", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/initialize_camera', methods=['POST'])
def initialize_camera():
    success = cloak.initialize()
    return jsonify({"success": success})

@app.route('/capture_background', methods=['POST'])
def capture_background():
    cloak.background = cloak.capture_background()
    return jsonify({"success": cloak.background is not None})

@app.route('/reset', methods=['POST'])
def reset():
    cloak.background = None
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)