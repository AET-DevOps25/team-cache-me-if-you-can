# Persistent Volume Claim for MySQL data
resource "kubernetes_persistent_volume_claim" "mysql_data" {
  metadata {
    name      = "mysql-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
  }
}

# ConfigMap to initialize databases and users
resource "kubernetes_config_map" "mysql_init" {
  metadata {
    name      = "mysql-initdb-config"
    namespace = var.namespace
  }
  data = {
    "init.sql" = <<-EOF
      CREATE DATABASE IF NOT EXISTS ${var.mysql_database_files};
      CREATE DATABASE IF NOT EXISTS ${var.mysql_database_user};
      CREATE DATABASE IF NOT EXISTS ${var.mysql_database_group};

      CREATE USER IF NOT EXISTS '${var.mysql_user_files}'@'%' IDENTIFIED BY '${var.mysql_password_files}';
      GRANT ALL PRIVILEGES ON ${var.mysql_database_files}.* TO '${var.mysql_user_files}'@'%';

      CREATE USER IF NOT EXISTS '${var.mysql_user_user}'@'%' IDENTIFIED BY '${var.mysql_password_user}';
      GRANT ALL PRIVILEGES ON ${var.mysql_database_user}.* TO '${var.mysql_user_user}'@'%';

      CREATE USER IF NOT EXISTS '${var.mysql_user_group}'@'%' IDENTIFIED BY '${var.mysql_password_group}';
      GRANT ALL PRIVILEGES ON ${var.mysql_database_group}.* TO '${var.mysql_user_group}'@'%';

      FLUSH PRIVILEGES;
    EOF
  }
}

# Secret for root password
resource "kubernetes_secret" "mysql_root" {
  metadata {
    name      = "mysql-root-password"
    namespace = var.namespace
  }
  data = {
    password = base64encode(var.mysql_root_password)
  }
  type = "Opaque"
}

# MySQL Deployment
resource "kubernetes_deployment" "mysql" {
  metadata {
    name      = "mysql"
    namespace = var.namespace
    labels    = { app = "mysql" }
  }
  spec {
    replicas = 1
    selector { match_labels = { app = "mysql" } }
    template {
      metadata { labels = { app = "mysql" } }
      spec {
        container {
          name  = "mysql"
          image = "mysql:8.0.33"
          port {
            container_port = 3306
          }
          env {
            name = "MYSQL_ROOT_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.mysql_root.metadata[0].name
                key  = "password"
              }
            }
          }
          volume_mount {
            name       = "mysql-data"
            mount_path = "/var/lib/mysql"
          }
          volume_mount {
            name       = "mysql-initdb"
            mount_path = "/docker-entrypoint-initdb.d"
          }
          readiness_probe {
            exec {
              command = [
                "/bin/sh",
                "-c",
                "mysql --user=root --password=$MYSQL_ROOT_PASSWORD --host=127.0.0.1 --execute='SELECT 1;'"
              ]
            }
            initial_delay_seconds = 20
            period_seconds        = 5
          }
        }
        volume {
          name = "mysql-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.mysql_data.metadata[0].name
          }
        }
        volume {
          name = "mysql-initdb"
          config_map {
            name = kubernetes_config_map.mysql_init.metadata[0].name
          }
        }
      }
    }
  }
}

# MySQL Service
resource "kubernetes_service" "mysql" {
  metadata {
    name      = "mysql"
    namespace = var.namespace
    labels = {
      app = "mysql"
    }
  }
  spec {
    selector = { app = "mysql" }
    port {
      port        = 3306
      target_port = 3306
    }
    type = "ClusterIP"
  }
}
