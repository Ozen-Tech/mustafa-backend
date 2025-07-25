"use client";

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading, logout } = useAuth();
  
  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-100 text-gray-800">Carregando...</div>;
  }
  
  if (!user && !isLoading) {
    // Embora o middleware redirecione, é uma boa prática ter um fallback.
    // Retornamos nulo para não exibir o layout em páginas de login/públicas
    return null; 
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white p-5 shadow-lg flex flex-col">
        <h2 className="text-xl font-bold text-gray-800">Mustafa App</h2>
        <nav className="mt-10 flex-1 space-y-2">
          <Link href="/dashboard" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Dashboard</Link>
          <Link href="/dashboard/fotos" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Galeria de Fotos</Link>
          {/* << ATUALIZADO >> Link para a nova página de gerenciamento de usuários */}
          <Link href="/dashboard/promotores" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-gray-200 text-gray-700">Usuários</Link>
        </nav>
        <div className="pt-4 mt-4 border-t border-gray-200">
           {user && (
            <div className="text-center text-gray-600">
              <p className="font-semibold">{user.nome}</p>
              <p className="text-sm">{user.email}</p>
            </div>
          )}
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white shadow-md flex items-center justify-between px-6">
          <div className="text-gray-800">
            {/* O middleware cuida do redirecionamento, então o user deve existir aqui */}
            Bem-vindo, {user?.nome}! 
          </div>
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