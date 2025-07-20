# ===================================
# TERRAFORM OUTPUTS
# ===================================

# Service Names
output "user_service_name" {
  description = "Name of the user service"
  value       = kubernetes_service.user.metadata[0].name
}

output "group_service_name" {
  description = "Name of the group service"
  value       = kubernetes_service.group.metadata[0].name
}

output "gateway_service_name" {
  description = "Name of the gateway service"  
  value       = kubernetes_service.gateway.metadata[0].name
}

output "files_service_name" {
  description = "Name of the files service"
  value       = kubernetes_service.files.metadata[0].name
}

output "genai_service_name" {
  description = "Name of the GenAI service"
  value       = kubernetes_service.genai_app.metadata[0].name
}

output "client_service_name" {
  description = "Name of the client service"
  value       = kubernetes_service.client.metadata[0].name
}

# Application URLs
output "client_ingress_url" {
  description = "URL to access the client application"
  value       = "https://cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
}

output "genai_ingress_url" {
  description = "URL to access the GenAI API"
  value       = "https://genai-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
}

output "grafana_ingress_url" {
  description = "URL to access Grafana monitoring"
  value       = "https://grafana-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
}

output "prometheus_ingress_url" {
  description = "URL to access Prometheus monitoring"
  value       = "https://prometheus-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
}

output "loki_ingress_url" {
  description = "URL to access Loki logs"
  value       = "https://loki-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
}

# Environment Information
output "deployment_environment" {
  description = "The environment namespace where services are deployed"
  value       = var.namespace
}

output "spring_profile" {
  description = "Active Spring profile for Java services"
  value       = var.spring_profile
}

# Deployment Summary
output "deployment_summary" {
  description = "Complete deployment summary with all access information"
  value = <<-EOT
    🚀 Deployment Complete!
    
    Environment: ${var.namespace}
    Spring Profile: ${var.spring_profile}
    
    🌐 Application URLs:
    - Frontend: https://cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de
    - GenAI API: https://genai-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de
    - Grafana: https://grafana-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de
    - Prometheus: https://prometheus-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de
    - Loki: https://loki-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de
    
    📊 Monitoring Credentials:
    - Username: admin
    - Password: password
    
    🔧 Services Deployed:
    - user-service (${kubernetes_service.user.metadata[0].name})
    - group-service (${kubernetes_service.group.metadata[0].name})  
    - gateway-service (${kubernetes_service.gateway.metadata[0].name})
    - files-service (${kubernetes_service.files.metadata[0].name})
    - genai-app-service (${kubernetes_service.genai_app.metadata[0].name})
    - client-service (${kubernetes_service.client.metadata[0].name})
  EOT
}
