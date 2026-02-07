#!/bin/bash
# Deploy to AWS Lambda using AWS CLI (without Serverless Framework)
# More manual but no Node.js dependency

set -e

FUNCTION_NAME=${1:-podbotnik}
ROLE_NAME=${2:-lambda-podbotnik-role}
BUCKET_NAME=${3:-podbotnik-transcripts-$(aws sts get-caller-identity --query Account --output text)}

echo "🚀 Deploying Podbotnik to AWS Lambda"
echo "===================================="
echo "Function: $FUNCTION_NAME"
echo "Role: $ROLE_NAME"
echo "Bucket: $BUCKET_NAME"
echo ""

# Check prerequisites
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ GROQ_API_KEY environment variable not set"
    exit 1
fi

# Step 1: Create IAM role
echo "1️⃣  Creating IAM role..."
if ! aws iam get-role --role-name "$ROLE_NAME" &> /dev/null; then
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }'
    
    # Attach basic Lambda execution policy
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
    # Attach S3 read policy
    aws iam attach-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
    
    echo "✅ Role created"
    sleep 10  # Wait for role to propagate
else
    echo "✅ Role already exists"
fi

# Step 2: Create S3 bucket for transcripts
echo ""
echo "2️⃣  Creating S3 bucket..."
if aws s3 ls "s3://$BUCKET_NAME" 2> /dev/null; then
    echo "✅ Bucket already exists"
else
    aws s3 mb "s3://$BUCKET_NAME"
    echo "✅ Bucket created"
fi

# Step 3: Upload sample transcripts
echo ""
echo "3️⃣  Uploading sample transcripts..."
aws s3 cp sample_transcripts.json "s3://$BUCKET_NAME/transcripts.json"
echo "✅ Transcripts uploaded"

# Step 4: Create deployment package
echo ""
echo "4️⃣  Creating Lambda package..."
rm -rf package/ function.zip
mkdir package/

# Install dependencies
pip install -q -r requirements-lambda.txt -t package/

# Copy source files
cp lambda_handler.py package/
cp chatbot.py package/
cp transcripts.py package/
cp llm.py package/

# Create zip
cd package/
zip -q -r ../function.zip .
cd ..
echo "✅ Package created"

# Step 5: Create/Update Lambda function
echo ""
echo "5️⃣  Creating/updating Lambda function..."

ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)

# Check if function exists
if aws lambda get-function --function-name "$FUNCTION_NAME" &> /dev/null; then
    echo "   Updating existing function..."
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --zip-file fileb://function.zip > /dev/null
else
    echo "   Creating new function..."
    aws lambda create-function \
        --function-name "$FUNCTION_NAME" \
        --runtime python3.11 \
        --handler lambda_handler.handler \
        --role "$ROLE_ARN" \
        --zip-file fileb://function.zip \
        --timeout 30 \
        --memory-size 512 \
        --environment "Variables={GROQ_API_KEY=$GROQ_API_KEY,TRANSCRIPTS_BUCKET=$BUCKET_NAME,TRANSCRIPTS_KEY=transcripts.json}" > /dev/null
fi

echo "✅ Lambda function ready"

# Step 6: Create API Gateway
echo ""
echo "6️⃣  Setting up API Gateway..."

API_NAME="${FUNCTION_NAME}-api"

# Create REST API
API_ID=$(aws apigateway create-rest-api \
    --name "$API_NAME" \
    --description "API for Podbotnik podcast chatbot" \
    --query 'id' \
    --output text 2> /dev/null || echo "")

if [ -z "$API_ID" ]; then
    API_ID=$(aws apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text)
fi

if [ -z "$API_ID" ]; then
    echo "⚠️  Skipping API Gateway (Serverless Framework recommended for full setup)"
else
    echo "✅ API Gateway created"
    echo "   API ID: $API_ID"
fi

# Cleanup
rm -rf package/

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "===================================="
echo "📊 Deployment Details"
echo "===================================="
echo "Function Name: $FUNCTION_NAME"
echo "Region: $(aws configure get region)"
echo "Bucket: $BUCKET_NAME"
echo ""
echo "🧪 Test the function:"
echo ""
echo "aws lambda invoke \\"
echo "  --function-name $FUNCTION_NAME \\"
echo "  --payload '{\"httpMethod\":\"POST\",\"path\":\"/api/ask\",\"body\":\"{\\\"question\\\":\\\"What is machine learning?\\\"}\"}' \\"
echo "  response.json"
echo ""
echo "cat response.json"
echo ""
echo "📚 View logs:"
echo "aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo ""
