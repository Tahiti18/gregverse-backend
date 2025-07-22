from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.video import db

class YouTubeStats(db.Model):
    __tablename__ = 'youtube_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    subscriber_count = db.Column(db.Integer, nullable=False)
    total_views = db.Column(db.BigInteger, nullable=False)
    video_count = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'subscriber_count': self.subscriber_count,
            'total_views': self.total_views,
            'video_count': self.video_count,
            'progress_to_million': round((self.subscriber_count / 1000000) * 100, 1),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def get_latest(cls):
        """Get the most recent stats"""
        return cls.query.order_by(cls.updated_at.desc()).first()
    
    @classmethod
    def get_latest_cached(cls):
        """Get latest stats as fallback data"""
        latest = cls.get_latest()
        if latest:
            return latest.to_dict()
        else:
            # Fallback data if no stats exist
            return {
                'subscriber_count': 412000,
                'total_views': 50000000,
                'video_count': 659,
                'progress_to_million': 41.2,
                'updated_at': datetime.utcnow().isoformat(),
                'is_fallback': True
            }
    
    @classmethod
    def update_stats(cls, subscriber_count, total_views, video_count):
        """Update stats with new data"""
        new_stats = cls(
            subscriber_count=subscriber_count,
            total_views=total_views,
            video_count=video_count
        )
        db.session.add(new_stats)
        db.session.commit()
        return new_stats

