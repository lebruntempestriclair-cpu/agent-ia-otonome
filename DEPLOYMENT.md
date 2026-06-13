# Deployment Guide: Multilingual Video Dubbing Platform

This document outlines the deployment process for the dubbing platform in various environments.

## 🐳 Docker Deployment (Production)

1. **Build the image:**
   ```bash
   docker build -t dubbing-platform .
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

## ☁️ Cloud Infrastructure (AWS Example)

The platform is designed to be highly scalable using a microservices architecture.

### Architecture Components
- **API Gateway:** NGINX or AWS ALB.
- **Compute:** AWS EKS (Kubernetes) with Auto Scaling.
- **Storage:** Amazon S3 for media files (Object Storage).
- **Cache/State:** Amazon ElastiCache (Redis).
- **Database:** Amazon RDS (PostgreSQL).
- **CDN:** Amazon CloudFront for video distribution.

### Ingress & Security
- **TLS:** Port 443 with AWS Certificate Manager.
- **WAF:** AWS WAF to filter malicious requests.
- **VPC:** Private subnets for processing nodes.

## ⚙️ Configuration (config.yaml)

Ensure the `ai.providers` section is correctly configured with valid API keys for:
- STT (OpenAI, Google)
- MT (DeepL, Google)
- TTS (AWS Polly, Azure)

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated deployment:
- **Linting:** Flake8
- **Testing:** Pytest (with coverage)
- **Build:** Docker Image push to ECR/GHCR
- **Deploy:** Rolling update to Kubernetes cluster

## 🛡️ GDPR Compliance Checklist

Before deploying to production (EU), ensure:
1. Consent banner is active for voice processing.
2. Data processing agreement (DPA) is signed with AI providers.
3. DPIA (Data Protection Impact Assessment) has been completed.
