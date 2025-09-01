# Document Portal 📚

An intelligent document analysis and comparison system powered by Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG). This project enables users to upload, analyze, compare, and chat with documents using state-of-the-art AI models.

## Features

- **Document Chat**: Interactive Q&A with your documents using RAG
- **Document Analysis**: AI-powered analysis of single documents  
- **Document Comparison**: Side-by-side comparison of multiple documents
- **Multi-format Support**: PDF, DOCX, and TXT files
- **Session Management**: Isolated sessions for different document sets
- **Multiple LLM Providers**: Groq, Gemini, Ollama, OpenAI

## What You'll Learn

- LLMOps best practices and production-ready LLM application development
  - You will setup CICD pipelines using GitHub Actions to build and push docker images to AWS ECR and deploy it via ECS Fargate
- RAG implementation and vector database usage with FAISS
- Document processing and text extraction from multiple formats
- Session management and error handling in AI applications
- Configuration management and testing for AI systems


## Conda Environment Setup

```bash
# Create environment
conda create -p ./dp_env python==3.10 -y

# Activate environment
conda activate ./dp_env

# Install dependencies
pip install -r requirements.txt
```

## How to Run Locally

### 1. Clone Repository
```bash
git clone https://github.com/ArunSubramanian456/document_portal
cd document_portal
```

### 2. Setup Environment Variables
Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Run Application
```bash
# FastAPI Backend
uvicorn api.main:app --port 8080 --reload
```

## How to Run on AWS ECS Fargate

### Prerequisites
- AWS Account with appropriate permissions
- GitHub Account
- Docker installed locally (optional, for testing)

### 1. Fork and Clone Repository
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/document_portal
cd document_portal
```

### 2. Setup GitHub Repository Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
```

### 3. Create AWS Resources

#### 3.1 Create ECR Repository
```bash
aws ecr create-repository --repository-name document-portal --region us-east-1
```

#### 3.2 Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name document-portal-cluster
```

#### 3.3 Create AWS Secrets for API Keys
```bash
# Create secret for foundation model API keys
aws secretsmanager create-secret \
    --name "document-portal/api-keys" \
    --description "API keys for foundation models" \
    --secret-string '{
        "GROQ_API_KEY": "your_groq_api_key_here",
        "GOOGLE_API_KEY": "your_gemini_api_key_here"
    }'

# Get the secret ARN (save this for IAM policy)
aws secretsmanager describe-secret --secret-id "document-portal/api-keys" --query 'ARN' --output text
```

#### 3.4 Create IAM Execution Role
```bash
# Create trust policy file
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Add inline policy for CloudWatch Logs
cat > ecs-logs-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-name CloudWatchLogsPolicy \
    --policy-document file://ecs-logs-policy.json
    

# Add inline policy for AWS Secrets access
# Replace YOUR_ACCOUNT_ID and YOUR_REGION with actual values
cat > ecs-secrets-access-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:YOUR_REGION:YOUR_ACCOUNT_ID:secret:document-portal/api-keys-*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-name SecretsAccessPolicy \
    --policy-document file://ecs-secrets-access-policy.json

# Clean up the temporary file
rm ecs-tasks-trust-policy.json
rm ecs-logs-policy.json
rm ecs-secrets-access-policy.json
```

#### 3.5 Register Task Definition
```bash
# Update task_definition.json with your account ID and region
aws ecs register-task-definition --cli-input-json file://.github/workflows/task_definition.json
```

#### 3.6 Create ECS Service
```bash
aws ecs create-service \
  --cluster document-portal-cluster \
  --service-name document-portal-service \
  --task-definition document-portal-task:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

#### 3.7 Update ECS Task Security group to allow inbound access from any IP
aws ec2 authorize-security-group-ingress \
    --group-id <ECS task security group ID> \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0

```

### 4. Configure GitHub Actions Workflow

The repository includes a pre-configured GitHub Actions workflow (`.github/workflows/aws.yml`) that:
- Builds Docker image on code push
- Pushes image to AWS ECR
- Updates ECS service with new image
- Handles environment variables securely

### 5. Deploy Application

#### 5.1 Push Code to Trigger CI/CD
```bash
# Make any changes to your code
git add .
git commit -m "Deploy to AWS ECS Fargate"
git push origin main
```

#### 5.2 Monitor Deployment
- Check GitHub Actions tab for build status
- Monitor ECS service in AWS Console
- View application logs in CloudWatch

### 6. Access Your Application

Once deployed, your application will be available at:
- Find the public IP in ECS Console → Clusters → Tasks
- Access via: `http://PUBLIC_IP:8080`


### Troubleshooting

- **Build Fails**: Check GitHub Actions logs
- **Service Won't Start**: Verify task definition and IAM roles
- **Can't Access App**: Check security groups and network configuration
- **API Errors**: Verify environment variables in task definition


## Minimum Requirements

### System Requirements
- Python 3.10+
- 4GB RAM minimum, 8GB recommended
- 2GB free storage

### LLM Providers
| Provider | Cost | Link |
|----------|------|------|
| Groq | Free | [Get API Key](https://console.groq.com/keys) |
| Gemini | 15 Days Free | [Get API Key](https://aistudio.google.com/apikey) |
| OpenAI | Paid | [Get API Key](https://platform.openai.com/api-keys) |
| Hugging Face | Free | [Get API Key](https://huggingface.co/settings/tokens) |

### Embedding Models
- OpenAI: text-embedding-ada-002, text-embedding-3-small
- Google: text-embedding-004
- Hugging Face: sentence-transformers models

### Vector Database
- FAISS with in-memory and persistent storage
- Session-based isolated indices