from flask import Flask, render_template, Response
import cv2
from invisible_cloak import InvisibleCloak

app = Flask(__name__)
cloak = InvisibleCloak()

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