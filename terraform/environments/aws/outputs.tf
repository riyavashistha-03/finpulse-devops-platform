output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "application_url" {
  description = "Public URL to access the deployed FinPulse platform"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecs_cluster_name" {
  description = "ECS Cluster Name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS Fargate Service Name"
  value       = aws_ecs_service.main.name
}

output "vpc_id" {
  description = "ID of the dedicated VPC"
  value       = aws_vpc.main.id
}
