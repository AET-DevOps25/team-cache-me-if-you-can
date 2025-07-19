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
      GENAI_SERVICE_URL          = "http://genai-dev-genai-app-service.${var.namespace}.svc.cluster.local:8000/api/v1"
    }
    type = "Opaque"
  }

  resource "kubernetes_secret" "gateway_env" {
    metadata {
      name      = "gateway-env-secret"
      namespace = var.namespace
    }
    data = {
      JWT_SECRET_KEY         = var.jwt_secret_key
      SPRING_PROFILES_ACTIVE = var.spring_profile
      USER_SERVICE_URL       = "http://user-service.${var.namespace}.svc.cluster.local:8081"
      FILES_SERVICE_URL      = "http://files-service.${var.namespace}.svc.cluster.local:8082"
      GENAI_SERVICE_URL      = "http://genai-dev-genai-app-service.${var.namespace}.svc.cluster.local:8000"
      GROUP_SERVICE_URL      = "http://group-service.${var.namespace}.svc.cluster.local:8083"
    }
    type = "Opaque"
  }
  resource "kubernetes_secret" "files_env" {
    metadata {
      name      = "files-env-secret"
      namespace = var.namespace
    }
    data = {
      SPRING_DATASOURCE_URL      = "jdbc:mysql://${kubernetes_service.mysql.metadata[0].name}.${var.namespace}.svc.cluster.local:3306/${var.mysql_database_files}"
      SPRING_DATASOURCE_USERNAME = var.mysql_user_files
      SPRING_DATASOURCE_PASSWORD = var.mysql_password_files
      JWT_SECRET_KEY             = var.jwt_secret_key
      SPRING_PROFILES_ACTIVE     = var.spring_profile
    }
    type = "Opaque"
  }

  # OpenAI credentials secret for GenAI service
  resource "kubernetes_secret" "openai_credentials" {
    metadata {
      name      = "openai-credentials"
      namespace = var.namespace
    }
    data = {
      OPENAI_API_KEY = var.openai_api_key
    }
    type = "Opaque"
    
    lifecycle {
      ignore_changes = [data]
    }
  }
