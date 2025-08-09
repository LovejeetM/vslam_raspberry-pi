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

### The code to calibrate the camera using chackerboard images can be found in: [claibrate camera.](./calibrate_camera/)

The camera calibration is necessary to know the properties of the camera, which will
be further beneficial for the depth analysis.

### The properties we get from calibrating camera:

#### Intrinsic parameters:

*   Focal length

*   Optical center (principal point)

*   Lens distortion coefficients (radial and tangential)

#### Extrinsic parameters:

*   Rotation and translation vectors that relate the camera to the world coordinate system


<h3>            </h3>

---

<h3>            </h3>

### Follow the setup for setting up the stream either by python or mediamtx: [Stream Setup](./stream_setup/)

### Follow link for more info about the mediamtx stream: [MediaMTX](https://github.com/bluenviron/mediamtx)

---

<h3>        </h3>

<h3>        </h3>

## Depth Estimation Models I tested on my Live Stream Setup

My primary focus was on balancing speed, quality, and suitability for live depth estimation within my specific hardware and processing environment. Models were sourced and downloaded from the Hugging Face `transformers` library.
The code to the corresponding models can be found in [Depth Live](./Depth_live.ipynb), [Depth analysis](./Depth_analysis.ipynb).

---

### **Model Performance Findings**

---

### **`vinvino02/glpn-kitti`**

*   **Speed:** Exceptionally high speed.
*   **Quality:** Lower depth quality, with noticeable blurriness and inaccurate, "off" edges.
*   **Suitability:** While very fast, its significant quality compromises make it less ideal for applications requiring precise depth or clean object boundaries.

---

### **`vinvino02/glpn-nyu`**

*   **Speed:** Retains the high speed characteristic of the `glpn` family.
*   **Quality:** Good overall depth quality, a significant improvement over the Kitti variant. However, edges can still appear slightly off or less defined occasionally.
*   **Suitability:** A strong contender for live applications due to its speed, offering a better quality than `glpn-kitti`.

---

### **`apple/DepthPro-hf`**

*   **Speed:** Slow processing.
*   **Quality:** Delivers incredible, unparalleled depth quality – the best observed in terms of detail and accuracy.
*   **Suitability:** Due to its prohibitive processing time, this model is currently unfeasible for real-time, live depth estimation on this setup. It's best suited for more powerful GPU's or applications where quality is paramount and speed is not a constraint.

---

### **`Intel/dpt-large`**

*   **Speed:** Good speed, noticeably slower than `depth-anything-small-hf` but generally faster than `Depth-Pro-hf`.
*   **Quality:** Provides good overall depth quality.
*   **Size:** A larger model, which contributes to its slightly slower performance compared to smaller, optimized models.
*   **Suitability:** A viable option if quality is prioritized and medium speed is needed, offering a good balance for many applications that aren't strictly real-time.

---

### **`LiheYoung/depth-anything-large-hf`**

*   **Speed:** Similar to `Intel/dpt-large`, but significantly faster than `apple/depth-pro`. It sits in a moderate speed tier.
*   **Quality:** Great depth quality, striking a good balance between detail and performance.
*   **Suitability:** A solid choice for scenarios where good quality is essential and some processing latency is acceptable, acting as a middle ground in terms of speed and quality.

---

### **`LiheYoung/depth-anything-small-hf`**

*   **Speed:** Fast processing.
*   **Quality:** Surprisingly accurate and detailed depth output for its compact size and high speed.
*   **Size:** A remarkably small model.
*   **Suitability:** **Currently the best model for live depth estimation** on my specific Raspberry Pi to Google Colab streaming setup. Its combination of high speed, excellent accuracy, and small model size makes it ideal for real-time applications where resource efficiency is key.

---

For optimal real-time performance on my **Raspberry Pi to Google Colab/ Kaggle streaming setup**, **`LiheYoung/depth-anything-small-hf`** stands out as the most suitable model, offering an excellent balance of speed and surprisingly accurate depth output.

---

### Hugging Face Model Links

Find more details and download these models directly from Hugging Face:

*   [`vinvino02/glpn-kitti`](https://huggingface.co/vinvino02/glpn-kitti)
*   [`vinvino02/glpn-nyu`](https://huggingface.co/vinvino02/glpn-nyu)
*   [`Intel/dpt-large`](https://huggingface.co/Intel/dpt-large)
*   [`apple/DepthPro-hf`](https://huggingface.co/apple/DepthPro-hf)
*   [`LiheYoung/depth-anything-large-hf`](https://huggingface.co/LiheYoung/depth-anything-large-hf)
*   [`LiheYoung/depth-anything-small-hf`](https://huggingface.co/LiheYoung/depth-anything-small-hf)

---
