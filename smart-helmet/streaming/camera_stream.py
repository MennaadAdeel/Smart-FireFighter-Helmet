import os
import subprocess
import time
import sys
from pathlib import Path

class MediaMTXServer:
    def __init__(self, executable_path="./mediamtx", config_path="./mediamtx.yml"):
        self.executable_path = Path(executable_path)
        self.config_path = Path(config_path)
        self.process = None
        
    def validate_paths(self):
        """Validate that the MediaMTX executable and config exist and have proper permissions"""
        if not self.executable_path.exists():
            raise FileNotFoundError(f"MediaMTX executable not found at {self.executable_path}")
            
        if not os.access(self.executable_path, os.X_OK):
            raise PermissionError(f"MediaMTX executable at {self.executable_path} is not executable. Run 'chmod +x {self.executable_path}'")
            
        if self.config_path.exists() and not os.access(self.config_path, os.R_OK):
            raise PermissionError(f"Config file at {self.config_path} is not readable")

    def start(self):
        """Start the MediaMTX server with proper error handling"""
        print("Starting MediaMTX server...")
        
        try:
            self.validate_paths()
            
            # Get the absolute path of the executable
            abs_path = self.executable_path.absolute()
            
            # Change to the directory containing the executable
            os.chdir(abs_path.parent)
            
            self.process = subprocess.Popen(
                [f"./{abs_path.name}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Use text mode for easier output handling
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            # Check if process started successfully
            if self.process.poll() is not None:
                raise RuntimeError("MediaMTX failed to start")
                
            print("MediaMTX server started successfully")
            return True
            
        except Exception as e:
            print(f"Failed to start MediaMTX: {str(e)}")
            # Get detailed error information from stderr if available
            if hasattr(self, 'process') and self.process:
                stderr_output = self.process.stderr.read()
                if stderr_output:
                    print(f"Error output:\n{stderr_output}")
            return False

    def monitor_logs(self):
        """Monitor MediaMTX logs with proper error handling"""
        if not self.process:
            raise RuntimeError("Server not started")
            
        try:
            while self.process.poll() is None:
                stdout_line = self.process.stdout.readline()
                stderr_line = self.process.stderr.readline()
                
                if stdout_line:
                    print(f"[MediaMTX] {stdout_line.strip()}")
                if stderr_line:
                    print(f"[MediaMTX Error] {stderr_line.strip()}")
                    
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"Error monitoring logs: {str(e)}")
            self.stop()

    def stop(self):
        """Properly shutdown the MediaMTX server"""
        if self.process:
            print("Shutting down MediaMTX server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
            except subprocess.TimeoutExpired:
                print("Force killing MediaMTX server...")
                self.process.kill()
            self.process = None

def main():
    server = MediaMTXServer(
        executable_path="mtx/mediamtx",
        config_path="mtx/mediamtx.yml"
    )
    
    if server.start():
        try:
            server.monitor_logs()
        except KeyboardInterrupt:
            print("\nReceived shutdown signal")
        finally:
            server.stop()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
