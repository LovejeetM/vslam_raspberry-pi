# this code stream the WebRTC stream via whem extension frame by frame from mediamtx. Now we can get frames from the
# lightweight .h264 mediamtx stream and load frames for processing in colab/kaggle

### this code is to be used in kaggle/colab

try:
    import aiortc
    import aiohttp
except ImportError:
    print("Installing necessary libraries: aiortc, aiohttp")
    %pip install aiortc aiohttp --quiet


import asyncio
import cv2
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.mediastreams import MediaStreamError
from IPython.display import display, HTML
import aiohttp
import logging
import base64


WHEP_URL = "https://<<--Your url-->>/video/whep"
# The rate at which we update the image in Colab. 10-15 FPS
DISPLAY_FPS = 15

# Suppress verbose logging
logging.basicConfig(level=logging.WARNING)
for logger_name in ["aiortc", "aiohttp"]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


class WebRTCStreamViewer:
    def __init__(self, whep_url):
        self.whep_url = whep_url
        self.pc = RTCPeerConnection()
        self.done = asyncio.Event()
        self.lock = asyncio.Lock()
        self.latest_frame = None

        # WebRTC event handlers
        @self.pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                print("Video track received.")
                asyncio.create_task(self._frame_receiver_task(track))
        
        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state is {self.pc.connectionState}")
            if self.pc.connectionState in ["failed", "closed", "disconnected"]:
                self.done.set()

    async def _frame_receiver_task(self, track):
        """Receives frames from WebRTC and updates the shared `latest_frame`."""
        while not self.done.is_set():
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
                async with self.lock:
                    self.latest_frame = img
            except MediaStreamError:
                print("Video stream ended.")
                return
            except Exception as e:
                print(f"Error: {e}")
                return

    async def _display_loop_task(self):
        """Displays the latest frame at a fixed rate using HTML data URLs."""
        display_handle = display(HTML('<img>'), display_id=True)
        
        while not self.done.is_set():
            frame_to_display = None
            async with self.lock:
                if self.latest_frame is not None:
                    frame_to_display = self.latest_frame.copy()
            
            if frame_to_display is not None:
                
                processed_frame = frame_to_display
                

                # encodeing to  jpeg
                _, buffer = cv2.imencode('.jpg', processed_frame)
                b64_str = base64.b64encode(buffer).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{b64_str}"
                
                display_handle.update(HTML(f'<img src="{data_url}" style="width: 80%;" />'))

            await asyncio.sleep(1 / DISPLAY_FPS)

    async def run(self):
        """Connects to WebRTC"""
        self.pc.addTransceiver("video", direction="recvonly")
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        
        try:
            # Starts loop as a background task
            display_task = asyncio.create_task(self._display_loop_task())

            async with aiohttp.ClientSession() as session:
                print(f"Connecting to {self.whep_url}...")
                async with session.post(
                    self.whep_url, data=self.pc.localDescription.sdp,
                    headers={"Content-Type": "application/sdp"}, timeout=15
                ) as resp:
                    if resp.status != 201:
                        print(f"error: {resp.status} {await resp.text()}")
                        self.done.set()
                    else:
                        print("WHEP connection accepted.")
                        answer_sdp = await resp.text()
                        await self.pc.setRemoteDescription(RTCSessionDescription(sdp=answer_sdp, type="answer"))
            
            await self.done.wait()
            
        except Exception as e:
            print(f"error: {e}")
        finally:
            if 'display_task' in locals():
                display_task.cancel()
            if self.pc.connectionState != "closed":
                await self.pc.close()

async def main():
    viewer = WebRTCStreamViewer(WHEP_URL)
    await viewer.run()

try:
    await main()
except Exception as e:
    print(f"An error occurred during execution: {e}")