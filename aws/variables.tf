variable "aws_region" {
  default = "us-east-1"
}

variable "client_image" {
  description = "GHCR Docker image"
  default     = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client"
}