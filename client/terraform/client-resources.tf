# Deployment
resource "kubernetes_deployment" "client" {
  metadata {
    name      = "client"
    namespace = "developmentv1"
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
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client:amd64-latest"
          image_pull_policy = "Always"

          port {
            container_port = 3000
          }
        }
      }
    }
  }
}

# Service
resource "kubernetes_service" "client_service" {
  metadata {
    name      = "client-service"
    namespace = "developmentv1"
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

# Ingress
resource "kubernetes_ingress_v1" "client_ingress" {
  metadata {
    name      = "client-ingress"
    namespace = "developmentv1"
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
        path {
          path      = "/api/"
          path_type = "Prefix"

          backend {
            service {
              name = "gateway-service"
              port {
                number = 8080
              }
            }
          }
        }

        path {
          path      = "/"
          path_type = "Prefix"

          backend {
            service {
              name = kubernetes_service.client_service.metadata[0].name
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
