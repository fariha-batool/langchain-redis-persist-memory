import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.memory.redis_memory import RedisMemoryChat

# Initialize with 24-hour TTL
chat = RedisMemoryChat(
    redis_url="redis://192.168.0.101:6379/0",
    ttl=86400  # 24 hours
)

# Day 1
chat.chat("My name is Alex", session_id="user_123")
chat.chat("I love Python programming", session_id="user_123")

# Restart application...

# Day 2 - memory persists!
response = chat.chat("What's my name?", session_id="user_123")

