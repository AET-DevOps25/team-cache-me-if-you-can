# ===================================
# CLIENT DEPLOYMENT TO KUBERNETES
# ===================================

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Variables
variable "redeploy_id" {
  description = "Unique ID to force redeployment"
  type        = string
  default     = "latest"
}

variable "namespace" {
  description = "Kubernetes namespace for deployment"
  type        = string
  default     = "devel"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

# Client Deployment
resource "kubernetes_deployment" "client" {
  metadata {
    name      = "client"
    namespace = var.namespace
    labels    = { 
      app = "client" 
      redeploy = var.redeploy_id
    }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations
    ]
  }

  spec {
    replicas = 1
    selector { match_labels = { app = "client" } }
    template {
      metadata { 
        labels = { 
          app = "client"
          redeploy = var.redeploy_id
        }
      }
      spec {
        container {
          name  = "client"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client:${var.image_tag}"
          
          port {
            container_port = 3000
            name          = "http"
          }
          
          resources {
            requests = {
              memory = "128Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }
          
          readiness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }
        }
      }
    }
  }
}

# Client Service
resource "kubernetes_service" "client" {
  metadata {
    name      = "client-service"
    namespace = var.namespace
    labels    = { app = "client" }
  }
  spec {
    selector = { app = "client" }
    port {
      port        = 3000
      target_port = 3000
      name        = "http"
    }
    type = "ClusterIP"
  }
}

# Client Ingress (for devel namespace)
resource "kubernetes_ingress_v1" "client_ingress" {
  metadata {
    name      = "client-ingress"
    namespace = var.namespace
    annotations = {
      "nginx.ingress.kubernetes.io/rewrite-target" = "/"
      "nginx.ingress.kubernetes.io/cors-allow-origin" = "*"
      "nginx.ingress.kubernetes.io/cors-allow-methods" = "GET, POST, PUT, DELETE, OPTIONS"
      "nginx.ingress.kubernetes.io/cors-allow-headers" = "Content-Type, Authorization"
    }
  }

  spec {
    ingress_class_name = "nginx"
    
    rule {
      host = "cache-me-if-you-can-client-devel.student.k8s.aet.cit.tum.de"
      http {
        path {
          path      = "/"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.client.metadata[0].name
              port {
                number = 3000
              }
            }
          }
        }
      }
    }
  }
}

# Outputs
output "client_service_name" {
  value = kubernetes_service.client.metadata[0].name
}

output "client_ingress_url" {
  value = "https://cache-me-if-you-can-client-devel.student.k8s.aet.cit.tum.de"
} 