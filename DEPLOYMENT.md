# 🚀 GREGVERSE Railway Deployment Guide

## 🎯 Pre-Deployment Checklist

### ✅ Required Files (All Created)
- `main.py` - Main application entry point
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process configuration
- `runtime.txt` - Python version specification
- Complete `src/` directory with all modules

### 🔑 Environment Variables Required

**Essential Variables:**
```
YOUTUBE_API_KEY=your_youtube_api_key_here
YOUTUBE_CHANNEL_ID=UCGy7SkBjcIAgTiwkXEtPnYg
SECRET_KEY=your_secure_random_string_here
CORS_ORIGINS=*
```

**Optional Variables:**
```
OPENAI_API_KEY=your_openai_key_for_ai_categorization
REDIS_URL=redis://localhost:6379
```

## 🚀 Railway Deployment Steps

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   - Commit all files to your repository
   - Push to main branch

2. **Connect to Railway**
   - Go to railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your gregverse-backend repository

3. **Add Database**
   - In Railway dashboard, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set DATABASE_URL

4. **Set Environment Variables**
   - Go to your service settings
   - Add all required environment variables
   - Save changes

5. **Deploy**
   - Railway will automatically deploy
   - Monitor logs for any issues

### Method 2: Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Initialize**
   ```bash
   railway login
   railway init
   ```

3. **Add PostgreSQL**
   ```bash
   railway add postgresql
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set YOUTUBE_API_KEY=your_key_here
   railway variables set SECRET_KEY=your_secret_here
   railway variables set CORS_ORIGINS=*
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## 🔧 Post-Deployment Setup

### 1. Initialize Database
Once deployed, run the database initialization:
```bash
railway run python scripts/init_db.py
```

### 2. Sync YouTube Data
Populate the database with Greg's videos:
```bash
railway run python scripts/sync_youtube_data.py
```

### 3. Verify Deployment
Check these endpoints:
- `https://your-app.railway.app/health` - Health check
- `https://your-app.railway.app/api` - API documentation
- `https://your-app.railway.app/api/stats/youtube` - YouTube stats

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
- Ensure all files are in the repository
- Check that `src/` directory structure is correct
- Verify Python path in main.py

**2. Database Connection Issues**
- Ensure PostgreSQL is added to Railway project
- Check DATABASE_URL is automatically set
- Verify database tables are created

**3. YouTube API Issues**
- Verify YOUTUBE_API_KEY is correct
- Check API quotas in Google Cloud Console
- Ensure channel ID is correct

**4. WebSocket Issues**
- Verify gevent is in requirements.txt
- Check Procfile uses gevent worker
- Ensure CORS is properly configured

### Health Check Responses

**Healthy Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "youtube_api": "active",
  "message": "🔥 GREGVERSE Backend is LIVE!"
}
```

**Degraded Response:**
```json
{
  "status": "degraded",
  "database": "connected",
  "youtube_api": "degraded",
  "youtube_note": "Using cached data"
}
```

## 📊 Monitoring

### Key Metrics to Monitor
- **Response Times**: Should be <500ms for search
- **Database Connections**: Monitor for connection leaks
- **API Quotas**: YouTube API has daily limits
- **Memory Usage**: Monitor for memory leaks

### Logs to Watch
- Application startup logs
- Database connection logs
- YouTube API response logs
- WebSocket connection logs

## 🔄 Updates and Maintenance

### Updating the Application
1. Push changes to GitHub main branch
2. Railway will automatically redeploy
3. Monitor deployment logs
4. Verify health endpoints

### Database Maintenance
- Regular stats updates via cron jobs
- Periodic video sync for new content
- Database optimization for search performance

### API Key Rotation
1. Generate new YouTube API key
2. Update environment variable in Railway
3. Restart application
4. Verify functionality

## 🎉 Success Indicators

### Deployment Successful When:
- ✅ Health endpoint returns 200 status
- ✅ Database connection established
- ✅ YouTube API responding
- ✅ Search endpoints functional
- ✅ WebSocket connections working

### Performance Targets:
- 🎯 Search response time: <500ms
- 🎯 Uptime: >99.9%
- 🎯 Database queries: <100ms
- 🎯 API availability: >99%

---

**🚀 Ready to serve millions of entrepreneurs with Greg's wisdom!**

