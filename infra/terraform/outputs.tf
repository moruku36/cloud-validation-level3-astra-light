output "alb_dns_name" {
  description = "ALB DNS name (Private application: do not publicize or commit to repo)"
  value       = module.alb.alb_dns_name
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}

output "ecs_service_name" {
  value = module.ecs.service_name
}

output "db_endpoint" {
  value     = module.rds.db_endpoint
  sensitive = true
}
