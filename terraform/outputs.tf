output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "web_security_group_id" {
  description = "Web security group ID"
  value       = aws_security_group.web.id
}

output "db_security_group_id" {
  description = "Database security group ID"
  value       = aws_security_group.db.id
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "ec2_public_ip" {
  description = "EC2 public IP address"
  value       = aws_eip.web.public_ip
}

output "ec2_private_ip" {
  description = "EC2 private IP address"
  value       = aws_instance.web.private_ip
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = var.use_rds ? aws_db_instance.main[0].endpoint : null
}

output "rds_port" {
  description = "RDS port"
  value       = var.use_rds ? aws_db_instance.main[0].port : null
}

output "s3_backup_bucket" {
  description = "S3 backup bucket name"
  value       = aws_s3_bucket.backups.bucket
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.app.name
}

output "iam_role_arn" {
  description = "IAM role ARN for EC2 instance"
  value       = aws_iam_role.ec2_role.arn
}

output "key_pair_name" {
  description = "Key pair name"
  value       = aws_key_pair.main.key_name
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${aws_key_pair.main.key_name}.pem ec2-user@${aws_eip.web.public_ip}"
}

output "application_urls" {
  description = "Application URLs"
  value = {
    website = "http://${aws_eip.web.public_ip}"
    admin   = "http://${aws_eip.web.public_ip}/admin/"
  }
}

output "monitoring_urls" {
  description = "Monitoring URLs"
  value = {
    cloudwatch = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:"
    logs       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logStream:group=${aws_cloudwatch_log_group.app.name}"
  }
}

output "deployment_info" {
  description = "Important deployment information"
  value = {
    region                = var.aws_region
    project_name          = var.project_name
    environment           = var.environment
    instance_type         = var.instance_type
    instance_id           = aws_instance.web.id
    public_ip             = aws_eip.web.public_ip
    backup_bucket         = aws_s3_bucket.backups.bucket
    log_group             = aws_cloudwatch_log_group.app.name
    sns_topic             = aws_sns_topic.alerts.arn
    database_endpoint     = var.use_rds ? aws_db_instance.main[0].endpoint : "Docker PostgreSQL"
    ssl_enabled           = var.ssl_certificate_arn != ""
    domain_configured     = var.domain_name != ""
  }
} 