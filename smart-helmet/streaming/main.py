import os
import subprocess
import time

# Configuration for MediaMTX
MEDIA_MTX_PATH = "/home/Helmet/myenv/stream/mediamtx"
CONFIG_FILE = "/home/Helmet/myenv/stream/mediamtx.yml"
STREAM_PATH = "cam1"
HOST = "192.168.1.11"
WEBRTC_PORT = 8889

# Function to start MediaMTX server
def start_mediamtx():
    print("Starting MediaMTX...")
    process = subprocess.Popen(
        [MEDIA_MTX_PATH, "-conf", CONFIG_FILE],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

# Function to generate WebRTC stream URL
def generate_webrtc_url(host, port, path):
    return f"http://{host}:{port}/{path}"

# Function to monitor MediaMTX logs (optional)
def monitor_mediamtx_logs(process):
    try:
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(output.decode().strip())
    except KeyboardInterrupt:
        print("Shutting down MediaMTX...")
        process.terminate()

# Main script
if __name__ == "__main__":
    # Step 1: Start MediaMTX
    mediamtx_process = start_mediamtx()

    # Allow time for MediaMTX to initialize
    time.sleep(5)

    # Step 2: Generate WebRTC URL
    webrtc_url = generate_webrtc_url(HOST, WEBRTC_PORT, STREAM_PATH)
    print(f"WebRTC stream available at: {webrtc_url}")

    # Step 3: Monitor logs or keep the server running
    try:
        monitor_mediamtx_logs(mediamtx_process)
    except Exception as e:
        print(f"Error: {e}")
        mediamtx_process.terminate()
