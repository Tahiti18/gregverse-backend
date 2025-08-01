import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import feedparser
import requests
from datetime import datetime

app = Flask(__name__)

# Enable CORS for Netlify integration
CORS(app)

@app.route("/")
def home():
    # Serve your HTML file instead of plain text
    return send_from_directory('src/static', 'index.html')

@app.route("/health")
def health():
    return "OK"

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': '🔥 GREGVERSE API',
        'version': '1.0.0',
        'description': 'The ultimate Greg Isenberg archive and tribute backend',
        'mission': 'Honor Greg\'s no-gatekeeping philosophy with world-class engineering',
        'endpoints': {
            'podcast': {
                'episodes': 'GET /api/episodes',
                'stats': 'GET /api/podcast-stats',
                'guests': 'GET /api/featured-guests',
                'rss_health': 'GET /api/rss-health'
            },
            'health': {
                'basic': 'GET /health'
            }
        },
        'philosophy': 'No gatekeeping - built with love for Greg Isenberg and the entrepreneur community',
        'tribute': 'Honoring someone who has helped over 1 million entrepreneurs worldwide'
    })

@app.route('/api/episodes', methods=['GET'])
def api_episodes():
    """Get latest podcast episodes from RSS feed"""
    RSS_URL = 'https://rss.flightcast.com/ordbkg8yojpehffas7vr7qpc.xml'
    
    try:
        feed = feedparser.parse(RSS_URL)
        episodes = []
        
        for entry in feed.entries[:6]:  # Latest 6 episodes
            episodes.append({
                'title': entry.title,
                'description': entry.summary[:200] + '...' if len(entry.summary) > 200 else entry.summary,
                'date': entry.published,
                'duration': getattr(entry, 'itunes_duration', '32:07'),
                'image': 'https://assets.flightcast.com/static/t8c97hs8oy7a2xnobsfu5p42.jpg',
                'link': entry.link,
                'tags': ['AI', 'Startup', 'Business']
            })
        
        return jsonify({
            'success': True,
            'episodes': episodes, 
            'total': len(feed.entries),
            'message': 'Latest episodes from Greg\'s podcast'
        })
        
    except Exception as e:
        fallback_episodes = [
            {
                'title': '$3,370/Day with ONE AI Ad (Arcads Founder Explains HOW)',
                'description': 'Romain Torres, founder of Arcads, shows how businesses use AI to create diverse ad content at scale...',
                'date': 'Jul 30, 2025',
                'duration': '32:07',
                'image': 'https://assets.flightcast.com/static/t8c97hs8oy7a2xnobsfu5p42.jpg',
                'link': '#',
                'tags': ['AI', 'Ads', 'Revenue']
            }
        ]
        return jsonify({
            'success': False,
            'episodes': fallback_episodes, 
            'total': 100,
            'message': 'Using fallback episode data'
        })

@app.route('/api/podcast-stats', methods=['GET'])
def api_podcast_stats():
    """Get podcast and overall statistics"""
    RSS_URL = 'https://rss.flightcast.com/ordbkg8yojpehffas7vr7qpc.xml'
    
    try:
        feed = feedparser.parse(RSS_URL)
        podcast_count = len(feed.entries)
    except:
        podcast_count = 100
    
    return jsonify({
        'success': True,
        'stats': {
            'podcast_episodes': podcast_count,
            'youtube_videos': 659,
            'startup_ideas': 50,
            'companies_built': 4,
            'expert_guests': 100,
            'industries_covered': 12
        },
        'message': 'Real-time stats for the Gregverse',
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/featured-guests', methods=['GET'])
def api_featured_guests():
    """Get featured podcast guests"""
    featured_guests = [
        {
            'name': 'Romain Torres',
            'company': 'Arcads',
            'title': 'Founder, Arcads',
            'description': 'AI ad generation platform helping businesses create diverse content at scale',
            'image': 'https://pbs.twimg.com/profile_images/1472933274209107968/6u-LQfjG_400x400.jpg',
            'tags': ['AI', 'Ads', 'SaaS'],
            'quote': 'AI-generated ads are enabling businesses to create high-volume, diverse creative content.',
            'episodes': ['Latest'],
            'revenue': '$3,370/day'
        },
        {
            'name': 'Alex Hormozi',
            'company': 'Acquisition.com',
            'title': 'CEO, Acquisition.com',
            'description': 'Built $100M+ business empire through acquisitions and scaling strategies',
            'image': 'https://www.acquisition.com/hubfs/ACQ_Web_Bio-AlexHormozi%202.png',
            'tags': ['Business', 'Acquisition', 'Sales'],
            'quote': 'Focus on systems, processes, and relentless execution.',
            'episodes': ['#23', '#89'],
            'revenue': '$100M+'
        },
        {
            'name': 'Sahil Lavingia',
            'company': 'Gumroad',
            'title': 'Founder & CEO, Gumroad',
            'description': 'Creator Economy Platform Pioneer bootstrapped to profitability',
            'image': 'https://cdn.prod.website-files.com/5fdb2fcbe8cb905cd95d758f/6808e2061de1b35fe955fc28_Sahil%20Lavingia.webp',
            'tags': ['SaaS', 'Creator', 'Bootstrap'],
            'quote': 'Build something people want, then figure out how to make money.',
            'episodes': ['#19', '#67'],
            'revenue': '$10M+ ARR'
        }
    ]
    
    return jsonify({
        'success': True,
        'guests': featured_guests,
        'total': len(featured_guests),
        'message': 'Featured guests from Greg\'s podcast'
    })

@app.route('/api/rss-health', methods=['GET'])
def api_rss_health():
    """Check RSS feed health"""
    RSS_URL = 'https://rss.flightcast.com/ordbkg8yojpehffas7vr7qpc.xml'
    
    try:
        response = requests.get(RSS_URL, timeout=10)
        rss_status = 'healthy' if response.status_code == 200 else 'error'
        
        if rss_status == 'healthy':
            feed = feedparser.parse(RSS_URL)
            episode_count = len(feed.entries)
            latest_episode = feed.entries[0].title if feed.entries else 'Unknown'
        else:
            episode_count = 0
            latest_episode = 'Unable to fetch'
            
    except Exception as e:
        rss_status = 'error'
        episode_count = 0
        latest_episode = 'Connection failed'
    
    return jsonify({
        'status': 'healthy',
        'rss_feed': {
            'status': rss_status,
            'episode_count': episode_count,
            'latest_episode': latest_episode
        },
        'timestamp': datetime.now().isoformat()
    })

# Add this route to serve static files (CSS, JS, images)
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory('src/static', path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
