pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry-url'
        IMAGE_NAME = 'myblog'
        DEPLOY_HOST = '3.27.147.21'
        DEPLOY_USER = 'ec2-user'
        SLACK_WEBHOOK = credentials('slack-webhook-url')
    }
    
    stages {
        stage('环境检查') {
            steps {
                script {
                    echo "🚀 开始构建流水线..."
                    echo "分支: ${env.BRANCH_NAME}"
                    echo "构建号: ${env.BUILD_NUMBER}"
                    echo "提交SHA: ${env.GIT_COMMIT}"
                }
            }
        }
        
        stage('代码检查') {
            parallel {
                stage('代码风格检查') {
                    steps {
                        script {
                            echo "🔍 执行代码风格检查..."
                            sh """
                                python -m pip install flake8 black isort
                                flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                                black --check .
                                isort --check-only .
                            """
                        }
                    }
                }
                
                stage('安全扫描') {
                    steps {
                        script {
                            echo "🔒 执行安全扫描..."
                            sh """
                                python -m pip install bandit safety
                                bandit -r . -f json -o bandit-report.json || true
                                safety check --json --output safety-report.json || true
                            """
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('单元测试') {
            steps {
                script {
                    echo "🧪 运行单元测试..."
                    sh """
                        python -m pip install -r requirements.txt
                        python -m pip install coverage
                        python manage.py test
                        coverage run --source='.' manage.py test
                        coverage report
                        coverage html
                    """
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: '测试覆盖率报告'
                    ])
                }
            }
        }
        
        stage('构建Docker镜像') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🐳 构建Docker镜像..."
                    def imageTag = "${IMAGE_NAME}:${env.BUILD_NUMBER}"
                    def latestTag = "${IMAGE_NAME}:latest"
                    
                    sh """
                        docker build -t ${imageTag} .
                        docker tag ${imageTag} ${latestTag}
                        echo "镜像构建完成: ${imageTag}"
                    """
                }
            }
        }
        
        stage('部署到生产环境') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🚀 部署到生产环境..."
                    
                    // 使用SSH凭证部署
                    withCredentials([sshUserPrivateKey(
                        credentialsId: 'deploy-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} << 'EOF'
                                cd /home/ec2-user/myblog
                                sudo docker-compose down
                                sudo docker-compose pull
                                sudo docker-compose up -d
                                
                                echo "等待服务启动..."
                                sleep 30
                                
                                # 健康检查
                                if curl -f http://localhost/health/; then
                                    echo "✅ 部署成功！"
                                else
                                    echo "❌ 部署失败！"
                                    exit 1
                                fi
                            EOF
                        """
                    }
                }
            }
        }
        
        stage('部署验证') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "🔍 验证部署状态..."
                    sh """
                        # 验证网站可访问性
                        curl -f http://${DEPLOY_HOST}/health/ || exit 1
                        
                        # 验证关键功能
                        curl -f http://${DEPLOY_HOST}/ || exit 1
                        
                        echo "✅ 部署验证通过！"
                    """
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo "🧹 清理工作空间..."
                // 清理临时文件
                sh "docker system prune -f || true"
            }
        }
        
        success {
            script {
                echo "🎉 构建成功！"
                // 发送成功通知
                httpRequest(
                    url: "${SLACK_WEBHOOK}",
                    httpMode: 'POST',
                    contentType: 'APPLICATION_JSON',
                    requestBody: """
                    {
                        "text": "🚀 博客系统部署成功！\\n📝 分支: ${env.BRANCH_NAME}\\n🔢 构建号: ${env.BUILD_NUMBER}\\n👤 提交者: ${env.CHANGE_AUTHOR}\\n🔗 访问: http://${DEPLOY_HOST}"
                    }
                    """
                )
            }
        }
        
        failure {
            script {
                echo "❌ 构建失败！"
                // 发送失败通知
                httpRequest(
                    url: "${SLACK_WEBHOOK}",
                    httpMode: 'POST',
                    contentType: 'APPLICATION_JSON',
                    requestBody: """
                    {
                        "text": "❌ 博客系统部署失败！\\n📝 分支: ${env.BRANCH_NAME}\\n🔢 构建号: ${env.BUILD_NUMBER}\\n🔗 查看日志: ${env.BUILD_URL}"
                    }
                    """
                )
            }
        }
    }
} 