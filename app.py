from flask import Flask, render_template, Response
import cv2
from invisible_cloak import InvisibleCloak

app = Flask(__name__)
def initialize_cloak():
    try:
        return InvisibleCloak(camera_index=0)
    except ValueError as e:
        print(f"Failed to initialize InvisibleCloak: {e}")
        raise

try:
    cloak = initialize_cloak()
except ValueError as e:
    print(f"Error: {e}")
    exit(1) 

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        frame = cloak.process_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)