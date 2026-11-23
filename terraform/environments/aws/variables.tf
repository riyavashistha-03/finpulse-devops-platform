variable "aws_region" {
  description = "Target AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Target environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the dedicated FinPulse VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets across availability zones"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs for private subnets across availability zones"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.20.0/24"]
}

variable "app_container_image" {
  description = "Docker image repository for ECS task definition"
  type        = string
  default     = "ghcr.io/riyavashistha-03/finpulse-app:1.0.0"
}

variable "app_port" {
  description = "Application listening port"
  type        = number
  default     = 5050
}

variable "desired_task_count" {
  description = "Number of ECS Fargate tasks to maintain"
  type        = number
  default     = 2
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units (1024 = 1 vCPU)"
  type        = string
  default     = "512"
}

variable "fargate_memory" {
  description = "Fargate instance memory in MiB"
  type        = string
  default     = "1024"
}
