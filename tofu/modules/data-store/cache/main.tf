resource "aws_elasticache_serverless_cache" "redis" {
  engine = "redis"
  name   = "${var.name_prefix}-redis"

  description              = "Appointment Caches"
  major_engine_version     = "7"
  security_group_ids       = [aws_security_group.redis.id]
  subnet_ids               = var.subnets

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_security_group" "redis" {
  name        = "${var.name_prefix}-redis"
  description = "Appointment redis SG"
  vpc_id      = var.vpc

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_vpc_security_group_ingress_rule" "ingress_6379" {
  for_each = toset(var.source_security_groups)

  security_group_id            = aws_security_group.redis.id
  description                  = "redis(6379) ingress"
  from_port                    = 6379
  to_port                      = 6379
  ip_protocol                  = "tcp"
  referenced_security_group_id = each.key

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_vpc_security_group_ingress_rule" "ingress_6380" {
  for_each = toset(var.source_security_groups)

  security_group_id            = aws_security_group.redis.id
  description                  = "redis(6380) ingress"
  from_port                    = 6380
  to_port                      = 6380
  ip_protocol                  = "tcp"
  referenced_security_group_id = each.key

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_vpc_security_group_egress_rule" "egress_3306" {
  for_each = toset(var.database_subnet_cidrs)

  security_group_id = aws_security_group.redis.id
  description                  = "mysql(3306) to DB"
  from_port                    = 3306
  to_port                      = 3306
  ip_protocol                  = "tcp"
  cidr_ipv4                    = each.key

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_vpc_security_group_egress_rule" "egress_6379" {
  for_each = toset(var.source_security_groups)

  security_group_id            = each.key
  description                  = "redis(6379) egress"
  from_port                    = 6379
  to_port                      = 6379
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.redis.id

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}

resource "aws_vpc_security_group_egress_rule" "egress_6380" {
  for_each = toset(var.source_security_groups)

  security_group_id            = each.key
  description                  = "redis(6380) egress"
  from_port                    = 6380
  to_port                      = 6380
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.redis.id

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-redis"
  })
}
