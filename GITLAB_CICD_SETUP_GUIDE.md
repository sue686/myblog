# GitLab CI/CD 配置指南

## 🚀 为什么选择GitLab CI/CD？

### **成本优势**
- ✅ **完全免费**：GitLab.com提供每月400分钟免费CI/CD
- ✅ **无需额外EC2**：避免超出AWS免费额度
- ✅ **集成度高**：代码仓库+CI/CD一体化

### **技术优势**
- 配置简单，学习成本低
- Docker原生支持
- 自动化测试+安全扫描
- 可视化Pipeline界面

## 📋 实施步骤

### 1. 创建GitLab项目

```bash
# 如果还没有GitLab账号，先注册：https://gitlab.com/users/sign_up

# 创建新项目或导入现有项目
git remote add gitlab https://gitlab.com/yourusername/myblog.git
git push -u gitlab main
```

### 2. 配置GitLab CI/CD Variables

在GitLab项目中设置以下环境变量：

**项目设置 > CI/CD > Variables**

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `SSH_PRIVATE_KEY` | `~/Downloads/Myblog.pem内容` | SSH私钥 |
| `DEPLOY_HOST` | `3.27.147.21` | 部署服务器IP |
| `DEPLOY_USER` | `ec2-user` | 部署用户名 |
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/...` | Slack通知（可选） |

### 3. 配置SSH私钥

```bash
# 查看SSH私钥内容
cat ~/Downloads/Myblog.pem

# 复制全部内容到GitLab的SSH_PRIVATE_KEY变量中
# 注意：包含-----BEGIN RSA PRIVATE KEY-----和-----END RSA PRIVATE KEY-----
```

### 4. 验证Pipeline

```bash
# 推送代码触发Pipeline
git add .
git commit -m "添加GitLab CI/CD配置"
git push gitlab main
```

## 🎯 Pipeline功能说明

### 阶段1：测试 (test)
- **代码风格检查**：flake8 + black + isort
- **单元测试**：Django test + 覆盖率报告
- **并行执行**：提高效率

### 阶段2：安全扫描 (security)
- **Bandit**：Python安全漏洞扫描
- **Safety**：依赖包安全检查
- **报告生成**：JSON格式报告

### 阶段3：构建 (build)
- **Docker镜像构建**：自动化构建
- **镜像推送**：推送到GitLab Registry
- **版本标记**：基于Git commit SHA

### 阶段4：部署 (deploy)
- **自动部署**：SSH连接到EC2部署
- **健康检查**：验证部署成功
- **通知发送**：Slack通知（可选）

## 🔧 高级配置

### 1. 分支策略

```yaml
# 不同分支不同策略
only:
  - main        # 生产部署
  - develop     # 开发测试
  - /^feature/  # 功能分支
```

### 2. 缓存优化

```yaml
# 添加缓存提高构建速度
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .pip-cache/
    - node_modules/
```

### 3. 手动部署

```yaml
# 生产环境手动触发
deploy_production:
  when: manual
  only:
    - main
```

## 🛠️ 故障排除

### 1. SSH连接失败

```bash
# 检查SSH私钥格式
echo "$SSH_PRIVATE_KEY" | head -1
# 应该显示：-----BEGIN RSA PRIVATE KEY-----

# 检查服务器连接
ssh -i ~/Downloads/Myblog.pem ec2-user@3.27.147.21
```

### 2. Docker构建失败

```bash
# 检查Dockerfile
docker build -t myblog:test .

# 查看构建日志
docker logs <container_id>
```

### 3. 部署失败

```bash
# 检查服务器状态
ssh -i ~/Downloads/Myblog.pem ec2-user@3.27.147.21
sudo docker-compose ps
sudo docker-compose logs
```

## 📊 监控与告警

### 1. Pipeline监控

- **Pipeline状态**：GitLab自动显示
- **测试覆盖率**：集成在MR中
- **安全报告**：Security Dashboard

### 2. 部署监控

```bash
# 添加健康检查
curl -f http://3.27.147.21/health/
```

### 3. 告警配置

```yaml
# Slack通知配置
notify_failure:
  stage: deploy
  script:
    - echo "发送失败通知"
  when: on_failure
```

## 🎉 完成检查清单

- [ ] GitLab项目创建完成
- [ ] CI/CD Variables配置完成
- [ ] SSH私钥配置正确
- [ ] Pipeline运行成功
- [ ] 部署验证通过
- [ ] 健康检查正常
- [ ] 通知配置工作

## 💡 成本优化建议

### 当前方案：**完全免费**
- GitLab.com免费版：400分钟/月
- 无需额外EC2实例
- 总成本：**$0/月**

### 如果超出免费额度：
1. **GitLab Premium**：$19/月/用户
2. **自建GitLab Runner**：在现有EC2上运行
3. **Jenkins轻量级版**：2GB内存版本

## 🚀 下一步计划

1. ✅ 配置GitLab CI/CD
2. 🔄 测试Pipeline
3. 📊 添加监控
4. 🛡️ 完善安全扫描
5. 📈 优化性能

---

**澳洲求职加分项：**
- GitLab CI/CD：现代化DevOps工具
- 安全扫描：DevSecOps实践
- 自动化部署：提高效率
- 监控告警：运维能力证明 