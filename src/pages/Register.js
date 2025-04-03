import React, { useState } from 'react';
import { Form, Button, Card, Alert, Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { register } from '../services/auth';

const Register = ({ setUser }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 基本验证
    if (!username || !email || !password || !passwordConfirm) {
      setError('所有字段都是必填的');
      return;
    }
    
    if (password !== passwordConfirm) {
      setError('两次输入的密码不一致');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      const user = await register(username, email, password, passwordConfirm);
      setUser(user);
      window.location.href = '/'; // 强制刷新页面，确保全局状态更新
    } catch (err) {
      console.error('Registration error:', err);
      if (err.response && err.response.data) {
        // 格式化后端验证错误
        const errors = err.response.data;
        let errorMsg = '';
        Object.keys(errors).forEach(key => {
          errorMsg += `${key}: ${errors[key].join(', ')} `;
        });
        setError(errorMsg || '注册失败，请稍后重试');
      } else {
        setError('注册失败，请稍后重试');
      }
      setLoading(false);
    }
  };

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Body className="p-4">
              <h2 className="text-center mb-4">用户注册</h2>
              
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>用户名</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="选择一个用户名"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>邮箱</Form.Label>
                  <Form.Control
                    type="email"
                    placeholder="输入您的邮箱"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>密码</Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="设置密码"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>确认密码</Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="再次输入密码"
                    value={passwordConfirm}
                    onChange={e => setPasswordConfirm(e.target.value)}
                  />
                </Form.Group>
                
                <div className="d-grid">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loading}
                  >
                    {loading ? '注册中...' : '注册'}
                  </Button>
                </div>
              </Form>
              
              <div className="text-center mt-3">
                <p>
                  已有账号？ <Link to="/login">立即登录</Link>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Register; 