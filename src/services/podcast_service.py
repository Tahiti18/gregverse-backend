import feedparser
import requests
from datetime import datetime
import re
import logging
from typing import List, Dict, Optional
from ..models.podcast import PodcastEpisode, db

logger = logging.getLogger(__name__)

class PodcastService:
    def __init__(self):
        self.rss_url = "https://feeds.transistor.fm/the-startup-ideas-podcast"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Gregverse/1.0 (Podcast Aggregator)'
        })
    
    def fetch_episodes(self) -> List[Dict]:
        """Fetch episodes from RSS feed"""
        try:
            logger.info(f"Fetching podcast episodes from {self.rss_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has issues: {feed.bozo_exception}")
            
            episodes = []
            for entry in feed.entries:
                episode_data = self._parse_episode(entry)
                if episode_data:
                    episodes.append(episode_data)
            
            logger.info(f"Successfully parsed {len(episodes)} episodes")
            return episodes
            
        except Exception as e:
            logger.error(f"Error fetching podcast episodes: {str(e)}")
            return []
    
    def _parse_episode(self, entry) -> Optional[Dict]:
        """Parse individual episode from RSS entry"""
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            description = entry.get('description', '').strip()
            
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                try:
                    published_at = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
                except:
                    pass
            
            # Extract audio URL
            audio_url = None
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if 'audio' in enclosure.get('type', ''):
                        audio_url = enclosure.get('href')
                        break
            
            # Extract episode number from title
            episode_number = self._extract_episode_number(title)
            
            # Extract guest name from title/description
            guest = self._extract_guest_name(title, description)
            
            # Extract duration
            duration = entry.get('itunes_duration', '')
            
            # Extract tags from description
            tags = self._extract_tags(description)
            
            # Generate platform URLs (these would need to be actual URLs in production)
            spotify_url = self._generate_spotify_url(title)
            apple_url = self._generate_apple_url(title)
            youtube_url = self._generate_youtube_url(title)
            
            return {
                'title': title,
                'description': self._clean_description(description),
                'guest': guest,
                'published_at': published_at,
                'duration': duration,
                'episode_number': episode_number,
                'audio_url': audio_url,
                'tags': ','.join(tags) if tags else None,
                'spotify_url': spotify_url,
                'apple_url': apple_url,
                'youtube_url': youtube_url
            }
            
        except Exception as e:
            logger.error(f"Error parsing episode: {str(e)}")
            return None
    
    def _extract_episode_number(self, title: str) -> Optional[int]:
        """Extract episode number from title"""
        # Look for patterns like "Episode 123", "#123", "Ep 123"
        patterns = [
            r'Episode\s+(\d+)',
            r'Ep\s+(\d+)',
            r'#(\d+)',
            r'(\d+):',  # Number followed by colon
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def _extract_guest_name(self, title: str, description: str) -> Optional[str]:
        """Extract guest name from title or description"""
        # Common patterns for guest names
        patterns = [
            r'with\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "with John Doe"
            r'featuring\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "featuring Jane Smith"
            r'guest:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "guest: Bob Johnson"
            r'interviews?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "interview John Doe"
        ]
        
        text = f"{title} {description}"
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                guest_name = match.group(1).strip()
                # Filter out common false positives
                if guest_name.lower() not in ['greg isenberg', 'startup ideas', 'the startup']:
                    return guest_name
        
        return None
    
    def _extract_tags(self, description: str) -> List[str]:
        """Extract relevant tags from description"""
        tags = []
        
        # Common startup/business keywords
        keywords = [
            'startup', 'entrepreneur', 'business', 'saas', 'ai', 'tech',
            'marketing', 'growth', 'funding', 'venture capital', 'vc',
            'product', 'strategy', 'innovation', 'digital', 'ecommerce',
            'fintech', 'healthtech', 'edtech', 'marketplace', 'platform'
        ]
        
        description_lower = description.lower()
        for keyword in keywords:
            if keyword in description_lower:
                tags.append(keyword)
        
        return list(set(tags))  # Remove duplicates
    
    def _clean_description(self, description: str) -> str:
        """Clean HTML and formatting from description"""
        # Remove HTML tags
        description = re.sub(r'<[^>]+>', '', description)
        
        # Remove extra whitespace
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Limit length
        if len(description) > 1000:
            description = description[:997] + '...'
        
        return description
    
    def _generate_spotify_url(self, title: str) -> Optional[str]:
        """Generate Spotify URL (placeholder - would need actual mapping)"""
        # In production, you'd maintain a mapping of episodes to Spotify URLs
        return f"https://open.spotify.com/episode/placeholder-{hash(title) % 1000000}"
    
    def _generate_apple_url(self, title: str) -> Optional[str]:
        """Generate Apple Podcasts URL (placeholder)"""
        return f"https://podcasts.apple.com/podcast/placeholder-{hash(title) % 1000000}"
    
    def _generate_youtube_url(self, title: str) -> Optional[str]:
        """Generate YouTube URL (placeholder)"""
        return f"https://youtube.com/watch?v=placeholder-{hash(title) % 1000000}"
    
    def sync_episodes(self) -> Dict[str, int]:
        """Sync episodes from RSS feed to database"""
        try:
            episodes_data = self.fetch_episodes()
            
            new_count = 0
            updated_count = 0
            
            for episode_data in episodes_data:
                # Check if episode already exists
                existing = PodcastEpisode.query.filter_by(
                    title=episode_data['title']
                ).first()
                
                if existing:
                    # Update existing episode
                    for key, value in episode_data.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    updated_count += 1
                else:
                    # Create new episode
                    episode = PodcastEpisode(**episode_data)
                    db.session.add(episode)
                    new_count += 1
            
            db.session.commit()
            
            logger.info(f"Podcast sync completed: {new_count} new, {updated_count} updated")
            
            return {
                'new_episodes': new_count,
                'updated_episodes': updated_count,
                'total_processed': len(episodes_data)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing podcast episodes: {str(e)}")
            raise
    
    def get_episode_stats(self) -> Dict:
        """Get podcast statistics"""
        try:
            total_episodes = PodcastEpisode.query.count()
            unique_guests = len(PodcastEpisode.get_guests())
            latest_episode = PodcastEpisode.query.order_by(
                PodcastEpisode.published_at.desc()
            ).first()
            
            return {
                'total_episodes': total_episodes,
                'unique_guests': unique_guests,
                'latest_episode': latest_episode.to_dict() if latest_episode else None,
                'total_tags': len(PodcastEpisode.get_tags())
            }
            
        except Exception as e:
            logger.error(f"Error getting podcast stats: {str(e)}")
            return {
                'total_episodes': 0,
                'unique_guests': 0,
                'latest_episode': None,
                'total_tags': 0
            }

