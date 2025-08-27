#!/usr/bin/env python3
"""
Setup script for SB Notes - Personal Note Management System
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")
    if not env_path.exists():
        print("Creating .env file...")
        print("Please enter your Anthropic API key:")
        api_key = input("ANTHROPIC_API_KEY= ").strip()
        if not api_key:
            print("❌ API key is required!")
            return False
        
        with open(env_path, "w") as f:
            f.write(f"ANTHROPIC_API_KEY={api_key}\n")
        print("✅ .env file created!")
    else:
        print("✅ .env file already exists")
    return True

def main():
    print("🚀 Setting up SB Notes - Personal Note Management System...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Make main script executable
    try:
        import os
        os.chmod("sbnotes.py", 0o755)
        print("✅ Made sbnotes.py executable")
    except:
        pass
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nTo run the application:")
    print("python sbnotes.py")
    print("\nOr make it executable and run:")
    print("chmod +x sbnotes.py")
    print("./sbnotes.py")

if __name__ == "__main__":
    main()
