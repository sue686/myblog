# 轻量级监控系统使用指南

## 🎯 设计目标

针对**t2.micro (1GB内存)**实例优化的轻量级监控方案，总内存消耗<100MB。

## 📊 当前服务器状态

- **总内存**: 949Mi (1GB)
- **当前使用**: 48% (453Mi/949Mi)
- **主要应用**: Django博客 + PostgreSQL + Nginx
- **磁盘使用**: 86% (需要关注)

## 🚀 启动监控系统

```bash
# 启动基础监控
chmod +x start_basic_monitoring.sh
./start_basic_monitoring.sh
```

## 🛑 停止监控系统

```bash
# 停止监控
chmod +x stop_basic_monitoring.sh
./stop_basic_monitoring.sh
```

## 📱 监控界面

启动后可以访问：

- **网站监控**: http://3.26.32.171:3001 (Uptime Kuma)
- **日志监控**: http://3.26.32.171:9999 (Dozzle)
- **系统指标**: http://3.26.32.171:9100 (Node Exporter)

## 🔧 手动检查

```bash
# 检查内存和磁盘使用
chmod +x monitor_memory.sh
./monitor_memory.sh
```

## ⚠️ 告警阈值

- **内存使用率**: >70% 告警
- **磁盘使用率**: >90% 告警
- **网站响应时间**: >5秒 告警

## 📋 推荐配置

### 1. Uptime Kuma 配置

访问 http://3.26.32.171:3001 并添加监控：

```
监控类型: HTTP(s)
名称: 博客网站
URL: https://selwyn-blog.duckdns.org
间隔: 60秒
```

### 2. 设置定时监控

```bash
# 添加到crontab，每5分钟检查一次
sudo crontab -e

# 添加这行：
*/5 * * * * /home/ec2-user/myblog/monitor_memory.sh
```

### 3. 查看监控日志

```bash
# 查看监控日志
sudo tail -f /var/log/memory_monitor.log
```

## 🎛️ 资源限制

每个监控容器都设置了资源限制：

- **node-exporter**: 最大20MB内存
- **uptime-kuma**: 最大50MB内存  
- **dozzle**: 最大20MB内存

**总计**: <100MB内存消耗

## 🆘 紧急情况处理

### 内存不足时：

```bash
# 1. 停止监控系统
./stop_basic_monitoring.sh

# 2. 清理Docker
sudo docker system prune -f

# 3. 重启主要服务
sudo docker-compose -f docker-compose.prod.yml restart
```

### 磁盘空间不足时：

```bash
# 1. 清理日志
sudo journalctl --vacuum-time=7d
sudo docker logs myblog-web-1 2>/dev/null | tail -100 > /tmp/app.log

# 2. 清理Docker
sudo docker system prune -af

# 3. 删除旧的数据库备份
rm -f backup_*.sql
```

## 📈 监控指标

### 关键指标：
- ✅ 内存使用率 (当前: 48%)
- ✅ 磁盘使用率 (当前: 86% - 需要关注)
- ✅ 网站可用性
- ✅ 容器状态

### 可选指标：
- CPU使用率
- 网络流量
- 数据库连接数

## 🔄 日常维护

1. **每天检查**: `./monitor_memory.sh`
2. **每周清理**: `sudo docker system prune -f`
3. **每月备份**: 数据库备份文件管理
4. **监控访问**: 定期查看Uptime Kuma界面

## 🎯 性能优化建议

如果内存使用率持续>70%：

1. 考虑升级到t3.small (2GB内存)
2. 优化Django应用配置
3. 调整PostgreSQL内存设置
4. 临时停止监控系统 