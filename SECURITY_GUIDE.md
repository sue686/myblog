# 🔒 安全部署和监控指南

## 🚨 安全问题分析

### 之前的不安全配置：
- ❌ **8个端口对外开放** - 攻击面太大
- ❌ **PostgreSQL (5432)对外开放** - 数据库直接暴露在互联网
- ❌ **Django (8000)对外开放** - 应用服务器不应该直接访问
- ❌ **监控端口对外开放** - 监控信息可能泄露

### 安全风险：
1. **数据库攻击** - PostgreSQL端口直接暴露
2. **应用绕过** - 可以直接访问Django，绕过nginx安全配置
3. **信息泄露** - 监控端口暴露系统信息
4. **DDoS攻击** - 更多端口意味着更多攻击向量

## ✅ 安全解决方案

### 端口安全配置：

**只对外开放必要端口：**
- ✅ **22 (SSH)** - 管理服务器必需
- ✅ **80 (HTTP)** - 网站访问，自动重定向到HTTPS  
- ✅ **443 (HTTPS)** - 安全的网站访问

**内部绑定端口：**
- 🔒 **5432 (PostgreSQL)** → `127.0.0.1:5432`
- 🔒 **8000 (Django)** → `127.0.0.1:8000`
- 🔒 **3001 (Uptime Kuma)** → `127.0.0.1:3001`
- 🔒 **9100 (Node Exporter)** → `127.0.0.1:9100`
- 🔒 **9999 (Dozzle)** → `127.0.0.1:9999`

## 🚀 安全部署步骤

### 1. 部署安全的主应用

```bash
# 备份并部署安全配置
./deploy_secure.sh
```

这会：
- 备份当前配置
- 使用 `docker-compose.prod-secure.yml`
- PostgreSQL和Django只绑定localhost
- 只开放22, 80, 443端口

### 2. 启动安全监控

```bash
# 启动安全监控系统
./start_secure_monitoring.sh
```

这会：
- 停止旧的不安全监控
- 启动只绑定localhost的监控服务
- 检查端口安全性

### 3. 通过SSH隧道访问监控

在**本地电脑**上运行：
```bash
# 创建SSH隧道
./ssh_tunnel.sh
```

然后在本地浏览器访问：
- http://localhost:3001 - 网站监控
- http://localhost:9999 - 日志监控
- http://localhost:9100 - 系统指标

## 🔧 SSH隧道使用

### 访问监控界面：
```bash
ssh -L 3001:localhost:3001 -L 9999:localhost:9999 -L 9100:localhost:9100 -N ec2-user@3.26.32.171
```

### 访问数据库：
```bash
ssh -L 5432:localhost:5432 -N ec2-user@3.26.32.171
# 然后可以在本地连接 localhost:5432
```

### 访问Django管理：
```bash
ssh -L 8000:localhost:8000 -N ec2-user@3.26.32.171
# 然后可以访问 http://localhost:8000/admin/
```

## 📊 安全验证

### 检查端口绑定：
```bash
# 在服务器上运行
sudo netstat -tuln

# 应该看到：
# 0.0.0.0:22    (SSH - 对外开放)
# 0.0.0.0:80    (HTTP - 对外开放)  
# 0.0.0.0:443   (HTTPS - 对外开放)
# 127.0.0.1:*   (其他服务 - 内部绑定)
```

### 测试端口访问：
```bash
# 这些应该失败 (从外网无法访问)
curl http://3.26.32.171:5432  # PostgreSQL - 应该超时
curl http://3.26.32.171:8000  # Django - 应该超时
curl http://3.26.32.171:3001  # 监控 - 应该超时

# 这些应该成功
curl https://selwyn-blog.duckdns.org/  # 网站正常访问
```

## 🛡️ 安全优势

### 1. **最小攻击面**
- 只开放绝对必要的端口
- 所有服务通过nginx代理或SSH隧道访问

### 2. **数据库安全**
- PostgreSQL不直接暴露在互联网
- 只能通过SSH隧道或应用内部访问

### 3. **监控安全**
- 监控界面不暴露系统信息
- 通过加密的SSH隧道安全访问

### 4. **应用安全**
- Django应用只能通过nginx访问
- 无法绕过nginx的安全配置

## 🚨 紧急恢复

### 如果出现问题，快速恢复：

```bash
# 恢复到之前的配置
sudo docker-compose -f docker-compose.prod-secure.yml down
sudo docker-compose -f docker-compose.prod.yml up -d

# 或者使用备份
sudo docker-compose -f docker-compose.prod.yml.backup.YYYYMMDD_HHMMSS up -d
```

## 📋 日常维护

### 1. 定期检查端口安全性：
```bash
sudo netstat -tuln | grep "0.0.0.0:"
```

### 2. 监控内存使用：
```bash
./monitor_memory.sh
```

### 3. 检查服务状态：
```bash
sudo docker-compose -f docker-compose.prod-secure.yml ps
sudo docker-compose -f docker-compose.monitoring-secure.yml ps
```

## 🎯 最佳实践

1. **定期更新系统和Docker镜像**
2. **使用强密码和SSH密钥认证**
3. **定期备份数据库**
4. **监控异常访问日志**
5. **定期检查安全配置**

## 📞 故障排除

### SSH隧道连接失败：
- 检查SSH密钥权限：`chmod 600 ~/.ssh/id_rsa`
- 确认服务器SSH服务运行：`sudo systemctl status sshd`

### 监控服务无法启动：
- 检查内存使用：`free -h`
- 查看Docker日志：`docker logs container_name`

### 网站无法访问：
- 检查nginx状态：`docker logs myblog-nginx-1`
- 确认SSL证书：`openssl s_client -connect selwyn-blog.duckdns.org:443`

---

**记住：安全是一个持续的过程，定期检查和更新配置非常重要！** 🔒 