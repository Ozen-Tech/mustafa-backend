"use client"; 

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Cookies from 'js-cookie'; // js-cookie só é usado no lado do cliente aqui, o que está correto

// Interfaces
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
  isAuthenticated: boolean;
  login: (data: LoginParams) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Função para verificar o token e buscar dados do usuário.
  const checkAuth = useCallback(async () => {
    const token = Cookies.get('accessToken');
    if (token) {
      api.defaults.headers.Authorization = `Bearer ${token}`;
      try {
        const response = await api.get('/users/me');
        setUser(response.data);
      } catch {
        Cookies.remove('accessToken');
        setUser(null);
      }
    }
    setIsLoading(false);
  }, []);
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (formData: LoginParams) => {
    const params = new URLSearchParams();
    params.append('username', formData.email);
    params.append('password', formData.password);
    
    const response = await api.post('/users/token', params);
    const { access_token } = response.data;
    
    Cookies.set('accessToken', access_token, { expires: 7, secure: true });
    
    // Após o login, atualiza os dados do usuário. O redirecionamento
    // será feito pela página de login.
    await checkAuth();
  };

  const logout = () => {
    Cookies.remove('accessToken');
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

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  return context;
};
