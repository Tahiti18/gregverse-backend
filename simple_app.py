"""
GREGVERSE Backend - Ultra Simple Version for Railway
Minimal dependencies, maximum compatibility
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

# Create minimal Flask app
app = Flask(__name__)
CORS(app, origins="*")

@app.route('/')
def home():
    return jsonify({
        'message': '🔥 GREGVERSE Backend is LIVE!',
        'status': 'healthy',
        'mission': 'Honor Greg Isenberg\'s no-gatekeeping philosophy',
        'tribute': 'The ultimate entrepreneur resource',
        'version': '1.0.0-minimal',
        'philosophy': 'No gatekeeping - maximum value for entrepreneurs worldwide'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'GREGVERSE backend is running',
        'timestamp': '2025-07-22',
        'tribute': 'Built for Greg Isenberg and the entrepreneur community'
    })

@app.route('/api')
def api_info():
    return jsonify({
        'name': '🔥 GREGVERSE API',
        'version': '1.0.0-minimal',
        'description': 'The ultimate Greg Isenberg archive and tribute backend',
        'status': 'minimal version - full features coming soon',
        'philosophy': 'No gatekeeping - built with love for entrepreneurs'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🔥 GREGVERSE Backend Starting (Minimal Version)...")
    print("🎯 Mission: Honor Greg Isenberg's no-gatekeeping philosophy")
    print("🚀 Building the ultimate entrepreneur resource...")
    print(f"💫 Starting on port {port}...")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )

