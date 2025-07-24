
import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
    // A baseURL é lida da variável de ambiente, como já está configurado.
    baseURL: process.env.NEXT_PUBLIC_API_URL, 
});

// Este interceptor só roda no navegador (CLIENT-SIDE), o que está correto.
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
