variable "container_name" {
  description = "Name for the local FinPulse Docker container"
  type        = string
  default     = "finpulse-local"
}

variable "image_name" {
  description = "Docker image repository"
  type        = string
  default     = "finpulse-app"
}

variable "image_tag" {
  description = "Docker image version tag"
  type        = string
  default     = "1.0.0"
}

variable "external_port" {
  description = "Host port mapped to application container"
  type        = number
  default     = 5050
}

variable "flask_env" {
  description = "Flask runtime environment"
  type        = string
  default     = "production"
}
