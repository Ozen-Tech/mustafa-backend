"use client";

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // CORREÇÃO CRÍTICA AQUI TAMBÉM: A rota de proteção deve apontar para o caminho completo
      router.push('/login'); 
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return <div className="flex items-center justify-center min-h-screen">Carregando...</div>;
  }
  
  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-64 bg-white p-5 shadow-lg flex flex-col">
        <h2 className="text-xl font-bold text-gray-800">Mustafa App</h2>
        <nav className="mt-10 flex-1">
          <Link href="/dashboard" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Dashboard</Link>
          <Link href="/dashboard/fotos" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Fotos</Link>
          <Link href="/dashboard/contratos" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Contratos</Link>
          {/* <<<<< NOVO LINK AQUI >>>>> */}
          <Link href="/dashboard/promotores" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Promotores</Link>
        </nav>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white shadow-md flex items-center justify-between px-6">
          <div className="text-gray-800">Bem-vindo, {user?.nome}!</div>
          <button onClick={logout} className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors">
              Sair
          </button>
        </header>
        <main className="flex-1 p-6 overflow-y-auto">
            {children}
        </main>
      </div>
    </div>
  );
};
export default DashboardLayout;
