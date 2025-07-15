variable "aws_region" {
  default = "us-east-1"
}

variable "client_image" {
  description = "GHCR Docker image"
  default     = "ghcr.io/your-username/your-repo:latest"
}

variable "ghcr_username" {}
variable "ghcr_token" {
  sensitive = true
}
