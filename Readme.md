# Image/Video Depth Scan on Raspberry Pi

Hey, I'm starting this repository to explore image depth analysis using various models. The ultimate goal is to implement Visual SLAM on the robot I previously built. This space will serve as a sandbox for experimentation—where I'll test out different depth estimation models and work on automating the robot's navigation in new environments.

This repo will provide you a way to stream your Raspberry Pi's camera feed directly into a Google Colab notebook. This allows you to leverage Colab's powerful GPUs for real-time image processing on a live video stream from your Pi.


### Here is the first image i tested it on (this photo was taken on my phone):

<div align="center">
  <img src="./depth.png" alt="Depth Scan Example" width="100%">
</div>

### Added simple steup to get video stream from raspberry pi to the google colab

I have added 2 simple methods for streaming video to google colab, you can use either ngrok or cloudflare for streaming.
Cloudflare works best for me and gives around 30~ ms latency on average. For even lower latency you can use webRTC but i will upload it later.

Follow the setup for setting up simple stream: [simple_stream_colab](./simple_stream_colab/)

---