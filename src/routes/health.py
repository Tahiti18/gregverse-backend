from flask import Blueprint, jsonify
from ..models.video import db, Video
from ..models.youtube_stats import YouTubeStats
from ..services.youtube_service import YouTubeService
from datetime import datetime
import os
import sys

health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'message': '🔥 GREGVERSE Backend is LIVE!'
    }
    
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = 'disconnected'
        health_status['database_error'] = str(e)
        health_status['status'] = 'degraded'
    
    # Check YouTube API
    try:
        youtube_service = YouTubeService()
        if youtube_service.api_key:
            # Quick API test
            stats = youtube_service.get_channel_stats()
            if stats.get('is_live', False):
                health_status['youtube_api'] = 'active'
            else:
                health_status['youtube_api'] = 'degraded'
                health_status['youtube_note'] = 'Using cached data'
        else:
            health_status['youtube_api'] = 'no_api_key'
            health_status['youtube_note'] = 'API key not configured'
    except Exception as e:
        health_status['youtube_api'] = 'error'
        health_status['youtube_error'] = str(e)
        health_status['status'] = 'degraded'
    
    # Check Redis (if configured)
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            health_status['redis'] = 'connected'
        except Exception as e:
            health_status['redis'] = 'disconnected'
            health_status['redis_error'] = str(e)
    else:
        health_status['redis'] = 'not_configured'
    
    # Overall status determination
    if health_status['database'] == 'disconnected':
        health_status['status'] = 'unhealthy'
        status_code = 503
    elif health_status['status'] == 'degraded':
        status_code = 200  # Still functional
    else:
        status_code = 200
    
    return jsonify(health_status), status_code

@health_bp.route('/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system information"""
    try:
        detailed_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'python_version': sys.version,
                'flask_env': os.getenv('FLASK_ENV', 'production'),
                'debug_mode': os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
            },
            'database': {
                'total_videos': Video.query.count(),
                'categories': len(Video.get_categories()),
                'latest_video': None,
                'latest_stats_update': None
            },
            'api_status': {
                'search_endpoint': 'active',
                'stats_endpoint': 'active',
                'websocket': 'active'
            }
        }
        
        # Get latest video info
        latest_video = Video.query.order_by(Video.published_at.desc()).first()
        if latest_video:
            detailed_info['database']['latest_video'] = {
                'title': latest_video.title,
                'published_at': latest_video.published_at.isoformat() if latest_video.published_at else None
            }
        
        # Get latest stats update
        latest_stats = YouTubeStats.get_latest()
        if latest_stats:
            detailed_info['database']['latest_stats_update'] = latest_stats.updated_at.isoformat()
        
        return jsonify(detailed_info)
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': 'Detailed health check failed',
            'error_details': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

