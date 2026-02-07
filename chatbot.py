"""
Main chatbot implementation combining RAG retrieval with Groq LLM.
Uses minsearch directly for document indexing and retrieval.
"""

import json
import os
from typing import List, Dict, Any, Optional
from minsearch import Index
from llm import GroqLLM
from urllib.parse import quote


class PodcastChatbot:
    """RAG-based chatbot for podcast Q&A using minsearch for retrieval."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot.
        
        Args:
            api_key: Groq API key (if None, reads from environment)
        """
        # Initialize minsearch index with fields we need
        self.index = Index(
            fields=["episode_id", "episode_title", "episode_number", "text"],
            contents=[]
        )
        
        # Keep track of episodes for metadata
        self.episodes: Dict[str, Dict[str, Any]] = {}
        
        self.llm = GroqLLM(api_key=api_key)
    
    def load_transcripts(self, json_file: str) -> None:
        """
        Load transcripts from a JSON file and index them.
        
        JSON format:
        [
            {
                "episode_id": "ep001",
                "episode_title": "Episode Title",
                "episode_number": 1,
                "transcript": "Full transcript text...",
                "video_url": "https://...",
                "audio_url": "https://..."
            },
            ...
        ]
        """
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Transcript file not found: {json_file}")
        
        with open(json_file, "r", encoding="utf-8") as f:
            episodes = json.load(f)
        
        # Index all episodes
        docs = []
        for episode in episodes:
            episode_id = episode["episode_id"]
            
            # Store episode metadata
            self.episodes[episode_id] = {
                "title": episode["episode_title"],
                "number": episode["episode_number"],
                "video_url": episode.get("video_url", ""),
                "audio_url": episode.get("audio_url", ""),
                "transcript": episode["transcript"],
            }
            
            # Create document for indexing
            doc = {
                "episode_id": episode_id,
                "episode_title": episode["episode_title"],
                "episode_number": episode["episode_number"],
                "text": episode["transcript"],
            }
            docs.append(doc)
        
        # Index documents
        if docs:
            self.index.index_documents(docs)
    
    def add_transcript(
        self,
        episode_id: str,
        episode_title: str,
        episode_number: int,
        transcript_text: str,
        video_url: str = "",
        audio_url: str = "",
    ) -> None:
        """Add a single transcript and index it."""
        # Store episode metadata
        self.episodes[episode_id] = {
            "title": episode_title,
            "number": episode_number,
            "video_url": video_url,
            "audio_url": audio_url,
            "transcript": transcript_text,
        }
        
        # Create and index document
        doc = {
            "episode_id": episode_id,
            "episode_title": episode_title,
            "episode_number": episode_number,
            "text": transcript_text,
        }
        self.index.index_documents([doc])
    
    def _time_to_seconds(self, time_str: str) -> int:
        """Convert MM:SS or HH:MM:SS to seconds."""
        parts = time_str.split(":")
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 0
    
    def _build_timestamp_link(
        self,
        url: str,
        time_str: str,
    ) -> str:
        """
        Build a direct link to a specific timestamp.
        
        Supports:
        - YouTube: https://youtube.com/watch?v=VIDEO_ID&t=SECONDS
        - Generic media player: url#t=SECONDS
        
        Args:
            url: Base URL to the media
            time_str: Timestamp in MM:SS or HH:MM:SS format
        
        Returns:
            URL with timestamp
        """
        if not url:
            return ""
        
        seconds = self._time_to_seconds(time_str)
        
        # YouTube URLs
        if "youtube.com" in url or "youtu.be" in url:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}t={seconds}"
        # Spotify and other platforms (using media fragment identifier)
        elif "spotify.com" in url:
            return f"{url}#t={seconds}"
        # Generic fallback (works with HTML5 audio/video)
        else:
            return f"{url}#t={seconds}"
    
    def answer_question(
        self,
        question: str,
        max_context_segments: int = 3,
    ) -> Dict[str, Any]:
        """
        Answer a question about the podcast.
        
        Args:
            question: User's natural language question
            max_context_segments: Number of transcript segments to use as context
        
        Returns:
            Dictionary with:
                - answer: Generated answer
                - sources: List of source segments with timestamps and links
                - context_used: Number of context segments used
        """
        # Retrieve relevant segments using minsearch
        search_results = self.index.search(
            query=question,
            fields=["episode_title", "text"],
            max_results=max_context_segments,
        )
        
        if not search_results:
            return {
                "answer": "I couldn't find relevant information in the podcast transcripts to answer your question.",
                "sources": [],
                "context_used": 0,
            }
        
        # Build context for LLM
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results, 1):
            # Format context segment
            episode_id = result.get("episode_id", "")
            episode_title = result.get("episode_title", "Unknown")
            text = result.get("text", "")
            
            context_parts.append(f"[Episode: {episode_title}] {text}")
            
            # Get episode metadata
            episode = self.episodes.get(episode_id, {})
            
            # Build source info
            source = {
                "episode": episode_title,
                "episode_number": result.get("episode_number", ""),
                "segment": text[:200] + "..." if len(text) > 200 else text,
                "timestamp": "",  # minsearch doesn't provide timestamps by default
            }
            
            # Add links if available
            video_url = episode.get("video_url", "")
            audio_url = episode.get("audio_url", "")
            
            if video_url:
                source["video_link"] = video_url
            
            if audio_url:
                source["audio_link"] = audio_url
            
            sources.append(source)
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using LLM
        answer = self.llm.generate_answer(
            question=question,
            context=context,
            max_tokens=400,
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "context_used": len(search_results),
        }
    
    def list_episodes(self) -> List[Dict[str, Any]]:
        """Get list of all loaded episodes."""
        return [
            {
                "episode_id": ep_id,
                "title": ep["title"],
                "number": ep["number"],
            }
            for ep_id, ep in sorted(
                self.episodes.items(),
                key=lambda x: x[1]["number"],
            )
        ]
