import os
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def init_db():
    try:
        # Add the project root to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import models
        from src.models.video import db
        
        # Create a minimal app context
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data/gregverse.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize database
        db.init_app(app)
        
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
