#!/usr/bin/env python3
"""
SB Notes Web Launcher
Simple script to launch the Streamlit web interface.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 Launching SB Notes Web Interface...")
    print("=" * 50)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your Anthropic API key:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        print("\nOr run: python3 setup.py")
        return
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.32.0"])
    
    # Launch Streamlit
    print("🌐 Starting web server...")
    print("📱 The web interface will open in your browser at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "sbnotes_web.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Web server stopped. Goodbye!")

if __name__ == "__main__":
    main()
