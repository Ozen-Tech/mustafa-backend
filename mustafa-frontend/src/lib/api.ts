import axios from 'axios';

// **NÃO definimos a baseURL na criação**
const api = axios.create(); 

// Usamos um INTERCEPTOR. Esta função é executada ANTES de CADA requisição.
// Isso garante que os valores corretos sejam usados sempre.
api.interceptors.request.use(
  (config) => {
    // 1. Defina a baseURL aqui, garantindo que ela seja lida em tempo real
    //    Isso resolve o problema de cache/build do Next.js
    if (process.env.NEXT_PUBLIC_API_URL) {
      config.baseURL = process.env.NEXT_PUBLIC_API_URL;
    } else {
      // Se a variável de ambiente não estiver disponível, registre um erro claro.
      console.error("ERRO CRÍTICO: a variável NEXT_PUBLIC_API_URL não está definida!");
    }

    // 2. Anexe o token do localStorage
    //    Isso garante que a requisição sempre use o token mais recente, 
    //    mesmo que o usuário tenha logado em outra aba.
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // [DEBUG] Imprime a URL final de CADA requisição que sai.
    // Use isso para confirmar que as chamadas estão corretas.
    console.log(`[API Interceptor] Fazendo requisição ${config.method?.toUpperCase()} para: ${config.baseURL}${config.url}`);

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
