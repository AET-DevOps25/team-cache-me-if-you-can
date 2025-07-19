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
      hosts       = ["grafana-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "grafana-dev-tls"
    }

    rule {
      host = "grafana-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

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
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["genai-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "genai-dev-tls"
    }

    rule {
      host = "genai-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

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
      hosts       = ["prometheus-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"]
      secret_name = "prometheus-dev-tls"
    }

    rule {
      host = "prometheus-developmentv1.team-cache-me-if-you-can.student.k8s.aet.cit.tum.de"

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