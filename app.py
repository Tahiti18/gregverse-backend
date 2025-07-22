"""
GREGVERSE Backend - Railway Entry Point
The ultimate Greg Isenberg archive and tribute backend
"""

from src.main import create_app

# Create app instance for Railway
app, socketio = create_app()

if __name__ == "__main__":
    # This won't be called in Railway, but useful for testing
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)

