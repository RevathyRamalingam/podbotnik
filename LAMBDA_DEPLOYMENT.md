# AWS Lambda Deployment Guide

## Overview

Deploy Podbotnik to AWS Lambda for serverless, pay-as-you-go hosting. Scales automatically with traffic.

## Architecture

```
API Gateway → Lambda (ChatBot) → S3 (Transcripts)
               ↓
          Groq API (LLM)
```

**Benefits:**
- ✅ No servers to manage
- ✅ Auto-scaling
- ✅ Pay only for usage
- ✅ Integrated with AWS ecosystem
- ✅ CI/CD ready

**Considerations:**
- ⏱️ Cold starts (~5-10 seconds on first request)
- 💾 Max 15 minute timeout
- 💭 Max 3GB memory
- 📁 Max 250MB deployment package

## Prerequisites

1. **AWS Account** - [Create one](https://aws.amazon.com)
2. **AWS CLI** - [Install](https://aws.amazon.com/cli/)
3. **Groq API Key** - From https://console.groq.com
4. **Node.js** (optional) - For Serverless Framework

## Option 1: Deploy with Serverless Framework (Recommended)

### Setup

```bash
# Install Serverless Framework
npm install -g serverless

# Configure AWS credentials
aws configure
# Enter: AWS Access Key, Secret Key, Region, Output format

# Set Groq API key
export GROQ_API_KEY=gsk_...
```

### Deploy

```bash
# Deploy the stack
serverless deploy

# Or with custom region
serverless deploy --region us-west-2

# Or with parameters
serverless deploy \
  --param="groqApiKey=$GROQ_API_KEY" \
  --param="transcriptsBucket=my-bucket"
```

### Test

```bash
# Test the ask endpoint
serverless invoke -f ask -d '{
  "httpMethod": "POST",
  "path": "/api/ask",
  "body": "{\"question\":\"What is machine learning?\"}"
}'

# Test list episodes
serverless invoke -f episodes -d '{
  "httpMethod": "GET",
  "path": "/api/episodes"
}'

# View logs
serverless logs -f ask

# Redeploy after changes
serverless deploy function -f ask
```

### Configure Environment

Edit `serverless.yml` to customize:
- `memorySize` - Adjust RAM (128-3008 MB)
- `timeout` - Adjust timeout (1-900 seconds)
- `region` - Change AWS region

## Option 2: Deploy with AWS CLI

### Setup

```bash
# Configure AWS
aws configure

# Set Groq API key
export GROQ_API_KEY=gsk_...

# Make scripts executable
chmod +x deploy-lambda-cli.sh deploy-lambda.sh
```

### Deploy

```bash
# Use the automated script
./deploy-lambda-cli.sh podbotnik

# Or specify custom values
./deploy-lambda-cli.sh my-function my-role my-bucket
```

### Manual Deployment (No Script)

```bash
# 1. Create IAM role
ROLE_ARN=$(aws iam create-role \
  --role-name lambda-podbotnik \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }' --query 'Role.Arn' --output text)

# 2. Attach policies
aws iam attach-role-policy \
  --role-name lambda-podbotnik \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name lambda-podbotnik \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# 3. Create S3 bucket
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws s3 mb s3://podbotnik-transcripts-$ACCOUNT
aws s3 cp sample_transcripts.json s3://podbotnik-transcripts-$ACCOUNT/

# 4. Create deployment package
pip install -r requirements-lambda.txt -t package/
cp lambda_handler.py chatbot.py transcripts.py llm.py package/
cd package && zip -r ../function.zip . && cd ..

# 5. Create Lambda function
sleep 10  # Wait for role to propagate

aws lambda create-function \
  --function-name podbotnik \
  --runtime python3.11 \
  --handler lambda_handler.handler \
  --role $ROLE_ARN \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{GROQ_API_KEY=$GROQ_API_KEY,TRANSCRIPTS_BUCKET=podbotnik-transcripts-$ACCOUNT}"

# 6. Test
aws lambda invoke \
  --function-name podbotnik \
  --payload '{"httpMethod":"POST","path":"/api/ask","body":"{\"question\":\"What is machine learning?\"}"}' \
  response.json

cat response.json
```

## Upload Transcripts

### From Local File

```bash
aws s3 cp transcripts.json s3://podbotnik-transcripts-<account-id>/

# Or with custom key
aws s3 cp transcripts.json s3://podbotnik-transcripts-<account-id>/my-podcasts.json
```

### Update Environment Variable

```bash
aws lambda update-function-configuration \
  --function-name podbotnik \
  --environment Variables="{GROQ_API_KEY=$GROQ_API_KEY,TRANSCRIPTS_BUCKET=podbotnik-transcripts-<account-id>,TRANSCRIPTS_KEY=my-podcasts.json}"
```

## Invoke from Web

### Using API Gateway URL

If using Serverless Framework, endpoints are automatically created:

```bash
# Ask question
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is machine learning?"}'

# List episodes  
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/api/episodes

# Search
curl -X POST https://<api-id>.execute-api.us-east-1.amazonaws.com/dev/api/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"machine learning","max_results":5}'
```

### Create API Gateway Manually

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
  --name podbotnik-api \
  --query 'id' \
  --output text)

# Get root resource
RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' \
  --output text)

# Create /api/ask resource
ASK_RESOURCE=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $RESOURCE_ID \
  --path-part api \
  --query 'id' \
  --output text)

ask=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ASK_RESOURCE \
  --path-part ask \
  --query 'id' \
  --output text)

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name podbotnik \
  --statement-id apigateway-access \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $ask \
  --http-method POST \
  --authorization-type NONE

# And so on... (complex, use Serverless Framework instead)
```

## Monitor & Debug

### View Logs

```bash
# Stream logs in real-time
aws logs tail /aws/lambda/podbotnik --follow

# Get logs for specific time
aws logs filter-log-events \
  --log-group-name /aws/lambda/podbotnik \
  --start-time $(date -d '5 minutes ago' +%s)000
```

### Invoke and Debug

```bash
# Invoke with payload
aws lambda invoke \
  --function-name podbotnik \
  --log-type Tail \
  --payload '{"httpMethod":"POST","path":"/api/ask","body":"{\"question\":\"test\"}"}' \
  response.json \
  --query 'LogResult' --output text | base64 -d

# See response
cat response.json | jq .
```

### CloudWatch Metrics

```bash
# View duration metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=podbotnik \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average,Maximum

# View invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=podbotnik \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Performance Optimization

### Reduce Cold Start

```yaml
# In serverless.yml
provider:
  memorySize: 1024  # More memory = faster CPU = faster cold start
  architecture: arm64  # ARM is faster for Python
  
functions:
  ask:
    provisionedConcurrency: 1  # Warm up one instance
```

### Optimize Package Size

```bash
# Remove unnecessary files
zip -r function.zip . -x \
  "*.git*" \
  "venv/*" \
  "*/__pycache__/*" \
  "*.pyc" \
  "*.egg-info*" \
  "tests/*"

# Use Lambda Layers for dependencies
serverless plugin install -n serverless-python-requirements
```

## Costs

**Free Tier (Always):**
- 1M free requests/month
- 400,000 GB-seconds compute/month

**Typical Costs:**
- $0.20 per 1M requests
- $0.0000166667 per GB-second
- Example: 100 requests/day, 2 seconds each, 512MB = ~$0.50/month

**Cost Optimization:**
- Use lower memory for simple queries
- Use reserved concurrency for consistent traffic
- Archive old transcripts to S3 Glacier

## Scaling

### Auto-Scaling

Lambda automatically scales up to handle traffic. To limit costs:

```bash
# Set reserved concurrency (prevents unlimited scaling)
aws lambda put-function-concurrency \
  --function-name podbotnik \
  --reserved-concurrent-executions 10
```

### Handle Traffic Spikes

```bash
# Provisioned concurrency (keeps instances warm)
aws lambda put-provisioned-concurrency-config \
  --function-name podbotnik \
  --provisioned-concurrent-executions 5 \
  --qualifier LIVE
```

## Cleanup

```bash
# Delete Lambda function
aws lambda delete-function --function-name podbotnik

# Delete S3 bucket and contents
aws s3 rm s3://podbotnik-transcripts-<account-id> --recursive
aws s3 rb s3://podbotnik-transcripts-<account-id>

# Delete IAM role
aws iam detach-role-policy \
  --role-name lambda-podbotnik \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name lambda-podbotnik

# Using Serverless
serverless remove
```

## Troubleshooting

### Cold Start Issues

```bash
# Increase memory for faster CPU
aws lambda update-function-configuration \
  --function-name podbotnik \
  --memory-size 1024

# Or use provisioned concurrency (warmer instances)
aws lambda put-provisioned-concurrency-config \
  --function-name podbotnik \
  --provisioned-concurrent-executions 1 \
  --qualifier LIVE
```

### Timeout Errors

```bash
# Increase timeout (max 900 seconds)
aws lambda update-function-configuration \
  --function-name podbotnik \
  --timeout 60
```

### S3 Access Denied

```bash
# Check role has S3 permissions
aws iam get-role-policy \
  --role-name lambda-podbotnik \
  --policy-name S3-Access

# Add if missing
aws iam attach-role-policy \
  --role-name lambda-podbotnik \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### ImportError for minsearch

```bash
# Ensure minsearch is in package
pip install minsearch -t package/
```

## Next Steps

1. **Deploy:** Use `serverless deploy` or `./deploy-lambda-cli.sh`
2. **Upload Transcripts:** Place JSON in S3
3. **Test:** Call API endpoints
4. **Monitor:** View logs in CloudWatch
5. **Optimize:** Adjust memory, concurrency, timeout as needed
6. **Scale:** Monitor costs and consider reserved concurrency

---

**Need Help?**
- AWS Lambda Docs: https://docs.aws.amazon.com/lambda/
- Serverless Framework: https://www.serverless.com/
- Troubleshooting: Check CloudWatch logs with `aws logs tail`
