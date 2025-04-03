import React, { useState } from 'react';
import { Form, Button, Card, Alert, Container, Row, Col } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { login } from '../services/auth';

const Login = ({ setUser }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('请输入用户名和密码');
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      const user = await login(username, password);
      setUser(user);
      window.location.href = '/'; // 强制刷新页面，确保全局状态更新
    } catch (err) {
      console.error('Login error:', err);
      setError('登录失败，请检查用户名和密码');
      setLoading(false);
    }
  };

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={6}>
          <Card className="shadow-sm">
            <Card.Body className="p-4">
              <h2 className="text-center mb-4">用户登录</h2>
              
              {error && <Alert variant="danger">{error}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>用户名</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="输入用户名"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>密码</Form.Label>
                  <Form.Control
                    type="password"
                    placeholder="输入密码"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                  />
                </Form.Group>
                
                <div className="d-grid">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loading}
                  >
                    {loading ? '登录中...' : '登录'}
                  </Button>
                </div>
              </Form>
              
              <div className="text-center mt-3">
                <p>
                  还没有账号？ <Link to="/register">立即注册</Link>
                </p>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Login; 