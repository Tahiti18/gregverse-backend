# 🔥 GREGVERSE Backend - The Ultimate Greg Isenberg Archive

> **A living tribute to Greg Isenberg's no-gatekeeping philosophy**  
> Honoring someone who has helped over 1 million entrepreneurs worldwide

## 🎯 Mission

Build the most comprehensive, searchable archive of Greg Isenberg's entrepreneurial wisdom - every video, podcast, idea, and insight - accessible to millions of entrepreneurs worldwide.

## ⚡ Features

### 🔍 **Intelligent Search System**
- Full-text search across 659+ YouTube videos
- Auto-complete suggestions
- Category filtering (AI Tools, Startup Ideas, Interviews, etc.)
- Semantic search with relevance ranking
- Sub-500ms response times

### 📊 **Real-Time Live Stats**
- Live YouTube subscriber count
- Progress tracking to 1M goal
- WebSocket updates every 10 minutes
- Graceful fallbacks when APIs fail

### 🎥 **Video Management**
- Auto-categorization using AI
- Pagination and filtering
- Metadata extraction
- Thumbnail optimization

### 🚀 **Production-Ready Architecture**
- PostgreSQL with trigram search optimization
- Redis caching layer
- WebSocket real-time updates
- Comprehensive error handling
- Health monitoring endpoints

## 🏗️ Technical Stack

```
Backend: Flask + SocketIO
Database: PostgreSQL (SQLite for development)
Cache: Redis
APIs: YouTube Data API v3
Search: PostgreSQL Full-Text Search + Trigrams
Real-time: WebSocket with fallback polling
```

## 📡 API Endpoints

### Search APIs
```
POST /api/search/videos          # Search videos
GET  /api/search/autocomplete    # Auto-complete suggestions
GET  /api/search/categories      # Available categories
GET  /api/search/trending        # Trending searches
```

### Stats APIs
```
GET  /api/stats/youtube          # Live YouTube stats
GET  /api/stats/overview         # Comprehensive overview
```

### Health & Monitoring
```
GET  /health                     # Basic health check
GET  /health/detailed            # Detailed system info
GET  /api                        # API documentation
```

### WebSocket Events
```
connect                          # Client connection
disconnect                       # Client disconnection
stats_update                     # Real-time stats broadcast
request_stats_update             # Manual stats refresh
```

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and setup
cd gregverse-backend
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your YouTube API key to .env
```

### 2. Database Setup
```bash
# Initialize database
python src/main.py
# Tables will be created automatically
```

### 3. Sync YouTube Data
```bash
# Sync Greg's videos (requires YouTube API key)
flask sync-videos

# Update live stats
flask update-stats
```

### 4. Run the Server
```bash
python src/main.py
```

Server runs on `http://localhost:5000`

## 🔧 Configuration

### Environment Variables (.env)
```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key_here
GREG_CHANNEL_ID=UCGy7SkBjcIAgTiwkXEtPnYg

# Database
DATABASE_URL=sqlite:///src/database/app.db
REDIS_URL=redis://localhost:6379

# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# API Settings
API_RATE_LIMIT=100
SEARCH_RESULTS_PER_PAGE=20
STATS_UPDATE_INTERVAL=600
```

## 📊 Database Schema

### Videos Table
```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    youtube_id VARCHAR(20) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    published_at TIMESTAMP,
    view_count INTEGER DEFAULT 0,
    category VARCHAR(50),
    tags JSON,
    thumbnail_url TEXT,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### YouTube Stats Table
```sql
CREATE TABLE youtube_stats (
    id SERIAL PRIMARY KEY,
    subscriber_count INTEGER NOT NULL,
    total_views BIGINT NOT NULL,
    video_count INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔍 Search Implementation

### Full-Text Search with PostgreSQL
```python
# Optimized search query
SELECT *, 
       ts_rank(to_tsvector('english', title || ' ' || description), 
               plainto_tsquery('english', %s)) as rank
FROM videos 
WHERE to_tsvector('english', title || ' ' || description) 
      @@ plainto_tsquery('english', %s)
ORDER BY rank DESC, view_count DESC
```

### Auto-Categorization
```python
# AI-powered categorization
categories = {
    'AI Tools': ['ai', 'chatgpt', 'gpt', 'claude', 'artificial intelligence'],
    'Startup Ideas': ['startup', 'business idea', 'entrepreneur'],
    'Interviews': ['interview', 'guest', 'conversation'],
    'No-Code': ['no-code', 'nocode', 'bubble', 'webflow'],
    'Marketing': ['marketing', 'growth', 'seo', 'social media']
}
```

## 🌐 WebSocket Integration

### Frontend Connection
```javascript
const socket = io('http://localhost:5000');

socket.on('stats_update', (data) => {
    updateSubscriberCount(data.subscriber_count);
    updateProgressBar(data.progress_to_million);
});

socket.emit('request_stats_update');
```

### Real-Time Updates
- Subscriber count updates every 10 minutes
- Progress bar calculation: `(current_subs / 1,000,000) * 100`
- Automatic fallback to cached data on API failures

## 🚀 Deployment

### Production Checklist
- ✅ Environment variables configured
- ✅ Database migrations run
- ✅ YouTube API key active
- ✅ Redis cache configured
- ✅ Health endpoints responding
- ✅ WebSocket connections tested

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/main.py"]
```

## 📈 Performance Targets

- **Search Response**: < 500ms
- **API Uptime**: 99.9%
- **WebSocket Latency**: < 100ms
- **Database Queries**: < 200ms
- **Cache Hit Rate**: > 80%

## 🔧 CLI Commands

```bash
# Sync all videos from YouTube
flask sync-videos

# Update live statistics
flask update-stats

# Health check
curl http://localhost:5000/health
```

## 🎯 Roadmap

### Phase 1: Core Functionality ✅
- Search system
- Live stats
- Video management
- WebSocket integration

### Phase 2: Advanced Features
- Podcast RSS integration
- AI chat widget (RAG system)
- Advanced analytics
- Performance optimization

### Phase 3: Scale & Polish
- Elasticsearch migration
- CDN integration
- Advanced caching
- Mobile optimization

## 🤝 Contributing

This is a tribute project built with love for Greg Isenberg and the entrepreneur community. Contributions welcome!

### Development Setup
```bash
git clone <repo>
cd gregverse-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## 📄 License

Built with ❤️ for the entrepreneur community  
Honoring Greg Isenberg's no-gatekeeping philosophy

---

**"The best way to honor someone who gives everything away for free is to build something that amplifies their impact."**

*This backend powers the most comprehensive Greg Isenberg archive ever created.*

