
resource "kubernetes_deployment" "user" {
  metadata {
    name      = "user-service"
    namespace = var.namespace
    labels    = { app = "user-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "user-service" } }
    template {
      metadata { labels = { app = "user-service" } }
      spec {
        container {
          name  = "user-service"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/user-service:${var.image_tag_user}"
          # <-- Use 'port', not 'ports'
          port {
            container_port = 8081
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.user_env.metadata[0].name
            }
          }

          readiness_probe {
            http_get {
              path = "/actuator/health"
              port = 8081
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "group" {
  metadata {
    name      = "group-service"
    namespace = var.namespace
    labels    = { app = "group-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "group-service" } }
    template {
      metadata { labels = { app = "group-service" } }
      spec {
        container {
          name  = "group-service"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/group-service:${var.image_tag_group}"
          port {
            container_port = 8083
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.group_env.metadata[0].name
            }
          }

          readiness_probe {
            http_get {
              path = "/actuator/health"
              port = 8083
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }
        }
      }
    }
  }
}

resource "kubernetes_deployment" "gateway" {
  metadata {
    name      = "gateway-service"
    namespace = var.namespace
    labels    = { app = "gateway-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "gateway-service" } }
    template {
      metadata { labels = { app = "gateway-service" } }
      spec {
        container {
          name  = "gateway-service"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/gateway-service:${var.image_tag_gateway}"
          port {
            container_port = 8080
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.gateway_env.metadata[0].name
            }
          }

          readiness_probe {
            http_get {
              path = "/actuator/health/readiness"
              port = 8080
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }
        }
      }
    }
  }
}
