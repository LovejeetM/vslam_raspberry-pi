# Raspberry Pi to Colab Video Streaming

The Python script to run the server on the Pi is `server_script.py`, and the code to view the stream in Colab is in `colab_setup.py`.

We will cover two methods to create a secure tunnel from your Pi to the internet:
1.  **ngrok**
2.  **Cloudflare Tunnel**

## Prerequisites

- A Raspberry Pi (I used it on Raspberry Pi Zero 2W) with Raspberry Pi OS Lite.
- A camera module connected and enabled on the Pi.
- The Pi is connected to the internet.
- You are able to connect to your Pi via SSH from your main computer.

## Initial Server Setup (Common for Both Methods)

Before choosing a tunneling method, you need to set up the video server on your Raspberry Pi.

1.  **Connect to your Pi via SSH.**

2.  **Install Dependencies:**
    Update your package list and install the required Python libraries for the camera and the web server.
    ```bash
    sudo apt update
    sudo apt install -y python-picamera2 python-flask

    #use python3 if python does not work
    ```

3.  **Place the Script:**
    Make sure the `server_script.py` file is on your Raspberry Pi (e.g., in your home directory). This script will start a local web server on port 5000 that streams the camera feed.

---

## Method 1: Using ngrok

This method is excellent for getting started quickly without much configuration.

#### Step 1: Set up ngrok on the Pi

1.  Sign up on ngrok and there will be an option of raspberry pi.
    
    Click that and choose your download option and then extract it in raspberry pi using:
    ```bash
    sudo tar -xvzf ~/Downloads/ngrok-v3-stable-linux-arm64.tgz -C /usr/local/bin
    ```

2.  Add your authtoken from the [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
    ```bash
    ngrok config add-authtoken "2w**********  -- Your token --"
    ```

#### Step 2: Start the Server and Tunnel

You will need two separate SSH windows connected to your Pi for this.

-   **In Terminal 1**, start the video server:
    ```bash
    python3 server_script.py
    ```

-   **In Terminal 2**, start the ngrok tunnel to expose port 5000:
    ```bash
    ./ngrok http 5000
    ```

3.  `ngrok` will display a public URL in the terminal (e.g., `https://<random-string>.ngrok-free.app`). **Copy this URL.**

#### Step 3: View the Stream in Colab

1.  Open Google Colab on your main computer.
2.  Use the code provided in `colab_setup.py`.
3.  Find the line `Stream_URL = "..."` and paste the URL you copied from ngrok.
4.  Run the cell. The live video feed from your Pi should appear.

    You can also see your stream on "https://---your Link---.app/video"

---

---

## Method 2: Using Cloudflare Tunnel


#### Step 1: Install and Configure Cloudflare on the Pi

1.  **Install the `cloudflared` client:**
    ```bash
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm
    chmod +x cloudflared-linux-arm
    sudo mv cloudflared-linux-arm /usr/local/bin/cloudflared
    ```
2.  **Login to your Cloudflare account:**
    ```bash
    cloudflared tunnel login
    ```
    This will provide a link. Open it on your main computer, log in, and authorize the tunnel for the domain you wish to use (e.g., `your-domain.com`).

3.  **Create a Tunnel:** Choose a name for your tunnel (e.g., `rpi-stream`).
    ```bash
    cloudflared tunnel create rpi-stream
    ```
    This will generate a credentials file with a UUID in `~/.cloudflared/`.

#### Step 2: Configure the Tunnel for System-Wide Use

This is the standard and most reliable way to run the tunnel.

1.  **Create a DNS Route:** Link a subdomain to your tunnel. This will be your permanent public address.
    ```bash
    # Example: cloudflared tunnel route dns <TUNNEL_NAME> <public.hostname.com>
    cloudflared tunnel route dns rpi-stream rpi-camera.your-domain.com
    ```
2.  **Move Configuration Files:** The system service expects its files in `/etc/cloudflared/`.
    ```bash
    # Create the directory
    sudo mkdir -p /etc/cloudflared/

    # Move the credentials file (replace the UUID with your actual one)
    sudo mv ~/.cloudflared/<YOUR-TUNNEL-UUID>.json /etc/cloudflared/

    # Copy the provided config.yml.template to the new location
    # Note: You will need to edit this file next.
    sudo cp config.yml.template /etc/cloudflared/config.yml
    ```
3.  **Edit the Configuration File:**
    Open the file with `sudo nano /etc/cloudflared/config.yml`. Edit the placeholder values to match your tunnel name, UUID file, and public hostname. The `credentials-file` path must point to its new location inside `/etc/cloudflared/`.

#### Step 3: Run as a Service

1.  **Install and Start the Service:**
    ```bash
    sudo cloudflared service install
    sudo systemctl start cloudflared
    ```
    ```bash
    # you can use this commmand to stop the cloudeflared service
    sudo systemctl stop cloudflared
    ```
2.  You can check its status anytime with `sudo systemctl status cloudflared`.
    ```bash
    sudo systemctl status cloudflared
    ```

#### Step 4: View the Stream in Colab

1.  On your Pi, start the video server: `python server_script.py`.
2.  In your Colab notebook (`colab_setup.py`), update the URL to your permanent Cloudflare address.
    `Stream_URL = "https://rpi-camera.your-domain.com"`
3.  Run the cell. Your stream should now be live on its permanent address.

---