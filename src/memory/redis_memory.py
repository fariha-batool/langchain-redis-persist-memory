"""Redis-based persistent chat memory with LangChain."""

from typing import Optional
from langchain_redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.config import settings


class RedisMemoryChat:
    """Chat with Redis-backed persistent memory."""
    
    def __init__(
        self,
        model_name: str = "openai/gpt-oss-120b:free",
        redis_url: str = settings.redis_url,
        ttl: Optional[int] = None,  # None = never expire
        key_prefix: str = "chat:"
    ):
        """Initialize Redis memory chat.
        
        Args:
            model_name: LLM model to use
            redis_url: Redis connection string
            ttl: Time-to-live in seconds (None for no expiration)
            key_prefix: Redis key prefix for isolation
        """
        self.model = ChatOpenAI(model=model_name, 
                                api_key=settings.openrouter_api_key,
                                base_url="https://openrouter.ai/api/v1",
                                temperature=0.7)
        self.redis_url = redis_url
        self.ttl = ttl
        self.key_prefix = key_prefix
        
        # Setup prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with persistent memory.
            You remember previous conversations even across sessions.
            Reference past discussions naturally when relevant."""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        # Create chain
        chain = prompt | self.model
        
        # Wrap with Redis message history
        self.chain_with_history = RunnableWithMessageHistory(
            chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )
    
    def _get_session_history(self, session_id: str) -> RedisChatMessageHistory:
        """Get or create Redis session history."""
        return RedisChatMessageHistory(
            session_id=session_id,
            redis_url=self.redis_url,
            key_prefix=self.key_prefix,
            ttl=self.ttl
        )
    
    def chat(self, message: str, session_id: str = "default") -> str:
        """Send message and get response with Redis persistence."""
        response = self.chain_with_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
        return response.content
    
    def search_history(self, session_id: str, query: str, limit: int = 5) -> list:
        """Search conversation history using Redis search."""
        history = self._get_session_history(session_id)
        if hasattr(history, 'search'):
            results = history.search(query, limit=limit)
            return results
        return []
    
    def clear_session(self, session_id: str) -> None:
        """Clear specific session history."""
        history = self._get_session_history(session_id)
        history.clear()
    
    def get_message_count(self, session_id: str) -> int:
        """Get number of messages in session."""
        history = self._get_session_history(session_id)
        return len(history.messages)
