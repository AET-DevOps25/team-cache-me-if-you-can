# Kubernetes namespace
variable "namespace" {
  description = "Kubernetes namespace to deploy into"
  type        = string
  default     = "pre-prod"
}

# Docker image tags
variable "image_tag_user" {
  description = "Image tag for user-service"
  type        = string
  default     = "latest"
}
variable "image_tag_group" {
  description = "Image tag for group-service"
  type        = string
  default     = "latest"
}
variable "image_tag_gateway" {
  description = "Image tag for gateway-service"
  type        = string
  default     = "latest"
}
variable "image_tag_files" {
  description = "Image tag for files-service"
  type        = string
  default     = "latest"
}

# GenAI image tags
variable "image_tag_genai" {
  description = "Image tag for genai-app"
  type        = string
  default     = "latest"
}

# Client image tags
variable "image_tag_client" {
  description = "Image tag for client"
  type        = string
  default     = "latest"
}

# MySQL credentials & database names
variable "mysql_root_password" {
  description = "MySQL root password"
  type        = string
  default     = "StrongRootPass123!"
}
variable "mysql_database_files" {
  description = "Name of the files database"
  type        = string
  default     = "files_database"
}
variable "mysql_database_user" {
  description = "Name of the user database"
  type        = string
  default     = "user_database"
}
variable "mysql_database_group" {
  description = "Name of the group database"
  type        = string
  default     = "group_database"
}
variable "mysql_user_files" {
  description = "MySQL username for files DB"
  type        = string
  default     = "files"
}
variable "mysql_password_files" {
  description = "MySQL password for files DB"
  type        = string
  default     = "Files123!"
}
variable "mysql_user_user" {
  description = "MySQL username for user DB"
  type        = string
  default     = "user"
}
variable "mysql_password_user" {
  description = "MySQL password for user DB"
  type        = string
  default     = "User123!"
}
variable "mysql_user_group" {
  description = "MySQL username for group DB"
  type        = string
  default     = "group"
}
variable "mysql_password_group" {
  description = "MySQL password for group DB"
  type        = string
  default     = "Group123!"
}
variable "rancher_project_id" {
  description = "Rancher Project ID for this namespace"
  type        = string
  default     = "p-v6sq2%"
}

# JWT secret for all services
variable "jwt_secret_key" {
  description = "Shared JWT secret key"
  type        = string
  default     = "u8jA1hTSe7Z9Qa8bH6h+qOqEAvFR6l4dNMb7rJH4Jmg="
}

# Spring profile
variable "spring_profile" {
  description = "Active Spring profile"
  type        = string
  default     = "pre-prod"
}

# OpenAI API Key for GenAI service
variable "openai_api_key" {
  description = "OpenAI API key for GenAI service"
  type        = string
  sensitive   = true
  default     = ""  # Should be provided via environment variable or terraform.tfvars
}

