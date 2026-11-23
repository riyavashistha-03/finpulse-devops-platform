# Local Docker Network
resource "docker_network" "finpulse_net" {
  name   = "finpulse-local-network"
  driver = "bridge"
}

# Persistent Volume for SQLite Database
resource "docker_volume" "finpulse_data" {
  name = "finpulse-local-data"
}

# Persistent Volume for Application Logs
resource "docker_volume" "finpulse_logs" {
  name = "finpulse-local-logs"
}

# FinPulse Application Container
resource "docker_container" "finpulse" {
  name  = var.container_name
  image = "${var.image_name}:${var.image_tag}"

  ports {
    internal = 5050
    external = var.external_port
  }

  env = [
    "FLASK_ENV=${var.flask_env}",
    "PORT=5050",
    "SECRET_KEY=terraform-local-super-secret-key-9988",
    "DATABASE_URL=sqlite:////app/instance/finpulse_prod.db",
    "GUNICORN_WORKERS=2",
    "GUNICORN_THREADS=4"
  ]

  volumes {
    volume_name    = docker_volume.finpulse_data.name
    container_path = "/app/instance"
  }

  volumes {
    volume_name    = docker_volume.finpulse_logs.name
    container_path = "/app/logs"
  }

  networks_advanced {
    name = docker_network.finpulse_net.name
  }

  restart = "unless-stopped"
}
