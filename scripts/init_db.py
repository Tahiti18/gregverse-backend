#!/usr/bin/env python3
"""
GREGVERSE Database Initialization Script
Creates all tables and indexes for production deployment
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.models.video import db
from src.models.youtube_stats import YouTubeStats
from src.main import app
from sqlalchemy import text

def init_database():
    """Initialize database with tables and indexes"""
    print("🚀 Initializing GREGVERSE database...")
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we're using PostgreSQL for advanced features
            db_url = os.getenv('DATABASE_URL', '')
            if 'postgresql' in db_url:
                print("📊 Setting up PostgreSQL optimizations...")
                
                # Create PostgreSQL extensions and indexes
                try:
                    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
                    print("✅ pg_trgm extension enabled")
                except Exception as e:
                    print(f"⚠️  pg_trgm extension warning: {e}")
                
                # Create search indexes
                try:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_search_idx ON videos 
                        USING GIN(to_tsvector('english', title || ' ' || COALESCE(description, '')));
                    """))
                    print("✅ Full-text search index created")
                except Exception as e:
                    print(f"⚠️  Search index warning: {e}")
                
                try:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_similarity_idx ON videos 
                        USING GIN(title gin_trgm_ops, description gin_trgm_ops);
                    """))
                    print("✅ Similarity search index created")
                except Exception as e:
                    print(f"⚠️  Similarity index warning: {e}")
                
                # Create category index
                try:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_category_idx ON videos (category);
                    """))
                    print("✅ Category index created")
                except Exception as e:
                    print(f"⚠️  Category index warning: {e}")
                
                # Create published date index
                try:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_published_idx ON videos (published_at DESC);
                    """))
                    print("✅ Published date index created")
                except Exception as e:
                    print(f"⚠️  Published date index warning: {e}")
            
            else:
                print("📝 Using SQLite - basic indexes only")
                # Create basic indexes for SQLite
                try:
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_title_idx ON videos (title);
                    """))
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS videos_category_idx ON videos (category);
                    """))
                    print("✅ Basic indexes created for SQLite")
                except Exception as e:
                    print(f"⚠️  Index creation warning: {e}")
            
            db.session.commit()
            print("🎯 Database initialization completed successfully!")
            
            # Verify tables exist
            tables = db.engine.table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            db.session.rollback()
            sys.exit(1)

def verify_database():
    """Verify database connection and tables"""
    print("🔍 Verifying database setup...")
    
    with app.app_context():
        try:
            # Test database connection
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check if tables exist
            from src.models.video import Video
            video_count = Video.query.count()
            print(f"📊 Videos table: {video_count} records")
            
            stats_count = YouTubeStats.query.count()
            print(f"📊 YouTube stats table: {stats_count} records")
            
            print("🎉 Database verification completed!")
            
        except Exception as e:
            print(f"❌ Database verification failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("🔥 GREGVERSE Database Setup")
    print("🎯 Mission: Honor Greg Isenberg's no-gatekeeping philosophy")
    print("=" * 50)
    
    init_database()
    verify_database()
    
    print("=" * 50)
    print("🚀 Database is ready for the ultimate entrepreneur archive!")
    print("💡 Next step: Run sync_youtube_data.py to populate with content")

