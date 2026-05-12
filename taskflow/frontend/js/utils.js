// Small reusable helpers

function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.innerHTML = `<span>${type === 'success' ? '✓' : '✕'}</span> ${msg}`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function initials(name) {
  if (!name) return '?';
  return name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function isOverdue(dateStr) {
  if (!dateStr) return false;
  return new Date(dateStr) < new Date();
}

function getCurrentUser() {
  const raw = localStorage.getItem('current_user');
  return raw ? JSON.parse(raw) : null;
}

function saveCurrentUser(user) {
  localStorage.setItem('current_user', JSON.stringify(user));
}

function requireAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  const token = localStorage.getItem('access_token');
  if (token) {
    window.location.href = '/index.html';
  }
}

function handleApiError(err) {
  if (typeof err === 'object') {
    const msgs = Object.values(err).flat();
    return msgs.join(', ');
  }
  return 'Something went wrong';
}

function el(tag, cls, html = '') {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (html) node.innerHTML = html;
  return node;
}

function priorityTag(level) {
  return `<span class="tag tag-${level}">${level}</span>`;
}