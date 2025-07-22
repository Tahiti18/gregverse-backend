from flask import Blueprint, request, jsonify
from src.models.video import Video, db
from datetime import datetime
import time

search_bp = Blueprint('search', __name__)

@search_bp.route('/videos', methods=['POST'])
def search_videos():
    """Search videos with full-text search and filtering"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        category = data.get('category', 'all')
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 20))
        
        # Log search for analytics
        start_time = time.time()
        
        # Perform search
        pagination = Video.search(
            query=query,
            category=category if category != 'all' else None,
            page=page,
            per_page=per_page
        )
        
        # Calculate search time
        search_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        # Format results
        results = [video.to_dict() for video in pagination.items]
        
        response_data = {
            'success': True,
            'results': results,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'meta': {
                'query': query,
                'category': category,
                'search_time_ms': search_time,
                'results_count': len(results)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'error': True,
            'message': 'Search temporarily unavailable',
            'fallback_data': [],
            'retry_after': 30,
            'error_code': 'SEARCH_ERROR'
        }), 500

@search_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Get autocomplete suggestions for search"""
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 10))
        
        if len(query) < 2:
            return jsonify({'suggestions': []})
        
        suggestions = Video.get_autocomplete_suggestions(query, limit)
        
        return jsonify({
            'suggestions': suggestions,
            'query': query
        })
        
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return jsonify({
            'suggestions': [],
            'error': 'Autocomplete temporarily unavailable'
        })

@search_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available video categories"""
    try:
        categories = Video.get_categories()
        
        # Add counts for each category
        category_counts = []
        for category in categories:
            count = Video.query.filter_by(category=category).count()
            category_counts.append({
                'name': category,
                'count': count,
                'slug': category.lower().replace(' ', '-')
            })
        
        # Sort by count descending
        category_counts.sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'categories': category_counts,
            'total_categories': len(category_counts)
        })
        
    except Exception as e:
        print(f"Categories error: {e}")
        return jsonify({
            'error': True,
            'message': 'Categories temporarily unavailable',
            'categories': []
        }), 500

@search_bp.route('/trending', methods=['GET'])
def get_trending_searches():
    """Get trending search queries (placeholder for future analytics)"""
    try:
        # For now, return popular categories as trending
        trending = [
            'AI tools',
            'startup ideas',
            'no-code business',
            'ChatGPT',
            'entrepreneur tips',
            'business automation',
            'SaaS ideas',
            'marketing strategies'
        ]
        
        return jsonify({
            'trending': trending,
            'updated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'trending': [],
            'error': 'Trending data unavailable'
        })

@search_bp.route('/stats', methods=['GET'])
def search_stats():
    """Get search statistics"""
    try:
        total_videos = Video.query.count()
        categories = Video.get_categories()
        
        return jsonify({
            'total_videos': total_videos,
            'total_categories': len(categories),
            'searchable_content': 'videos, titles, descriptions',
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': True,
            'message': 'Stats unavailable'
        }), 500

