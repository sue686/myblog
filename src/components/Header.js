import React from 'react';
import { Navbar, Nav, Container, Button, NavDropdown } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/auth';

const Header = ({ user, setUser }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setUser(null);
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand as={Link} to="/">个人博客</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">首页</Nav.Link>
          </Nav>
          <Nav>
            {user ? (
              <>
                <Button 
                  as={Link} 
                  to="/editor" 
                  variant="outline-light" 
                  className="me-2"
                >
                  写文章
                </Button>
                <NavDropdown title={user.username} id="basic-nav-dropdown">
                  <NavDropdown.Item as={Link} to="/profile">个人资料</NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleLogout}>退出登录</NavDropdown.Item>
                </NavDropdown>
              </>
            ) : (
              <>
                <Nav.Link as={Link} to="/login">登录</Nav.Link>
                <Nav.Link as={Link} to="/register">注册</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header; 