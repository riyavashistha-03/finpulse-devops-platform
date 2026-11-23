# Infrastructure as Code (IaC) with Terraform

This directory provides automated infrastructure provisioning for the **FinPulse** platform across both local Docker environments and enterprise AWS cloud infrastructure.

## Directory Structure

```
terraform/
├── README.md
└── environments/
    ├── local/                  # Local Docker deployment environment
    │   ├── versions.tf         # Docker provider requirements
    │   ├── variables.tf        # Configurable parameters (ports, image, etc.)
    │   ├── terraform.tfvars    # Environment variables
    │   ├── main.tf             # Networks, volumes, containers
    │   └── outputs.tf          # Container status and URL
    └── aws/                    # AWS Cloud Production deployment
        ├── versions.tf         # AWS provider settings
        ├── variables.tf        # VPC, subnets, sizing parameters
        ├── terraform.tfvars    # Default AWS parameter values
        ├── main.tf             # VPC, ALB, ECS Fargate, IAM, CloudWatch
        └── outputs.tf          # Load balancer URL and cluster IDs
```

## Local Docker Deployment

```bash
cd environments/local
terraform init
terraform validate
terraform plan
terraform apply -auto-approve
```

## AWS Cloud Production Deployment

```bash
cd environments/aws
terraform init -backend=false
terraform validate
terraform plan
```
