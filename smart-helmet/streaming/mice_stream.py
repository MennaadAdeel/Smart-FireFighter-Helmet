# microphone.py
import subprocess

def start_microphone(rtsp_url):
    """
    Starts audio capture and streams using FFmpeg.
    """
    try:
        cmd = [
            "arecord", "-D", "hw:3,0", "-f", "S16_LE", "-r", "44100", 
            "|", "ffmpeg", "-f", "alsa", "-i", "-", 
            "-c:a", "aac", "-f", "rtsp", rtsp_url
        ]
        subprocess.Popen(" ".join(cmd), shell=True)
        print(f"Microphone stream started: {rtsp_url}")
    except Exception as e:
        print(f"Error starting microphone: {e}")

def stop_microphone():
    """
    Stops the microphone process.
    """
    subprocess.call(["pkill", "arecord"])
    print("Microphone stream stopped.")
