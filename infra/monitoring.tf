# ===================================
# MONITORING STACK TERRAFORM CONFIG
# ===================================

# Prometheus ConfigMap
resource "kubernetes_config_map" "prometheus_config" {
  metadata {
    name      = "prometheus-config"
    namespace = var.namespace
    labels    = { app = "prometheus" }
  }

  data = {
    "prometheus.yml" = file("${path.module}/../environment/prometheus/prometheus.yml")
  }
}

# Prometheus Deployment
resource "kubernetes_deployment" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = var.namespace
    labels    = { app = "prometheus" }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations
    ]
  }

  spec {
    replicas = 1
    selector { match_labels = { app = "prometheus" } }
    template {
      metadata { 
        labels = { app = "prometheus" }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/path"   = "/metrics"
          "prometheus.io/port"   = "9090"
        }
      }
      spec {
        volume {
          name = "prometheus-config"
          config_map {
            name = kubernetes_config_map.prometheus_config.metadata[0].name
          }
        }
        
        container {
          name  = "prometheus"
          image = "prom/prometheus:v2.37.0"
          
          args = [
            "--config.file=/etc/prometheus/prometheus.yml",
            "--storage.tsdb.path=/prometheus/",
            "--web.console.libraries=/etc/prometheus/console_libraries",
            "--web.console.templates=/etc/prometheus/consoles",
            "--storage.tsdb.retention.time=200h",
            "--web.enable-lifecycle"
          ]
          
          port {
            container_port = 9090
            name          = "web"
          }
          
          volume_mount {
            name       = "prometheus-config"
            mount_path = "/etc/prometheus"
          }
          
          resources {
            requests = {
              memory = "400Mi"
              cpu    = "200m"
            }
            limits = {
              memory = "1Gi"
              cpu    = "1000m"
            }
          }
        }
      }
    }
  }
}

# Prometheus Service
resource "kubernetes_service" "prometheus" {
  metadata {
    name      = "prometheus"
    namespace = var.namespace
    labels    = { app = "prometheus" }
  }
  spec {
    selector = { app = "prometheus" }
    port {
      port        = 9090
      target_port = 9090
      name        = "web"
    }
    type = "ClusterIP"
  }
}

# Loki ConfigMap
resource "kubernetes_config_map" "loki_config" {
  metadata {
    name      = "loki-config"
    namespace = var.namespace
    labels    = { app = "loki" }
  }

  data = {
    "loki-config.yaml" = file("${path.module}/../environment/loki/loki-config.yaml")
  }
}

# Loki Deployment
resource "kubernetes_deployment" "loki" {
  metadata {
    name      = "loki"
    namespace = var.namespace
    labels    = { app = "loki" }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations
    ]
  }

  spec {
    replicas = 1
    selector { match_labels = { app = "loki" } }
    template {
      metadata { labels = { app = "loki" } }
      spec {
        volume {
          name = "loki-config"
          config_map {
            name = kubernetes_config_map.loki_config.metadata[0].name
          }
        }
        
        volume {
          name = "loki-data"
          empty_dir {}
        }
        
        container {
          name  = "loki"
          image = "grafana/loki:2.6.1"
          
          args = [
            "-config.file=/etc/loki/loki-config.yaml"
          ]
          
          port {
            container_port = 3100
            name          = "http-metrics"
          }
          
          volume_mount {
            name       = "loki-config"
            mount_path = "/etc/loki"
          }
          
          volume_mount {
            name       = "loki-data"
            mount_path = "/tmp/loki"
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
}

# Loki Service
resource "kubernetes_service" "loki" {
  metadata {
    name      = "loki"
    namespace = var.namespace
    labels    = { app = "loki" }
  }
  spec {
    selector = { app = "loki" }
    port {
      port        = 3100
      target_port = 3100
      name        = "http-metrics"
    }
    type = "ClusterIP"
  }
}

# Promtail ConfigMap
resource "kubernetes_config_map" "promtail_config" {
  metadata {
    name      = "promtail-config"
    namespace = var.namespace
    labels    = { app = "promtail" }
  }

  data = {
    "promtail-config.yaml" = file("${path.module}/../environment/promtail/promtail-config.yaml")
  }
}

# Promtail ServiceAccount
resource "kubernetes_service_account" "promtail" {
  metadata {
    name      = "promtail"
    namespace = var.namespace
    labels    = { app = "promtail" }
  }
}

# Promtail Role (namespace-scoped instead of cluster-wide)
resource "kubernetes_role" "promtail" {
  metadata {
    name      = "promtail"
    namespace = var.namespace
    labels    = { app = "promtail" }
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/log"]
    verbs      = ["get", "watch", "list"]
  }
}

# Promtail RoleBinding (namespace-scoped)
resource "kubernetes_role_binding" "promtail" {
  metadata {
    name      = "promtail"
    namespace = var.namespace
    labels    = { app = "promtail" }
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.promtail.metadata[0].name
  }
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.promtail.metadata[0].name
    namespace = var.namespace
  }
}

# Promtail Deployment (simplified for namespace-only permissions)
resource "kubernetes_deployment" "promtail" {
  metadata {
    name      = "promtail"
    namespace = var.namespace
    labels    = { app = "promtail" }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations
    ]
  }

  spec {
    replicas = 1
    selector { match_labels = { app = "promtail" } }
    template {
      metadata { 
        labels = { app = "promtail" }
      }
      spec {
        service_account_name = kubernetes_service_account.promtail.metadata[0].name
        
        volume {
          name = "promtail-config"
          config_map {
            name = kubernetes_config_map.promtail_config.metadata[0].name
          }
        }
        
        container {
          name  = "promtail"
          image = "grafana/promtail:2.6.1"
          
          args = [
            "-config.file=/etc/promtail/promtail-config.yaml"
          ]
          
          volume_mount {
            name       = "promtail-config"
            mount_path = "/etc/promtail"
          }
          
          env {
            name  = "LOKI_URL"
            value = "http://loki:3100"
          }
          
          resources {
            requests = {
              memory = "128Mi"
              cpu    = "100m"
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
}

# Grafana ConfigMaps
resource "kubernetes_config_map" "grafana_datasources" {
  metadata {
    name      = "grafana-datasources"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }

  data = {
    for file in fileset("${path.module}/../environment/grafana/provisioning/datasources", "*.yml") :
    file => file("${path.module}/../environment/grafana/provisioning/datasources/${file}")
  }
}

resource "kubernetes_config_map" "grafana_dashboards_config" {
  metadata {
    name      = "grafana-dashboards-config"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }

  data = {
    for file in fileset("${path.module}/../environment/grafana/provisioning/dashboards", "*.yml") :
    file => file("${path.module}/../environment/grafana/provisioning/dashboards/${file}")
  }
}

# Grafana Dashboard JSON Files ConfigMap
resource "kubernetes_config_map" "grafana_dashboards_json" {
  metadata {
    name      = "grafana-dashboards-json"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }

  data = {
    for file in fileset("${path.module}/../environment/grafana/provisioning/dashboards", "*.json") :
    file => file("${path.module}/../environment/grafana/provisioning/dashboards/${file}")
  }
}

# Grafana Secret
resource "kubernetes_secret" "grafana_admin" {
  metadata {
    name      = "grafana-admin"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }

  data = {
    admin-password = "password"
  }
}

# Grafana Deployment
resource "kubernetes_deployment" "grafana" {
  metadata {
    name      = "grafana"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }
  
  lifecycle {
    ignore_changes = [
      spec[0].template[0].metadata[0].annotations
    ]
  }

  spec {
    replicas = 1
    selector { match_labels = { app = "grafana" } }
    template {
      metadata { labels = { app = "grafana" } }
      spec {
        volume {
          name = "grafana-datasources"
          config_map {
            name = kubernetes_config_map.grafana_datasources.metadata[0].name
          }
        }
        
        volume {
          name = "grafana-dashboards-config"
          config_map {
            name = kubernetes_config_map.grafana_dashboards_config.metadata[0].name
          }
        }
        
        volume {
          name = "grafana-dashboards-json"
          config_map {
            name = kubernetes_config_map.grafana_dashboards_json.metadata[0].name
          }
        }
        
        container {
          name  = "grafana"
          image = "grafana/grafana:9.1.0"
          
          port {
            container_port = 3000
            name          = "http-grafana"
          }
          
          env {
            name = "GF_SECURITY_ADMIN_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.grafana_admin.metadata[0].name
                key  = "admin-password"
              }
            }
          }
          
          volume_mount {
            name       = "grafana-datasources"
            mount_path = "/etc/grafana/provisioning/datasources"
          }
          
          volume_mount {
            name       = "grafana-dashboards-config"
            mount_path = "/etc/grafana/provisioning/dashboards"
          }
          
          volume_mount {
            name       = "grafana-dashboards-json"
            mount_path = "/var/lib/grafana/dashboards"
          }
          
          resources {
            requests = {
              memory = "128Mi"
              cpu    = "100m"
            }
            limits = {
              memory = "256Mi"
              cpu    = "500m"
            }
          }
        }
      }
    }
  }
}

# Grafana Service
resource "kubernetes_service" "grafana" {
  metadata {
    name      = "grafana"
    namespace = var.namespace
    labels    = { app = "grafana" }
  }
  spec {
    selector = { app = "grafana" }
    port {
      port        = 3000
      target_port = 3000
      name        = "http-grafana"
    }
    type = "ClusterIP"
  }
} 