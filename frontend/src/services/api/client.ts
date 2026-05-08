// Feature: API Client Configuration
// Traceability: All Features

// Feature: API Client Configuration
// Traceability: All Features

import axios from 'axios';

const TOKEN_KEY = 'clutchup_token';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
