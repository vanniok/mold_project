import axios from 'axios';

const api = axios.create({
  baseURL: '/api',   // 改为相对路径，后续 Nginx 将 /api 代理到后端
  timeout: 10000,
});

export default api;