# Kubernetes Deployment Guide

This guide explains how to deploy the Team Cache Me If You Can application to your Kubernetes cluster using the unified Terraform approach.

## Overview

The application consists of several microservices:
- **Java Services**: user-service, group-service, gateway-service, files-service  
- **GenAI Services**: genai-app, genai-celery-worker
- **Supporting Services**: MySQL, Redis, Weaviate (vector database)

All services are now managed by **Terraform** for consistent infrastructure-as-code deployment.

## Prerequisites

1. **Tools Required**:
   - `kubectl` (configured with access to your cluster)
   - `terraform` (v1.0+)
   - `helm` (for cleanup of old deployments)
   - Docker images built and pushed to GHCR

2. **Cluster Access**:
   - Access to namespace `developmentv1` 
   - Kubeconfig properly configured

3. **Secrets**:
   - OpenAI API key (for GenAI services)

## Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

2. Run the deployment script:
   ```bash
   ./deploy-to-k8s.sh
   ```

The script will:
- Check dependencies and cluster access
- Clean up any conflicting helm deployments
- Deploy everything via Terraform
- Verify the deployment

### Option 2: Manual Terraform Deployment

1. Navigate to the infrastructure directory:
   ```bash
   cd infra
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Plan the deployment:
   ```bash
   terraform plan \
     -var="openai_api_key=your-openai-api-key" \
     -var="image_tag_user=latest" \
     -var="image_tag_group=latest" \
     -var="image_tag_gateway=latest" \
     -var="image_tag_files=latest" \
     -var="image_tag_genai=latest"
   ```

4. Apply the configuration:
   ```bash
   terraform apply \
     -var="openai_api_key=your-openai-api-key" \
     -var="image_tag_user=latest" \
     -var="image_tag_group=latest" \
     -var="image_tag_gateway=latest" \
     -var="image_tag_files=latest" \
     -var="image_tag_genai=latest"
   ```

## CI/CD Deployment

The unified CI/CD pipeline in `.github/workflows/server-ci-cd.yml` handles:

1. **Building and Testing**:
   - Java services (Gradle build + tests)
   - GenAI service (Python tests)

2. **Docker Image Building**:
   - Builds and pushes all service images to GHCR
   - Tags with both `latest` and commit SHA

3. **Terraform Deployment**:
   - Deploys all services using Terraform
   - Uses commit SHA for image tags

### Required GitHub Secrets

Set these in your GitHub repository settings:

- `KUBE_CONFIG_DATA`: Base64 encoded kubeconfig file
- `OPENAI_API_KEY`: Your OpenAI API key

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                   Namespace: developmentv1                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Gateway       │    │   User Service  │                │
│  │   Port: 8080    │    │   Port: 8081    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  Group Service  │    │  Files Service  │                │
│  │   Port: 8083    │    │   Port: 8082    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   GenAI App     │    │ Celery Worker   │                │
│  │   Port: 8000    │    │  (Background)   │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │     MySQL       │    │     Redis       │                │
│  │   Port: 3306    │    │   Port: 6379    │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
│  ┌─────────────────┐                                       │
│  │    Weaviate     │                                       │
│  │   Port: 8080    │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

## Service Dependencies

- **Gateway** → User, Group, Files, GenAI services
- **Group Service** → MySQL, GenAI service  
- **User Service** → MySQL
- **Files Service** → MySQL
- **GenAI App** → Weaviate, Redis, OpenAI API
- **Celery Worker** → GenAI App, Redis

## Verification

After deployment, verify everything is working:

1. **Check pod status**:
   ```bash
   kubectl get pods -n developmentv1
   ```

2. **Check services**:
   ```bash
   kubectl get services -n developmentv1
   ```

3. **Check logs** (if issues):
   ```bash
   kubectl logs -l app=genai-app -n developmentv1
   kubectl logs -l app=gateway-service -n developmentv1
   ```

4. **Port forward for testing**:
   ```bash
   # Gateway (main entry point)
   kubectl port-forward svc/gateway-service 8080:8080 -n developmentv1
   
   # GenAI service directly
   kubectl port-forward svc/genai-app-service 8000:8000 -n developmentv1
   ```

## Migration from Helm

If you previously used Helm for GenAI deployment:

1. The deployment script automatically cleans up old Helm releases
2. Old genai-ci-cd.yml workflow is disabled  
3. Everything now goes through the unified terraform approach

## Troubleshooting

### Common Issues

1. **"Secret already exists" error**:
   ```bash
   kubectl delete secret openai-credentials -n developmentv1
   terraform apply -auto-approve
   ```

2. **Service conflicts**:
   ```bash
   # Clean up conflicting resources
   kubectl delete deployment,service -l app=genai-app -n developmentv1
   terraform apply -auto-approve
   ```

3. **Images not found**:
   - Ensure CI/CD has run and pushed images to GHCR
   - Check image tags in terraform variables

### Resource Cleanup

To completely remove the deployment:

```bash
cd infra
terraform destroy -auto-approve
```

## Development Workflow

1. **Local Development**: Use `docker-compose.yml`
2. **Feature Branch**: Push to trigger CI/CD build
3. **Main Branch**: Automatic deployment to `developmentv1` namespace
4. **Production**: Adjust terraform variables for production namespace

## Configuration

Key configuration files:
- `infra/variables.tf`: Terraform variables
- `infra/genai.tf`: GenAI service definitions  
- `infra/deployments.tf`: Java service definitions
- `infra/secrets.tf`: Environment secrets
- `.github/workflows/server-ci-cd.yml`: CI/CD pipeline 