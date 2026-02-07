#!/usr/bin/env python3
"""
Helper script to generate transcripts from audio/video files.
Supports multiple services.
"""

import argparse
import json
import os
from pathlib import Path


def transcribe_with_whisper(file_path: str) -> str:
    """
    Transcribe using OpenAI Whisper API.
    Requires: pip install openai
    """
    # Check for required API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Set it in the environment or in a .env file before using Whisper."
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI library not installed. Install with: pip install openai"
        )

    client = OpenAI(api_key=api_key)

    print(f"📤 Uploading {file_path} to OpenAI Whisper...")

    with open(file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )

    return transcript.text


def transcribe_with_groq(file_path: str) -> str:
    """
    Note: Groq doesn't have audio transcription API yet.
    This is a placeholder for future support.
    """
    # Groq does not currently provide a public audio transcription API
    # If Groq introduces audio transcription in the future, implement it here.
    # Provide helpful errors and environment checks for users who try this option.
    groq_key = os.getenv("GROQ_API_KEY")
    try:
        import groq  # noqa: F401
    except ImportError:
        raise NotImplementedError(
            "Groq audio transcription is not implemented in this script.\n"
            "Install a Groq SDK (if available) or use OpenAI Whisper instead (set OPENAI_API_KEY)."
        )

    if not groq_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Set it in the environment or in a .env file.\n"
            "Note: Groq audio transcription is not implemented in this script."
        )

    raise NotImplementedError(
        "Groq audio transcription is not implemented. Use OpenAI Whisper (OPENAI_API_KEY) instead."
    )


def create_transcript_json(
    episode_id: str,
    episode_title: str,
    episode_number: int,
    transcript_text: str,
    video_url: str = "",
    audio_url: str = "",
) -> dict:
    """Create a transcript dictionary."""
    return {
        "episode_id": episode_id,
        "episode_title": episode_title,
        "episode_number": episode_number,
        "transcript": transcript_text,
        "video_url": video_url,
        "audio_url": audio_url,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate transcripts for podcast episodes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe a single episode
  python transcript_generator.py --method whisper \\
    --episode-id ep001 --episode-title "My Episode" \\
    --episode-number 1 --audio episode.mp3

  # Transcribe and save to JSON
  python transcript_generator.py --method whisper \\
    --episode-id ep001 --episode-title "My Episode" \\
    --episode-number 1 --audio episode.mp3 \\
    --output transcripts.json --video "https://youtube.com/..."

  # Use existing transcript
  python transcript_generator.py --use-existing \\
    --episode-id ep001 --episode-title "My Episode" \\
    --episode-number 1 --transcript-file transcript.txt \\
    --output transcripts.json
        """,
    )
    
    parser.add_argument(
        "--method",
        choices=["whisper", "groq"],
        help="Transcription method to use (whisper or groq)",
    )
    parser.add_argument(
        "--audio",
        type=str,
        help="Path to audio/video file to transcribe",
    )
    parser.add_argument(
        "--use-existing",
        action="store_true",
        help="Use an existing transcript file instead of transcribing",
    )
    parser.add_argument(
        "--transcript-file",
        type=str,
        help="Path to existing transcript file (text)",
    )
    parser.add_argument(
        "--episode-id",
        required=True,
        help="Episode ID (e.g., ep001)",
    )
    parser.add_argument(
        "--episode-title",
        required=True,
        help="Episode title",
    )
    parser.add_argument(
        "--episode-number",
        type=int,
        required=True,
        help="Episode number",
    )
    parser.add_argument(
        "--video",
        type=str,
        default="",
        help="URL to the video (YouTube, etc.)",
    )
    parser.add_argument(
        "--audio-url",
        type=str,
        default="",
        help="URL to the audio file",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path (default: print to stdout)",
    )
    parser.add_argument(
        "--append",
        type=str,
        help="Append to existing JSON file instead of creating new",
    )
    
    args = parser.parse_args()
    
    # Get transcript
    if args.use_existing:
        if not args.transcript_file:
            parser.error("--transcript-file required when using --use-existing")
        
        if not os.path.exists(args.transcript_file):
            parser.error(f"Transcript file not found: {args.transcript_file}")
        
        print(f"📖 Reading transcript from {args.transcript_file}...")
        with open(args.transcript_file, "r", encoding="utf-8") as f:
            transcript_text = f.read()
    else:
        if not args.method:
            parser.error("--method required when transcribing audio")
        
        if not args.audio:
            parser.error("--audio required for transcription")
        
        if not os.path.exists(args.audio):
            parser.error(f"Audio file not found: {args.audio}")
        
        print(f"🎙️  Transcribing {args.audio} with {args.method}...")
        
        if args.method == "whisper":
            transcript_text = transcribe_with_whisper(args.audio)
    
    # Create transcript entry
    transcript = create_transcript_json(
        episode_id=args.episode_id,
        episode_title=args.episode_title,
        episode_number=args.episode_number,
        transcript_text=transcript_text,
        video_url=args.video,
        audio_url=args.audio_url,
    )
    
    # Load existing transcripts if appending
    transcripts = []
    if args.append:
        if os.path.exists(args.append):
            with open(args.append, "r", encoding="utf-8") as f:
                transcripts = json.load(f)
        output_file = args.append
    elif args.output:
        if os.path.exists(args.output):
            with open(args.output, "r", encoding="utf-8") as f:
                transcripts = json.load(f)
        output_file = args.output
    else:
        output_file = None
    
    # Add new transcript
    transcripts.append(transcript)
    
    # Output
    output_json = json.dumps(transcripts, indent=2, ensure_ascii=False)
    
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n✅ Saved to {output_file}")
    else:
        print(f"\n{output_json}")
    
    print(f"\n📊 Transcript stats:")
    print(f"   Episode: #{args.episode_number} {args.episode_title}")
    print(f"   Words: {len(transcript_text.split())}")
    print(f"   Characters: {len(transcript_text)}")


if __name__ == "__main__":
    main()
