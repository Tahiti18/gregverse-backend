from flask import Blueprint, request, jsonify
from flask_socketio import emit
from ..models.podcast import PodcastEpisode, StartupIdea, Tweet
from ..services.podcast_service import PodcastService
import logging

logger = logging.getLogger(__name__)
podcast_bp = Blueprint('podcast', __name__)

@podcast_bp.route('/episodes', methods=['GET'])
def get_episodes():
    """Get podcast episodes with search and filtering"""
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        guest = request.args.get('guest', '').strip()
        tag = request.args.get('tag', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Search episodes
        result = PodcastEpisode.search(
            query=query if query else None,
            guest=guest if guest else None,
            tag=tag if tag else None,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'episodes': [episode.to_dict() for episode in result.items],
            'pagination': {
                'page': result.page,
                'pages': result.pages,
                'per_page': result.per_page,
                'total': result.total,
                'has_next': result.has_next,
                'has_prev': result.has_prev
            },
            'filters': {
                'query': query,
                'guest': guest,
                'tag': tag
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting episodes: {str(e)}")
        return jsonify({'error': 'Failed to fetch episodes'}), 500

@podcast_bp.route('/episodes/<int:episode_id>', methods=['GET'])
def get_episode(episode_id):
    """Get specific episode by ID"""
    try:
        episode = PodcastEpisode.query.get_or_404(episode_id)
        return jsonify(episode.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting episode {episode_id}: {str(e)}")
        return jsonify({'error': 'Episode not found'}), 404

@podcast_bp.route('/guests', methods=['GET'])
def get_guests():
    """Get all unique podcast guests"""
    try:
        guests = PodcastEpisode.get_guests()
        
        # Get episode count for each guest
        guest_stats = []
        for guest in guests:
            episode_count = PodcastEpisode.query.filter(
                PodcastEpisode.guest.ilike(f'%{guest}%')
            ).count()
            guest_stats.append({
                'name': guest,
                'episode_count': episode_count
            })
        
        # Sort by episode count
        guest_stats.sort(key=lambda x: x['episode_count'], reverse=True)
        
        return jsonify({
            'guests': guest_stats,
            'total_guests': len(guest_stats)
        })
        
    except Exception as e:
        logger.error(f"Error getting guests: {str(e)}")
        return jsonify({'error': 'Failed to fetch guests'}), 500

@podcast_bp.route('/tags', methods=['GET'])
def get_tags():
    """Get all unique podcast tags"""
    try:
        tags = PodcastEpisode.get_tags()
        
        # Get episode count for each tag
        tag_stats = []
        for tag in tags:
            episode_count = PodcastEpisode.query.filter(
                PodcastEpisode.tags.ilike(f'%{tag}%')
            ).count()
            tag_stats.append({
                'name': tag,
                'episode_count': episode_count
            })
        
        # Sort by episode count
        tag_stats.sort(key=lambda x: x['episode_count'], reverse=True)
        
        return jsonify({
            'tags': tag_stats,
            'total_tags': len(tag_stats)
        })
        
    except Exception as e:
        logger.error(f"Error getting tags: {str(e)}")
        return jsonify({'error': 'Failed to fetch tags'}), 500

@podcast_bp.route('/stats', methods=['GET'])
def get_podcast_stats():
    """Get podcast statistics"""
    try:
        service = PodcastService()
        stats = service.get_episode_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting podcast stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch podcast stats'}), 500

@podcast_bp.route('/sync', methods=['POST'])
def sync_episodes():
    """Sync episodes from RSS feed"""
    try:
        service = PodcastService()
        result = service.sync_episodes()
        
        # Emit real-time update
        emit('podcast_sync_complete', result, broadcast=True, namespace='/stats')
        
        return jsonify({
            'message': 'Podcast sync completed successfully',
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error syncing episodes: {str(e)}")
        return jsonify({'error': 'Failed to sync episodes'}), 500

# Startup Ideas Routes
@podcast_bp.route('/startup-ideas', methods=['GET'])
def get_startup_ideas():
    """Get startup ideas with search and filtering"""
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        difficulty = request.args.get('difficulty', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Search startup ideas
        result = StartupIdea.search(
            query=query if query else None,
            category=category if category else None,
            difficulty=difficulty if difficulty else None,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'ideas': [idea.to_dict() for idea in result.items],
            'pagination': {
                'page': result.page,
                'pages': result.pages,
                'per_page': result.per_page,
                'total': result.total,
                'has_next': result.has_next,
                'has_prev': result.has_prev
            },
            'filters': {
                'query': query,
                'category': category,
                'difficulty': difficulty
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting startup ideas: {str(e)}")
        return jsonify({'error': 'Failed to fetch startup ideas'}), 500

@podcast_bp.route('/startup-ideas/<int:idea_id>', methods=['GET'])
def get_startup_idea(idea_id):
    """Get specific startup idea by ID"""
    try:
        idea = StartupIdea.query.get_or_404(idea_id)
        return jsonify(idea.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting startup idea {idea_id}: {str(e)}")
        return jsonify({'error': 'Startup idea not found'}), 404

# Twitter/Social Routes
@podcast_bp.route('/tweets', methods=['GET'])
def get_tweets():
    """Get tweets with search and filtering"""
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        hashtag = request.args.get('hashtag', '').strip()
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        
        # Search tweets
        result = Tweet.search(
            query=query if query else None,
            hashtag=hashtag if hashtag else None,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'tweets': [tweet.to_dict() for tweet in result.items],
            'pagination': {
                'page': result.page,
                'pages': result.pages,
                'per_page': result.per_page,
                'total': result.total,
                'has_next': result.has_next,
                'has_prev': result.has_prev
            },
            'filters': {
                'query': query,
                'hashtag': hashtag
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting tweets: {str(e)}")
        return jsonify({'error': 'Failed to fetch tweets'}), 500

@podcast_bp.route('/tweets/<int:tweet_id>', methods=['GET'])
def get_tweet(tweet_id):
    """Get specific tweet by ID"""
    try:
        tweet = Tweet.query.get_or_404(tweet_id)
        return jsonify(tweet.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting tweet {tweet_id}: {str(e)}")
        return jsonify({'error': 'Tweet not found'}), 404

# Cross-content search
@podcast_bp.route('/search/all', methods=['GET'])
def search_all_content():
    """Search across all content types"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        
        # Search across all content types
        episodes = PodcastEpisode.search(query=query, page=1, per_page=per_page)
        ideas = StartupIdea.search(query=query, page=1, per_page=per_page)
        tweets = Tweet.search(query=query, page=1, per_page=per_page)
        
        # Also search videos (assuming video model exists)
        from ..models.video import Video
        videos = Video.search(query=query, page=1, per_page=per_page)
        
        return jsonify({
            'query': query,
            'results': {
                'episodes': {
                    'items': [episode.to_dict() for episode in episodes.items],
                    'total': episodes.total
                },
                'videos': {
                    'items': [video.to_dict() for video in videos.items],
                    'total': videos.total
                },
                'startup_ideas': {
                    'items': [idea.to_dict() for idea in ideas.items],
                    'total': ideas.total
                },
                'tweets': {
                    'items': [tweet.to_dict() for tweet in tweets.items],
                    'total': tweets.total
                }
            },
            'total_results': episodes.total + videos.total + ideas.total + tweets.total
        })
        
    except Exception as e:
        logger.error(f"Error searching all content: {str(e)}")
        return jsonify({'error': 'Failed to search content'}), 500

