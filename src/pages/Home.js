import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Badge, Form, InputGroup, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { getArticles, getCategories, getTags } from '../services/blog';

const Home = () => {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 筛选和搜索状态
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // 加载文章数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = {
          page: currentPage,
          search: searchQuery,
        };
        
        if (selectedCategory) {
          params.category = selectedCategory;
        }
        
        if (selectedTag) {
          params.tag = selectedTag;
        }
        
        const response = await getArticles(params);
        setArticles(response.results);
        setTotalPages(Math.ceil(response.count / 10));
        
        // 获取分类和标签
        const categoriesData = await getCategories();
        const tagsData = await getTags();
        
        setCategories(categoriesData.results);
        setTags(tagsData.results);
        
        setLoading(false);
      } catch (err) {
        setError('加载数据失败，请稍后重试');
        setLoading(false);
        console.error('Error fetching data:', err);
      }
    };
    
    fetchData();
  }, [currentPage, searchQuery, selectedCategory, selectedTag]);

  // 处理搜索
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // 重置到第一页
  };

  // 重置筛选
  const handleReset = () => {
    setSearchQuery('');
    setSelectedCategory('');
    setSelectedTag('');
    setCurrentPage(1);
  };

  if (loading && articles.length === 0) {
    return <div className="text-center my-5">加载中...</div>;
  }

  if (error) {
    return <div className="text-center my-5 text-danger">{error}</div>;
  }

  return (
    <div>
      <h1 className="mb-4">最新文章</h1>
      
      <Row className="mb-4">
        <Col md={8}>
          <Form onSubmit={handleSearch}>
            <InputGroup>
              <Form.Control
                placeholder="搜索文章..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <Button type="submit" variant="primary">搜索</Button>
              <Button variant="secondary" onClick={handleReset}>重置</Button>
            </InputGroup>
          </Form>
        </Col>
        <Col md={2}>
          <Form.Select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option value="">所有分类</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Form.Select>
        </Col>
        <Col md={2}>
          <Form.Select
            value={selectedTag}
            onChange={(e) => {
              setSelectedTag(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option value="">所有标签</option>
            {tags.map(tag => (
              <option key={tag.id} value={tag.id}>
                {tag.name}
              </option>
            ))}
          </Form.Select>
        </Col>
      </Row>
      
      {articles.length === 0 ? (
        <div className="text-center my-5">未找到文章</div>
      ) : (
        <Row>
          {articles.map(article => (
            <Col md={6} lg={4} key={article.id} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body>
                  <Card.Title>
                    <Link to={`/articles/${article.id}`} className="text-decoration-none text-dark">
                      {article.title}
                    </Link>
                  </Card.Title>
                  <div className="mb-2">
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
                  <Card.Text className="text-muted small">
                    作者: {article.author.username} | 
                    发布: {new Date(article.created_at).toLocaleDateString()} | 
                    浏览: {article.view_count}
                  </Card.Text>
                  <div className="d-flex justify-content-between align-items-center mt-2">
                    <div>
                      <small className="text-muted me-2">
                        <i className="bi bi-chat"></i> {article.comments_count}
                      </small>
                      <small className="text-muted">
                        <i className="bi bi-heart"></i> {article.likes_count}
                      </small>
                    </div>
                    <Link to={`/articles/${article.id}`} className="btn btn-sm btn-outline-primary">
                      阅读更多
                    </Link>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
      
      {/* 分页 */}
      <div className="d-flex justify-content-center mt-4">
        <Button
          variant="outline-primary"
          className="me-2"
          disabled={currentPage === 1}
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
        >
          上一页
        </Button>
        <span className="align-self-center mx-2">
          第 {currentPage} 页 / 共 {totalPages} 页
        </span>
        <Button
          variant="outline-primary"
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
        >
          下一页
        </Button>
      </div>
    </div>
  );
};

export default Home; 