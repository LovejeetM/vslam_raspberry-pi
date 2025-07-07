# You can run this script inside the raspberry pi to create a server using flask which streams video
# to the local port 5000

# after running this server run "ngrok http 5000"  in another terminal to expose port 5000     

from flask import Flask, Response
from picamera2 import Picamera2
# import libcamera     # If your camera is upside-down
import io

app = Flask(__name__)

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))

# for upside-down camera use this instead: 
# picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}, transform= libcamera.Transform(hflip = True, vflip = True)))
picam2.start()

def generate_frames():
    while True:
        stream = io.BytesIO()
        picam2.capture_file(stream, format='jpeg')
        
        frame = stream.getvalue()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video_feed():
    """The route that will serve our video stream."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

