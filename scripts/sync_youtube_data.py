#!/usr/bin/env python3
"""
GREGVERSE YouTube Data Sync Script
Syncs all of Greg Isenberg's YouTube content to the database
"""

import os
import sys
import time
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from main import app
from src.services.youtube_service import YouTubeService
from src.models.video import Video, db

def sync_all_videos():
    """Sync all videos from Greg's YouTube channel"""
    print("🚀 Starting GREGVERSE YouTube sync...")
    print("🎯 Syncing Greg Isenberg's complete video archive")
    print("=" * 60)
    
    with app.app_context():
        youtube_service = YouTubeService()
        
        # Check API key
        if not youtube_service.api_key:
            print("❌ YouTube API key not found!")
            print("💡 Set YOUTUBE_API_KEY in your environment variables")
            return False
        
        print(f"📺 Channel ID: {youtube_service.channel_id}")
        print("🔄 Starting video synchronization...")
        
        try:
            # Sync videos
            synced_count = youtube_service.sync_videos_to_database()
            
            print("=" * 60)
            print(f"✅ Successfully synced {synced_count} videos!")
            
            # Get final stats
            total_videos = Video.query.count()
            categories = Video.get_categories()
            
            print(f"📊 Total videos in database: {total_videos}")
            print(f"📂 Categories found: {len(categories)}")
            print(f"🏷️  Categories: {', '.join(categories)}")
            
            # Show recent videos
            recent_videos = Video.query.order_by(Video.published_at.desc()).limit(5).all()
            print("\n🎬 Most recent videos:")
            for video in recent_videos:
                published = video.published_at.strftime('%Y-%m-%d') if video.published_at else 'Unknown'
                print(f"   • {video.title[:60]}... ({published})")
            
            return True
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return False

def update_live_stats():
    """Update YouTube channel statistics"""
    print("\n📊 Updating live YouTube statistics...")
    
    with app.app_context():
        youtube_service = YouTubeService()
        
        try:
            stats = youtube_service.get_channel_stats()
            
            if stats.get('is_live', False):
                print("✅ Live stats updated successfully!")
                print(f"👥 Subscribers: {stats['subscriber_count']:,}")
                print(f"👀 Total views: {stats['total_views']:,}")
                print(f"🎬 Video count: {stats['video_count']:,}")
                print(f"📈 Progress to 1M: {stats['progress_to_million']}%")
            else:
                print("⚠️  Using cached stats (API unavailable)")
                print(f"👥 Subscribers: {stats['subscriber_count']:,}")
                
            return True
            
        except Exception as e:
            print(f"❌ Stats update failed: {e}")
            return False

def categorize_existing_videos():
    """Re-categorize all existing videos with improved AI"""
    print("\n🤖 Re-categorizing existing videos...")
    
    with app.app_context():
        youtube_service = YouTubeService()
        
        videos = Video.query.filter(
            db.or_(Video.category.is_(None), Video.category == '')
        ).all()
        
        print(f"🔄 Found {len(videos)} videos to categorize...")
        
        categorized = 0
        for video in videos:
            try:
                category = youtube_service._categorize_video(video.title, video.description)
                video.category = category
                categorized += 1
                
                if categorized % 10 == 0:
                    print(f"   Categorized {categorized}/{len(videos)} videos...")
                    
            except Exception as e:
                print(f"⚠️  Failed to categorize '{video.title[:30]}...': {e}")
        
        db.session.commit()
        print(f"✅ Categorized {categorized} videos successfully!")

def show_sync_summary():
    """Show comprehensive sync summary"""
    print("\n" + "=" * 60)
    print("🎉 GREGVERSE SYNC COMPLETE!")
    print("=" * 60)
    
    with app.app_context():
        total_videos = Video.query.count()
        categories = Video.get_categories()
        
        print(f"📊 CONTENT ARCHIVE SUMMARY:")
        print(f"   • Total Videos: {total_videos:,}")
        print(f"   • Categories: {len(categories)}")
        print(f"   • Database: Ready for search")
        print(f"   • API: Ready for frontend")
        
        print(f"\n🏷️  CONTENT CATEGORIES:")
        for category in categories:
            count = Video.query.filter_by(category=category).count()
            print(f"   • {category}: {count} videos")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Deploy backend to Railway")
        print(f"   2. Connect frontend to API")
        print(f"   3. Test search functionality")
        print(f"   4. Monitor live stats")
        
        print(f"\n💡 Greg's wisdom is now searchable and accessible!")
        print(f"🌟 Honoring the no-gatekeeping philosophy with technology")

if __name__ == "__main__":
    print("🔥 GREGVERSE YouTube Data Sync")
    print("🎯 Building the ultimate Greg Isenberg archive")
    print("💫 No gatekeeping - maximum value for entrepreneurs")
    
    start_time = time.time()
    
    # Run sync process
    success = True
    
    # 1. Sync videos
    if not sync_all_videos():
        success = False
    
    # 2. Update stats
    if not update_live_stats():
        success = False
    
    # 3. Categorize videos
    try:
        categorize_existing_videos()
    except Exception as e:
        print(f"⚠️  Categorization warning: {e}")
    
    # 4. Show summary
    if success:
        show_sync_summary()
        
        duration = time.time() - start_time
        print(f"\n⏱️  Total sync time: {duration:.1f} seconds")
        print("🎉 GREGVERSE is ready to serve millions of entrepreneurs!")
    else:
        print("\n❌ Sync completed with errors")
        print("💡 Check your API keys and try again")
        sys.exit(1)

