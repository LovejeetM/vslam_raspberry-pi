# You can Run this in Google-Colab to connect to the video strem after creating server and ngrok tunnel 

from IPython.display import Image, display


NGROK_URL = "https://<Your ADDRESS>.ngrok-free.app"
# ----------------------------------------------------

video_url = f"{NGROK_URL}/video_feed"


print(f"Connecting to: {video_url}")


display(Image(url=video_url, width=640))