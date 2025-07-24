"use client"; 

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

// Define o formato do seu usuário e do contexto
interface User {
  nome: string;
  email: string;
  perfil: string;
}

interface LoginParams {
  email: string;
  password: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean; // Adicionado para facilitar a checagem
  login: (data: LoginParams) => Promise<void>; 
  logout: () => void;
  isLoading: boolean;
}



const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Efeito que roda na inicialização para verificar se o usuário já tem um token válido
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      // Se o token existe, define o header padrão para futuras requisições
      api.defaults.headers.Authorization = `Bearer ${token}`;
      // E busca os dados do usuário para validar a sessão
      api.get('/users/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          // Se o token for inválido (ex: expirado), limpa tudo
          localStorage.removeItem('accessToken');
          setUser(null);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      // Se não há token, termina o carregamento
      setIsLoading(false);
    }
  }, []);


  const login = async (formData: LoginParams) => {
    // Seu backend espera 'application/x-www-form-urlencoded' para o token
    const params = new URLSearchParams();
    params.append('username', formData.email);
    params.append('password', formData.password);
    
    // 1. Pega o token
    const response = await api.post('/users/token', params);
    const { access_token } = response.data;
    
    // 2. Salva o token e configura o header padrão da API
    localStorage.setItem('accessToken', access_token);
    api.defaults.headers.Authorization = `Bearer ${access_token}`;
    
    // 3. Busca os dados do usuário para salvar no estado global
    const userResponse = await api.get('/users/me');
    setUser(userResponse.data);

    // IMPORTANTE: A responsabilidade de redirecionar foi movida para a página de login.
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    router.push('/auth/login'); // Após o logout, sempre vai para a tela de login
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook customizado para facilitar o uso do contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
