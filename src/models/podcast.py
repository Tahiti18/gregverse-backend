from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .video import db

class PodcastEpisode(db.Model):
    __tablename__ = 'podcast_episodes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    guest = db.Column(db.String(200))
    published_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.String(20))  # e.g., "45:30"
    episode_number = db.Column(db.Integer)
    season_number = db.Column(db.Integer)
    audio_url = db.Column(db.String(500))
    transcript = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    spotify_url = db.Column(db.String(500))
    apple_url = db.Column(db.String(500))
    youtube_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'guest': self.guest,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'duration': self.duration,
            'episode_number': self.episode_number,
            'season_number': self.season_number,
            'audio_url': self.audio_url,
            'transcript': self.transcript,
            'tags': self.tags.split(',') if self.tags else [],
            'spotify_url': self.spotify_url,
            'apple_url': self.apple_url,
            'youtube_url': self.youtube_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def search(cls, query=None, guest=None, tag=None, page=1, per_page=20):
        """Search podcast episodes with filters"""
        query_obj = cls.query
        
        if query:
            search_filter = db.or_(
                cls.title.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%'),
                cls.guest.ilike(f'%{query}%'),
                cls.transcript.ilike(f'%{query}%')
            )
            query_obj = query_obj.filter(search_filter)
        
        if guest:
            query_obj = query_obj.filter(cls.guest.ilike(f'%{guest}%'))
        
        if tag:
            query_obj = query_obj.filter(cls.tags.ilike(f'%{tag}%'))
        
        return query_obj.order_by(cls.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @classmethod
    def get_guests(cls):
        """Get all unique guests"""
        guests = db.session.query(cls.guest).filter(cls.guest.isnot(None)).distinct().all()
        return [guest[0] for guest in guests if guest[0]]
    
    @classmethod
    def get_tags(cls):
        """Get all unique tags"""
        episodes = cls.query.filter(cls.tags.isnot(None)).all()
        all_tags = []
        for episode in episodes:
            if episode.tags:
                all_tags.extend([tag.strip() for tag in episode.tags.split(',')])
        return list(set(all_tags))

class StartupIdea(db.Model):
    __tablename__ = 'startup_ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))  # Easy, Medium, Hard
    market_size = db.Column(db.String(50))  # Small, Medium, Large
    source_type = db.Column(db.String(50))  # video, podcast, tweet
    source_id = db.Column(db.String(100))  # ID of source content
    source_url = db.Column(db.String(500))
    tags = db.Column(db.String(500))  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'market_size': self.market_size,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'source_url': self.source_url,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def search(cls, query=None, category=None, difficulty=None, page=1, per_page=20):
        """Search startup ideas with filters"""
        query_obj = cls.query
        
        if query:
            search_filter = db.or_(
                cls.title.ilike(f'%{query}%'),
                cls.description.ilike(f'%{query}%'),
                cls.tags.ilike(f'%{query}%')
            )
            query_obj = query_obj.filter(search_filter)
        
        if category:
            query_obj = query_obj.filter(cls.category == category)
        
        if difficulty:
            query_obj = query_obj.filter(cls.difficulty == difficulty)
        
        return query_obj.order_by(cls.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

class Tweet(db.Model):
    __tablename__ = 'tweets'
    
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(50), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='Greg Isenberg')
    published_at = db.Column(db.DateTime, nullable=False)
    retweet_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    url = db.Column(db.String(500))
    media_urls = db.Column(db.Text)  # JSON array of media URLs
    hashtags = db.Column(db.String(500))  # Comma-separated hashtags
    mentions = db.Column(db.String(500))  # Comma-separated mentions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'tweet_id': self.tweet_id,
            'content': self.content,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'retweet_count': self.retweet_count,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'url': self.url,
            'media_urls': json.loads(self.media_urls) if self.media_urls else [],
            'hashtags': self.hashtags.split(',') if self.hashtags else [],
            'mentions': self.mentions.split(',') if self.mentions else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def search(cls, query=None, hashtag=None, page=1, per_page=20):
        """Search tweets with filters"""
        query_obj = cls.query
        
        if query:
            search_filter = db.or_(
                cls.content.ilike(f'%{query}%'),
                cls.hashtags.ilike(f'%{query}%')
            )
            query_obj = query_obj.filter(search_filter)
        
        if hashtag:
            query_obj = query_obj.filter(cls.hashtags.ilike(f'%{hashtag}%'))
        
        return query_obj.order_by(cls.published_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

