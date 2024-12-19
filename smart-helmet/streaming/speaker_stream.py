# speaker.py
import subprocess

def start_speaker(input_url):
    """
    Plays audio from an RTSP stream.
    """
    try:
        cmd = ["ffplay", "-nodisp", "-autoexit", input_url]
        subprocess.Popen(cmd)
        print(f"Speaker playback started: {input_url}")
    except Exception as e:
        print(f"Error starting speaker: {e}")

def stop_speaker():
    """
    Stops the speaker process.
    """
    subprocess.call(["pkill", "ffplay"])
    print("Speaker playback stopped.")
