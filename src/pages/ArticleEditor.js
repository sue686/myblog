import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Button, Row, Col, Card, Alert } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { createArticle, updateArticle, getArticle, getCategories, getTags } from '../services/blog';

const ArticleEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = !!id;
  
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [tagsIds, setTagsIds] = useState([]);
  const [isPublished, setIsPublished] = useState(false);
  
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [preview, setPreview] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // 加载分类和标签数据
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [categoriesData, tagsData] = await Promise.all([
          getCategories(),
          getTags()
        ]);
        
        setCategories(categoriesData.results);
        setTags(tagsData.results);
      } catch (error) {
        console.error('Error fetching metadata:', error);
        setError('加载分类和标签失败');
      }
    };
    
    fetchMetadata();
  }, []);
  
  // 如果是编辑模式，加载文章数据
  useEffect(() => {
    if (isEditing) {
      const fetchArticle = async () => {
        try {
          setLoading(true);
          const article = await getArticle(id);
          
          setTitle(article.title);
          setContent(article.content);
          setCategoryId(article.category ? article.category.id : '');
          setTagsIds(article.tags.map(tag => tag.id));
          setIsPublished(article.is_published);
          setLoading(false);
        } catch (error) {
          console.error('Error fetching article:', error);
          setError('加载文章失败，请稍后重试');
          setLoading(false);
        }
      };

      fetchArticle();
    }
  }, [id, isEditing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      
      const articleData = {
        title,
        content,
        category: categoryId,
        tags: tagsIds,
        is_published: isPublished,
      };
      
      if (isEditing) {
        await updateArticle(id, articleData);
      } else {
        await createArticle(articleData);
      }
      
      navigate('/');
    } catch (error) {
      console.error('Error saving article:', error);
      setError('保存文章失败，请稍后重试');
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>{isEditing ? '编辑文章' : '写新文章'}</h1>
      <Form onSubmit={handleSubmit}>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form.Group className="mb-3">
          <Form.Label>标题</Form.Label>
          <Form.Control
            type="text"
            placeholder="输入文章标题"
            value={title}
            onChange={e => setTitle(e.target.value)}
            required
          />
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Label>内容</Form.Label>
          <Form.Control
            as="textarea"
            rows={10}
            placeholder="输入文章内容"
            value={content}
            onChange={e => setContent(e.target.value)}
            required
          />
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Label>分类</Form.Label>
          <Form.Select
            value={categoryId}
            onChange={e => setCategoryId(e.target.value)}
          >
            <option value="">选择分类</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </Form.Select>
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Label>标签</Form.Label>
          <Form.Select
            multiple
            value={tagsIds}
            onChange={e => setTagsIds([...e.target.selectedOptions].map(option => option.value))}
          >
            {tags.map(tag => (
              <option key={tag.id} value={tag.id}>
                {tag.name}
              </option>
            ))}
          </Form.Select>
        </Form.Group>
        
        <Form.Group className="mb-3">
          <Form.Check
            type="checkbox"
            label="发布文章"
            checked={isPublished}
            onChange={e => setIsPublished(e.target.checked)}
          />
          <Form.Text className="text-muted">
            未发布的文章仅自己可见
          </Form.Text>
        </Form.Group>
        
        <div className="d-flex justify-content-between">
          <Button
            variant="outline-secondary"
            onClick={() => setPreview(!preview)}
          >
            {preview ? '关闭预览' : '预览'}
          </Button>
          
          <div>
            <Button
              variant="secondary"
              className="me-2"
              onClick={() => navigate(-1)}
            >
              取消
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
            >
              {loading ? '保存中...' : '保存文章'}
            </Button>
          </div>
        </div>
      </Form>
      
      {preview && (
        <Card className="mt-4">
          <Card.Body>
            <h2>预览</h2>
            <h3>{title || '文章标题'}</h3>
            <ReactMarkdown>{content || '文章内容'}</ReactMarkdown>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default ArticleEditor; 