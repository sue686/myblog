import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  return (
    <footer className="bg-dark text-white py-4 mt-4">
      <Container>
        <Row>
          <Col md={6}>
            <h5>个人博客</h5>
            <p>分享知识，连接世界</p>
          </Col>
          <Col md={6} className="text-md-end">
            <p>&copy; {new Date().getFullYear()} 个人博客. 保留所有权利.</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer; 