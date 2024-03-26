resource "aws_ecs_service" "backend_service" {
  name    = "${var.name_prefix}-backend"
  cluster = var.ecs_cluster

  launch_type = "FARGATE"

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "backend"
    container_port   = 5000
  }

  network_configuration {
    security_groups = [var.security_group]
    subnets         = var.subnets
  }

  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  tags            = var.tags
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "appointment-definition"
  execution_role_arn       = "arn:aws:iam::768512802988:role/apointments-ci-role"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }
  tags = var.tags
  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "backend-latest"
      cpu       = 0
      essential = true
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ]
      environment = [
        {
          "name" : "FRONTEND_URL",
          "value" : "https://stage.appointment.day"
        },
        {
          "name" : "SHORT_BASE_URL",
          "value" : "https://stage.apmt.day"
        },
        {
          "name" : "TIER_BASIC_CALENDAR_LIMIT",
          "value" : "3"
        },
        {
          "name" : "TIER_PLUS_CALENDAR_LIMIT",
          "value" : "5"
        },
        {
          "name" : "TIER_PRO_CALENDAR_LIMIT",
          "value" : "10"
        },
        {
          "name" : "LOG_USE_STREAM",
          "value" : "True"
        },
        {
          "name" : "LOG_LEVEL",
          "value" : "INFO"
        },
        {
          "name" : "APP_ENV",
          "value" : "stage"
        },
        {
          "name" : "SENTRY_DSN",
          "value" : "https://5dddca3ecc964284bb8008bc2beef808@o4505428107853824.ingest.sentry.io/4505428124827648"
        },
        {
          "name" : "ZOOM_API_ENABLED",
          "value" : "True"
        },
        {
          "name" : "ZOOM_AUTH_CALLBACK",
          "value" : "https://stage.appointment.day/api/v1/zoom/callback"
        },
        {
          "name" : "SERVICE_EMAIL",
          "value" : "no-reply@appointment.day"
        },
        {
          "name" : "AUTH_SCHEME",
          "value" : "fxa"
        },
        {
          "name" : "JWT_ALGO",
          "value" : "HS256"
        },
        {
          "name" : "JWT_EXPIRE_IN_MINS",
          "value" : "10000"
        }
      ],
      secrets = [
        {
          "name" : "DATABASE_SECRETS",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/db-mysql-Ixf6qD"
        },
        {
          "name" : "DB_ENC_SECRET",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/db-secret-CYKglI"
        },
        {
          "name" : "SMTP_SECRETS",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/socketlabs-UYmjaC"
        },
        {
          "name" : "GOOGLE_OAUTH_SECRETS",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/google-cal-oauth-VevaSo"
        },
        {
          "name" : "ZOOM_SECRETS",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/zoom-S862zi"
        },
        {
          "name" : "FXA_SECRETS",
          "valueFrom" : "arn:aws:secretsmanager:us-east-1:768512802988:secret:staging/appointment/fxa-7koQF0"
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.log_group
          awslogs-region        = var.region
          awslogs-stream-prefix = "apmt"
        }
      }
    }
  ])
}