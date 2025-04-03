import api from './api';

// 文章相关API
export const getArticles = async (params) => {
  try {
    const response = await api.get('blog/articles/', { params });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const getArticle = async (id) => {
  try {
    const response = await api.get(`blog/articles/${id}/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createArticle = async (articleData) => {
  try {
    const response = await api.post('blog/articles/', articleData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const updateArticle = async (id, articleData) => {
  try {
    const response = await api.put(`blog/articles/${id}/`, articleData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const deleteArticle = async (id) => {
  try {
    await api.delete(`blog/articles/${id}/`);
    return true;
  } catch (error) {
    throw error;
  }
};

export const likeArticle = async (id) => {
  try {
    const response = await api.post(`blog/articles/${id}/like/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const favoriteArticle = async (id) => {
  try {
    const response = await api.post(`blog/articles/${id}/favorite/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 分类相关API
export const getCategories = async () => {
  try {
    const response = await api.get('blog/categories/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 标签相关API
export const getTags = async () => {
  try {
    const response = await api.get('blog/tags/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// 评论相关API
export const getComments = async (articleId) => {
  try {
    const response = await api.get('blog/comments/', {
      params: { article: articleId }
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const createComment = async (articleId, content, parentId = null) => {
  try {
    const response = await api.post('blog/comments/', {
      article_id: articleId,
      content,
      parent_id: parentId
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

export const likeComment = async (id) => {
  try {
    const response = await api.post(`blog/comments/${id}/like/`);
    return response.data;
  } catch (error) {
    throw error;
  }
}; 