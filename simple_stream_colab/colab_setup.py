# You can Run this in Google-Colab to connect to the video strem after creating server and ngrok tunnel 

from IPython.display import Image, display


Stream_URL = "https://<Your Tunnel ADDRESS>"
# ----------------------------------------------------

video_url = f"{Stream_URL}/video"


print(f"Connecting to: {video_url}")


display(Image(url=video_url, width=640))