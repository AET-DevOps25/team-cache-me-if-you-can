# Commenting out Redis deployment - using existing Redis pod
# resource "kubernetes_deployment" "genai_redis" {
#   metadata {
#     name      = "genai-redis"
#     namespace = var.namespace
#     labels    = { app = "genai-redis" }
#   }
#   spec {
#     replicas = 1
#     selector { match_labels = { app = "genai-redis" } }
#     template {
#       metadata { labels = { app = "genai-redis" } }
#       spec {
#         container {
#           name  = "redis"
#           image = "redis:7-alpine"
#           port {
#             container_port = 6379
#           }
#         }
#       }
#     }
#   }
# }

# Using existing Redis service instead of creating new one
# resource "kubernetes_service" "genai_redis" {
#   metadata {
#     name      = "genai-redis"
#     namespace = var.namespace
#     labels    = { app = "genai-redis" }
#   }
#   spec {
#     selector = { app = "genai-redis" }
#     port {
#       port        = 6379
#       target_port = 6379
#     }
#     type = "ClusterIP"
#   }
# }

# Commenting out Weaviate deployment - using existing Weaviate pod
# resource "kubernetes_deployment" "weaviate" {
#   metadata {
#     name      = "genai-weaviate"
#     namespace = var.namespace
#     labels    = { app = "genai-weaviate" }
#   }
#   spec {
#     replicas = 1
#     selector { match_labels = { app = "genai-weaviate" } }
#     template {
#       metadata { labels = { app = "genai-weaviate" } }
#       spec {
#         volume {
#           name = "weaviate-data"
#           empty_dir {}
#         }
#         
#         container {
#           name  = "weaviate"
#           image = "semitechnologies/weaviate:1.23.7"
#           port {
#             container_port = 8080
#           }
#           port {
#             container_port = 50051
#           }
#           
#           volume_mount {
#             name       = "weaviate-data"
#             mount_path = "/var/lib/weaviate"
#           }
#           
#           env_from {
#             secret_ref {
#               name = kubernetes_secret.openai_credentials.metadata[0].name
#             }
#           }
#           
#           env {
#             name  = "QUERY_DEFAULTS_LIMIT"
#             value = "25"
#           }
#           env {
#             name  = "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED"
#             value = "true"
#           }
#           env {
#             name  = "PERSISTENCE_DATA_PATH"
#             value = "/var/lib/weaviate"
#           }
#           env {
#             name  = "DEFAULT_VECTORIZER_MODULE"
#             value = "text2vec-openai"
#           }
#           env {
#             name  = "ENABLE_MODULES"
#             value = "text2vec-openai,generative-openai"
#           }
#           env {
#             name  = "CLUSTER_HOSTNAME"
#             value = "node1"
#           }
#         }
#       }
#     }
#   }
# }

# Using existing Weaviate service instead of creating new one
# resource "kubernetes_service" "weaviate" {
#   metadata {
#     name      = "genai-weaviate"
#     namespace = var.namespace
#     labels    = { app = "genai-weaviate" }
#   }
#   spec {
#     selector = { app = "genai-weaviate" }
#     port {
#       name        = "http"
#       port        = 8080
#       target_port = 8080
#     }
#     port {
#       name        = "grpc"
#       port        = 50051
#       target_port = 50051
#     }
#     type = "ClusterIP"
#   }
# }

# GenAI App deployment
resource "kubernetes_deployment" "genai_app" {
  metadata {
    name      = "genai-app"
    namespace = var.namespace
    labels    = { app = "genai-app" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "genai-app" } }
    template {
      metadata { 
        labels = { app = "genai-app" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/path"   = "/metrics"
          "prometheus.io/port"   = "8000"
        }
      }
      spec {
        container {
          name  = "genai-app"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/genai-app:${var.image_tag_genai}"
          port {
            container_port = 8000
          }
          
          env_from {
            secret_ref {
              name = kubernetes_secret.openai_credentials.metadata[0].name
            }
          }
          
          env {
            name  = "WEAVIATE_URL"
            value = "http://weaviate-service:8080"
          }
          env {
            name  = "CELERY_BROKER_URL"
            value = "redis://redis:6379/0"
          }
          env {
            name  = "CELERY_RESULT_BACKEND"
            value = "redis://redis:6379/0"
          }
          
          command = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
          
          readiness_probe {
            http_get {
              path = "/api/v1/health"
              port = 8000
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
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
  }
}

resource "kubernetes_service" "genai_app" {
  metadata {
    name      = "genai-app-service"
    namespace = var.namespace
    labels    = { app = "genai-app" }
  }
  spec {
    selector = { app = "genai-app" }
    port {
      port        = 8000
      target_port = 8000
    }
    type = "ClusterIP"
  }
}

# GenAI Celery Worker deployment
resource "kubernetes_deployment" "genai_celery_worker" {
  metadata {
    name      = "genai-celery-worker"
    namespace = var.namespace
    labels    = { app = "genai-celery-worker" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "genai-celery-worker" } }
    template {
      metadata { labels = { app = "genai-celery-worker" } }
      spec {
        container {
          name  = "genai-celery-worker"
          image = "ghcr.io/aet-devops25/team-cache-me-if-you-can/genai-app:${var.image_tag_genai}"
          
          env_from {
            secret_ref {
              name = kubernetes_secret.openai_credentials.metadata[0].name
            }
          }
          
          env {
            name  = "WEAVIATE_URL"
            value = "http://weaviate-service:8080"
          }
          env {
            name  = "CELERY_BROKER_URL"
            value = "redis://redis:6379/0"
          }
          env {
            name  = "CELERY_RESULT_BACKEND"
            value = "redis://redis:6379/0"
          }
          
          command = ["celery", "-A", "app.celery_app:celery_app", "worker", "--loglevel=info"]
        }
      }
    }
  }
  
  depends_on = [
    kubernetes_deployment.genai_app
  ]
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations,
      spec[0].template[0].spec[0].container[0].termination_message_path,
      spec[0].template[0].spec[0].container[0].termination_message_policy
    ]
  }
} 