resource "kubernetes_service" "user" {
  metadata {
    name      = "user"
    namespace = var.namespace
    labels    = { app = "user-service" }
  }
  spec {
    selector = { app = "user-service" }
    port {
      port        = 8081
      target_port = 8081
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_service" "group" {
  metadata {
    name      = "group"
    namespace = var.namespace
    labels    = { app = "group-service" }
  }
  spec {
    selector = { app = "group-service" }
    port {
      port        = 8083
      target_port = 8083
    }
    type = "ClusterIP"
  }
}

resource "kubernetes_service" "gateway" {
  metadata {
    name      = "gateway-service"
    namespace = var.namespace
    labels    = { app = "gateway-service" }
  }
  spec {
    selector = { app = "gateway-service" }
    port {
      port        = 8080
      target_port = 8080
    }
    type = "ClusterIP"
  }
}
