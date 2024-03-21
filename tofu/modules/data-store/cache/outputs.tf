output "endpoint" {
  value = aws_elasticache_serverless_cache.redis.endpoint
}

output "security_group_id" {
  value = aws_security_group.redis.id
}