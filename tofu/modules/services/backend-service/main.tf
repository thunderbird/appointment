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

  health_check_grace_period_seconds = 180
  task_definition                   = aws_ecs_task_definition.backend.arn
  desired_count                     = 1
  tags                              = var.tags
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "appointment-definition"
  execution_role_arn       = var.task_execution_role
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
      image     = var.image
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
          "value" : var.frontend_url
        },
        {
          "name" : "SHORT_BASE_URL",
          "value" : var.short_base_url
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
          "value" : var.log_level
        },
        {
          "name" : "APP_ENV",
          "value" : var.app_env
        },
        {
          "name" : "SENTRY_DSN",
          "value" : var.sentry_dsn
        },
        {
          "name" : "ZOOM_API_ENABLED",
          "value" : "True"
        },
        {
          "name" : "ZOOM_AUTH_CALLBACK",
          "value" : var.zoom_auth_callback
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
        # Redis integration disabled pending application code updates
        #},
        #{
        #  "name": "REDIS_URL",
        #  "value": "" #var.redis_endpoint
        #},
        #{
        #  "name": "REDIS_PORT",
        #  "value": "" #"6379"
        #},
        #{
        #  "name": "REDIS_DB",
        #  "value": "" #"0"
        #},
        #{
        #  "name": "REDIS_USE_SSL",
        #  "value": "" #"True"
        }
      ],
      secrets = [
        {
          "name" : "DATABASE_SECRETS",
          "valueFrom" : var.database_secret
        },
        {
          "name" : "DB_ENC_SECRET",
          "valueFrom" : var.db_enc_secret
        },
        {
          "name" : "SMTP_SECRETS",
          "valueFrom" : var.smtp_secret
        },
        {
          "name" : "GOOGLE_OAUTH_SECRETS",
          "valueFrom" : var.google_oauth_secret
        },
        {
          "name" : "ZOOM_SECRETS",
          "valueFrom" : var.zoom_secret
        },
        {
          "name" : "FXA_SECRETS",
          "valueFrom" : var.fxa_secret
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = var.log_group
          awslogs-region        = var.region
          awslogs-stream-prefix = "${var.short_name}/${var.app_env}"
        }
      }
    }
  ])
}