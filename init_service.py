from flask import Flask, jsonify
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Database initialization service"})

@app.route('/init_db')
def init_db():
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import database
        from src.models.video import db
        
        # Create a minimal Flask app
        test_app = Flask("test_app")
        test_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data/gregverse.db')
        test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(test_app)
        
        with test_app.app_context():
            db.create_all()
        
        return jsonify({
            'success': True,
            'message': 'Database tables created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/sync_videos')
def sync_videos():
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import YouTube service
        from src.services.youtube_service import YouTubeService
        
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
