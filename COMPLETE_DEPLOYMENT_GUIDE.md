# 🔥 COMPLETE GREGVERSE DEPLOYMENT GUIDE

## 🎯 Full Feature Deployment

This guide will deploy The Gregverse with ALL features enabled:
- ✅ YouTube video search and stats
- ✅ Real-time subscriber counter
- ✅ Podcast RSS integration
- ✅ Startup ideas database
- ✅ AI Chat with RAG system
- ✅ Cross-content search
- ✅ WebSocket real-time updates

## 🔑 Required API Keys & Setup

### 1. YouTube API (Already Have)
- ✅ `YOUTUBE_API_KEY` - Your existing key
- ✅ `YOUTUBE_CHANNEL_ID=UCGy7SkBjcIAgTiwkXEtPnYg`

### 2. OpenAI API (For AI Chat)
**What it does:** Powers the "Ask GregQ" AI chat that answers questions about Greg's content

**How to get:**
1. Go to https://platform.openai.com/api-keys
2. Sign up/login
3. Click "Create new secret key"
4. Copy the key (starts with sk-...)

**Cost:** Free tier available, then $0.002 per 1K tokens (very cheap)

### 3. Pinecone API (For AI Vector Search)
**What it does:** Stores vector embeddings of Greg's content for semantic search

**How to get:**
1. Go to https://www.pinecone.io/
2. Sign up for free account
3. Create a new index:
   - Name: `gregverse`
   - Dimension: `1536`
   - Metric: `cosine`
4. Copy your API key and environment from dashboard

**Cost:** Free tier (100M embeddings/month) - more than enough

## 🚀 Railway Environment Variables

Add these to your Railway project:

```
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CHANNEL_ID=UCGy7SkBjcIAgTiwkXEtPnYg
SECRET_KEY=any_random_string_like_abc123xyz789
CORS_ORIGINS=*
OPENAI_API_KEY=sk-your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=us-west1-gcp-free
PINECONE_INDEX_NAME=gregverse
```

## 📦 Deployment Steps

### 1. Deploy to Railway
1. Push all files to your GitHub repository
2. Connect Railway to your repo
3. Add PostgreSQL database to Railway project
4. Set all environment variables above
5. Deploy!

### 2. Initialize Database
After deployment, run these commands in Railway console:

```bash
# Initialize database tables
python scripts/init_db.py

# Sync YouTube videos
python scripts/sync_youtube_data.py

# Index content for AI chat
python -c "from src.services.ai_chat_service import AIChatService; AIChatService().index_content(True)"
```

### 3. Test All Features
Visit your Railway URL and test:
- ✅ Health check: `/health`
- ✅ YouTube stats: `/api/stats/youtube`
- ✅ Video search: `/api/search/videos`
- ✅ AI chat: `/api/chat/ask` (POST with {"question": "What does Greg say about startups?"})
- ✅ Podcast episodes: `/api/podcast/episodes`

## 🎉 What You'll Have

### Frontend Features Powered:
1. **Search Bar** - Full-text search across all content
2. **Filter Buttons** - AI tools, startups, interviews, etc.
3. **Live Subscriber Counter** - Real-time YouTube stats
4. **Progress Bar** - Current subs / 1M goal
5. **Podcast Directory** - Episodes with guests and metadata
6. **AI Chat Widget** - "Ask GregQ" with source citations
7. **Startup Ideas Database** - Searchable and categorized
8. **Cross-Platform Search** - Videos + podcasts + tweets

### API Endpoints Available:
- `/api/search/*` - Search functionality
- `/api/stats/*` - Live YouTube stats with WebSocket
- `/api/podcast/*` - Podcast episodes, guests, tags, sync
- `/api/chat/*` - AI chat with RAG system
- `/health` - Health monitoring
- `/socket.io` - Real-time WebSocket updates

## 💰 Total Cost Estimate
- **Railway**: ~$5-10/month for hosting
- **OpenAI**: ~$1-5/month for AI chat (depends on usage)
- **Pinecone**: Free tier (sufficient for this project)
- **YouTube API**: Free (within quotas)

**Total: ~$6-15/month for a fully-featured AI-powered content portal**

## 🔧 Maintenance Commands

```bash
# Sync new podcast episodes
railway run python scripts/sync_youtube_data.py

# Update AI index with new content
railway run python -c "from src.services.ai_chat_service import AIChatService; AIChatService().index_content(True)"

# Check system health
curl https://your-app.railway.app/health
```

## 🎯 Success Indicators

✅ Health endpoint returns 200 status
✅ YouTube API responding with subscriber count
✅ Search returns video results
✅ AI chat answers questions with source citations
✅ Podcast episodes loading from RSS feed
✅ WebSocket connections working for real-time updates

**You'll have the most advanced Greg Isenberg content portal ever built! 🚀**

