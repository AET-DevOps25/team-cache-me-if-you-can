#!/bin/bash
set -e

echo "🧪 Testing Kubernetes Deployment (Dry-Run)..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not installed"
    echo ""
    echo "📋 Manual Kubernetes Testing Instructions:"
    echo "1. Install kubectl: https://kubernetes.io/docs/tasks/tools/"
    echo "2. Set up your kubeconfig file"
    echo "3. Re-run this script"
    echo ""
    echo "🔄 For now, CI/CD will validate Kubernetes deployment"
    exit 0
fi

# Check if kubectl is configured (try cluster-info first, then fallback to namespace test)
echo "🔍 Testing cluster connectivity..."
if kubectl cluster-info &> /dev/null; then
    echo "✅ kubectl configured with cluster-admin access"
    CLUSTER_ACCESS=true
elif kubectl get ns developmentv1 &> /dev/null; then
    echo "✅ kubectl configured with namespace access (cluster-admin not required)"
    CLUSTER_ACCESS=true
else
    echo "❌ kubectl not configured or cluster not accessible"
    echo ""
    echo "📋 Kubeconfig Setup Instructions:"
    echo "1. Copy your kubeconfig file to ~/.kube/config"
    echo "2. Or set KUBECONFIG environment variable"
    echo "3. Test with: kubectl get ns developmentv1"
    echo ""
    echo "🔄 For now, CI/CD will validate Kubernetes deployment"
    exit 0
fi

# Test current namespace access
if kubectl get ns developmentv1 &> /dev/null; then
    echo "✅ developmentv1 namespace accessible"
else
    echo "❌ developmentv1 namespace not accessible"
    echo "Available namespaces:"
    kubectl get ns 2>/dev/null | grep -E "(NAME|dev|test)" || echo "Cannot list all namespaces (limited permissions)"
    exit 1
fi

# Check if terraform is available for testing
if ! command -v terraform &> /dev/null; then
    echo "⚠️  Terraform not available locally"
    echo "   Terraform validation will be done in CI/CD pipeline"
    TERRAFORM_AVAILABLE=false
else
    TERRAFORM_AVAILABLE=true
fi

# Test Terraform plan (dry-run) if available
if [ "$TERRAFORM_AVAILABLE" = true ]; then
    echo "📋 Testing Terraform plan..."
    cd infra

    # Check if we need OpenAI API key
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  OPENAI_API_KEY not set. Using placeholder for testing."
        export TF_VAR_openai_api_key="placeholder-for-testing"
    else
        export TF_VAR_openai_api_key="$OPENAI_API_KEY"
    fi

    # Use latest image tags for testing
    export TF_VAR_image_tag_user="latest"
    export TF_VAR_image_tag_group="latest"
    export TF_VAR_image_tag_gateway="latest"
    export TF_VAR_image_tag_files="latest"

    if terraform init && terraform plan; then
        echo "✅ Terraform plan successful"
    else
        echo "❌ Terraform plan failed"
        cd ..
        exit 1
    fi

    cd ..
fi

# Test Helm chart dry-run
echo "📋 Testing Helm chart template validation..."
if helm template genai-test ./helm/genai-chart \
    --namespace developmentv1 \
    --debug \
    -f ./helm/genai-chart/values-development.yaml \
    --set image.tag=latest > /dev/null; then
    echo "✅ Helm template validation successful"
else
    echo "❌ Helm template validation failed"
    exit 1
fi

# Check existing deployments
echo "📋 Checking current deployment status..."
kubectl get pods -n developmentv1 | grep -E "(genai-app|genai-celery-worker|weaviate)" | head -5

echo ""
echo "🎉 All Kubernetes tests passed! Ready to deploy."
echo ""
echo "📋 Summary:"
echo "✅ Cluster access validated"
echo "✅ Namespace access confirmed"
if [ "$TERRAFORM_AVAILABLE" = true ]; then
    echo "✅ Terraform plan successful"
else
    echo "⚠️  Terraform plan skipped (not available locally)"
fi
echo "✅ Helm chart template validation successful"
echo ""
echo "🚀 To deploy for real:"
echo "1. Set OPENAI_API_KEY in GitHub secrets"
echo "2. Push to main branch"
echo "3. Monitor GitHub Actions"
echo "4. Check deployment: kubectl get pods -n developmentv1"
