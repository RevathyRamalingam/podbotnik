"""
AWS Lambda handler for the podcast chatbot.
Converts Lambda events to chatbot requests.

Deploy with Serverless Framework:
    serverless deploy

Or manually to AWS Lambda with AWS CLI:
    zip -r function.zip . -x "*.git*" "venv/*" "node_modules/*"
    aws lambda create-function --function-name podbotnik \
      --runtime python3.11 --handler lambda_handler.handler \
      --zip-file fileb://function.zip --timeout 30 --memory-size 512
"""

import json
import os
import sys
from typing import Any, Dict

# Load transcripts from S3 on cold start (once per Lambda container)
CHATBOT = None

def load_chatbot():
    """Initialize chatbot and load transcripts from S3."""
    global CHATBOT
    
    if CHATBOT is not None:
        return CHATBOT
    
    from chatbot import PodcastChatbot
    import boto3
    from io import BytesIO
    
    print("[Lambda] Initializing chatbot...")
    
    try:
        chatbot = PodcastChatbot()
        
        # Load transcripts from S3
        s3_bucket = os.environ.get("TRANSCRIPTS_BUCKET")
        s3_key = os.environ.get("TRANSCRIPTS_KEY", "transcripts.json")
        
        if s3_bucket:
            print(f"[Lambda] Loading transcripts from s3://{s3_bucket}/{s3_key}...")
            
            s3 = boto3.client("s3")
            obj = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            transcript_json = obj["Body"].read().decode("utf-8")
            
            # Save to /tmp for local access
            tmp_file = "/tmp/transcripts.json"
            with open(tmp_file, "w") as f:
                f.write(transcript_json)
            
            chatbot.load_transcripts(tmp_file)
        else:
            print("[Lambda] TRANSCRIPTS_BUCKET not set, using local transcripts")
            # Try local sample file
            if os.path.exists("sample_transcripts.json"):
                chatbot.load_transcripts("sample_transcripts.json")
        
        episodes = chatbot.list_episodes()
        print(f"[Lambda] Loaded {len(episodes)} episode(s)")
        
        CHATBOT = chatbot
        return chatbot
    
    except Exception as e:
        print(f"[Lambda] Error initializing chatbot: {e}")
        raise


def build_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """Build AWS Lambda API Gateway response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def handler(event, context):
    """
    AWS Lambda handler for HTTP requests from API Gateway.
    
    Event structure:
    {
      "httpMethod": "GET|POST",
      "path": "/api/episodes|/api/ask",
      "body": JSON string (for POST)
    }
    """
    
    print(f"[Lambda] Event: {json.dumps(event)}")
    
    try:
        chatbot = load_chatbot()
        
        http_method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        
        # Root endpoint
        if path == "/" or path == "":
            return build_response(200, {
                "name": "Podbotnik",
                "status": "running",
                "version": "1.0.0",
                "endpoints": {
                    "episodes": "/api/episodes",
                    "ask": "/api/ask",
                    "search": "/api/search",
                },
            })
        
        # List episodes
        if path == "/api/episodes" and http_method == "GET":
            episodes = chatbot.list_episodes()
            return build_response(200, {
                "episodes": episodes,
                "count": len(episodes),
            })
        
        # Ask question
        if path == "/api/ask" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            question = body.get("question", "").strip()
            max_context = body.get("max_context_segments", 3)
            
            if not question:
                return build_response(400, {
                    "error": "Question is required",
                })
            
            result = chatbot.answer_question(
                question=question,
                max_context_segments=max_context,
            )
            
            return build_response(200, result)
        
        # Search transcripts
        if path == "/api/search" and http_method == "POST":
            body = json.loads(event.get("body", "{}"))
            query = body.get("query", "").strip()
            max_results = body.get("max_results", 5)
            
            if not query:
                return build_response(400, {
                    "error": "Query is required",
                })
            
            results = chatbot.index.search(
                query=query,
                fields=["episode_title", "text"],
                max_results=max_results,
            )
            
            return build_response(200, {
                "query": query,
                "results": results,
                "count": len(results),
            })
        
        # Not found
        return build_response(404, {
            "error": f"Not found: {http_method} {path}",
        })
    
    except json.JSONDecodeError as e:
        return build_response(400, {
            "error": f"Invalid JSON: {str(e)}",
        })
    
    except Exception as e:
        print(f"[Lambda] Error: {str(e)}")
        print(f"[Lambda] Traceback:", sys.exc_info())
        
        return build_response(500, {
            "error": f"Internal error: {str(e)}",
        })


# For local testing
if __name__ == "__main__":
    import sys
    
    # Simulated API Gateway event
    event = {
        "httpMethod": "POST",
        "path": "/api/ask",
        "body": json.dumps({
            "question": "What is machine learning?",
            "max_context_segments": 2,
        }),
    }
    
    class MockContext:
        pass
    
    result = handler(event, MockContext())
    print(json.dumps(result, indent=2))
