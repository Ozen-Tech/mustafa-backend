"use client";

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Camera, 
  Users, 
  Brain, 
  FileText, 
  MessageCircle, 
  LogOut,
  User,
  ChevronRight
} from 'lucide-react';
import { motion } from 'framer-motion';

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading, logout } = useAuth();
  const pathname = usePathname();
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="loading-shimmer w-16 h-16 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando...</p>
        </div>
      </div>
    );
  }
  
  if (!user && !isLoading) return null;

  const navigationItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/dashboard/fotos', label: 'Galeria de Fotos', icon: Camera },
    { href: '/dashboard/promotores', label: 'Promotores', icon: Users },
    { href: '/dashboard/insights', label: 'Assistente IA', icon: Brain },
  ];

  const isActive = (href: string) => pathname === href;

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Sidebar */}
      <motion.aside 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        className="w-72 bg-white/80 backdrop-blur-xl border-r border-gray-200/50 flex flex-col shadow-xl"
      >
        {/* Logo */}
        <div className="p-6 border-b border-gray-200/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Mustafa App
              </h2>
              <p className="text-xs text-gray-500">Gestão Premium</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            
            return (
              <Link key={item.href} href={item.href}>
                <motion.div
                  whileHover={{ x: 4 }}
                  className={`group flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                    active 
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg' 
                      : 'text-gray-600 hover:bg-gray-100/80 hover:text-gray-900'
                  }`}
                >
                  <Icon size={20} className={active ? 'text-white' : 'text-gray-400 group-hover:text-gray-600'} />
                  <span className="font-medium">{item.label}</span>
                  {active && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="ml-auto"
                    >
                      <ChevronRight size={16} className="text-white" />
                    </motion.div>
                  )}
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* User Profile & Actions */}
        <div className="p-4 border-t border-gray-200/50 space-y-3">
          {/* Feedback Link */}
          <a 
            href="mailto:representadasmustafa@gmail.com?subject=Feedback sobre o Mustafa App"
            className="flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-600 hover:bg-gray-100/80 hover:text-gray-900 transition-all duration-200 group"
          >
            <MessageCircle size={20} className="text-gray-400 group-hover:text-gray-600" />
            <span className="font-medium text-sm">Enviar Feedback</span>
          </a>
          
          {/* User Info */}
          {user && (
            <div className="flex items-center space-x-3 px-4 py-3 rounded-xl bg-gray-50/80">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <User size={16} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 truncate">{user.nome}</p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
          )}
        </div>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <motion.header 
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="h-16 bg-white/80 backdrop-blur-xl border-b border-gray-200/50 flex items-center justify-between px-6 shadow-sm"
        >
          <div className="flex items-center space-x-4">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">Bem-vindo de volta!</h1>
              <p className="text-sm text-gray-500">{user?.nome}</p>
            </div>
          </div>
          
          <motion.button 
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={logout} 
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl hover:from-red-600 hover:to-red-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <LogOut size={16} />
            <span className="font-medium">Sair</span>
          </motion.button>
        </motion.header>
        
        {/* Main Content Area */}
        <main className="flex-1 p-6 overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;