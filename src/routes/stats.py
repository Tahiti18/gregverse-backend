from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit
from ..services.youtube_service import YouTubeService
from ..models.youtube_stats import YouTubeStats
from ..models.video import Video, db
from datetime import datetime
import threading
import time

stats_bp = Blueprint('stats', __name__)

# WebSocket connection management
active_connections = set()
socketio = None  # Will be initialized in main.py

def init_socketio(app_socketio):
    """Initialize SocketIO instance"""
    global socketio
    socketio = app_socketio

@stats_bp.route('/youtube', methods=['GET'])
def get_youtube_stats():
    """Get current YouTube channel statistics"""
    try:
        youtube_service = YouTubeService()
        stats = youtube_service.get_channel_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"YouTube stats error: {e}")
        # Return cached data as fallback
        cached_stats = YouTubeStats.get_latest_cached()
        return jsonify({
            'success': False,
            'data': cached_stats,
            'error': 'Live stats temporarily unavailable',
            'fallback': True,
            'timestamp': datetime.utcnow().isoformat()
        }), 200  # Still return 200 since we have fallback data

@stats_bp.route('/overview', methods=['GET'])
def get_overview_stats():
    """Get comprehensive overview statistics"""
    try:
        # YouTube stats
        youtube_service = YouTubeService()
        youtube_stats = youtube_service.get_channel_stats()
        
        # Database stats
        total_videos = Video.query.count()
        categories = Video.get_categories()
        latest_video = Video.query.order_by(Video.published_at.desc()).first()
        
        overview = {
            'youtube': youtube_stats,
            'content': {
                'total_videos': total_videos,
                'categories_count': len(categories),
                'latest_video': {
                    'title': latest_video.title if latest_video else None,
                    'published_at': latest_video.published_at.isoformat() if latest_video and latest_video.published_at else None
                }
            },
            'milestones': {
                'subscriber_goal': 1000000,
                'progress_percentage': youtube_stats.get('progress_to_million', 0),
                'subscribers_to_goal': max(0, 1000000 - youtube_stats.get('subscriber_count', 0))
            },
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': overview
        })
        
    except Exception as e:
        print(f"Overview stats error: {e}")
        return jsonify({
            'error': True,
            'message': 'Overview stats temporarily unavailable'
        }), 500

# WebSocket Events
def setup_websocket_events(socketio):
    """Setup WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        active_connections.add(request.sid)
        print(f'Client connected: {request.sid}')
        
        # Send current stats immediately
        try:
            youtube_service = YouTubeService()
            current_stats = youtube_service.get_channel_stats()
            emit('stats_update', {
                'type': 'youtube_stats',
                'data': current_stats,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Error sending initial stats: {e}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        active_connections.discard(request.sid)
        print(f'Client disconnected: {request.sid}')
    
    @socketio.on('request_stats_update')
    def handle_stats_request():
        """Handle manual stats update request"""
        try:
            youtube_service = YouTubeService()
            stats = youtube_service.get_channel_stats()
            emit('stats_update', {
                'type': 'youtube_stats',
                'data': stats,
                'timestamp': datetime.utcnow().isoformat(),
                'requested': True
            })
        except Exception as e:
            emit('stats_error', {
                'error': 'Failed to fetch latest stats',
                'timestamp': datetime.utcnow().isoformat()
            })

def broadcast_stats_update():
    """Broadcast stats update to all connected clients"""
    if not socketio or not active_connections:
        return
    
    try:
        youtube_service = YouTubeService()
        stats = youtube_service.get_channel_stats()
        
        socketio.emit('stats_update', {
            'type': 'youtube_stats',
            'data': stats,
            'timestamp': datetime.utcnow().isoformat(),
            'broadcast': True
        }, broadcast=True)
        
        print(f"Broadcasted stats update to {len(active_connections)} clients")
        
    except Exception as e:
        print(f"Error broadcasting stats: {e}")
        # Send error notification to clients
        socketio.emit('stats_error', {
            'error': 'Stats update failed',
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)

def start_background_stats_updater():
    """Start background thread for periodic stats updates"""
    def stats_updater():
        while True:
            try:
                time.sleep(600)  # 10 minutes
                broadcast_stats_update()
            except Exception as e:
                print(f"Background stats updater error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    # Start background thread
    stats_thread = threading.Thread(target=stats_updater, daemon=True)
    stats_thread.start()
    print("Background stats updater started")

