#!/bin/bash

# Terraform部署脚本
set -e

echo "🏗️ 准备Terraform基础设施部署..."

# 1. 检查Terraform是否安装
echo "🔍 检查Terraform安装..."
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform未安装，请先安装Terraform"
    echo "💡 macOS: brew install terraform"
    echo "💡 Linux: 下载 https://www.terraform.io/downloads"
    exit 1
fi

terraform --version

# 2. 检查AWS CLI配置
echo "🔍 检查AWS CLI配置..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI未安装，请先安装AWS CLI"
    echo "💡 macOS: brew install awscli"
    exit 1
fi

# 3. 检查AWS凭证
echo "🔐 检查AWS凭证..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS凭证已配置"
    aws sts get-caller-identity
else
    echo "❌ AWS凭证未配置，请运行: aws configure"
    exit 1
fi

# 4. 创建terraform.tfvars文件
echo "⚙️ 创建terraform.tfvars配置文件..."
cat > terraform/terraform.tfvars << EOF
# 项目配置
project_name = "myblog"
environment = "production"

# AWS区域
aws_region = "ap-southeast-2"  # 悉尼

# 网络配置
vpc_cidr = "10.0.0.0/16"
az_count = 2

# EC2配置
instance_type = "t3.micro"  # 免费套餐
ami_id = "ami-0892a9a01908fafd1"  # Amazon Linux 2023

# 管理员访问CIDR (你的IP地址)
admin_cidr = "0.0.0.0/0"  # 请替换为你的实际IP地址

# 数据库配置
db_instance_class = "db.t3.micro"
db_name = "myblogdb"
db_username = "admin"
db_password = "YourSecurePassword123!"

# 密钥对路径
public_key_path = "~/.ssh/id_rsa.pub"  # 请确保这个路径存在

# 通知邮箱
notification_email = "your-email@example.com"
EOF

echo "📝 已创建 terraform/terraform.tfvars 配置文件"
echo "⚠️  请编辑 terraform/terraform.tfvars 文件，更新以下信息:"
echo "   - admin_cidr: 你的IP地址"
echo "   - db_password: 数据库密码"
echo "   - public_key_path: SSH公钥路径"
echo "   - notification_email: 通知邮箱"

# 5. 初始化Terraform
echo "🚀 初始化Terraform..."
cd terraform
terraform init

# 6. 验证配置
echo "✅ 验证Terraform配置..."
terraform validate

# 7. 规划部署
echo "📋 生成部署计划..."
terraform plan -out=tfplan

echo "✅ Terraform准备完成！"
echo ""
echo "🎯 下一步操作:"
echo "   1. 编辑 terraform/terraform.tfvars 文件"
echo "   2. 运行 'cd terraform && terraform apply tfplan' 部署基础设施"
echo "   3. 部署完成后，基础设施将包括:"
echo "      - VPC和子网"
echo "      - EC2实例"
echo "      - RDS数据库"
echo "      - CloudWatch监控"
echo "      - S3备份存储"
echo "      - IAM角色和策略"
echo ""
echo "💰 预估费用: $10-15/月 (大部分服务在免费套餐内)" 