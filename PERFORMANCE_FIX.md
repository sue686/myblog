# 🚑 网站性能问题修复指南

## 🔍 问题诊断

### **问题现象**
- 网站打不开或响应极慢
- SSH连接超时或响应缓慢
- EC2实例资源不足

### **根本原因**
1. **监控系统资源消耗过大**
   - 完整监控栈需要1.5-2GB内存
   - t2.micro实例只有1GB内存
   - 导致系统内存不足，性能急剧下降

2. **nginx配置问题**
   - 配置文件路径错误
   - 静态文件路径不匹配

3. **Docker容器冲突**
   - 监控服务与主应用争夺资源
   - 网络配置冲突

## 🚀 立即修复方案

### **第1步：登录EC2服务器**
```bash
ssh -i ~/Downloads/Myblog.pem ec2-user@3.26.32.171
```

### **第2步：执行紧急修复**
```bash
# 进入项目目录
cd /home/ec2-user/myblog

# 下载修复脚本
git pull origin main

# 执行紧急修复
chmod +x quick_fix.sh
./quick_fix.sh
```

### **第3步：验证修复结果**
```bash
# 检查网站状态
curl http://3.26.32.171

# 检查内存使用
free -h

# 检查运行的容器
sudo docker ps
```

## 📊 资源使用对比

### **修复前（完整监控）**
- **内存使用**: 1.5-2GB
- **CPU使用**: 60-80%
- **容器数量**: 11个
- **网络端口**: 8个

### **修复后（仅主应用）**
- **内存使用**: 400-500MB
- **CPU使用**: 10-20%
- **容器数量**: 3个
- **网络端口**: 3个

## 🎯 长期解决方案

### **方案1：升级EC2实例（推荐）**
```bash
# 升级到t3.small或t3.medium
# t3.small: 2GB内存，足够运行轻量级监控
# t3.medium: 4GB内存，可运行完整监控
```

### **方案2：使用轻量级监控**
```bash
# 启动轻量级监控（仅550MB内存）
chmod +x start_lite_monitoring.sh
./start_lite_monitoring.sh
```

### **方案3：分离监控服务**
```bash
# 在独立的EC2实例运行监控系统
# 主应用实例：运行Django+nginx+PostgreSQL
# 监控实例：运行Prometheus+Grafana
```

## 🔧 配置优化

### **已修复的配置问题**

1. **nginx配置修复**
   ```nginx
   # 修复前
   - ./nginx/nginx.conf:/etc/nginx/nginx.conf
   
   # 修复后
   - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
   ```

2. **静态文件路径修复**
   ```nginx
   # 修复前
   alias /app/static/;
   
   # 修复后
   alias /app/staticfiles/;
   ```

3. **代理配置优化**
   ```nginx
   # 增加超时时间
   proxy_connect_timeout 60s;
   proxy_send_timeout 60s;
   proxy_read_timeout 60s;
   ```

## 🚨 故障排除

### **如果网站仍然无法访问**
```bash
# 检查容器状态
sudo docker-compose -f docker-compose.prod.yml ps

# 查看应用日志
sudo docker-compose -f docker-compose.prod.yml logs web

# 查看nginx日志
sudo docker-compose -f docker-compose.prod.yml logs nginx

# 重启所有服务
sudo docker-compose -f docker-compose.prod.yml restart
```

### **如果SSH连接仍然很慢**
```bash
# 检查系统负载
top

# 检查内存使用
free -h

# 检查磁盘使用
df -h

# 清理Docker资源
sudo docker system prune -f
```

## 💡 预防措施

### **资源监控**
```bash
# 定期检查资源使用
free -h
df -h
sudo docker stats
```

### **自动化监控**
```bash
# 设置资源告警
# 内存使用 > 80%
# 磁盘使用 > 90%
# CPU使用 > 80%
```

### **备份策略**
```bash
# 定期备份数据库
sudo docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres myblogdb > backup.sql
```

## 🎉 修复完成验证

### **网站功能测试**
- [ ] 主页正常加载
- [ ] 用户注册/登录功能
- [ ] 博客文章显示正常
- [ ] 管理后台可访问
- [ ] 静态文件加载正常

### **性能测试**
- [ ] 页面响应时间 < 2秒
- [ ] 内存使用 < 80%
- [ ] CPU使用 < 50%
- [ ] 磁盘使用 < 80%

## 📞 支持

如果问题仍然存在，请提供以下信息：
1. 执行`sudo docker ps`的输出
2. 执行`free -h`的输出
3. 执行`df -h`的输出
4. 应用日志的最后50行

---

**记住：t2.micro实例的限制是1GB内存，运行完整监控系统会导致资源不足！** 