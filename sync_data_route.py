from flask import Flask, jsonify
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.youtube_service import YouTubeService
from main import app

@app.route('/admin/sync_videos', methods=['GET'])
def sync_videos_route():
    """Sync videos from YouTube API"""
    try:
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
    # This won't be run when imported
    pass
