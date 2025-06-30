#!/usr/bin/env python3
"""Simple script to run the Personal Finance Assistant."""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app."""
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("Error: app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found. You'll need to set up your Gemini API key.")
        print("Copy .env.example to .env and add your API key.")
    
    # Run the Streamlit app
    try:
        print("Starting Personal Finance Assistant...")
        print("The app will open in your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the app")
        
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.headless', 'true',
            '--server.port', '8501'
        ])
    except KeyboardInterrupt:
        print("\nApp stopped.")
    except Exception as e:
        print(f"Error running app: {e}")
        print("Try running manually: python3 -m streamlit run app.py")

if __name__ == "__main__":
    main() 