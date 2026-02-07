# Project Overview & File Reference

## Quick Reference

### Core Files

| File | Purpose |
|------|---------|
| `chatbot.py` | Main RAG chatbot engine |
| `transcripts.py` | Transcript management & BM25 retrieval |
| `llm.py` | Groq LLM integration |

### Interfaces

| File | Purpose | Usage |
|------|---------|-------|
| `cli.py` | Command-line interface | `python cli.py --help` |
| `web.py` | FastAPI web UI with HTML | `python web.py sample_transcripts.json 5000` |
| `web.py` | Streamlit web UI | `streamlit run web.py` |
| `api.py` | FastAPI REST API | `python api.py --reload` |

### Utilities

| File | Purpose | Usage |
|------|---------|-------|
| `transcript_generator.py` | Generate transcripts from audio | `python transcript_generator.py --help` |
| `setup.py` | Initial setup & verification | `python setup.py` |
| `test.py` | Test suite | `python test.py` |
| `example.py` | Example usage | `python example.py` |

### Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment template |
| `.gitignore` | Git ignore rules |
| `Dockerfile` | Docker containerization |
| `docker-compose.yml` | Docker Compose setup |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Full documentation & API reference |
| `GETTING_STARTED.md` | Quick start guide |

### Data

| File | Purpose |
|------|---------|
| `sample_transcripts.json` | Sample podcast episodes for testing |

## Data Flow

```
User Question
    ↓
[CLI/Web/API]
    ↓
minsearch.Index.search()  ← minsearch (BM25 retrieval)
    ↓
Top-K Relevant Segments
    ↓
Build Context
    ↓
GroqLLM.generate_answer()   ← Groq API call
    ↓
Answer + Sources + Timestamps
    ↓
Rendered Response
```

## Architecture

### PodcastChatbot (`chatbot.py`)
- **Transcript Index**: minsearch Index for fast BM25 retrieval
- **Storage**: Dictionary of episodes with metadata
- **Search**: Uses `index.search()` to find relevant segments
- **Pipeline**:
  1. Search transcript index for relevant segments
  2. Build context from segments
  3. Generate answer via Groq LLM
  4. Format with timestamps & links
- **Public Methods**:
  - `load_transcripts(file_path)` - Load transcripts from JSON file
  - `answer_question(question, max_context_segments=3)` - Main RAG pipeline
  - `list_episodes()` - List all loaded episodes

### GroqLLM (`llm.py`)
- **Client**: Groq API client
- **Model**: mixtral-8x7b-32768 (default, configurable)
- **Methods**:
  - `generate()` - Generic LLM calls
  - `generate_answer()` - Question answering with context

## Usage Patterns

### Pattern 1: Single Question (Simple)
```python
from chatbot import PodcastChatbot

chatbot = PodcastChatbot()
chatbot.load_transcripts("transcripts.json")
result = chatbot.answer_question("Your question?")
print(result["answer"])
```

### Pattern 2: Batch Processing (Efficient)
```python
from chatbot import PodcastChatbot

chatbot = PodcastChatbot()
chatbot.load_transcripts("transcripts.json")

for question in questions_list:
    result = chatbot.answer_question(question)
    # process result
```

### Pattern 3: Direct Search (No LLM)
```python
from chatbot import PodcastChatbot

chatbot = PodcastChatbot()
chatbot.load_transcripts("transcripts.json")
results = chatbot.index.search(
    query="machine learning",
    fields=["episode_title", "text"],
    max_results=5
)
# results contain raw segments
```

### Pattern 4: Custom LLM
```python
from llm import GroqLLM

llm = GroqLLM(model="llama2-70b-4096")
answer = llm.generate(prompt)
```

## Performance Metrics

- **Retrieval**: ~10-100ms (minsearch BM25)
- **LLM Generation**: ~1-3 seconds (Groq API)
- **Total latency**: ~2-4 seconds typically
- **Memory**: ~50MB base + transcript size
- **Cost**: Free (Groq free tier very generous)

## Deployment Options

### Local Development
```bash
python cli.py chat --transcripts transcripts.json
python example.py
```

### Web Server (FastAPI)
### Web Server (Streamlit)
```bash
streamlit run web.py
# Open http://localhost:8501
```

### REST API Server (FastAPI)
```bash
python api.py
# Open http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Docker Container
```bash
docker build -t podbotnik .
docker run -p 5000:5000 -e GROQ_API_KEY=... podbotnik
```

### Docker Compose
```bash
docker-compose up
```

## Configuration

### Environment Variables
```bash
GROQ_API_KEY=gsk_...           # Required: Groq API key
PODCAST_NAME=My Podcast        # Optional: For branding
PODCAST_PLATFORM=https://...   # Optional: Base URL
```

### Model Selection
```python
## in llm.py
self.model = "mixtral-8x7b-32768"  # Default
# Alternative: llama2-70b-4096
```

### Answer Customization
```python
# Max context segments (default 3)
result = chatbot.answer_question(question, max_context_segments=5)

# Temperature (0-2, higher = more creative)
llm.generate(prompt, temperature=0.7)

# Max tokens
llm.generate(prompt, max_tokens=400)
```

## Extension Points

### Add Custom Retrieval
1. Modify `chatbot.index` (minsearch.Index) with custom fields
2. Or: Create new retriever that implements `search()` interface returning list of docs

### Add Vector Search
```python
# Replace minsearch with FAISS
from faiss import Index
self.vector_index = Index(...)
```

### Support New Media Platforms
```python
# Edit `_build_timestamp_link()` in chatbot.py
elif "twitch.tv" in url:
    return f"{url}?t={total_seconds}s"
```

### Add Conversation Memory
```python
# Extend PodcastChatbot class
class ChatbotWithMemory(PodcastChatbot):
    def __init__(self):
        super().__init__()
        self.conversation_history = []
```

## Testing

Run full test suite:
```bash
python test.py
```

Run specific tests:
```python
# In Python
from test import test_imports, test_sample_transcripts
test_imports()  # ✅ or ❌
test_sample_transcripts()
```

## Troubleshooting Checklist

- [ ] Python 3.8+: `python --version`
- [ ] Dependencies: `pip install -r requirements.txt`
- [ ] Groq API key: Check `.env` file
- [ ] Network: Can reach `api.groq.com`
- [ ] Sample file: `ls sample_transcripts.json`
- [ ] Tests pass: `python test.py`

## Size & Performance

| Metric | Value |
|--------|-------|
| Code size | ~2KB (core logic) |
| Startup time | <1s |
| Query latency | 2-4s (network bound) |
| Memory usage | ~50MB base + data |
| Max transcripts | Unlimited (memory limited) |

## Future Enhancements

```
Priority 1 (Easy):
- [ ] Multi-language support
- [ ] Custom timestamp formats
- [ ] Conversation history

Priority 2 (Medium):
- [ ] Vector embeddings (FAISS)
- [ ] Conversation memory
- [ ] Analytics dashboard

Priority 3 (Hard):
- [ ] Real-time streaming
- [ ] Multi-modal (video + text)
- [ ] Podcast platform APIs
```

---

For more details, see:
- `README.md` - Full documentation
- `GETTING_STARTED.md` - Quick start guide
- `example.py` - Code examples
