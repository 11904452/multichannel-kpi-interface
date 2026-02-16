import os
import sys
from pyngrok import ngrok
import subprocess
import time

def main():
    print("Starting Email Campaign Dashboard with Ngrok...")
    
    # Establish ngrok tunnel
    try:
        # Connect to port 8501 (Streamlit's default)
        public_url = ngrok.connect(8501).public_url
        print(f"\n========================================================")
        print(f"   PUBLIC URL: {public_url}")
        print(f"========================================================\n")
    except Exception as e:
        print(f"\n[Warning] Could not create ngrok tunnel: {e}")
        print("Continuing with local launch only...\n")

    # Run Streamlit
    # We use sys.executable to ensure we use the same python environment
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        ngrok.kill()

if __name__ == "__main__":
    main()
