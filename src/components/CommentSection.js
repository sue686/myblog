import React, { useState } from 'react';
import { Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { createComment, likeComment } from '../services/blog';

const Comment = ({ comment, user, onReply }) => {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const navigate = useNavigate();
  
  const handleLike = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    try {
      await likeComment(comment.id);
      // 页面刷新来获取更新后的评论数据
      window.location.reload();
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };
  
  return (
    <Card className="mb-3">
      <Card.Body>
        <div className="d-flex justify-content-between">
          <div className="d-flex mb-2">
            <img
              src={comment.author.avatar || "https://via.placeholder.com/40"}
              alt={comment.author.username}
              className="rounded-circle me-2"
              width="32"
              height="32"
            />
            <div>
              <div className="fw-bold">{comment.author.username}</div>
              <small className="text-muted">
                {new Date(comment.created_at).toLocaleString()}
              </small>
            </div>
          </div>
          <div>
            <Button
              variant={comment.is_liked ? "primary" : "outline-primary"}
              size="sm"
              onClick={handleLike}
            >
              {comment.likes_count} 赞
            </Button>
          </div>
        </div>
        
        <p className="mt-2">{comment.content}</p>
        
        <div className="d-flex">
          <Button
            variant="link"
            className="text-decoration-none p-0"
            onClick={() => setShowReplyForm(!showReplyForm)}
          >
            {showReplyForm ? '取消回复' : '回复'}
          </Button>
        </div>
        
        {showReplyForm && (
          <div className="mt-3">
            <ReplyForm
              parentId={comment.id}
              articleId={comment.article_id}
              onSubmit={() => {
                setShowReplyForm(false);
                window.location.reload();
              }}
              user={user}
            />
          </div>
        )}
        
        {comment.replies && comment.replies.length > 0 && (
          <div className="mt-3 ms-4">
            {comment.replies.map(reply => (
              <Comment
                key={reply.id}
                comment={reply}
                user={user}
                onReply={() => {}}
              />
            ))}
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

const ReplyForm = ({ parentId, articleId, onSubmit, user }) => {
  const [content, setContent] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      navigate('/login');
      return;
    }
    
    if (!content.trim()) {
      setError('评论内容不能为空');
      return;
    }
    
    try {
      setSubmitting(true);
      await createComment(articleId, content, parentId);
      setContent('');
      setError('');
      onSubmit();
    } catch (err) {
      setError('提交评论失败，请稍后重试');
      console.error('Error submitting comment:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form.Group className="mb-2">
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="写下你的评论..."
          value={content}
          onChange={e => setContent(e.target.value)}
        />
      </Form.Group>
      <Button
        type="submit"
        variant="primary"
        size="sm"
        disabled={submitting}
      >
        {submitting ? '提交中...' : '提交评论'}
      </Button>
    </Form>
  );
};

const CommentSection = ({ article, user }) => {
  return (
    <div className="mt-5">
      <h3>评论 ({article.comments_count})</h3>
      
      <div className="my-4">
        <ReplyForm
          articleId={article.id}
          parentId={null}
          onSubmit={() => window.location.reload()}
          user={user}
        />
      </div>
      
      {article.comments && article.comments.length > 0 ? (
        article.comments.map(comment => (
          <Comment
            key={comment.id}
            comment={comment}
            user={user}
            onReply={() => {}}
          />
        ))
      ) : (
        <p className="text-center text-muted my-5">暂无评论，来发表第一条评论吧！</p>
      )}
    </div>
  );
};

export default CommentSection; 