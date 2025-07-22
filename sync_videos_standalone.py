import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def sync_videos():
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import services
        from src.services.youtube_service import YouTubeService
        
        # Create a minimal app context
        app.config['YOUTUBE_API_KEY'] = os.environ.get('YOUTUBE_API_KEY')
        app.config['YOUTUBE_CHANNEL_ID'] = os.environ.get('YOUTUBE_CHANNEL_ID')
        
        # Sync videos
        youtube_service = YouTubeService()
        synced_count = youtube_service.sync_videos_to_database()
        
        return jsonify({
            'success': True,
            'message': f'Synced {synced_count} videos successfully!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
