provider "aws" {
  region = "us-east-1"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# -------------------------------------
# 1. VPC + Networking
# -------------------------------------
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  map_public_ip_on_launch = true
  availability_zone       = element(data.aws_availability_zones.available.names, count.index)
}

data "aws_availability_zones" "available" {}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_route_table_association" "a" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# -------------------------------------
# 2. Security Group
# -------------------------------------
resource "aws_security_group" "ecs_sg" {
  name        = "ecs-sg-${random_id.suffix.hex}"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 65535
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

# -------------------------------------
# 3. IAM Role for ECS
# -------------------------------------
resource "aws_iam_role" "ecs_task_execution" {
  name = "ecsTaskExecutionRole-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -------------------------------------
# 4. ECS Cluster
# -------------------------------------
resource "aws_ecs_cluster" "main" {
  name = "multi-service-cluster-${random_id.suffix.hex}"
}

# -------------------------------------
# 5. ALB for client
# -------------------------------------
resource "aws_lb" "client_alb" {
  name               = "client-alb-${random_id.suffix.hex}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "client_tg" {
  name        = "client-tg-${random_id.suffix.hex}"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200-399"
  }
}

resource "aws_lb_listener" "client_listener" {
  load_balancer_arn = aws_lb.client_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.client_tg.arn
  }
}

# -------------------------------------
# 6. ECS Task + Services for Each Container
# -------------------------------------
locals {
  services = [
    {
      name         = "client"
      port         = 3000
      image        = "ghcr.io/aet-devops25/team-cache-me-if-you-can/client:latest"
      public       = true
      command      = ["/bin/sh", "-lc", "npm install && npm run dev -- --host 0.0.0.0 --port 3000"]
    },
    {
      name   = "user"
      port   = 8081
      image  = "ghcr.io/aet-devops25/team-cache-me-if-you-can/user-service:latest"
    },
    {
      name   = "gateway"
      port   = 8080
      image  = "ghcr.io/aet-devops25/team-cache-me-if-you-can/gateway-service:latest"
    },
    {
      name   = "files"
      port   = 8082
      image  = "ghcr.io/aet-devops25/team-cache-me-if-you-can/files-service:latest"
    },
    {
      name   = "group"
      port   = 8083
      image  = "ghcr.io/aet-devops25/team-cache-me-if-you-can/group-service:latest"
      command = ["-Dspring.profiles.active=dev", "-Dlogging.level.root=DEBUG", "-Dlogging.level.org.springframework=DEBUG"]
    },
    {
      name   = "genai"
      port   = 8000
      image  = "ghcr.io/aet-devops25/team-cache-me-if-you-can/genai-app:latest"
    },
    {
      name   = "mysql"
      port   = 3306
      image  = "mysql:8.0.33"
      command = [
        "--lower-case-table-names=1",
        "--socket=/tmp/mysql.sock",
        "--pid-file=/tmp/mysql.pid",
        "--default-authentication-plugin=mysql_native_password"
      ]
    }
  ]
}

resource "aws_ecs_task_definition" "services" {
  for_each                 = { for svc in local.services : svc.name => svc }
  family                   = "${each.value.name}-${random_id.suffix.hex}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name         = each.value.name
      image        = each.value.image
      portMappings = [{
        containerPort = each.value.port
        hostPort      = each.value.port
      }]
      command      = lookup(each.value, "command", null)
    }
  ])
}

resource "aws_ecs_service" "services" {
  deployment_controller {
    type = "ECS"
  }
  health_check_grace_period_seconds = 60

  for_each        = aws_ecs_task_definition.services
  name            = "${each.key}-${random_id.suffix.hex}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = each.value.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    assign_public_ip = true
    security_groups  = [aws_security_group.ecs_sg.id]
  }

  dynamic "load_balancer" {
    for_each = each.key == "client" ? [1] : []
    content {
      target_group_arn = aws_lb_target_group.client_tg.arn
      container_name   = "client"
      container_port   = 3000
    }
  }

  depends_on = [aws_lb_listener.client_listener]
}

output "client_url" {
  value = "http://${aws_lb.client_alb.dns_name}"
}