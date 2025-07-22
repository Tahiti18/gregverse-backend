from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index, text

db = SQLAlchemy()

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), index=True)
    tags = db.Column(db.JSON)  # Store as JSON array
    thumbnail_url = db.Column(db.Text)
    duration = db.Column(db.Integer)  # Duration in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add search index for full-text search
    __table_args__ = (
        Index('videos_search_idx', 
              text("title || ' ' || COALESCE(description, '')")),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'youtube_id': self.youtube_id,
            'title': self.title,
            'description': self.description,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'view_count': self.view_count,
            'category': self.category,
            'tags': self.tags or [],
            'thumbnail_url': self.thumbnail_url,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def search(cls, query, category=None, page=1, per_page=20):
        """Search videos with full-text search and filtering"""
        search_query = cls.query
        
        if query:
            # Simple LIKE search for SQLite compatibility
            search_term = f"%{query}%"
            search_query = search_query.filter(
                db.or_(
                    cls.title.ilike(search_term),
                    cls.description.ilike(search_term)
                )
            )
        
        if category and category != 'all':
            search_query = search_query.filter(cls.category == category)
        
        # Order by relevance (title matches first, then description)
        if query:
            search_query = search_query.order_by(
                cls.title.ilike(f"%{query}%").desc(),
                cls.published_at.desc()
            )
        else:
            search_query = search_query.order_by(cls.published_at.desc())
        
        return search_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @classmethod
    def get_categories(cls):
        """Get all unique categories"""
        categories = db.session.query(cls.category).distinct().filter(
            cls.category.isnot(None)
        ).all()
        return [cat[0] for cat in categories if cat[0]]
    
    @classmethod
    def get_autocomplete_suggestions(cls, query, limit=10):
        """Get autocomplete suggestions based on video titles"""
        if not query or len(query) < 2:
            return []
        
        search_term = f"%{query}%"
        suggestions = cls.query.filter(
            cls.title.ilike(search_term)
        ).with_entities(cls.title).limit(limit).all()
        
        return [suggestion[0] for suggestion in suggestions]

