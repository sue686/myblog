import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Container, Row, Col, Image } from 'react-bootstrap';
import { updateProfile } from '../services/auth';
import { getArticles } from '../services/blog';
import { Link } from 'react-router-dom';

const Profile = ({ user, setUser }) => {
  const [avatar, setAvatar] = useState(null);
  const [bio, setBio] = useState(user?.bio || '');
  const [website, setWebsite] = useState(user?.website || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [avatarPreview, setAvatarPreview] = useState(user?.avatar || '');
  
  const [userArticles, setUserArticles] = useState([]);
  const [articlesLoading, setArticlesLoading] = useState(true);

  // 加载用户的文章
  useEffect(() => {
    const fetchUserArticles = async () => {
      try {
        setArticlesLoading(true);
        const response = await getArticles({ author: user.id });
        setUserArticles(response.results);
        setArticlesLoading(false);
      } catch (error) {
        console.error('Error fetching user articles:', error);
        setArticlesLoading(false);
      }
    };

    if (user) {
      fetchUserArticles();
    }
  }, [user]);

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setAvatar(file);
      
      // 创建预览URL
      const previewUrl = URL.createObjectURL(file);
      setAvatarPreview(previewUrl);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const formData = new FormData();
      if (avatar) {
        formData.append('avatar', avatar);
      }
      formData.append('bio', bio);
      formData.append('website', website);
      
      const updatedUser = await updateProfile(formData);
      setUser({...user, ...updatedUser});
      setSuccess('个人资料更新成功');
      setLoading(false);
    } catch (err) {
      console.error('Profile update error:', err);
      setError('更新个人资料失败，请稍后重试');
      setLoading(false);
    }
  };

  return (
    <Container>
      <h1 className="mb-4">个人资料</h1>
      
      <Row>
        <Col md={4}>
          <Card className="mb-4">
            <Card.Body className="text-center">
              <div className="mb-3">
                <Image 
                  src={avatarPreview || "https://via.placeholder.com/150"} 
                  roundedCircle 
                  width={150} 
                  height={150}
                  className="border"
                />
              </div>
              <h5>{user?.username}</h5>
              <p className="text-muted">注册于 {new Date(user?.date_joined).toLocaleDateString()}</p>
              
              {user?.bio && <p>{user.bio}</p>}
              {user?.website && (
                <p>
                  <a href={user.website} target="_blank" rel="noopener noreferrer">
                    {user.website.replace(/(^\w+:|^)\/\//, '')}
                  </a>
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={8}>
          <Card className="mb-4">
            <Card.Body>
              <h4 className="mb-3">编辑个人资料</h4>
              
              {error && <Alert variant="danger">{error}</Alert>}
              {success && <Alert variant="success">{success}</Alert>}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>头像</Form.Label>
                  <Form.Control
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarChange}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>个人简介</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    placeholder="写一些关于你自己的介绍"
                    value={bio}
                    onChange={e => setBio(e.target.value)}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>个人网站</Form.Label>
                  <Form.Control
                    type="url"
                    placeholder="例如: https://yourwebsite.com"
                    value={website}
                    onChange={e => setWebsite(e.target.value)}
                  />
                </Form.Group>
                
                <div className="d-grid">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loading}
                  >
                    {loading ? '保存中...' : '保存更改'}
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>
          
          <Card>
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="mb-0">我的文章</h4>
                <Link to="/editor" className="btn btn-sm btn-primary">
                  写新文章
                </Link>
              </div>
              
              {articlesLoading ? (
                <p className="text-center my-4">加载中...</p>
              ) : userArticles.length === 0 ? (
                <p className="text-center my-4">你还没有发布任何文章</p>
              ) : (
                <div>
                  {userArticles.map(article => (
                    <div key={article.id} className="border-bottom py-3">
                      <h5>
                        <Link to={`/articles/${article.id}`} className="text-decoration-none">
                          {article.title}
                        </Link>
                      </h5>
                      <div className="d-flex justify-content-between">
                        <small className="text-muted">
                          发布于 {new Date(article.created_at).toLocaleDateString()} • 
                          {article.comments_count} 评论 • 
                          {article.likes_count} 点赞
                        </small>
                        <div>
                          <Link to={`/editor/${article.id}`} className="btn btn-sm btn-outline-secondary me-2">
                            编辑
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Profile; 