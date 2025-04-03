import api from './api';

export const login = async (username, password) => {
  try {
    const response = await api.post('auth/token/', {
      username,
      password
    });
    
    const { access, refresh } = response.data;
    
    // 保存token到本地存储
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    // 获取用户信息
    const userResponse = await api.get('auth/users/me/');
    return userResponse.data;
  } catch (error) {
    throw error;
  }
};

export const register = async (username, email, password, passwordConfirm) => {
  try {
    const response = await api.post('auth/users/register/', {
      username,
      email,
      password,
      password_confirm: passwordConfirm
    });
    
    const { access, refresh, user } = response.data;
    
    // 保存token到本地存储
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    
    return user;
  } catch (error) {
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('auth/users/me/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateProfile = async (userData) => {
  try {
    const response = await api.patch('auth/users/me/', userData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const isAuthenticated = () => {
  return localStorage.getItem('access_token') !== null;
}; 