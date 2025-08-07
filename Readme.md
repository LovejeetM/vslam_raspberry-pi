# Image/Video Depth Scan on Raspberry Pi

Hey, I'm starting this repository to explore image depth analysis using various models. The ultimate goal is to implement Visual SLAM on the robot I previously built. This space will serve as a sandbox for experimentation—where I'll test out different depth estimation models and work on automating the robot's navigation in new environments.

This repo will provide you a way to stream your Raspberry Pi's camera feed directly into a Google Colab or kaggle notebook. This allows you to leverage Colab's powerful GPUs for real-time image processing on a live video stream from your Pi.


### Here is the first image i tested it on (this photo was taken on my phone):

<div align="center">
  <img src="./depth.png" alt="Depth Scan Example" width="100%">
</div>

### How to get video stream from raspberry pi to the google colab or kaggle:

I have added 2 simple methods for streaming video to google colab and you can use either ngrok or cloudflare for streaming to your internet url. Python server + Cloudflare works well and gives around 30~ ms - 45 ms latency on average. But Mediamtx + Cloudflare or Ngrok gives even lower latency by streaming using webRTC and making a secure peer to peer conection. While using Mediamtx the Cloudfared and Ngrok are only required to make initial handshake.

#### Added the code to read the MediaMTX stream in colab/kaggle for processing.

It reads the stream frame by frame and updates the latest frame only, there are few settings that must be done in order
to get `WebRTC/whep` stream frames.

the code to run whep added in:
```bash 
    stream.py
```

#### Instructions to run whep:

First change the default port of your tunnel address in `WebRTC config.yml`:
```bash
    # add this line, it must be port 8889
    - hostname: <<   --your host name--    >>
    service: http://localhost:8889     
```

Then, add these lines to your `mediamtx.yml`:
```bash
webrtcAddress: :8889

webrtcLocalTCPAddress: :8189

webrtcAdditionalHosts: [  --your host name--  ]


webrtcICEServers2:
  - url: stun:stun.l.google.com:19302

# add authentication if needed, but for this you have to add auth header with the initial connection to verify
# so, I am just setting no auth here, check mediamtx official documentation if you need auth.
authInternalUsers:
  - user: any
    pass:
    permissions:
      - action: read
      - action: publish
```

<h3>                </h3>

### Here I am streaming sensor data to the internet and then visualizing it on my laptop:

<h4>           </h4>

https://github.com/user-attachments/assets/7301b8d2-2f2b-4565-8982-16806c876d24

<h3>             </h3>

---

### Stream Sensor data using: [Stream Data](./sensor_data.py)

To check servo movement and control servos from webpage for testing see: [control_servo](./control_servo.py)
and add templates folder to render the joystick page. 

<h3>            </h3>

---

### The code to calibrate the camera using chackerboard image and open-cv can be found in: [claibrate camera](./calibrate_camera/)

The camera calibration is necessary to know the properties of the camera, which will
be further beneficial for the depth analysis.

### The properties we get from calibrating camera:

#### Intrinsic parameters:

*   Focal length

*   Optical center (principal point)

*   Lens distortion coefficients (radial and tangential)

#### Extrinsic parameters:

*   Rotation and translation vectors that relate the camera to the world coordinate system


<h2>            </h2>

---

<h3>            </h3>

### Follow the setup for setting up the stream either by pyhton or mediamtx: [Stream Setup](./stream_setup/)

### Follow link for more info about the mediamtx stream: [MediaMTX](https://github.com/bluenviron/mediamtx)

---
