"""
Transcript manager for loading and storing podcast episode transcripts.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from minsearch import Index
import json
import os


@dataclass
class TranscriptSegment:
    """A segment of a transcript with timestamp."""
    episode_id: str
    episode_title: str
    episode_number: int
    start_time: str  # Format: "MM:SS" or "HH:MM:SS"
    end_time: str
    text: str
    video_url: str = ""
    audio_url: str = ""


class TranscriptManager:
    """Manages podcast transcripts and provides retrieval capabilities."""
    
    def __init__(self):
        """Initialize the transcript manager."""
        self.episodes: Dict[str, Dict[str, Any]] = {}
        self.index = Index(
            fields=["episode_title", "episode_number", "text"],
            contents=[],
        )
    
    def add_transcript(
        self,
        episode_id: str,
        episode_title: str,
        episode_number: int,
        transcript_text: str,
        video_url: str = "",
        audio_url: str = "",
    ) -> None:
        """
        Add a complete episode transcript.
        
        Args:
            episode_id: Unique identifier for the episode
            episode_title: Title of the episode
            episode_number: Episode number
            transcript_text: Full transcript text
            video_url: URL to the video
            audio_url: URL to the audio
        """
        # Store episode metadata
        self.episodes[episode_id] = {
            "title": episode_title,
            "number": episode_number,
            "video_url": video_url,
            "audio_url": audio_url,
            "transcript": transcript_text,
        }
        
        # Add to search index
        doc = {
            "episode_id": episode_id,
            "episode_title": episode_title,
            "episode_number": episode_number,
            "text": transcript_text,
        }
        self.index.index_documents([doc])
    
    def add_transcript_with_segments(
        self,
        episode_id: str,
        episode_title: str,
        episode_number: int,
        segments: List[TranscriptSegment],
    ) -> None:
        """
        Add episode transcript as timestamped segments.
        
        Args:
            episode_id: Unique identifier for the episode
            episode_title: Title of the episode
            episode_number: Episode number
            segments: List of TranscriptSegment objects
        """
        # Store episode metadata
        self.episodes[episode_id] = {
            "title": episode_title,
            "number": episode_number,
            "video_url": segments[0].video_url if segments else "",
            "audio_url": segments[0].audio_url if segments else "",
            "segments": segments,
            "transcript": " ".join([s.text for s in segments]),
        }
        
        # Index all segments separately for better retrieval
        docs = []
        for segment in segments:
            doc = {
                "episode_id": episode_id,
                "episode_title": episode_title,
                "episode_number": episode_number,
                "text": segment.text,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
            }
            docs.append(doc)
        
        if docs:
            self.index.index_documents(docs)
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search transcripts for relevant segments.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            List of matching documents with episode info
        """
        results = self.index.search(
            query=query,
            fields=["episode_title", "text"],
            max_results=max_results,
        )
        
        # Enhance results with episode URLs
        enhanced_results = []
        for result in results:
            episode_id = result.get("episode_id")
            episode = self.episodes.get(episode_id, {})
            
            enhanced_result = {
                **result,
                "video_url": episode.get("video_url", ""),
                "audio_url": episode.get("audio_url", ""),
            }
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def load_from_json(self, json_file: str) -> None:
        """
        Load transcripts from a JSON file.
        
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
        
        Args:
            json_file: Path to the JSON file
        """
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Transcript file not found: {json_file}")
        
        with open(json_file, "r", encoding="utf-8") as f:
            episodes = json.load(f)
        
        for episode in episodes:
            self.add_transcript(
                episode_id=episode["episode_id"],
                episode_title=episode["episode_title"],
                episode_number=episode["episode_number"],
                transcript_text=episode["transcript"],
                video_url=episode.get("video_url", ""),
                audio_url=episode.get("audio_url", ""),
            )
    
    def get_episode(self, episode_id: str) -> Dict[str, Any] | None:
        """Get episode metadata and transcript."""
        return self.episodes.get(episode_id)
    
    def list_episodes(self) -> List[Dict[str, Any]]:
        """List all loaded episodes."""
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
