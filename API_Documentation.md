# Blog System API Documentation

## API Overview

This blog system provides a set of RESTful APIs that allow developers to programmatically access blog content and user information. All APIs return data in JSON format.

## Basic Information

- **Base URL**: `http://yourdomain.com/api/`
- **Authentication Method**: JWT (JSON Web Token)
- **Content Type**: `application/json`

## Authentication

Most APIs require authentication to access. Authentication uses JWT tokens, obtained as follows:

### Get Authentication Token

**Request**:
```
POST /api/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

In subsequent requests, place the access token in the request header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Refresh Token

**Request**:
```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Posts API

### Get Post List

**Request**:
```
GET /api/posts/
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number |
| category | string | No | Filter by category |
| tag | string | No | Filter by tag |
| search | string | No | Search keyword |

**Response**:
```json
{
  "count": 100,
  "next": "http://yourdomain.com/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Article Title",
      "slug": "article-slug",
      "excerpt": "Article excerpt...",
      "content": "Article content...",
      "author": {
        "id": 1,
        "username": "author_username"
      },
      "categories": [
        {
          "id": 1,
          "name": "Category Name",
          "slug": "category-slug"
        }
      ],
      "tags": [
        {
          "id": 1,
          "name": "Tag Name",
          "slug": "tag-slug"
        }
      ],
      "created_at": "2025-04-01T12:00:00Z",
      "updated_at": "2025-04-02T15:30:00Z",
      "featured_image": "http://yourdomain.com/media/post_covers/image.jpg",
      "status": "published"
    },
    // More posts...
  ]
}
```

### Get Single Post

**Request**:
```
GET /api/posts/{id}/
```
or
```
GET /api/posts/by-slug/{slug}/
```

**Response**:
```json
{
  "id": 1,
  "title": "Article Title",
  "slug": "article-slug",
  "excerpt": "Article excerpt...",
  "content": "Article content...",
  "author": {
    "id": 1,
    "username": "author_username",
    "avatar": "http://yourdomain.com/media/avatars/user.jpg"
  },
  "categories": [
    {
      "id": 1,
      "name": "Category Name",
      "slug": "category-slug"
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "Tag Name",
      "slug": "tag-slug"
    }
  ],
  "created_at": "2025-04-01T12:00:00Z",
  "updated_at": "2025-04-02T15:30:00Z",
  "featured_image": "http://yourdomain.com/media/post_covers/image.jpg",
  "status": "published",
  "comments_count": 5,
  "views_count": 120
}
```

### Create Post

**Request**:
```
POST /api/posts/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "title": "New Article Title",
  "content": "Article content...",
  "categories": [1, 2], // List of category IDs
  "tags": [1, 3], // List of tag IDs
  "status": "draft", // or "published"
  "featured_image": "uploaded_image.jpg" // Optional
}
```

**Response**:
```json
{
  "id": 5,
  "title": "New Article Title",
  "slug": "new-article-title",
  "excerpt": "Article content...",
  "content": "Article content...",
  "author": {
    "id": 1,
    "username": "your_username"
  },
  "categories": [
    {
      "id": 1,
      "name": "Category 1",
      "slug": "category-1"
    },
    {
      "id": 2,
      "name": "Category 2",
      "slug": "category-2"
    }
  ],
  "tags": [
    {
      "id": 1,
      "name": "Tag 1",
      "slug": "tag-1"
    },
    {
      "id": 3,
      "name": "Tag 3",
      "slug": "tag-3"
    }
  ],
  "created_at": "2025-04-06T10:15:00Z",
  "updated_at": "2025-04-06T10:15:00Z",
  "featured_image": "http://yourdomain.com/media/post_covers/uploaded_image.jpg",
  "status": "draft"
}
```

### Update Post

**Request**:
```
PUT /api/posts/{id}/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content...",
  "categories": [2], // List of category IDs
  "tags": [3, 4], // List of tag IDs
  "status": "published"
}
```

**Response**:
Similar to the create post response, but contains the updated data.

### Delete Post

**Request**:
```
DELETE /api/posts/{id}/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response**:
```
HTTP 204 No Content
```

## Comments API

### Get Post Comments

**Request**:
```
GET /api/posts/{post_id}/comments/
```

**Response**:
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "Comment content...",
      "author": {
        "id": 2,
        "username": "commenter",
        "avatar": "http://yourdomain.com/media/avatars/commenter.jpg"
      },
      "created_at": "2025-04-03T09:45:00Z",
      "parent": null, // If replying to another comment, this will show the parent comment ID
      "post": 1
    },
    // More comments...
  ]
}
```

### Add Comment

**Request**:
```
POST /api/posts/{post_id}/comments/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "content": "This is a new comment",
  "parent": null // Optional, set when replying to another comment
}
```

**Response**:
```json
{
  "id": 15,
  "content": "This is a new comment",
  "author": {
    "id": 1,
    "username": "your_username",
    "avatar": "http://yourdomain.com/media/avatars/user.jpg"
  },
  "created_at": "2025-04-06T11:20:00Z",
  "parent": null,
  "post": 1
}
```

## Users API

### Get Current User Information

**Request**:
```
GET /api/users/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response**:
```json
{
  "id": 1,
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "First",
  "last_name": "Last",
  "bio": "User bio...",
  "avatar": "http://yourdomain.com/media/avatars/user.jpg",
  "website": "https://yourwebsite.com",
  "date_joined": "2025-01-01T00:00:00Z",
  "is_staff": false
}
```

### Update User Profile

**Request**:
```
PATCH /api/users/me/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "bio": "Updated bio..."
}
```

**Response**:
```json
{
  "id": 1,
  "username": "your_username",
  "email": "your_email@example.com",
  "first_name": "Updated",
  "last_name": "Name",
  "bio": "Updated bio...",
  "avatar": "http://yourdomain.com/media/avatars/user.jpg",
  "website": "https://yourwebsite.com",
  "date_joined": "2025-01-01T00:00:00Z",
  "is_staff": false
}
```

### Change Password

**Request**:
```
POST /api/users/change-password/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "old_password": "current_password",
  "new_password": "new_password"
}
```

**Response**:
```json
{
  "detail": "Password successfully changed"
}
```

## Categories and Tags API

### Get All Categories

**Request**:
```
GET /api/categories/
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "posts_count": 15
  },
  {
    "id": 2,
    "name": "Life",
    "slug": "life",
    "posts_count": 8
  },
  // More categories...
]
```

### Get All Tags

**Request**:
```
GET /api/tags/
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Python",
    "slug": "python",
    "posts_count": 10
  },
  {
    "id": 2,
    "name": "Django",
    "slug": "django",
    "posts_count": 7
  },
  // More tags...
]
```

## Error Handling

The API uses standard HTTP status codes to indicate the result of requests:

- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Request processed successfully, no content returned (e.g., deletion)
- **400 Bad Request** - Request parameters incorrect
- **401 Unauthorized** - Authentication not provided or invalid
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource does not exist
- **500 Internal Server Error** - Server error

Error response example:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

or

```json
{
  "title": ["This field may not be blank."],
  "content": ["This field may not be blank."]
}
```

## API Rate Limiting

To prevent abuse, the API implements rate limiting:

- Anonymous users: 100 requests per hour
- Authenticated users: 1000 requests per hour

When limit is exceeded, a 429 status code is returned:

```json
{
  "detail": "Request was throttled. Please try again later."
}
```

## Usage Examples

### Python Example

```python
import requests

# Get authentication token
auth_response = requests.post(
    'http://yourdomain.com/api/token/',
    json={'username': 'your_username', 'password': 'your_password'}
)
token = auth_response.json()['access']

# Get post list
headers = {'Authorization': f'Bearer {token}'}
posts_response = requests.get('http://yourdomain.com/api/posts/', headers=headers)
posts = posts_response.json()

# Create new post
new_post = {
    'title': 'Post Created via API',
    'content': 'This is post content created using the API...',
    'categories': [1],
    'tags': [2, 3],
    'status': 'published'
}
create_response = requests.post(
    'http://yourdomain.com/api/posts/',
    json=new_post,
    headers=headers
)
created_post = create_response.json()
print(f"Post created successfully, ID: {created_post['id']}")
```

### JavaScript Example

```javascript
// Get authentication token
async function getToken() {
  const response = await fetch('http://yourdomain.com/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: 'your_username',
      password: 'your_password',
    }),
  });
  const data = await response.json();
  return data.access;
}

// Get post list
async function getPosts() {
  const token = await getToken();
  const response = await fetch('http://yourdomain.com/api/posts/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  const posts = await response.json();
  console.log(posts);
}

// Create new post
async function createPost() {
  const token = await getToken();
  const response = await fetch('http://yourdomain.com/api/posts/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      title: 'Post Created via API',
      content: 'This is post content created using the API...',
      categories: [1],
      tags: [2, 3],
      status: 'published',
    }),
  });
  const newPost = await response.json();
  console.log(`Post created successfully, ID: ${newPost.id}`);
}
``` 