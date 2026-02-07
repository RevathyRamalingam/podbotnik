# 🎙️ Podbotnik - Podcast Chatbot

A **RAG-powered chatbot** that allows visitors to ask natural-language questions about podcast episodes and receive **concise, timestamped answers** with **direct links** to the exact moment in the audio/video.

## Features

✨ **Smart Retrieval (RAG)**
- Uses `minsearch` for fast, lightweight retrieval (no vector DB needed!)
- Finds relevant transcript segments based on semantic similarity

🤖 **LLM-Powered Answers**
- Integrates with **Groq API** for fast inference (free tier available)
- Generates concise, contextual answers

⏱️ **Timestamped Responses**
- Automatically includes timestamps for relevant segments
- Generates direct links to YouTube, Spotify, or custom media players
- Example: `https://youtube.com/watch?v=VIDEO_ID&t=120` (jumps to 2:00)

🌐 **Multiple Interfaces**
- **CLI**: Interactive command-line interface
- **Web UI**: Beautiful, responsive web interface (FastAPI)
- **Web UI**: Beautiful, responsive web interface (Streamlit)
- **REST API**: Full REST API with interactive Swagger documentation
- **Python API**: Use programmatically in your own code

📊 **Flexible Transcript Format**
- JSON for easy transcript management
- Support for episode metadata (URLs, numbers, titles)
- Works with any podcast

## Architecture

```
Podcast Chatbot Architecture
├── Transcripts (JSON)
│   └── Load via minsearch Index
│
├── Retrieval (minsearch)
│   ├── Indexes transcript content
│   └── Finds top-K relevant segments
│
├── RAG Pipeline
│   ├── Retrieve relevant segments
│   └── Build context for LLM
│
└── LLM (Groq API)
    ├── Generate answer from context
    └── Format with timestamps & links
```

## Installation

### Prerequisites
- Python 3.8+
- Groq API key (free tier at https://console.groq.com)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd podbotnik

# Install dependencies (includes FastAPI & uvicorn)
# Install dependencies (includes Streamlit for web UI)
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Get your free Groq API key:
1. Visit https://console.groq.com
2. Sign up (free tier available)
3. Generate an API key
4. Add it to your `.env` file

## Quick Start

### Option 1: Command-Line Chat

```bash
# Interactive chat with sample transcripts
python cli.py chat --transcripts sample_transcripts.json

# Or ask a single question
python cli.py ask sample_transcripts.json "What is machine learning?"

# List all episodes
python cli.py list-episodes sample_transcripts.json
```

### Option 2: Web Interface


```bash
# Start the Streamlit web interface
streamlit run web.py
# Or with custom port: streamlit run web.py --server.port 5000
# Open browser to http://localhost:8501 (default Streamlit port)
```python
from chatbot import PodcastChatbot

# Initialize
chatbot = PodcastChatbot()
chatbot.load_transcripts("sample_transcripts.json")

# Ask a question
result = chatbot.answer_question("What is machine learning?")

print(result["answer"])
# Prints the generated answer

for source in result["sources"]:
    print(f"Episode: {source['episode']}")
    print(f"Timestamp: {source['timestamp']}")
    print(f"Watch: {source['video_link']}")
```

## Preparing Your Transcripts

### Transcript JSON Format

Organize your podcast transcripts as JSON:

```json
[
  {
    "episode_id": "ep001",
    "episode_title": "Introduction to AI",
    "episode_number": 1,
    "transcript": "Full episode transcript text here...",
    "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "audio_url": "https://example.com/podcast/ep001.mp3"
  },
  {
    "episode_id": "ep002",
    "episode_title": "Deep Learning Basics",
    "episode_number": 2,
    "transcript": "More transcript text...",
    "video_url": "https://youtube.com/watch?v=...",
    "audio_url": "https://example.com/podcast/ep002.mp3"
  }
]
```

### Auto-Generate Transcripts

You can use services like:
- **Rev.com** - Manual or AI transcription
- **Descript** - AI-powered with timestamps
- **AssemblyAI** - Accurate AI transcription API
- **OpenAI Whisper** - Free, open-source speech-to-text

Example using Whisper:
```python
import json
from openai import OpenAI

client = OpenAI()

with open("episode.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f
    )

print(transcript.text)
```

## API Reference

### `PodcastChatbot` Class

```python
from chatbot import PodcastChatbot

# Initialize
chatbot = PodcastChatbot(api_key="your_groq_key")

# Load transcripts
chatbot.load_transcripts("transcripts.json")

# Add single transcript
chatbot.add_transcript(
    episode_id="ep001",
    episode_title="Episode Title",
    episode_number=1,
    transcript_text="...",
    video_url="https://...",
    audio_url="https://..."
)

# Ask a question
result = chatbot.answer_question(
    question="Your question here",
    max_context_segments=3  # Number of relevant segments to use
)

# Result contains:
# {
#   "answer": "Generated answer text",
#   "sources": [
#     {
#       "episode": "Episode Title",
#       "episode_number": 1,
#       "timestamp": "05:32",
#       "segment": "Relevant text excerpt...",
#       "video_link": "https://youtube.com/watch?v=...&t=332",
#       "audio_link": "https://example.com/podcast/ep001.mp3#t=332"
#     }
#   ],
#   "context_used": 3
# }

# List episodes
episodes = chatbot.list_episodes()
```

### Direct Transcript Search

```python
from chatbot import PodcastChatbot

chatbot = PodcastChatbot()
chatbot.load_transcripts("transcripts.json")

# Search the transcript index
results = chatbot.index.search(
    query="machine learning",
    fields=["episode_title", "text"],
    max_results=5
)

# Get a specific episode
episodes = chatbot.list_episodes()
episode = episodes.get("ep001")
```

## Examples

### Example 1: Simple Question Answering

```bash
python cli.py ask sample_transcripts.json "What are neural networks?"
```

Output:
```
❓ Question: What are neural networks?

🤖 Answer:
Neural networks are computational systems inspired by biological neurons. They consist of interconnected nodes organized in layers with weights that adjust during training. The backpropagation algorithm is crucial for training them efficiently.

📍 Sources:

  [1] Episode #2: Deep Dive into Neural Networks
      Timestamp: 00:15
      "Neural networks are computational systems inspired by biological neurons found in animal brains..."
      🎬 https://youtube.com/watch?v=dQw4w9WgXcQ&t=15
```

### Example 2: Interactive Mode

```bash
python cli.py chat --transcripts sample_transcripts.json
```

```
✓ Ready! Loaded 4 episode(s):

  #1: Introduction to Machine Learning
  #2: Deep Dive into Neural Networks
  #3: Data Engineering Best Practices
  #4: Deploying ML Models to Production

💬 Interactive mode (type 'quit' to exit, 'list' to show episodes)

You: How do I deploy ML models?

🤔 Thinking...

🤖 Assistant:
Deploying models to production requires containerization with Docker, orchestration with Kubernetes, and CI/CD pipelines for automated testing. You should establish monitoring to detect performance degradation and use A/B testing before full rollout.

📍 Sources:

  [1] Episode #4: Deploying ML Models to Production
      Timestamp: 01:45
      "Model serialization using formats like ONNX, SavedModel, or pickle is the first step. Container technologies like Docker..."
      🎬 https://youtube.com/watch?v=dQw4w9WgXcQ&t=105
      🎙️ https://example.com/podcast/ep004.mp3#t=105

You: quit
```

### Example 3: Programmatic Usage

```python
from chatbot import PodcastChatbot

# Initialize
chatbot = PodcastChatbot()
chatbot.load_transcripts("sample_transcripts.json")

# Multiple questions
questions = [
    "What is supervised learning?",
    "Explain transformers",
    "What is MLOps?"
]

for q in questions:
    result = chatbot.answer_question(q, max_context_segments=2)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

## Web Interface

Start the web server:
```bash
python web.py sample_transcripts.json 5000
```

Features:
- 🎨 Beautiful, responsive design
- 💬 Real-time chat interface
- 📍 Clickable source links with timestamps
- 📱 Mobile-friendly
- ⚡ Fast responses with Groq API

## Customization
- 📚 Interactive API documentation at `/docs` and `/redoc`

### Change LLM Model

```python
from llm import GroqLLM

# Use a different model
llm = GroqLLM(model="llama2-70b-4096")
# Available models: mixtral-8x7b-32768, llama2-70b-4096, etc.
```

### Adjust Answer Length

```python
result = chatbot.answer_question(
    question="...",
    max_context_segments=5  # Use more context for longer answers
)
```

### Custom Timestamp Links

Modify the `_build_timestamp_link` method in `chatbot.py` to support additional platforms:

```python
def _build_timestamp_link(self, url: str, time_str: str) -> str:
    # YouTube
    if "youtube.com" in url:
        return f"{url}&t={seconds}"
    # Spotify
    elif "spotify.com" in url:
        return f"{url}#t={seconds}"
    # Custom platform
    elif "custom.com" in url:
        return f"{url}?start={seconds}"
    return url
```

## Performance Tips

1. **Batch Questions** - Process multiple questions in one session to avoid initialization overhead
2. **Optimize Transcripts** - Remove filler words or non-relevant sections to improve retrieval
3. **Adjust max_context_segments** - Use fewer segments (2-3) for faster responses, more (5+) for better accuracy
4. **Use Groq's Free Tier** - Extremely generous rate limits for this use case

## Troubleshooting

### "GROQ_API_KEY not provided"
```bash
# Make sure .env file exists and has your key
cat .env
# Should show: GROQ_API_KEY=your_actual_key

# Or set environment variable
export GROQ_API_KEY=your_key
```

### Module not found errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version (3.8+ required)
python --version
```

### Slow responses
- Reduce `max_context_segments` parameter
- Check your internet connection (Groq API calls)
- Ensure Groq API key is valid

### Poor answer quality
- Check transcript quality and completeness
- Use more `max_context_segments` for better context
- Rephrase your question to match transcript language

## Project Structure

```
podbotnik/
├── chatbot.py              # Main RAG chatbot
├── transcripts.py          # Transcript management & retrieval
├── llm.py                  # Groq LLM integration
├── cli.py                  # Command-line interface
├── web.py                  # Web UI (FastAPI)
├── web.py                  # Web UI (Streamlit)
├── example.py              # Example usage
├── sample_transcripts.json  # Sample data
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Stack

- **Retrieval**: [minsearch](https://github.com/alexmolas/minsearch) - Lightweight, fast BM25
- **LLM**: [Groq API](https://console.groq.com) - Free tier, extremely fast inference
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast, with auto-generated API docs
- **Web Framework**: [Streamlit](https://streamlit.io/) for web UI, [FastAPI](https://fastapi.tiangolo.com/) for REST API
- **Server**: [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server
- **Language**: Python 3.8+

## Why This Tech Stack?

| Component | Why? |
|-----------|------|
| minsearch | No external dependencies, BM25 is effective for text retrieval, instant setup |
| GastAPI | Modern Python framework, auto-generates API documentation, async support, very fast |
| Uvicorn | Lightning-fast ASGI server, minimal overhead, excellent performancec), no rate limit issues |
| Flask | Lightweight, perfect for simple UI, minimal overhead |
| Plain APIs | No heavy frameworks (no LangChain, no complex agents), easy to understand & modify |

## Cost

- **Groq API**: Free tier covers typical usage (generous limits)
- **Transcription**: 
  - Whisper API: $0.02/min
  - Rev.com: $1.25/min (manual), $0.25/min (AI)
  - Descript: Free (limited)
  - AssemblyAI: $0.00005/sec (~$0.18/minute)

**Total cost for running a podcast chatbot**: Essentially free if using Groq's free tier!

## Future Enhancements

- [ ] Vector embeddings with FAISS for semantic search
- [ ] Multi-modal support (images, timestamps with visuals)
- [ ] Conversation memory (multi-turn conversations)
- [ ] Analytics dashboard (popular questions, user engagement)
- [ ] Integration with podcast platforms (Apple Podcasts API, Spotify API)
- [ ] WebSocket support for real-time streaming responses
- [ ] Fine-tuning on specific podcast content

## Contributing

Contributions welcome! Areas to improve:
- Better transcript formatting
- Support for more media platforms
- Improved timestamp accuracy
- Frontend enhancements
- Performance optimizations

## License

MIT License - Feel free to use for your projects!

## Support

- 📖 Check examples: `example.py`
- 💬 Try the CLI: `python cli.py chat --help`
- 🌐 Use the web UI: `python web.py`
- 🐛 File issues on GitHub

---

Made with ❤️ for podcast lovers and developers
