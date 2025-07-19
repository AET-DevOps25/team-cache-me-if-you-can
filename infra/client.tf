# ===================================
# CLIENT DEPLOYMENT
# ===================================

resource "kubernetes_deployment" "client" {
  metadata {
    name      = "client"
    namespace = var.namespace
    labels = {
      app = "client"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "client"
      }
    }

    template {
      metadata {
        labels = {
          app = "client"
        }
      }

      spec {
        container {
          name  = "client"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client:${var.image_tag_client}"
          image_pull_policy = "Always"

          port {
            container_port = 3000
          }

          # Health checks
          readiness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }

          resources {
            requests = {
              memory = "64Mi"
              cpu    = "50m"
            }
            limits = {
              memory = "256Mi"
              cpu    = "200m"
            }
          }
        }
      }
    }
  }

  # Ignore metadata managed by k8s
  lifecycle {
    ignore_changes = [
      metadata[0].resource_version,
      metadata[0].generation,
      spec[0].template[0].metadata[0].annotations,
    ]
  }
}

resource "kubernetes_service" "client" {
  metadata {
    name      = "client-service"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "client"
    }

    port {
      protocol    = "TCP"
      port        = 3000
      target_port = 3000
    }

    type = "ClusterIP"
  }
}

# Client Ingress for external access
resource "kubernetes_ingress_v1" "client_ingress" {
  metadata {
    name      = "client-ingress"
    namespace = var.namespace
    annotations = {
      "cert-manager.io/cluster-issuer"                 = "letsencrypt-prod"
      "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
    }
  }

  spec {
    ingress_class_name = "nginx"

    tls {
      hosts       = ["developmentv1-client.student.k8s.aet.cit.tum.de"]
      secret_name = "cache-me-if-you-can-client-tls"
    }

    rule {
      host = "developmentv1-client.student.k8s.aet.cit.tum.de"

      http {
        # API routes go to gateway
        path {
          path      = "/api/"
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

        # Everything else goes to client
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