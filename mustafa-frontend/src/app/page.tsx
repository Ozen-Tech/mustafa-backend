"use client";

import { useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function RootPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Enquanto o AuthContext está checando o token, não faça nada
    if (isLoading) {
      return;
    }

    // Após carregar, decida para onde ir:
    if (isAuthenticated) {
      router.replace('/dashboard'); // Se logado, vai para o dashboard
    } else {
      router.replace('(auth)/login'); // Se não, vai para o login
    }


    
  }, [isAuthenticated, isLoading, router]);

  // Exibe um spinner/mensagem enquanto a lógica de redirecionamento acontece
  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Carregando aplicação...</p> 
    </div>
  );
}
