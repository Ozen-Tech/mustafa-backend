// src/contexts/AuthContext.tsx

"use client"; 

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import Cookies from 'js-cookie';

interface User {
  nome: string;
  email: string;
  perfil: 'ADMIN' | 'GESTOR' | 'OPERADOR';
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

  const checkAuth = useCallback(async () => {
    const token = Cookies.get('accessToken');
    if (token) {
      // Configura o header padrão para todas as futuras requisições do api
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      try {
        const response = await api.get('/users/me');
        setUser(response.data);
      } catch {
        // Se o token for inválido, limpa tudo
        Cookies.remove('accessToken');
        setUser(null);
        // <<<< CORREÇÃO APLICADA AQUI TAMBÉM (Boa Prática) >>>>
        delete api.defaults.headers.common['Authorization'];
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
    
    // Configura o cookie e o header padrão imediatamente
    Cookies.set('accessToken', access_token, { expires: 7, secure: true, sameSite: 'strict' });
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    // Atualiza os dados do usuário no contexto
    await checkAuth();
  };

  const logout = () => {
    Cookies.remove('accessToken');
    // <<<< CORREÇÃO PRINCIPAL AQUI >>>>
    // Em vez de 'api.defaults.headers.Authorization = undefined;', usamos 'delete'
    // para remover completamente a propriedade do objeto de headers.
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