import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib
import json

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# Pinecone imports
import pinecone

# Local imports
from ..models.video import Video
from ..models.podcast import PodcastEpisode, StartupIdea, Tweet
from ..config import Config

logger = logging.getLogger(__name__)

class AIChatService:
    def __init__(self):
        self.config = Config()
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Pinecone and LangChain services"""
        try:
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
            
            # Initialize Pinecone
            pinecone.init(
                api_key=os.getenv('PINECONE_API_KEY'),
                environment=os.getenv('PINECONE_ENVIRONMENT', 'us-west1-gcp-free')
            )
            
            # Connect to Pinecone index
            index_name = os.getenv('PINECONE_INDEX_NAME', 'gregverse')
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric='cosine'
                )
            
            # Initialize vector store
            self.vectorstore = LangchainPinecone.from_existing_index(
                index_name=index_name,
                embedding=self.embeddings
            )
            
            # Initialize QA chain
            self._setup_qa_chain()
            
            logger.info("AI Chat Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Chat Service: {str(e)}")
            raise
    
    def _setup_qa_chain(self):
        """Setup the QA chain with custom prompt"""
        prompt_template = """You are GregQ, an AI assistant that helps people learn from Greg Isenberg's content and expertise. Greg is an entrepreneur, investor, and content creator known for his insights on startups, community building, and business strategy.

Use the following pieces of context from Greg's content to answer the question. If you don't know the answer based on the provided context, just say that you don't have enough information to answer that question.

Always cite your sources by mentioning the specific video, podcast episode, or content piece where the information came from.

Context:
{context}

Question: {question}

Answer with source citations:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(
                temperature=0.7,
                openai_api_key=os.getenv('OPENAI_API_KEY')
            ),
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 5}  # Return top 5 most relevant chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def ask_question(self, question: str, user_id: Optional[str] = None) -> Dict:
        """Ask a question and get an answer with sources"""
        try:
            if not self.qa_chain:
                return {
                    'error': 'AI Chat service not properly initialized',
                    'answer': 'Sorry, the AI chat service is currently unavailable.',
                    'sources': []
                }
            
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            # Process source documents
            sources = self._process_sources(result.get('source_documents', []))
            
            # Log the interaction
            self._log_interaction(question, result['result'], sources, user_id)
            
            return {
                'question': question,
                'answer': result['result'],
                'sources': sources,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return {
                'error': str(e),
                'answer': 'Sorry, I encountered an error while processing your question. Please try again.',
                'sources': []
            }
    
    def _process_sources(self, source_docs: List[Document]) -> List[Dict]:
        """Process source documents into structured format"""
        sources = []
        
        for doc in source_docs:
            metadata = doc.metadata
            source_info = {
                'content_type': metadata.get('content_type', 'unknown'),
                'title': metadata.get('title', 'Unknown Title'),
                'url': metadata.get('url', ''),
                'excerpt': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content
            }
            
            # Add type-specific information
            if metadata.get('content_type') == 'video':
                source_info.update({
                    'channel': metadata.get('channel', 'Greg Isenberg'),
                    'published_at': metadata.get('published_at', ''),
                    'view_count': metadata.get('view_count', 0)
                })
            elif metadata.get('content_type') == 'podcast':
                source_info.update({
                    'guest': metadata.get('guest', ''),
                    'episode_number': metadata.get('episode_number', ''),
                    'published_at': metadata.get('published_at', '')
                })
            elif metadata.get('content_type') == 'startup_idea':
                source_info.update({
                    'category': metadata.get('category', ''),
                    'difficulty': metadata.get('difficulty', '')
                })
            
            sources.append(source_info)
        
        return sources
    
    def _log_interaction(self, question: str, answer: str, sources: List[Dict], user_id: Optional[str]):
        """Log chat interaction for analytics"""
        try:
            interaction = {
                'question': question,
                'answer': answer,
                'sources_count': len(sources),
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # In production, you might want to store this in a database
            logger.info(f"Chat interaction logged: {json.dumps(interaction)}")
            
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
    
    def index_content(self, force_reindex: bool = False) -> Dict:
        """Index all content for vector search"""
        try:
            if not force_reindex and self._is_index_current():
                return {
                    'message': 'Index is current, no reindexing needed',
                    'indexed_count': 0
                }
            
            documents = []
            
            # Index videos
            videos = Video.query.all()
            for video in videos:
                docs = self._create_video_documents(video)
                documents.extend(docs)
            
            # Index podcast episodes
            episodes = PodcastEpisode.query.all()
            for episode in episodes:
                docs = self._create_podcast_documents(episode)
                documents.extend(docs)
            
            # Index startup ideas
            ideas = StartupIdea.query.all()
            for idea in ideas:
                docs = self._create_startup_idea_documents(idea)
                documents.extend(docs)
            
            # Index tweets
            tweets = Tweet.query.all()
            for tweet in tweets:
                docs = self._create_tweet_documents(tweet)
                documents.extend(docs)
            
            # Add documents to vector store
            if documents:
                self.vectorstore.add_documents(documents)
                self._update_index_timestamp()
            
            logger.info(f"Successfully indexed {len(documents)} documents")
            
            return {
                'message': 'Content indexed successfully',
                'indexed_count': len(documents)
            }
            
        except Exception as e:
            logger.error(f"Error indexing content: {str(e)}")
            raise
    
    def _create_video_documents(self, video) -> List[Document]:
        """Create documents from video content"""
        documents = []
        
        # Main video document
        content = f"Title: {video.title}\n\nDescription: {video.description}"
        if video.transcript:
            content += f"\n\nTranscript: {video.transcript}"
        
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        for i, chunk in enumerate(chunks):
            metadata = {
                'content_type': 'video',
                'video_id': video.video_id,
                'title': video.title,
                'url': f"https://youtube.com/watch?v={video.video_id}",
                'channel': video.channel_title,
                'published_at': video.published_at.isoformat() if video.published_at else '',
                'view_count': video.view_count or 0,
                'chunk_index': i
            }
            
            documents.append(Document(
                page_content=chunk,
                metadata=metadata
            ))
        
        return documents
    
    def _create_podcast_documents(self, episode) -> List[Document]:
        """Create documents from podcast episode"""
        documents = []
        
        content = f"Title: {episode.title}\n\nDescription: {episode.description}"
        if episode.guest:
            content += f"\n\nGuest: {episode.guest}"
        if episode.transcript:
            content += f"\n\nTranscript: {episode.transcript}"
        
        chunks = self.text_splitter.split_text(content)
        
        for i, chunk in enumerate(chunks):
            metadata = {
                'content_type': 'podcast',
                'episode_id': episode.id,
                'title': episode.title,
                'url': episode.spotify_url or episode.apple_url or '',
                'guest': episode.guest or '',
                'episode_number': episode.episode_number,
                'published_at': episode.published_at.isoformat() if episode.published_at else '',
                'chunk_index': i
            }
            
            documents.append(Document(
                page_content=chunk,
                metadata=metadata
            ))
        
        return documents
    
    def _create_startup_idea_documents(self, idea) -> List[Document]:
        """Create documents from startup idea"""
        content = f"Startup Idea: {idea.title}\n\nDescription: {idea.description}"
        if idea.category:
            content += f"\n\nCategory: {idea.category}"
        
        metadata = {
            'content_type': 'startup_idea',
            'idea_id': idea.id,
            'title': idea.title,
            'url': idea.source_url or '',
            'category': idea.category or '',
            'difficulty': idea.difficulty or '',
            'market_size': idea.market_size or ''
        }
        
        return [Document(page_content=content, metadata=metadata)]
    
    def _create_tweet_documents(self, tweet) -> List[Document]:
        """Create documents from tweet"""
        content = f"Tweet: {tweet.content}"
        
        metadata = {
            'content_type': 'tweet',
            'tweet_id': tweet.tweet_id,
            'title': f"Tweet by {tweet.author}",
            'url': tweet.url or '',
            'author': tweet.author,
            'published_at': tweet.published_at.isoformat() if tweet.published_at else '',
            'like_count': tweet.like_count or 0
        }
        
        return [Document(page_content=content, metadata=metadata)]
    
    def _is_index_current(self) -> bool:
        """Check if the index is current"""
        # In production, you'd check against a timestamp stored in database
        # For now, return False to always allow reindexing
        return False
    
    def _update_index_timestamp(self):
        """Update the index timestamp"""
        # In production, store this timestamp in database
        pass
    
    def get_chat_stats(self) -> Dict:
        """Get chat service statistics"""
        try:
            # Get index stats
            index_name = os.getenv('PINECONE_INDEX_NAME', 'gregverse')
            index = pinecone.Index(index_name)
            stats = index.describe_index_stats()
            
            return {
                'total_vectors': stats.get('total_vector_count', 0),
                'index_fullness': stats.get('index_fullness', 0),
                'dimension': stats.get('dimension', 1536),
                'status': 'active' if self.qa_chain else 'inactive'
            }
            
        except Exception as e:
            logger.error(f"Error getting chat stats: {str(e)}")
            return {
                'total_vectors': 0,
                'index_fullness': 0,
                'dimension': 1536,
                'status': 'error'
            }

