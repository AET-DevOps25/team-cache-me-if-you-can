terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Networking Resources
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "team-cache-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "team-cache-igw"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = {
    Name = "team-cache-public-subnet-${count.index + 1}"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "team-cache-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# RDS MySQL Database
resource "aws_security_group" "rds_sg" {
  name        = "team-cache-rds-sg"
  description = "Allow ECS to access RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "default" {
  name       = "team-cache-db-subnet-group"
  subnet_ids = aws_subnet.public[*].id
  tags = {
    Name = "Team Cache DB Subnet Group"
  }
}

resource "aws_db_instance" "mysql" {
  identifier             = "team-cache-mysql"
  allocated_storage      = 20
  engine                 = "mysql"
  engine_version         = "8.0.33"
  instance_class         = "db.t3.micro"
  db_name                = "teamcache"
  username               = "admin"
  password               = var.db_password
  parameter_group_name   = "default.mysql8.0"
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
  publicly_accessible    = false
}

# ECS Cluster
resource "aws_ecs_cluster" "app_cluster" {
  name = "team-cache-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "team-cache-ecsTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Grant EFS permissions to ECS task role
resource "aws_iam_role_policy" "efs_access" {
  name = "team-cache-efs-access"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow"
      Action = [
        "elasticfilesystem:ClientMount",
        "elasticfilesystem:ClientWrite",
        "elasticfilesystem:ClientRootAccess",
      ]
      Resource = "*"
    }]
  })
}

# Security Groups
resource "aws_security_group" "ecs_sg" {
  name        = "team-cache-ecs-sg"
  description = "Allow inbound access to ECS services"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8083
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Load Balancer
resource "aws_lb" "app_lb" {
  name               = "team-cache-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
}

resource "aws_lb_target_group" "client" {
  name        = "team-cache-client-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "client" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.client.arn
  }
}

# EFS for file uploads
resource "aws_efs_file_system" "uploads" {
  creation_token = "team-cache-uploads"
  tags = {
    Name = "team-cache-uploads"
  }
}

resource "aws_efs_mount_target" "uploads" {
  count           = length(aws_subnet.public)
  file_system_id  = aws_efs_file_system.uploads.id
  subnet_id       = aws_subnet.public[count.index].id
  security_groups = [aws_security_group.ecs_sg.id]
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "client" {
  name              = "/ecs/team-cache-client"
  retention_in_days = 7
}
resource "aws_cloudwatch_log_group" "user" {
  name              = "/ecs/team-cache-user"
  retention_in_days = 7
}
resource "aws_cloudwatch_log_group" "gateway" {
  name              = "/ecs/team-cache-gateway"
  retention_in_days = 7
}
resource "aws_cloudwatch_log_group" "files" {
  name              = "/ecs/team-cache-files"
  retention_in_days = 7
}
resource "aws_cloudwatch_log_group" "group" {
  name              = "/ecs/team-cache-group"
  retention_in_days = 7
}

# Variables
variable "db_password" {
  description = "Password for the RDS MySQL database"
  type        = string
  sensitive   = true
}

variable "github_token" {
  description = "GitHub token for pulling from GHCR"
  type        = string
  sensitive   = true
}

# Outputs
output "alb_dns_name" {
  value       = aws_lb.app_lb.dns_name
  description = "The DNS name of the application load balancer"
}

output "rds_endpoint" {
  value       = aws_db_instance.mysql.address
  description = "The endpoint of the RDS MySQL instance"
}