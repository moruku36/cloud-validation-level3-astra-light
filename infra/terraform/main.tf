terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "cloud-validation-level3"
      Environment = var.env
      ManagedBy   = "Terraform"
      Owner       = "autonomous-validation"
    }
  }
}

module "vpc" {
  source   = "./modules/vpc"
  env      = var.env
  vpc_cidr = var.vpc_cidr
  azs      = var.azs
}

module "alb" {
  source     = "./modules/alb"
  env        = var.env
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids
}

module "ecs" {
  source                = "./modules/ecs"
  env                   = var.env
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.public_subnet_ids
  target_group_arn      = module.alb.target_group_arn
  alb_security_group_id = module.alb.alb_security_group_id
  task_count            = var.is_high_tier ? 2 : 1
}

module "rds" {
  source                = "./modules/rds"
  env                   = var.env
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_db_subnet_ids
  ecs_security_group_id = module.ecs.ecs_security_group_id
  multi_az              = var.is_high_tier
  instance_class        = var.is_high_tier ? "db.t4g.medium" : "db.t4g.micro"
}
