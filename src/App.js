import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// 页面组件
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import ArticleDetail from './pages/ArticleDetail';
import ArticleEditor from './pages/ArticleEditor';
import NotFound from './pages/NotFound';

// 组件
import Header from './components/Header';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';

// 服务
import { getCurrentUser, isAuthenticated } from './services/auth';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (isAuthenticated()) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('获取用户信息失败:', error);
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, []);

  if (loading) {
    return <div className="text-center my-5">加载中...</div>;
  }

  return (
    <Router>
      <Header user={user} setUser={setUser} />
      <Container className="py-4 min-vh-100">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/articles/:id" element={<ArticleDetail user={user} />} />
          <Route 
            path="/login" 
            element={user ? <Navigate to="/" /> : <Login setUser={setUser} />} 
          />
          <Route 
            path="/register" 
            element={user ? <Navigate to="/" /> : <Register setUser={setUser} />} 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute user={user}>
                <Profile user={user} setUser={setUser} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/editor" 
            element={
              <ProtectedRoute user={user}>
                <ArticleEditor user={user} />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/editor/:id" 
            element={
              <ProtectedRoute user={user}>
                <ArticleEditor user={user} />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Container>
      <Footer />
    </Router>
  );
}

export default App; 