variable "redeploy_id" {
  description = "A unique identifier to force redeployment (e.g., GitHub SHA)"
  type        = string
  default     = "latest" # Optional: Provide a default if not passed
}