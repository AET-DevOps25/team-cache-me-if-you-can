resource "kubernetes_service" "user" {
  metadata {
    name      = "user-service"
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
  
  lifecycle {
    ignore_changes = [metadata[0].labels, metadata[0].annotations]
    create_before_destroy = true
  }
}

resource "kubernetes_service" "group" {
  metadata {
    name      = "group-service"
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
  
  lifecycle {
    ignore_changes = [metadata[0].labels, metadata[0].annotations]
    create_before_destroy = true
  }
}

# Alias service for group - needed for gateway compatibility
# The gateway code uses hardcoded "http://group:8083" URLs
resource "kubernetes_service" "group_alias" {
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

resource "kubernetes_service" "files" {
  metadata {
    name      = "files-service"
    namespace = var.namespace
    labels    = { app = "files-service" }
  }
  spec {
    selector = { app = "files-service" }
    port {
      port        = 8082
      target_port = 8082
    }
    type = "ClusterIP"
  }
}
