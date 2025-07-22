import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from src.config import get_config

# Import models and routes
from src.models.video import db
from src.models.youtube_stats import YouTubeStats
from src.routes.search import search_bp
from src.routes.stats import stats_bp, start_background_stats_updater, init_socketio
from src.routes.health import health_bp
from src.routes.podcast import podcast_bp
from src.routes.ai_chat import ai_chat_bp
from src.services.youtube_service import YouTubeService

def setup_websocket_events(socketio):
    """Setup WebSocket events"""
    @socketio.on('connect', namespace='/stats')
    def handle_connect():
        print("Client connected to stats namespace")
    
    @socketio.on('disconnect', namespace='/stats')
    def handle_disconnect():
        print("Client disconnected from stats namespace")
    
    @socketio.on('request_stats_update', namespace='/stats')
    def handle_stats_update_request():
        youtube_service = YouTubeService()
        stats = youtube_service.get_channel_stats()
        socketio.emit('stats_update', stats, namespace='/stats')

def create_app(config_name=None):
    """Application factory pattern for production deployment"""
    
    # Create Flask app
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'production')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Enable CORS for all routes
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize SocketIO with gevent for Railway compatibility
    socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'], async_mode='gevent')
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(podcast_bp, url_prefix='/api/podcast')
    app.register_blueprint(ai_chat_bp, url_prefix='/api/chat')
    
    # Initialize WebSocket events
    setup_websocket_events(socketio)
    init_socketio(socketio)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️  Database setup warning: {e}")
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Serve frontend files or API info"""
        static_folder_path = app.static_folder
        if static_folder_path is None or not os.path.exists(static_folder_path):
            return jsonify({
                'message': '🔥 GREGVERSE Backend is LIVE!',
                'status': 'healthy',
                'mission': 'Honor Greg Isenberg\'s no-gatekeeping philosophy',
                'tribute': 'The ultimate entrepreneur resource',
                'endpoints': {
                    'search': '/api/search/videos',
                    'stats': '/api/stats/youtube',
                    'podcast': '/api/podcast/episodes',
                    'chat': '/api/chat/ask',
                    'health': '/health',
                    'websocket': '/socket.io',
                    'api_docs': '/api'
                },
                'version': '1.0.0',
                'philosophy': 'No gatekeeping - maximum value for entrepreneurs worldwide'
            })

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'message': '🔥 GREGVERSE Backend is LIVE!',
                    'status': 'healthy',
                    'mission': 'Honor Greg Isenberg\'s no-gatekeeping philosophy',
                    'tribute': 'The ultimate entrepreneur resource',
                    'endpoints': {
                        'search': '/api/search/videos',
                        'stats': '/api/stats/youtube',
                        'podcast': '/api/podcast/episodes',
                        'chat': '/api/chat/ask',
                        'health': '/health',
                        'websocket': '/socket.io',
                        'api_docs': '/api'
                    },
                    'version': '1.0.0',
                    'philosophy': 'No gatekeeping - maximum value for entrepreneurs worldwide'
                })
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """API information endpoint"""
        return jsonify({
            'name': '🔥 GREGVERSE API',
            'version': '1.0.0',
            'description': 'The ultimate Greg Isenberg archive and tribute backend',
            'mission': 'Honor Greg\'s no-gatekeeping philosophy with world-class engineering',
            'endpoints': {
                'search': {
                    'videos': 'POST /api/search/videos',
                    'autocomplete': 'GET /api/search/autocomplete',
                    'categories': 'GET /api/search/categories',
                    'trending': 'GET /api/search/trending',
                    'all': 'GET /api/search/all'
                },
                'stats': {
                    'youtube': 'GET /api/stats/youtube',
                    'overview': 'GET /api/stats/overview'
                },
                'podcast': {
                    'episodes': 'GET /api/podcast/episodes',
                    'episode': 'GET /api/podcast/episodes/<id>',
                    'guests': 'GET /api/podcast/guests',
                    'tags': 'GET /api/podcast/tags',
                    'stats': 'GET /api/podcast/stats',
                    'sync': 'POST /api/podcast/sync'
                },
                'startup_ideas': {
                    'list': 'GET /api/podcast/startup-ideas',
                    'detail': 'GET /api/podcast/startup-ideas/<id>'
                },
                'tweets': {
                    'list': 'GET /api/podcast/tweets',
                    'detail': 'GET /api/podcast/tweets/<id>'
                },
                'chat': {
                    'ask': 'POST /api/chat/ask',
                    'index': 'POST /api/chat/index',
                    'stats': 'GET /api/chat/stats'
                },
                'health': {
                    'basic': 'GET /health',
                    'detailed': 'GET /health/detailed'
                },
                'websocket': {
                    'endpoint': '/socket.io',
                    'events': ['connect', 'disconnect', 'stats_update', 'request_stats_update']
                }
            },
            'features': [
                'Sub-500ms search responses',
                'Real-time YouTube stats via WebSocket',
                'AI-powered video categorization',
                'Podcast RSS feed integration',
                'Startup ideas database',
                'AI chat with RAG system',
                'Cross-content search',
                'Comprehensive error handling',
                'Production-grade architecture'
            ],
            'philosophy': 'No gatekeeping - built with love for Greg Isenberg and the entrepreneur community',
            'tribute': 'Honoring someone who has helped over 1 million entrepreneurs worldwide',
            'impact': 'Making entrepreneurial wisdom searchable and accessible to millions'
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Custom 404 handler"""
        return jsonify({
            'error': True,
            'message': 'Endpoint not found',
            'available_endpoints': '/api for API documentation',
            'health_check': '/health',
            'tribute': 'Building the ultimate Greg Isenberg archive'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Custom 500 handler"""
        return jsonify({
            'error': True,
            'message': 'Internal server error',
            'fallback': 'Check /health for system status',
            'retry_after': 30,
            'philosophy': 'No gatekeeping - we\'ll fix this and keep serving entrepreneurs'
        }), 500
    
    # CLI Commands for data management
    @app.cli.command()
    def sync_videos():
        """Sync videos from YouTube API"""
        print("🚀 Starting YouTube video sync...")
        youtube_service = YouTubeService()
        synced_count = youtube_service.sync_videos_to_database()
        print(f"✅ Synced {synced_count} videos successfully!")
    
    @app.cli.command()
    def update_stats():
        """Update YouTube statistics"""
        print("📊 Updating YouTube statistics...")
        youtube_service = YouTubeService()
        stats = youtube_service.get_channel_stats()
        print(f"✅ Updated stats: {stats['subscriber_count']:,} subscribers")
    
    @app.cli.command()
    def sync_podcasts():
        """Sync podcast episodes from RSS feed"""
        from src.services.podcast_service import PodcastService
        print("🎙️ Starting podcast sync...")
        podcast_service = PodcastService()
        result = podcast_service.sync_episodes()
        print(f"✅ Synced {result['new_episodes']} new episodes, updated {result['updated_episodes']} episodes")
    
    @app.cli.command()
    def index_content():
        """Index content for AI chat"""
        from src.services.ai_chat_service import AIChatService
        print("🧠 Starting content indexing for AI chat...")
        ai_service = AIChatService()
        result = ai_service.index_content(force_reindex=True)
        print(f"✅ Indexed {result['indexed_count']} documents")
    
    return app, socketio

# Create app instance
app, socketio = create_app()

if __name__ == '__main__':
    print("🔥 GREGVERSE Backend Starting...")
    print("🎯 Mission: Honor Greg Isenberg's no-gatekeeping philosophy")
    print("🚀 Building the ultimate entrepreneur resource...")
    print("💫 Serving millions of entrepreneurs worldwide...")
    
    # Start background stats updater
    start_background_stats_updater()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app with SocketIO
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True
    )

