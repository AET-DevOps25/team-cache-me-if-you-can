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
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
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
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
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
          resources {
            requests = {
              memory = "256Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "1Gi" # Increase memory for large file handling
              cpu    = "500m"
            }
          }
        }
      }
    }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
  }
}

resource "kubernetes_deployment" "files" {
  metadata {
    name      = "files-service"
    namespace = var.namespace
    labels    = { app = "files-service" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "files-service" } }
    template {
      metadata { labels = { app = "files-service" } }
      spec {
        # mount a directory for uploads (ephemeral emptyDir)
        volume {
          name = "uploads"
          empty_dir {}
        }

        container {
          name  = "files-service"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/files-service:${var.image_tag_files}"
          port {
            container_port = 8082
          }

          env_from {
            secret_ref {
              name = kubernetes_secret.files_env.metadata[0].name
            }
          }

          # expose the upload volume
          volume_mount {
            name       = "uploads"
            mount_path = "/uploads"
          }

          readiness_probe {
            http_get {
              path = "/actuator/health"
              port = 8082
            }
            initial_delay_seconds = 10
            period_seconds        = 5
          }
          resources {
            requests = {
              memory = "256Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "1Gi"
              cpu    = "500m"
            }
        }
      }
    }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
  }
}

resource "kubernetes_deployment" "client" {
  metadata {
    name      = "client"
    namespace = var.namespace
    labels    = { app = "client" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "client" } }
    template {
      metadata { labels = { app = "client" } }
      spec {
        container {
          name  = "client"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client:${var.image_tag_client}"
          port {
            container_port = 3000
            name          = "http"
          }

          # Liveness probe to check if container is alive
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

          # Readiness probe to check if container is ready
          readiness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }
        }
      }
    }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
  }
}