#!/bin/bash

# GitLab CI/CD测试脚本
set -e

echo "🚀 测试GitLab CI/CD流水线..."

# 1. 检查Git远程仓库状态
echo "🔍 检查Git远程仓库..."
git remote -v

# 2. 检查当前分支
echo "🌿 当前分支状态..."
git branch -a
git status

# 3. 推送测试更改到GitLab
echo "📤 推送测试更改到GitLab..."
echo "# GitLab CI/CD测试 - $(date)" >> .gitlab-ci-test.md
git add .gitlab-ci-test.md
git commit -m "ci: 测试GitLab CI/CD流水线 - $(date)"

# 4. 推送到GitLab
echo "🚀 触发GitLab CI/CD..."
git push gitlab main

echo "✅ 测试推送完成！"
echo "🌐 请访问 GitLab 查看流水线状态:"
echo "   https://gitlab.com/sue686/myblog/-/pipelines"
echo ""
echo "📊 预期的CI/CD阶段:"
echo "   1. ✅ test_quality - 代码质量检查"
echo "   2. ✅ security_scan - 安全扫描"
echo "   3. ✅ build_docker - Docker构建"
echo "   4. 🔄 deploy_staging - 手动部署到staging"
echo "   5. 🔄 deploy_production - 手动部署到生产"
echo ""
echo "💡 如果看到流水线运行，说明GitLab CI/CD配置成功！" 