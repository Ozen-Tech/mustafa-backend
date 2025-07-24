"use client"; 

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Cookies from 'js-cookie';

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

  useEffect(() => {
    const token = Cookies.get('accessToken'); // <<<<<< LER DOS COOKIES
    if (token) {
      api.defaults.headers.Authorization = `Bearer ${token}`;
      api.get('/users/me')
        .then(response => { setUser(response.data); })
        .catch(() => {
          Cookies.remove('accessToken'); // Limpar cookie inválido
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (formData: LoginParams) => {
    const params = new URLSearchParams();
    params.append('username', formData.email);
    params.append('password', formData.password);
    
    const response = await api.post('/users/token', params);
    const { access_token } = response.data;
    
    Cookies.set('accessToken', access_token, { expires: 7, secure: true }); // <<<< SALVAR NO COOKIE
    api.defaults.headers.Authorization = `Bearer ${access_token}`;
    
    const userResponse = await api.get('/users/me');
    setUser(userResponse.data);
  };

  const logout = () => {
    Cookies.remove('accessToken'); // <<<< REMOVER DO COOKIE
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    router.push('/login'); 
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
