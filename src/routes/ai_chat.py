from flask import Blueprint, request, jsonify
from ..services.ai_chat_service import AIChatService
import logging

logger = logging.getLogger(__name__)
ai_chat_bp = Blueprint('ai_chat', __name__)

@ai_chat_bp.route('/ask', methods=['POST'])
def ask_question():
    """Ask a question to the AI chat system"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Question is required'}), 400
        
        question = data.get('question').strip()
        user_id = data.get('user_id')
        
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get answer from AI chat service
        service = AIChatService()
        result = service.ask_question(question, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({
            'error': 'Failed to process question',
            'answer': 'Sorry, I encountered an error while processing your question. Please try again.',
            'sources': []
        }), 500

@ai_chat_bp.route('/index', methods=['POST'])
def index_content():
    """Index content for vector search"""
    try:
        data = request.get_json() or {}
        force_reindex = data.get('force_reindex', False)
        
        # Index content
        service = AIChatService()
        result = service.index_content(force_reindex)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error indexing content: {str(e)}")
        return jsonify({'error': 'Failed to index content'}), 500

@ai_chat_bp.route('/stats', methods=['GET'])
def get_chat_stats():
    """Get chat service statistics"""
    try:
        service = AIChatService()
        stats = service.get_chat_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting chat stats: {str(e)}")
        return jsonify({'error': 'Failed to get chat stats'}), 500

