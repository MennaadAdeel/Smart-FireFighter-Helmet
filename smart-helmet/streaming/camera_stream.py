# camera.py
import subprocess


def start_camera(rtsp_url):
    """
    Starts the camera stream using FFmpeg.
    """
    try:
        cmd = [
            "rpicam-vid", "-t", "0", "--camera", "0", "--nopreview", 
            "--codec", "yuv420", "--width", "1280", "--height", "720", 
            "--inline", "--listen", "-o", "-",
            "|", "ffmpeg", "-f", "rawvideo", "-pix_fmt", "yuv420p", 
            "-s:v", "1280x720", "-i", "/dev/stdin", 
            "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", 
            "-f", "rtsp", rtsp_url
        ]
        subprocess.Popen(" ".join(cmd), shell=True)
        print(f"Camera stream started: {rtsp_url}")
    except Exception as e:
        print(f"Error starting camera: {e}")

def stop_camera():
    """
    Stops the camera process.
    """
    subprocess.call(["pkill", "rpicam-vid"])
    print("Camera stream stopped.")

