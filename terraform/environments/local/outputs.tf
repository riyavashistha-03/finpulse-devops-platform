output "container_id" {
  description = "Docker container ID"
  value       = docker_container.finpulse.id
}

output "application_url" {
  description = "Access URL for local FinPulse instance"
  value       = "http://localhost:${var.external_port}"
}

output "network_id" {
  description = "Bridge network ID"
  value       = docker_network.finpulse_net.id
}
