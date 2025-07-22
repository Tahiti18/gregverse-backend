"""
GREGVERSE Backend - Railway Entry Point
The ultimate Greg Isenberg archive and tribute backend
"""

import os
from src.main import create_app

# Create app instance for Railway
app, socketio = create_app()

if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.environ.get('PORT', 5000))
    
    print("🔥 GREGVERSE Backend Starting...")
    print("🎯 Mission: Honor Greg Isenberg's no-gatekeeping philosophy")
    print("🚀 Building the ultimate entrepreneur resource...")
    print(f"💫 Starting on port {port}...")
    
    # Run with SocketIO for Railway
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

