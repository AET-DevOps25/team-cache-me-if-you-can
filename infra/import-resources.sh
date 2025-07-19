#!/bin/bash

# Import existing Kubernetes resources into Terraform state
# Run this script from the infra/ directory

set -e

NAMESPACE="developmentv1"

echo "=== Terraform Resource Import Script ==="
echo "This script will import existing Kubernetes resources into Terraform state"
echo "Namespace: $NAMESPACE"
echo ""

# Function to check if a Kubernetes resource exists and import it
import_if_exists() {
  local resource_type=$1
  local resource_name=$2
  local terraform_resource=$3
  
  echo "Checking $resource_type/$resource_name..."
  if kubectl get $resource_type $resource_name -n $NAMESPACE >/dev/null 2>&1; then
    echo "✅ Found $resource_type/$resource_name - attempting import"
    if terraform import $terraform_resource $NAMESPACE/$resource_name 2>/dev/null; then
      echo "✅ Successfully imported $terraform_resource"
    else
      echo "⚠️  Import failed for $terraform_resource (may already be in state)"
    fi
  else
    echo "❌ $resource_type/$resource_name not found - will be created by Terraform"
  fi
  echo ""
}

# Initialize Terraform if needed
if [ ! -d ".terraform" ]; then
  echo "Initializing Terraform..."
  terraform init
  echo ""
fi

echo "=== Importing Services ==="
import_if_exists "service" "user-service" "kubernetes_service.user"
import_if_exists "service" "group-service" "kubernetes_service.group"
import_if_exists "service" "group" "kubernetes_service.group_alias"
import_if_exists "service" "gateway-service" "kubernetes_service.gateway"
import_if_exists "service" "files-service" "kubernetes_service.files"
import_if_exists "service" "genai-app-service" "kubernetes_service.genai_app"

echo "=== Importing Deployments ==="
import_if_exists "deployment" "user-service" "kubernetes_deployment.user"
import_if_exists "deployment" "group-service" "kubernetes_deployment.group"
import_if_exists "deployment" "gateway-service" "kubernetes_deployment.gateway"
import_if_exists "deployment" "files-service" "kubernetes_deployment.files"
import_if_exists "deployment" "genai-app" "kubernetes_deployment.genai_app"
import_if_exists "deployment" "genai-celery-worker" "kubernetes_deployment.genai_celery_worker"

echo "=== Importing Secrets ==="
import_if_exists "secret" "user-env-secret" "kubernetes_secret.user_env"
import_if_exists "secret" "group-env-secret" "kubernetes_secret.group_env"
import_if_exists "secret" "gateway-env-secret" "kubernetes_secret.gateway_env"
import_if_exists "secret" "files-env-secret" "kubernetes_secret.files_env"
import_if_exists "secret" "openai-credentials" "kubernetes_secret.openai_credentials"

echo "=== Import completed! ==="
echo ""
echo "Next steps:"
echo "1. Run 'terraform plan' to see what changes are needed"
echo "2. Run 'terraform apply' to apply any remaining changes"
echo ""
echo "Note: Some resources might show changes due to configuration drift."
echo "This is normal - Terraform will reconcile them to match your configuration." 