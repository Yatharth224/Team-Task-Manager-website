// Central API utility - Change BASE_URL when you deploy
const BASE_URL = 'http://127.0.0.1:8000/api';

function getToken() {
  return localStorage.getItem('access_token');
}

function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('current_user');
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;

  try {
    const resp = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (resp.ok) {
      const data = await resp.json();
      localStorage.setItem('access_token', data.access);
      return true;
    }
  } catch (e) {
    console.error('Token refresh failed:', e);
  }
  return false;
}

async function apiCall(endpoint, options = {}) {
  const token = getToken();

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  let resp = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });

  // Auto-refresh if 401
  if (resp.status === 401) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${getToken()}`;
      resp = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });
    } else {
      clearTokens();
      window.location.href = '/login.html';
      return;
    }
  }

  if (resp.status === 204) return null;

  const body = await resp.json();
  if (!resp.ok) throw body;
  return body;
}

// Auth APIs
const auth = {
  signup: (name, email, password) =>
    apiCall('/auth/signup/', { method: 'POST', body: JSON.stringify({ name, email, password }) }),

  login: (email, password) =>
    apiCall('/auth/login/', { method: 'POST', body: JSON.stringify({ email, password }) }),

  logout: () =>
    apiCall('/auth/logout/', { method: 'POST' }),

  me: () =>
    apiCall('/auth/me/'),

  activeSessions: () =>
    apiCall('/auth/sessions/'),
};

// Projects APIs
const projectsApi = {
  list: () => apiCall('/projects/'),
  create: (data) => apiCall('/projects/', { method: 'POST', body: JSON.stringify(data) }),
  get: (id) => apiCall(`/projects/${id}/`),
  update: (id, data) => apiCall(`/projects/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => apiCall(`/projects/${id}/`, { method: 'DELETE' }),
  addMember: (id, email, role) => apiCall(`/projects/${id}/members/`, { method: 'POST', body: JSON.stringify({ email, role }) }),
  removeMember: (id, userId) => apiCall(`/projects/${id}/members/`, { method: 'DELETE', body: JSON.stringify({ user_id: userId }) }),
};

// Tasks APIs
const tasksApi = {
  list: (projectId, params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiCall(`/tasks/${projectId}/tasks/${qs ? '?' + qs : ''}`);
  },
  create: (projectId, data) => apiCall(`/tasks/${projectId}/tasks/`, { method: 'POST', body: JSON.stringify(data) }),
  get: (projectId, taskId) => apiCall(`/tasks/${projectId}/tasks/${taskId}/`),
  update: (projectId, taskId, data) => apiCall(`/tasks/${projectId}/tasks/${taskId}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (projectId, taskId) => apiCall(`/tasks/${projectId}/tasks/${taskId}/`, { method: 'DELETE' }),
  dashboard: (projectId) => apiCall(`/tasks/${projectId}/dashboard/`),
};