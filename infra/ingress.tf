# ===================================
# INGRESS CONFIGURATION
# ===================================

# Grafana Ingress for external access
resource "kubernetes_ingress_v1" "grafana_ingress" {
  metadata {
    name      = "grafana-ingress"
    namespace = var.namespace
    annotations = {
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["grafana-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "grafana-${var.namespace}-tls"
    }

    rule {
      host = "grafana-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.grafana.metadata[0].name
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

# GenAI Ingress for external access
resource "kubernetes_ingress_v1" "genai_ingress" {
  metadata {
    name      = "genai-dev-ingress"
    namespace = var.namespace
    annotations = {
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "100m"
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["genai-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "genai-${var.namespace}-tls"
    }

    rule {
      host = "genai-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.genai_app.metadata[0].name
              port {
                number = 8000
              }
            }
          }
        }
      }
    }
  }
}

# Client API Ingress - Routes API calls to Gateway
resource "kubernetes_ingress_v1" "client_api_ingress" {
  metadata {
    name      = "client-api-ingress"
    namespace = var.namespace
    annotations = {
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "100m"
      # No rewrite target for API calls - pass them through as-is
    }
  }
  
  spec {
    ingress_class_name = "nginx"
    
    # TLS configuration
    tls {
      hosts       = ["cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "client-${var.namespace}-tls"
    }
    
    # Routing rules for API calls
    rule {
      host = "cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
      http {
        path {
          path      = "/api"
          path_type = "Prefix"
          backend {
            service {
              name = kubernetes_service.gateway.metadata[0].name
              port {
                number = 8080
              }
            }
          }
        }
      }
    }
  }
}

# Client Static Ingress - Serves static files from client
resource "kubernetes_ingress_v1" "client_ingress" {
  metadata {
    name      = "client-ingress"
    namespace = var.namespace
    annotations = {
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "100m"
    }
  }
  
  spec {
    ingress_class_name = "nginx"
    
    # TLS configuration
    tls {
      hosts       = ["cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "client-${var.namespace}-tls"
    }
    
    # Routing rules for static files
    rule {
      host = "cache-me-if-you-can-client-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"
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

# Prometheus Ingress for external access
resource "kubernetes_ingress_v1" "prometheus_ingress" {
  metadata {
    name      = "prometheus-ingress"
    namespace = var.namespace
    annotations = {
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["prometheus-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "prometheus-${var.namespace}-tls"
    }

    rule {
      host = "prometheus-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.prometheus.metadata[0].name
              port {
                number = 9090
              }
            }
          }
        }
      }
    }
  }
}

# Loki Ingress for external access
resource "kubernetes_ingress_v1" "loki_ingress" {
  metadata {
    name      = "loki-ingress"
    namespace = var.namespace
    annotations = {
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      "nginx.ingress.kubernetes.io/rewrite-target"     = "/"
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["loki-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "loki-${var.namespace}-tls"
    }

    rule {
      host = "loki-${var.namespace}.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

      http {
        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.loki.metadata[0].name
              port {
                number = 3100
              }
            }
          }
        }
      }
    }
  }
} 