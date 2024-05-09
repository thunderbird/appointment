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

resource "aws_vpc_security_group_ingress_rule" "ingress" {
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
