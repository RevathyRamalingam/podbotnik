#!/usr/bin/env python3
"""
Command-line interface for the podcast chatbot.
"""

import click
import json
import os
from pathlib import Path
from chatbot import PodcastChatbot


def load_env():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


@click.group()
def cli():
    """Podcast Chatbot - Ask questions about your podcast library."""
    load_env()


@cli.command()
@click.option(
    "--transcripts",
    "-t",
    type=click.Path(exists=True),
    help="Path to JSON file with transcripts",
)
@click.option(
    "--add-episode",
    "-a",
    nargs=3,
    multiple=True,
    type=(str, str, click.Path()),
    help="Add an episode: --add-episode TITLE EPISODE_NUMBER TRANSCRIPT_FILE",
)
def chat(transcripts, add_episode):
    """Interactive chat mode."""
    try:
        chatbot = PodcastChatbot()
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        return
    
    # Load transcripts from JSON file
    if transcripts:
        try:
            click.echo(f"📚 Loading transcripts from {transcripts}...")
            chatbot.load_transcripts(transcripts)
            click.echo("✓ Transcripts loaded")
        except Exception as e:
            click.echo(f"❌ Error loading transcripts: {e}", err=True)
            return
    
    # Add individual episodes
    for title, ep_num, transcript_file in add_episode:
        try:
            with open(transcript_file, "r", encoding="utf-8") as f:
                transcript = f.read()
            
            episode_id = f"ep{ep_num:03d}"
            chatbot.add_transcript(
                episode_id=episode_id,
                episode_title=title,
                episode_number=int(ep_num),
                transcript_text=transcript,
            )
            click.echo(f"✓ Added episode {ep_num}: {title}")
        except Exception as e:
            click.echo(f"❌ Error adding episode: {e}", err=True)
            return
    
    # Show loaded episodes
    episodes = chatbot.list_episodes()
    if not episodes:
        click.echo("⚠️  No transcripts loaded. Use --transcripts or --add-episode.", err=True)
        return
    
    click.echo(f"\n✓ Ready! Loaded {len(episodes)} episode(s):\n")
    for ep in episodes:
        click.echo(f"  #{ep['number']}: {ep['title']}")
    
    click.echo("\n💬 Interactive mode (type 'quit' to exit, 'list' to show episodes)\n")
    
    # Interactive loop
    while True:
        try:
            question = click.prompt("You")
        except (click.Abort, EOFError):
            break
        
        if question.lower() == "quit":
            break
        
        if question.lower() == "list":
            episodes = chatbot.list_episodes()
            click.echo("\nLoaded episodes:")
            for ep in episodes:
                click.echo(f"  #{ep['number']}: {ep['title']}")
            click.echo()
            continue
        
        if not question.strip():
            continue
        
        click.echo("\n🤔 Thinking...")
        
        try:
            result = chatbot.answer_question(question)
            
            click.echo(f"\n🤖 Assistant:\n{result['answer']}\n")
            
            if result["sources"]:
                click.echo("📍 Sources:")
                for i, source in enumerate(result["sources"], 1):
                    click.echo(f"\n  [{i}] Episode #{source['episode_number']}: {source['episode']}")
                    if source.get("timestamp"):
                        click.echo(f"      Timestamp: {source['timestamp']}")
                    click.echo(f"      Excerpt: {source['segment']}")
                    if source.get("video_link"):
                        click.echo(f"      Video: {source['video_link']}")
                    if source.get("audio_link"):
                        click.echo(f"      Audio: {source['audio_link']}")
            
            click.echo()
        
        except Exception as e:
            click.echo(f"\n❌ Error: {e}\n", err=True)


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
@click.argument("question")
@click.option(
    "--num-sources",
    "-n",
    default=3,
    type=int,
    help="Number of source segments to retrieve",
)
def ask(json_file, question, num_sources):
    """Ask a single question and exit."""
    try:
        chatbot = PodcastChatbot()
        chatbot.load_transcripts(json_file)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        return
    
    click.echo(f"\n❓ Question: {question}\n")
    click.echo("🤔 Processing...\n")
    
    try:
        result = chatbot.answer_question(question, max_context_segments=num_sources)
        
        click.echo(f"🤖 Answer:\n{result['answer']}\n")
        
        if result["sources"]:
            click.echo("📍 Sources:")
            for i, source in enumerate(result["sources"], 1):
                click.echo(f"\n  [{i}] Episode #{source['episode_number']}: {source['episode']}")
                click.echo(f"      Timestamp: {source.get('timestamp', 'N/A')}")
                click.echo(f"      \"{source['segment']}\"")
                if source.get("video_link"):
                    click.echo(f"      🎬 {source['video_link']}")
                if source.get("audio_link"):
                    click.echo(f"      🎙️  {source['audio_link']}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


@cli.command()
@click.argument("json_file", type=click.Path(exists=True))
def list_episodes(json_file):
    """List all episodes in a transcripts file."""
    try:
        chatbot = PodcastChatbot()
        chatbot.load_transcripts(json_file)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        return
    
    episodes = chatbot.list_episodes()
    
    click.echo(f"\n📚 Episodes in {json_file}:\n")
    for ep in episodes:
        click.echo(f"  #{ep['number']:3d} | {ep['title']}")
    
    click.echo(f"\nTotal: {len(episodes)} episode(s)\n")


if __name__ == "__main__":
    cli()
