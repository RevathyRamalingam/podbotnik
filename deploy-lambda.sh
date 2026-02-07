#!/bin/bash
# Deploy to AWS Lambda using Serverless Framework

set -e

echo "🚀 Deploying Podbotnik to AWS Lambda"
echo "===================================="

# Check prerequisites
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework not found"
    echo "Install with: npm install -g serverless"
    exit 1
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY environment variable not set"
    echo "Set it: export GROQ_API_KEY=your_key"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured"
    echo "Configure with: aws configure"
    exit 1
fi

# Create Lambda package
echo "📦 Creating Lambda package..."
pip install -r requirements-lambda.txt -t package/

# Copy source files
cp lambda_handler.py package/
cp chatbot.py package/
cp transcripts.py package/
cp llm.py package/
cp sample_transcripts.json package/

cd package || exit 1
zip -r ../function.zip . -x "*.git*" "*.md" "*.pyc"
cd - || exit 1

echo "✅ Package created: function.zip"

# Deploy with Serverless
echo "🌐 Deploying to AWS Lambda..."
serverless deploy --param="groqApiKey=$GROQ_API_KEY"

echo "🎉 Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Upload transcripts to S3:"
echo "   aws s3 cp sample_transcripts.json s3://podbotnik-transcripts-<account-id>/"
echo ""
echo "2. Test the API:"
echo "   curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/api/ask \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"question\":\"What is machine learning?\"}'"
echo ""
echo "3. View logs:"
echo "   serverless logs -f ask"
