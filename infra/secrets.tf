  # user-service environment secret
  resource "kubernetes_secret" "user_env" {
    metadata {
      name      = "user-env-secret"
      namespace = var.namespace
    }
    data = {
      SPRING_DATASOURCE_URL      = "jdbc:mysql://${kubernetes_service.mysql.metadata[0].name}.${var.namespace}.svc.cluster.local:3306/${var.mysql_database_user}"
      SPRING_DATASOURCE_USERNAME = var.mysql_user_user
      SPRING_DATASOURCE_PASSWORD = var.mysql_password_user
      JWT_SECRET_KEY             = var.jwt_secret_key
      SPRING_PROFILES_ACTIVE     = var.spring_profile
    }
    type = "Opaque"
  }

  # group-service environment secret
  resource "kubernetes_secret" "group_env" {
    metadata {
      name      = "group-env-secret"
      namespace = var.namespace
    }
    data = {
      SPRING_DATASOURCE_URL      = "jdbc:mysql://${kubernetes_service.mysql.metadata[0].name}.${var.namespace}.svc.cluster.local:3306/${var.mysql_database_group}"
      SPRING_DATASOURCE_USERNAME = var.mysql_user_group
      SPRING_DATASOURCE_PASSWORD = var.mysql_password_group
      JWT_SECRET_KEY             = var.jwt_secret_key
      SPRING_PROFILES_ACTIVE     = var.spring_profile
    }
    type = "Opaque"
  }

  # gateway-service environment secret
  resource "kubernetes_secret" "gateway_env" {
    metadata {
      name      = "gateway-env-secret"
      namespace = var.namespace
    }
    data = {
      JWT_SECRET_KEY         = var.jwt_secret_key
      SPRING_PROFILES_ACTIVE = var.spring_profile
    }
    type = "Opaque"
  }
