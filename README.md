# LangChain Chat with Redis Memory

A simple conversational AI chatbot with persistent Redis memory management, powered by LangChain.
<img width="1439" height="730" alt="Screenshot 2026-02-01 at 10 32 49 PM" src="https://github.com/user-attachments/assets/dfc82f22-649f-48ae-b036-885c460efee5" />

## Features

- **Persistent Storage**: Redis-backed chat history across sessions
- **TTL Management**: Automatic cleanup with configurable time-to-live
- **Fast Retrieval**: Sub-millisecond latency for chat operations
- **Streamlit UI**: Simple web interface
- **Session Support**: Multiple independent chat sessions

## Quick Start

### 1. Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:latest
```

### 2. Setup Project

```bash
# Clone repository
git clone <repo-url>
cd langchain-chat-with-memory

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run the App

```bash
# Run Streamlit UI
streamlit run src/app.py

# Run CLI
python src/main_redis.py
```

## Architecture   
<img width="428" height="804" alt="image" src="https://github.com/user-attachments/assets/b52cbcc9-7615-4c7d-849b-985871128526" />

## Configuration

Set these environment variables in `.env`:

```
OPENROUTER_API_KEY=your_api_key
REDIS_URL=redis://localhost:6379
DEFAULT_MODEL=openrouter_model_name
DEFAULT_TTL_HOURS=24
```

## Environment Variables

- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379`)
- `OPENROUTER_API_KEY`: API key for LLM (required)
- `DEFAULT_TTL_HOURS`: TTL for Redis keys in hours (default: 24)
