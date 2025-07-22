"""
GREGVERSE Backend - Production WSGI Entry Point
The ultimate Greg Isenberg archive and tribute backend
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app, socketio

# For Railway deployment
application = app

if __name__ == "__main__":
    # For local testing of production setup
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

