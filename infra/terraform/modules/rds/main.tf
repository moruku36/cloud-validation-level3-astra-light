variable "env" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "ecs_security_group_id" {
  type = string
}

variable "multi_az" {
  type        = bool
  description = "Enable Multi-AZ (false for L, true for H)"
  default     = false
}

variable "instance_class" {
  type        = string
  description = "DB Instance Class (e.g. db.t4g.micro for L, db.t4g.medium for H)"
  default     = "db.t4g.micro"
}

variable "db_password" {
  type        = string
  description = "Database master password"
  sensitive   = true
  default     = "ValidationLevel3Pass123!"
}

resource "aws_security_group" "rds" {
  name        = "${var.env}-rds-sg"
  description = "RDS PostgreSQL security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.env}-rds-sg"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.env}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${var.env}-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.env}-postgres"
  engine                 = "postgres"
  engine_version         = "15.7"
  instance_class         = var.instance_class
  allocated_storage      = 20
  max_allocated_storage  = 50
  storage_type           = "gp3"
  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  db_name  = "appdb"
  username = "dbadmin"
  password = var.db_password

  skip_final_snapshot     = true
  deletion_protection     = false
  backup_retention_period = 1

  tags = {
    Name = "${var.env}-postgres"
  }
}

output "db_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
