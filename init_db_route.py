from flask import Flask, jsonify
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.video import db
from main import app

@app.route('/admin/init_db', methods=['GET'])
def init_db_route():
    """Initialize database tables"""
    try:
        with app.app_context():
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

if __name__ == '__main__':
    # This won't be run when imported
    pass
