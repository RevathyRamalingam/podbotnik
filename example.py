#!/usr/bin/env python3
"""
Example script showing how to use the podcast chatbot programmatically.
"""

from chatbot import PodcastChatbot


def main():
    """Run example chatbot queries."""
    
    # Initialize the chatbot
    print("🚀 Initializing Podcast Chatbot...\n")
    chatbot = PodcastChatbot()
    
    # Load sample transcripts
    print("📚 Loading sample transcripts...")
    chatbot.load_transcripts("sample_transcripts.json")
    
    # Show loaded episodes
    episodes = chatbot.list_episodes()
    print(f"✓ Loaded {len(episodes)} episode(s):\n")
    for ep in episodes:
        print(f"  #{ep['number']}: {ep['title']}")
    
    # Example questions
    questions = [
        "What is machine learning?",
        "How do transformers work?",
        "What is data engineering?",
        "How do you deploy ML models?",
        "What are neural networks?",
    ]
    
    print("\n" + "="*60)
    print("💬 EXAMPLE CHATBOT QUERIES")
    print("="*60)
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        print("-" * 60)
        
        # Get answer
        result = chatbot.answer_question(question, max_context_segments=2)
        
        print(f"🤖 Answer:\n{result['answer']}\n")
        
        # Show sources
        if result["sources"]:
            print("📍 Sources:")
            for i, source in enumerate(result["sources"], 1):
                print(f"\n  [{i}] Episode #{source['episode_number']}: {source['episode']}")
                print(f"      Timestamp: {source['timestamp']}")
                print(f"      Excerpt: {source['segment'][:150]}...")
                if source.get("video_link"):
                    print(f"      Watch: {source['video_link']}")
        
        print("\n" + "-"*60)


if __name__ == "__main__":
    main()
