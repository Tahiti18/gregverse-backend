"""
GREGVERSE Backend Configuration
Production-ready configuration for Railway deployment
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'gregverse_secret_key_2024_change_in_production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # API Configuration
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 100))
    SEARCH_RESULTS_PER_PAGE = int(os.getenv('SEARCH_RESULTS_PER_PAGE', 20))
    STATS_UPDATE_INTERVAL = int(os.getenv('STATS_UPDATE_INTERVAL', 600))
    
    # YouTube API
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID', 'UCPjNBjflYl0-HQtUvOx0Ibw')
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')}"
    )

class ProductionConfig(Config):
    """Production configuration for Railway"""
    DEBUG = False
    FLASK_ENV = 'production'
    
    # Railway provides DATABASE_URL automatically
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/gregverse')
    
    # Fix for Railway's postgres:// URL format if needed
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

