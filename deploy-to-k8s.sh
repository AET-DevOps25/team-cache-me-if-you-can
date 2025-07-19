#!/bin/bash

# Kubernetes Deployment Script
# This script helps transition from helm+terraform to unified terraform deployment

set -e

NAMESPACE="developmentv1"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

echo "🚀 Kubernetes Deployment Script"
echo "==============================="

# Check if required tools are installed
check_dependencies() {
    echo "Checking dependencies..."
    
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install kubectl"
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        echo "❌ terraform not found. Please install terraform"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        echo "❌ helm not found (needed for cleanup). Please install helm"
        exit 1
    fi
    
    echo "✅ All dependencies found"
}

# Check cluster access
check_cluster_access() {
    echo "Checking cluster access..."
    
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo "❌ Cannot access namespace '$NAMESPACE'. Please check your kubeconfig"
        exit 1
    fi
    
    echo "✅ Cluster access confirmed"
}

# Clean up existing helm deployments that might conflict
cleanup_helm_deployments() {
    echo "Cleaning up conflicting helm deployments..."
    
    # Check if genai helm release exists
    if helm list -n $NAMESPACE | grep -q "genai-dev"; then
        echo "🧹 Removing existing genai-dev helm release..."
        helm uninstall genai-dev -n $NAMESPACE || echo "⚠️  Failed to uninstall genai-dev (might not exist)"
    fi
    
    # Check for other conflicting helm releases
    for service in user group gateway files; do
        if helm list -n $NAMESPACE | grep -q "${service}-service"; then
            echo "🧹 Removing existing ${service}-service helm release..."
            helm uninstall ${service}-service -n $NAMESPACE || echo "⚠️  Failed to uninstall ${service}-service"
        fi
    done
    
    echo "✅ Helm cleanup completed"
}

# Clean up old k8s resources that might conflict
cleanup_old_resources() {
    echo "Cleaning up old Kubernetes resources..."
    
    # List of resources that might conflict and should be removed
    OLD_RESOURCES=(
        "deployment/genai-dev-genai-app"
        "deployment/genai-dev-celery-worker"
        "deployment/genai-dev-redis"
        "deployment/genai-dev-weaviate"
        "service/genai-dev-genai-app-service"
        "service/genai-dev-redis"
        "service/genai-dev-weaviate-service"
    )
    
    for resource in "${OLD_RESOURCES[@]}"; do
        if kubectl get $resource -n $NAMESPACE &> /dev/null; then
            echo "🧹 Removing old resource: $resource"
            kubectl delete $resource -n $NAMESPACE --ignore-not-found=true
        fi
    done
    
    echo "✅ Old resource cleanup completed"
}

# Deploy with terraform
deploy_terraform() {
    echo "Deploying with Terraform..."
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ OPENAI_API_KEY environment variable is required"
        echo "Please set it with: export OPENAI_API_KEY='your-key-here'"
        exit 1
    fi
    
    cd infra
    
    echo "🔧 Initializing Terraform..."
    terraform init
    
    echo "📋 Planning Terraform deployment..."
    terraform plan \
        -var="openai_api_key=$OPENAI_API_KEY" \
        -var="image_tag_user=latest" \
        -var="image_tag_group=latest" \
        -var="image_tag_gateway=latest" \
        -var="image_tag_files=latest" \
        -var="image_tag_genai=latest"
    
    echo "🚀 Applying Terraform configuration..."
    terraform apply \
        -auto-approve \
        -var="openai_api_key=$OPENAI_API_KEY" \
        -var="image_tag_user=latest" \
        -var="image_tag_group=latest" \
        -var="image_tag_gateway=latest" \
        -var="image_tag_files=latest" \
        -var="image_tag_genai=latest"
    
    cd ..
    echo "✅ Terraform deployment completed"
}

# Verify deployment
verify_deployment() {
    echo "Verifying deployment..."
    
    # Wait for pods to be ready
    echo "⏳ Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=genai-app -n $NAMESPACE --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=user-service -n $NAMESPACE --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=gateway-service -n $NAMESPACE --timeout=300s || true
    
    echo "📊 Deployment status:"
    kubectl get pods -n $NAMESPACE
    echo ""
    kubectl get services -n $NAMESPACE
    
    echo "✅ Deployment verification completed"
}

# Main execution
main() {
    echo "Starting deployment process..."
    
    check_dependencies
    check_cluster_access
    cleanup_helm_deployments
    cleanup_old_resources
    deploy_terraform
    verify_deployment
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Check that all pods are running: kubectl get pods -n $NAMESPACE"
    echo "2. Check services: kubectl get services -n $NAMESPACE"
    echo "3. Test your applications"
    echo ""
    echo "To access your services locally, you can use port-forwarding:"
    echo "  kubectl port-forward svc/gateway-service 8080:8080 -n $NAMESPACE"
    echo "  kubectl port-forward svc/genai-app-service 8000:8000 -n $NAMESPACE"
}

# Run main function
main "$@" 