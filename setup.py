#!/usr/bin/env python3
"""
Setup script for the podcast chatbot.
Helps initialize the project and verify dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and return success status."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False


def check_python_version():
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}")
    return True


def check_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file exists")
        return True
    
    if env_example.exists():
        env_example.read_text()
        print("\n⚠️  .env file not found. Creating from .env.example...")
        env_file.write_text(env_example.read_text())
        print("📝 Created .env - Please edit it with your GROQ_API_KEY")
        return True
    
    print("⚠️  Neither .env nor .env.example found")
    return False


def install_dependencies():
    """Install Python dependencies."""
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies",
    ):
        print("\n⚠️  Failed to install some dependencies. Please run manually:")
        print("    pip install -r requirements.txt")
        return False
    return True


def test_imports():
    """Test if critical imports work."""
    print("\n🧪 Testing imports...")
    
    dependencies = {
        "minsearch": "minsearch",
        "groq": "groq",
        "dotenv": "python-dotenv",
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (install: pip install {package})")
            all_ok = False
    
    return all_ok


def verify_groq_key():
    """Check if GROQ_API_KEY is set."""
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and api_key != "your_groq_api_key_here":
        print("✅ GROQ_API_KEY is set")
        return True
    else:
        print("⚠️  GROQ_API_KEY not set")
        print("   1. Visit https://console.groq.com")
        print("   2. Create an account and generate an API key")
        print("   3. Edit .env and add your key")
        return False


def main():
    print("\n" + "="*60)
    print("🎙️  PODBOTNIK SETUP")
    print("="*60)
    
    steps = [
        ("Python version", check_python_version),
        (".env file", check_env_file),
        ("Dependencies", install_dependencies),
        ("Imports", test_imports),
        ("Groq API Key", verify_groq_key),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ {step_name} error: {e}")
            results.append((step_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📋 SETUP SUMMARY")
    print("="*60)
    
    for step_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {step_name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print("\n✨ Next steps:")
        print("\n1. Interactive chat mode:")
        print("   python cli.py chat --transcripts sample_transcripts.json")
        print("\n2. Ask a single question:")
        print("   python cli.py ask sample_transcripts.json \"What is machine learning?\"")
        print("\n3. Start web interface:")
        print("   pip install flask  # if not already installed")
        print("   python web.py sample_transcripts.json 5000")
        print("\n4. Use programmatically:")
        print("   python example.py")
        print("\n5. Add your own transcripts:")
        print("   python transcript_generator.py --help")
        print("\n" + "="*60)
    else:
        print("\n⚠️  Some setup steps failed. Please review above.")
        print("\nFor help:")
        print("  - Check README.md")
        print("  - Run: pip install -r requirements.txt")
        print("  - Ensure GROQ_API_KEY is in .env")
        print("\n" + "="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
