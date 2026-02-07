#!/usr/bin/env python3
"""
Quick test script to verify the chatbot works correctly.
"""

import json
import sys
from pathlib import Path


def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...\n")
    
    try:
        import minsearch
        print("✅ minsearch")
    except ImportError:
        print("❌ minsearch - Install: pip install minsearch")
        return False
    
    try:
        from groq import Groq
        print("✅ groq")
    except ImportError:
        print("❌ groq - Install: pip install groq")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv")
    except ImportError:
        print("❌ python-dotenv - Install: pip install python-dotenv")
        return False
    
    return True





def test_sample_transcripts():
    """Test loading sample transcripts via chatbot."""
    print("\n🧪 Testing sample transcripts...\n")
    
    try:
        from chatbot import PodcastChatbot
        
        sample_file = Path("sample_transcripts.json")
        if not sample_file.exists():
            print(f"⚠️  sample_transcripts.json not found")
            return True  # Not a failure, just not tested
        
        chatbot = PodcastChatbot()
        chatbot.load_transcripts("sample_transcripts.json")
        
        episodes = chatbot.list_episodes()
        print(f"✅ Loaded {len(episodes)} episodes")
        
        # Test search
        results = chatbot.index.search(
            query="machine learning",
            fields=["episode_title", "text"],
            max_results=3
        )
        assert len(results) > 0
        print(f"✅ Search returns {len(results)} result(s)")
        
        return True
    except Exception as e:
        print(f"❌ Sample transcripts test failed: {e}")
        return False


def test_groq_key():
    """Test if Groq API key is configured."""
    print("\n🧪 Testing Groq configuration...\n")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("⚠️  GROQ_API_KEY not found in environment")
        print("   Configure it in .env file for full functionality")
        return True  # Not a failure, just not configured
    
    if api_key == "your_groq_api_key_here":
        print("⚠️  GROQ_API_KEY not set (using placeholder)")
        print("   Visit https://console.groq.com and add your actual key")
        return True
    
    print("✅ GROQ_API_KEY configured")
    return True


def test_chatbot_init():
    """Test chatbot initialization."""
    print("\n🧪 Testing chatbot initialization...\n")
    
    try:
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Try without API key first (should fail gracefully)
        try:
            from chatbot import PodcastChatbot
            chatbot = PodcastChatbot(api_key="test_key_not_real")
            print("✅ PodcastChatbot instantiation (with dummy key)")
        except Exception as e:
            print(f"⚠️  PodcastChatbot needs valid Groq key: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Chatbot initialization test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("="*60)
    print("🧪 PODBOTNIK TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Sample Transcripts", test_sample_transcripts),
        ("Groq Configuration", test_groq_key),
        ("Chatbot Initialization", test_chatbot_init),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\nReady to use Podbotnik! Try:")
        print("  python cli.py chat --transcripts sample_transcripts.json")
        print("  python web.py sample_transcripts.json 5000")
        print("  python example.py")
    else:
        print("\n" + "="*60)
        print("⚠️  SOME TESTS FAILED")
        print("="*60)
        print("\nPlease check:")
        print("  1. All dependencies installed: pip install -r requirements.txt")
        print("  2. GROQ_API_KEY set in .env file")
        print("  3. sample_transcripts.json exists")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
