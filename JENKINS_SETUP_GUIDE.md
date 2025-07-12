# Jenkins 轻量级部署指南

## ⚠️ 重要提醒：成本考虑

### **EC2成本分析**
- **当前EC2**：1个t2.micro实例 (免费额度内)
- **新增EC2**：会超出免费额度，产生额外费用
- **解决方案**：在现有EC2上部署Jenkins

### **内存要求**
- **Jenkins最小要求**：1GB内存
- **推荐配置**：2GB内存
- **t2.micro限制**：1GB内存（可能不足）

## 🚀 为什么考虑Jenkins？

### **优点**
- 功能最强大，插件生态丰富
- 高度可定制，适合复杂场景
- 界面直观，历史悠久

### **缺点**
- 配置复杂，学习成本高
- 资源消耗大，维护成本高
- 需要大量插件配置

## 📋 Jenkins部署步骤

### 1. 检查服务器资源

```bash
# 连接到EC2服务器
ssh -i ~/Downloads/Myblog.pem ec2-user@3.27.147.21

# 检查内存使用情况
free -h

# 检查磁盘空间
df -h

# 检查当前运行的服务
sudo docker ps
```

### 2. 部署Jenkins

```bash
# 创建Jenkins目录
mkdir -p /home/ec2-user/jenkins
cd /home/ec2-user/jenkins

# 下载配置文件
wget https://raw.githubusercontent.com/your-repo/myblog/main/jenkins/docker-compose.jenkins.yml

# 设置权限
sudo chown -R 1000:1000 /home/ec2-user/jenkins

# 启动Jenkins
sudo docker-compose -f docker-compose.jenkins.yml up -d
```

### 3. 配置Jenkins

```bash
# 查看初始管理员密码
sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 访问Jenkins Web界面
# http://3.27.147.21:8080
```

### 4. 安装推荐插件

**必需插件：**
- Docker Pipeline
- SSH Agent
- HTTP Request
- HTML Publisher
- Git
- Pipeline

**安装命令：**
```bash
# 通过Web界面安装，或使用Jenkins CLI
docker exec jenkins jenkins-cli install-plugin docker-workflow ssh-agent http_request htmlpublisher git workflow-aggregator
```

### 5. 配置凭证

在Jenkins中添加以下凭证：

| 凭证ID | 类型 | 说明 |
|--------|------|------|
| `deploy-ssh-key` | SSH Username with private key | 部署SSH私钥 |
| `slack-webhook-url` | Secret text | Slack通知URL |

### 6. 创建Pipeline任务

```bash
# 在Jenkins中创建新的Pipeline任务
# 选择"Pipeline script from SCM"
# 设置Git仓库URL
# 指定Jenkinsfile路径
```

## 🔧 性能优化

### 1. 内存优化

```yaml
# docker-compose.jenkins.yml 中的优化
environment:
  - JAVA_OPTS=-Xmx512m -Xms512m -XX:MaxMetaspaceSize=256m
```

### 2. 清理策略

```bash
# 定期清理构建历史
# 在Jenkins系统配置中设置：
# - 保留构建天数：7天
# - 保留构建数量：10个
```

### 3. 代理配置

```yaml
# 使用轻量级代理
jenkins-agent:
  image: jenkins/inbound-agent:alpine
  environment:
    - JENKINS_AGENT_WORKDIR=/tmp
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# 开放Jenkins端口（仅限必要）
sudo ufw allow 8080/tcp

# 或者使用nginx代理
sudo nginx -t
sudo systemctl reload nginx
```

### 2. 访问控制

```bash
# 在Jenkins中配置：
# - 启用基于角色的访问控制
# - 设置强密码策略
# - 定期备份配置
```

## 📊 监控告警

### 1. 资源监控

```bash
# 监控Jenkins容器资源使用
docker stats jenkins

# 监控系统资源
htop
```

### 2. 日志监控

```bash
# 查看Jenkins日志
sudo docker logs jenkins -f

# 查看构建日志
sudo docker exec jenkins tail -f /var/jenkins_home/logs/jenkins.log
```

## 🛠️ 故障排除

### 1. 内存不足

```bash
# 症状：Jenkins运行缓慢或崩溃
# 解决方案：
# 1. 增加swap空间
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. 优化Java heap
export JAVA_OPTS="-Xmx512m -Xms256m"
```

### 2. 磁盘空间不足

```bash
# 清理Docker镜像
sudo docker system prune -af

# 清理Jenkins工作区
sudo docker exec jenkins find /var/jenkins_home/workspace -type f -name "*.log" -delete
```

### 3. 端口冲突

```bash
# 检查端口占用
sudo netstat -tulnp | grep 8080

# 修改Jenkins端口
# 在docker-compose.jenkins.yml中修改端口映射
```

## 💡 Jenkins vs GitLab CI/CD 对比

| 特性 | Jenkins | GitLab CI/CD |
|------|---------|--------------|
| **成本** | 需要服务器资源 | 免费400分钟/月 |
| **配置复杂度** | 高 | 低 |
| **功能丰富度** | 非常高 | 中等 |
| **维护成本** | 高 | 低 |
| **学习曲线** | 陡峭 | 平缓 |
| **推荐程度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎯 最终建议

### **推荐方案：GitLab CI/CD**
理由：
- ✅ 完全免费
- ✅ 配置简单
- ✅ 无需额外服务器
- ✅ 集成度高
- ✅ 学习成本低

### **考虑Jenkins的情况：**
- 需要复杂的自定义流水线
- 有大量现有Jenkins经验
- 需要特定的企业级功能
- 不介意额外的维护成本

## 🚀 快速决策

**如果你想要：**
- 快速上手 → 选择 GitLab CI/CD
- 功能强大 → 选择 Jenkins
- 零成本 → 选择 GitLab CI/CD
- 企业级 → 选择 Jenkins

**我的建议：先用GitLab CI/CD，有特殊需求再考虑Jenkins。**

---

**澳洲求职加分项：**
- 两种CI/CD工具都会更有竞争力
- GitLab CI/CD：现代化、云原生
- Jenkins：传统企业、功能强大
- 建议简历上写"熟悉Jenkins和GitLab CI/CD" 