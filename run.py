#!/usr/bin/env python3
"""
Zambian Farmer Chatbot - Startup Script
Run this file to start the chatbot application
"""

import os
import sys
from app import app

def main():
    """Main function to start the Flask application"""
    print("🌱 Starting Zambian Farmer Chatbot...")
    print("=" * 50)
    
    # Check if required directories exist
    if not os.path.exists('templates'):
        print("❌ Error: templates directory not found!")
        sys.exit(1)
    
    if not os.path.exists('static'):
        print("❌ Error: static directory not found!")
        sys.exit(1)
    
    print("✅ All required files found!")
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:8000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the Flask application
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 