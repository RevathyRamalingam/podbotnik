# Getting Started Guide - Podbotnik

Welcome to **Podbotnik**, a podcast chatbot powered by RAG (Retrieval-Augmented Generation)!

## Table of Contents

1. [Installation](#installation)
2. [First Run](#first-run)
3. [Using the CLI](#using-the-cli)
4. [Using the Web Interface](#using-the-web-interface)
5. [Using the Python API](#using-the-python-api)
6. [Adding Your Own Podcasts](#adding-your-own-podcasts)
7. [Troubleshooting](#troubleshooting)

## Installation

### Step 1: Get a Groq API Key (Free)

1. Go to https://console.groq.com
2. Sign up or log in
3. Create an API key
4. Copy the key

### Step 2: Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd podbotnik

# Copy environment template
cp .env.example .env

# Edit .env and paste your Groq API key
nano .env  # or use your favorite editor
# Change: GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Install Dependencies

```bash
# Install Python packages (includes FastAPI)
pip install -r requirements.txt
```

### Step 4: Run Tests

```bash
python test.py
```

You should see all ✅ checks if everything is set up correctly.

## First Run

### Option A: Try with Sample Transcripts (Beginner)

```bash
# Interactive chat
python cli.py chat --transcripts sample_transcripts.json
```

You'll see:
```
✓ Ready! Loaded 4 episode(s):

  #1: Introduction to Machine Learning
  #2: Deep Dive into Neural Networks
  #3: Data Engineering Best Practices
  #4: Deploying ML Models to Production

💬 Interactive mode (type 'quit' to exit)

You: What is machine learning?
```

### Option B: Run All Tests (Recommended)

```bash
python test.py
```

### Option C: Try Example Script

```bash
python example.py
```

## Using the CLI

### Interactive Chat Mode

```bash
python cli.py chat --transcripts sample_transcripts.json
```

Commands:
- Type your question and press Enter
- `quit` - Exit the chat
- `list` - Show loaded episodes

### Ask a Single Question

```bash
python cli.py ask sample_transcripts.json "What is machine learning?"
```

Output:
```
❓ Question: What is machine learning?

🤖 Answer:
Machine learning is a subset of artificial intelligence...

📍 Sources:

  [1] Episode #1: Introduction to Machine Learning
      Timestamp: 00:32
      "Machine learning is a subset of artificial intelligence..."
      🎬 https://youtube.com/watch?v=...&t=32
      🎙️ https://example.com/podcast/ep001.mp3#t=32
```

### List All Episodes

```bash
python cli.py list-episodes sample_transcripts.json
```

## Using the Web Interface

### Start the Server

```bash
streamlit run web.py
```

Or with custom port:
```bash
streamlit run web.py --server.port 5000
```

### Access the UI

Open http://localhost:8501 (default Streamlit port) in your web browser:
- Select a transcript file from the sidebar
- Click "🚀 Load Transcripts" to load it
- Ask questions in the main chat area
- Adjust "Max Context Segments" slider for answer precision
- View chat history below

### Using the REST API

If you need a REST API instead of/alongside Streamlit:
```bash
python api.py
```

This provides:
- FastAPI auto-docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- REST endpoints: POST /api/ask, GET /api/episodes, etc.

## Using the Python API

### Simple Example

```python
from chatbot import PodcastChatbot

# Create chatbot
chatbot = PodcastChatbot()

# Load transcripts
chatbot.load_transcripts("sample_transcripts.json")

# Ask a question
result = chatbot.answer_question("What is machine learning?")

# Print answer
print(result["answer"])

# Print sources
for source in result["sources"]:
    print(f"\nEpisode: {source['episode']}")
    print(f"Timestamp: {source['timestamp']}")
    print(f"Watch: {source['video_link']}")
```

### Advanced Example - Batch Processing

```python
from chatbot import PodcastChatbot

chatbot = PodcastChatbot()
chatbot.load_transcripts("sample_transcripts.json")

questions = [
    "What is supervised learning?",
    "What is deep learning?",
    "What is data engineering?",
]

for q in questions:
    result = chatbot.answer_question(q, max_context_segments=2)
    print(f"Q: {q}")
    print(f"A: {result['answer']}")
    print()
```

## Adding Your Own Podcasts

### Option 1: Prepare Transcripts Manually

Create a `my_transcripts.json` file:

```json
[
  {
    "episode_id": "ep001",
    "episode_title": "My First Episode",
    "episode_number": 1,
    "transcript": "Full episode transcript here...",
    "video_url": "https://youtube.com/watch?v=...",
    "audio_url": "https://example.com/podcast/ep001.mp3"
  }
]
```

Then use it:

```bash
python cli.py chat --transcripts my_transcripts.json
python web.py my_transcripts.json 5000
```

### Option 2: Auto-Generate Transcripts with Whisper

```bash
# Install OpenAI library
pip install openai

# Set OpenAI API key
export OPENAI_API_KEY=sk-...

# Transcribe an audio file
python transcript_generator.py \
  --method whisper \
  --episode-id ep001 \
  --episode-title "My Episode" \
  --episode-number 1 \
  --audio episode.mp3 \
  --video "https://youtube.com/watch?v=..." \
  --output my_transcripts.json
```

### Option 3: Use Existing Text Transcripts

```bash
python transcript_generator.py \
  --use-existing \
  --episode-id ep001 \
  --episode-title "My Episode" \
  --episode-number 1 \
  --transcript-file episode.txt \
  --output my_transcripts.json
```

### Option 4: Append to Existing JSON

```bash
python transcript_generator.py \
  --use-existing \
  --episode-id ep002 \
  --episode-title "Another Episode" \
  --episode-number 2 \
  --transcript-file episode2.txt \
  --append my_transcripts.json
```

## Troubleshooting

### "GROQ_API_KEY not found"

```bash
# Check .env file exists
ls -la .env  # Should exist

# Check it has your key
cat .env  # Should show: GROQ_API_KEY=gsk_...

# If missing, add it
echo "GROQ_API_KEY=your_key_here" > .env
```

### "ModuleNotFoundError: No module named 'groq'"

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individual package
pip install groq
```

### "sample_transcripts.json not found"

```bash
# Check file exists
ls sample_transcripts.json

# If missing, verify you're in the right directory
pwd  # Should end in /podbotnik
```

### "Connection error" or "API rate limit"

- Groq free tier is very generous. If you hit limits:
  - Wait a few minutes
  - Check your internet connection
  - Verify your API key is valid

### Slow responses

- Reduce `max_context_segments`: `chatbot.answer_question(q, max_context_segments=2)`
- Make sure you have good internet (Groq API calls need network)
- Check if Groq service is up: https://status.groq.com

## Next Steps

1. **Add your podcast transcripts** (see above)
2. **Customize the system** - Edit `chatbot.py` to change behavior
3. **Deploy** - Use Docker or your favorite hosting:
   ```bash
   docker build -t podbotnik .
   docker run -p 5000:5000 -e GROQ_API_KEY=your_key podbotnik
   ```
4. **Integrate** - Use the Python API or REST endpoints in your app

## Common Tasks

### Change LLM Model

```python
from chatbot import PodcastChatbot
from llm import GroqLLM

chatbot = PodcastChatbot()
# Models available: mixtral-8x7b-32768, llama2-70b-4096, etc.
```

### Get More Detailed Answers

```python
result = chatbot.answer_question(question, max_context_segments=5)
```

### Search Transcripts Without Generating Answer

```python
results = chatbot.index.search(
    query="machine learning", 
    fields=["episode_title", "text"],
    max_results=5
)
for r in results:
    print(r["text"])
```

### Get Episode Information

```python
episodes = chatbot.list_episodes()
for ep in episodes:
    print(f"#{ep['number']}: {ep['title']}")
```

## Features

✅ **RAG (Retrieval-Augmented Generation)**
- Retrieves relevant transcript segments
- Passes them to LLM for contextual answers

✅ **Timestamped Answers**
- Automatic timestamps for all sources
- Direct links to video/audio segments

✅ **Multiple Interfaces**
- CLI for power users
- Web UI for easy access
- Python API for integration

✅ **Flexible Transcripts**
- JSON format
- Auto-generated via Whisper
- Manual transcripts supported

✅ **Fast & Free**
- Groq free tier (generous limits)
- No vector database needed
- Instant setup

## Getting Help

1. **Check README.md** - Comprehensive documentation
2. **Check examples** - `python example.py`
3. **Run tests** - `python test.py`
4. **API Documentation** - Start server and visit `/docs` endpoint
5. **File an issue** - GitHub issues

## Tips for Best Results

1. **Quality transcripts matter** - Accurate, complete transcripts = better answers
2. **Ask clear questions** - Specific questions get better matches
3. **Use max_context_segments wisely** - More = better accuracy, slower response
4. **Rephrase if needed** - Try different wording if first answer is poor

---

**Enjoy your podcast chatbot!** 🎙️
