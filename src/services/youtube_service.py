import os
import requests
import time
from datetime import datetime
from ..models.youtube_stats import YouTubeStats
from ..models.video import Video, db

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.channel_id = os.getenv('YOUTUBE_CHANNEL_ID', 'UCGy7SkBjcIAgTiwkXEtPnYg')
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        
    def get_channel_stats(self):
        """Get real-time channel statistics"""
        if not self.api_key:
            print("Warning: No YouTube API key found, using cached data")
            return YouTubeStats.get_latest_cached()
        
        url = f"{self.base_url}/channels"
        params = {
            'part': 'statistics',
            'id': self.channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data or not data['items']:
                raise Exception("No channel data found")
            
            stats = data['items'][0]['statistics']
            
            # Update database with new stats
            subscriber_count = int(stats.get('subscriberCount', 0))
            total_views = int(stats.get('viewCount', 0))
            video_count = int(stats.get('videoCount', 0))
            
            # Save to database
            YouTubeStats.update_stats(subscriber_count, total_views, video_count)
            
            return {
                'subscriber_count': subscriber_count,
                'total_views': total_views,
                'video_count': video_count,
                'progress_to_million': round((subscriber_count / 1000000) * 100, 1),
                'updated_at': datetime.utcnow().isoformat(),
                'is_live': True
            }
            
        except Exception as e:
            print(f"YouTube API error: {e}")
            # Return cached data on failure
            cached_data = YouTubeStats.get_latest_cached()
            cached_data['is_live'] = False
            cached_data['error'] = str(e)
            return cached_data
    
    def get_channel_videos(self, max_results=50, page_token=None):
        """Get videos from the channel"""
        if not self.api_key:
            return {'videos': [], 'next_page_token': None}
        
        # First get the uploads playlist ID
        url = f"{self.base_url}/channels"
        params = {
            'part': 'contentDetails',
            'id': self.channel_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            url = f"{self.base_url}/playlistItems"
            params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': max_results,
                'key': self.api_key
            }
            
            if page_token:
                params['pageToken'] = page_token
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            videos = []
            for item in data.get('items', []):
                snippet = item['snippet']
                video_data = {
                    'youtube_id': snippet['resourceId']['videoId'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'published_at': snippet['publishedAt'],
                    'thumbnail_url': snippet['thumbnails'].get('high', {}).get('url', ''),
                }
                videos.append(video_data)
            
            return {
                'videos': videos,
                'next_page_token': data.get('nextPageToken')
            }
            
        except Exception as e:
            print(f"Error fetching videos: {e}")
            return {'videos': [], 'next_page_token': None}
    
    def sync_videos_to_database(self):
        """Sync all videos from YouTube to database"""
        print("Starting video sync...")
        page_token = None
        total_synced = 0
        
        while True:
            result = self.get_channel_videos(max_results=50, page_token=page_token)
            videos = result['videos']
            
            if not videos:
                break
            
            for video_data in videos:
                # Check if video already exists
                existing_video = Video.query.filter_by(
                    youtube_id=video_data['youtube_id']
                ).first()
                
                if not existing_video:
                    # Create new video record
                    video = Video(
                        youtube_id=video_data['youtube_id'],
                        title=video_data['title'],
                        description=video_data['description'],
                        published_at=datetime.fromisoformat(
                            video_data['published_at'].replace('Z', '+00:00')
                        ),
                        thumbnail_url=video_data['thumbnail_url'],
                        category=self._categorize_video(
                            video_data['title'], 
                            video_data['description']
                        )
                    )
                    db.session.add(video)
                    total_synced += 1
                else:
                    # Update existing video
                    existing_video.title = video_data['title']
                    existing_video.description = video_data['description']
                    existing_video.thumbnail_url = video_data['thumbnail_url']
                    existing_video.updated_at = datetime.utcnow()
            
            db.session.commit()
            print(f"Synced {len(videos)} videos (total: {total_synced})")
            
            page_token = result['next_page_token']
            if not page_token:
                break
            
            # Rate limiting - YouTube API has quotas
            time.sleep(1)
        
        print(f"Video sync complete. Total synced: {total_synced}")
        return total_synced
    
    def _categorize_video(self, title, description):
        """Simple categorization based on keywords"""
        content = (title + ' ' + (description or '')).lower()
        
        if any(keyword in content for keyword in ['ai', 'artificial intelligence', 'chatgpt', 'gpt', 'claude']):
            return 'AI Tools'
        elif any(keyword in content for keyword in ['startup', 'business idea', 'entrepreneur']):
            return 'Startup Ideas'
        elif any(keyword in content for keyword in ['interview', 'guest', 'conversation']):
            return 'Interviews'
        elif any(keyword in content for keyword in ['no-code', 'nocode', 'bubble', 'webflow']):
            return 'No-Code'
        elif any(keyword in content for keyword in ['marketing', 'growth', 'seo', 'social media']):
            return 'Marketing'
        else:
            return 'Business Building'

