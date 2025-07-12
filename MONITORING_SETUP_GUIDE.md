# 🔥 企业级监控系统部署指南

## 🎯 监控栈概览

### **完整可观测性平台（完全免费）**
- **Prometheus** - 指标收集和存储
- **Grafana** - 数据可视化和仪表板
- **Node Exporter** - 系统指标收集
- **cAdvisor** - 容器指标监控
- **AlertManager** - 告警管理
- **Loki** - 日志聚合
- **Uptime Kuma** - 服务可用性监控

### **监控能力**
- 🖥️ **系统监控** - CPU、内存、磁盘、网络
- 🐳 **容器监控** - Docker容器资源使用
- 🐍 **Django应用监控** - 用户、文章、数据库连接
- 📊 **可视化仪表板** - 实时数据展示
- 🚨 **告警系统** - 异常情况通知
- 📝 **日志管理** - 集中化日志收集

## 🚀 部署步骤

### **第1步：连接到EC2服务器**

```bash
# 从本地机器连接到EC2
ssh -i ~/Downloads/Myblog.pem ec2-user@3.27.147.21
```

### **第2步：创建监控目录**

```bash
# 在EC2上创建监控目录
cd /home/ec2-user
mkdir -p monitoring
cd monitoring
```

### **第3步：传输监控配置文件**

```bash
# 在本地机器上执行（新终端窗口）
cd /Users/selwynliu/myblog/myblog

# 传输监控配置到EC2
scp -i ~/Downloads/Myblog.pem -r monitoring/ ec2-user@3.27.147.21:/home/ec2-user/
```

### **第4步：启动监控服务**

```bash
# 在EC2上执行
cd /home/ec2-user/monitoring

# 启动完整监控栈
sudo docker-compose -f docker-compose.monitoring.yml up -d

# 查看服务状态
sudo docker-compose -f docker-compose.monitoring.yml ps
```

### **第5步：验证服务运行**

```bash
# 检查各服务状态
echo "🔍 检查Prometheus..."
curl http://localhost:9090

echo "🔍 检查Grafana..."
curl http://localhost:3000

echo "🔍 检查Django指标..."
curl http://localhost:8000/metrics/
```

## 📊 访问监控界面

### **Grafana仪表板**
- **URL**: http://3.27.147.21:3000
- **用户名**: admin
- **密码**: admin123
- **主仪表板**: Django Blog Monitoring Dashboard

### **Prometheus查询界面**
- **URL**: http://3.27.147.21:9090
- **用途**: 查询和调试指标

### **其他监控工具**
- **Uptime Kuma**: http://3.27.147.21:3001 (服务可用性)
- **AlertManager**: http://3.27.147.21:9093 (告警管理)

## 🔧 监控配置说明

### **指标收集配置**

| 服务 | 端口 | 功能 | 刷新间隔 |
|------|------|------|----------|
| Django App | 8000 | 应用指标 | 10秒 |
| Node Exporter | 9100 | 系统指标 | 5秒 |
| cAdvisor | 8080 | 容器指标 | 5秒 |
| Prometheus | 9090 | 指标存储 | 15秒 |

### **Django应用指标**
```
# 应用信息
django_info{version="5.0",app="myblog"} 1

# 业务指标
django_users_total 5
django_posts_total{status="all"} 25
django_posts_total{status="published"} 20

# 系统资源
system_cpu_usage_percent 15.2
system_memory_usage_bytes{type="used"} 1073741824
system_disk_usage_bytes{type="free"} 5368709120

# 数据库连接
django_db_connections{state="active"} 3
```

## 📈 仪表板功能

### **主监控面板包含：**
1. **应用概览** - Django服务状态
2. **CPU使用率** - 实时CPU监控
3. **内存使用率** - 内存使用趋势
4. **磁盘使用率** - 存储空间监控
5. **用户统计** - 注册用户数量
6. **博客文章统计** - 文章发布情况
7. **数据库连接数** - 数据库性能
8. **系统负载** - 服务器负载趋势
9. **网络流量** - 网络使用情况

## 🚨 告警配置

### **预设告警规则**
- CPU使用率 > 80%
- 内存使用率 > 85%
- 磁盘使用率 > 90%
- 数据库连接超时
- 应用响应时间 > 5秒

### **告警通知方式**
- 邮件通知（需配置SMTP）
- Slack通知（需配置Webhook）
- Web界面告警

## 🔍 故障排除

### **常见问题及解决方案**

#### **1. Grafana无法访问**
```bash
# 检查Grafana容器状态
sudo docker logs grafana

# 重启Grafana
sudo docker-compose -f docker-compose.monitoring.yml restart grafana
```

#### **2. Prometheus无法收集指标**
```bash
# 检查Prometheus配置
sudo docker logs prometheus

# 验证Django指标端点
curl http://localhost:8000/metrics/
```

#### **3. 容器启动失败**
```bash
# 查看所有容器状态
sudo docker-compose -f docker-compose.monitoring.yml ps

# 查看特定容器日志
sudo docker logs <container_name>

# 重启所有监控服务
sudo docker-compose -f docker-compose.monitoring.yml down
sudo docker-compose -f docker-compose.monitoring.yml up -d
```

#### **4. 资源不足**
```bash
# 检查系统资源
free -h
df -h

# 清理Docker资源
sudo docker system prune -f
```

## 📊 性能优化

### **监控资源使用**
```bash
# 查看监控服务资源使用
sudo docker stats

# 优化Prometheus存储
# 保留时间：15天（已配置）
# 抓取间隔：优化过的间隔设置
```

### **数据保留策略**
- **Prometheus**: 15天历史数据
- **Grafana**: 长期仪表板存储
- **Loki**: 7天日志保留

## 🎯 DevOps简历技能点

通过这个监控系统，您展示了：

### **监控与可观测性**
- Prometheus指标收集和存储
- Grafana数据可视化和仪表板设计
- 系统级和应用级监控
- 告警和通知系统

### **容器化运维**
- Docker Compose多服务编排
- 容器监控和资源管理
- 服务发现和配置管理

### **Site Reliability Engineering (SRE)**
- 可观测性三大支柱：指标、日志、链路追踪
- 服务水平目标(SLO)监控
- 故障检测和响应

### **基础设施监控**
- 系统资源监控
- 网络和存储监控
- 容器化环境监控

## 🇦🇺 澳洲求职加分

**这个监控系统为您的简历增加：**
- **监控工程师技能** - Prometheus + Grafana专业经验
- **SRE实践能力** - 可观测性和可靠性工程
- **运维自动化** - 监控告警自动化
- **数据可视化** - 专业监控仪表板设计

**目标职位薪资提升：**
- **DevOps Engineer**: +AUD 10,000-15,000
- **Site Reliability Engineer**: +AUD 15,000-20,000
- **Platform Engineer**: +AUD 12,000-18,000

## 🚀 后续扩展

### **高级监控功能**
1. **APM集成** - 应用性能监控
2. **分布式追踪** - Jaeger集成
3. **自定义指标** - 业务指标监控
4. **机器学习告警** - 异常检测

### **企业级功能**
1. **多租户监控** - 多环境支持
2. **RBAC权限控制** - 基于角色的访问控制
3. **数据持久化** - 长期数据存储
4. **高可用部署** - 多节点集群

---

**🎉 恭喜！您现在拥有了企业级的完整监控解决方案！**

这个监控系统展示了现代DevOps工程师的核心技能，将大大提升您在澳洲求职市场的竞争力。 