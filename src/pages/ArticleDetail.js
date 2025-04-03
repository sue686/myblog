import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Container, Row, Col, Button, Badge, Card } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { getArticle, likeArticle, favoriteArticle } from '../services/blog';
import CommentSection from '../components/CommentSection';

const ArticleDetail = ({ user }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        const data = await getArticle(id);
        setArticle(data);
        setLoading(false);
      } catch (err) {
        setError('加载文章失败，请稍后重试');
        setLoading(false);
        console.error('Error fetching article:', err);
      }
    };

    fetchArticle();
  }, [id]);

  const handleLike = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      await likeArticle(id);
      const updatedArticle = await getArticle(id);
      setArticle(updatedArticle);
    } catch (error) {
      console.error('Error liking article:', error);
    }
  };

  const handleFavorite = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      await favoriteArticle(id);
      const updatedArticle = await getArticle(id);
      setArticle(updatedArticle);
    } catch (error) {
      console.error('Error favoriting article:', error);
    }
  };

  if (loading) {
    return <div className="text-center my-5">加载中...</div>;
  }

  if (error || !article) {
    return <div className="text-center my-5 text-danger">{error || '文章不存在'}</div>;
  }

  return (
    <Container>
      <article>
        <h1 className="mb-3">{article.title}</h1>
        
        <div className="d-flex justify-content-between mb-3">
          <div>
            <small className="text-muted">
              作者: {article.author.username} | 
              发布: {new Date(article.published_at || article.created_at).toLocaleString()} | 
              浏览: {article.view_count}
            </small>
          </div>
          {user && user.id === article.author.id && (
            <Link to={`/editor/${article.id}`} className="btn btn-sm btn-outline-secondary">
              编辑文章
            </Link>
          )}
        </div>
        
        <div className="mb-3">
          {article.category && (
            <Badge bg="primary" className="me-1">
              {article.category.name}
            </Badge>
          )}
          {article.tags.map(tag => (
            <Badge bg="secondary" key={tag.id} className="me-1">
              {tag.name}
            </Badge>
          ))}
        </div>
        
        <div className="d-flex mb-4">
          <Button
            variant={article.is_liked ? "primary" : "outline-primary"}
            className="me-2"
            onClick={handleLike}
          >
            {article.is_liked ? '已点赞' : '点赞'} ({article.likes_count})
          </Button>
          <Button
            variant={article.is_favorited ? "warning" : "outline-warning"}
            onClick={handleFavorite}
          >
            {article.is_favorited ? '已收藏' : '收藏'}
          </Button>
        </div>
        
        <Card className="mb-4 p-4">
          <ReactMarkdown className="article-content">
            {article.content}
          </ReactMarkdown>
        </Card>
      </article>
      
      <CommentSection article={article} user={user} />
    </Container>
  );
};

export default ArticleDetail; 