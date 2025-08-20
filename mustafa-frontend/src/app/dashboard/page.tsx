
"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { 
  Camera, 
  Users, 
  FileText, 
  TrendingUp, 
  Award, 
  Calendar,
  ArrowUpRight,
  Star,
  Activity
} from 'lucide-react';
import { motion } from 'framer-motion';

interface KpiData {
  fotos_hoje: number;
  promotores_ativos_hoje: number;
  fotos_mes: number;
  ranking_promotores: { nome: string; total: number }[];
}

export default function DashboardHomePage() {
  const [kpis, setKpis] = useState<KpiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/insights/kpis')
      .then(response => setKpis(response.data))
      .catch(error => console.error("Falha ao buscar KPIs:", error))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="loading-shimmer w-12 h-12 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando dados...</p>
        </div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: 'Fotos Recebidas Hoje',
      value: kpis?.fotos_hoje || 0,
      icon: Camera,
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50',
      change: '+12%'
    },
    {
      title: 'Promotores Ativos Hoje',
      value: kpis?.promotores_ativos_hoje || 0,
      icon: Users,
      gradient: 'from-emerald-500 to-green-500',
      bgGradient: 'from-emerald-50 to-green-50',
      change: '+8%'
    },
    {
      title: 'Total de Fotos no Mês',
      value: kpis?.fotos_mes || 0,
      icon: TrendingUp,
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50',
      change: '+24%'
    }
  ];

  const quickActions = [
    {
      title: 'Ver Galeria de Fotos',
      description: 'Filtre e visualize todas as imagens enviadas',
      href: '/dashboard/fotos',
      icon: Camera,
      gradient: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Gerenciar Contratos',
      description: 'Visualize e adicione novos contratos',
      href: '/dashboard/contratos',
      icon: FileText,
      gradient: 'from-emerald-500 to-green-500'
    },
    {
      title: 'Gerenciar Promotores',
      description: 'Edite informações e contatos da equipe',
      href: '/dashboard/promotores',
      icon: Users,
      gradient: 'from-purple-500 to-pink-500'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            Painel de Controle
          </h1>
          <p className="text-gray-600 mt-1">Acompanhe o desempenho em tempo real</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Calendar size={16} />
          <span>{new Date().toLocaleDateString('pt-BR', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}</span>
        </div>
      </div>
      
      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative overflow-hidden bg-gradient-to-br ${card.bgGradient} p-6 rounded-2xl border border-white/20 shadow-lg hover:shadow-xl transition-all duration-300`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-gray-600 font-medium text-sm mb-2">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{card.value}</p>
                  <div className="flex items-center space-x-1 text-green-600 text-sm font-medium">
                    <ArrowUpRight size={14} />
                    <span>{card.change}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-r ${card.gradient} shadow-lg`}>
                  <Icon size={24} className="text-white" />
                </div>
              </div>
              <div className={`absolute -bottom-2 -right-2 w-20 h-20 bg-gradient-to-r ${card.gradient} opacity-10 rounded-full`}></div>
            </motion.div>
          );
        })}
      </div>

      {/* Ações Rápidas */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg"
      >
        <div className="flex items-center space-x-2 mb-6">
          <Activity className="text-blue-600" size={24} />
          <h2 className="text-xl font-bold text-gray-900">Ações Rápidas</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link key={action.title} href={action.href}>
                <motion.div
                  whileHover={{ y: -4, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="group relative p-6 bg-gradient-to-br from-white to-gray-50 rounded-xl border border-gray-200/50 hover:border-gray-300/50 transition-all duration-300 hover:shadow-lg"
                >
                  <div className="flex items-start space-x-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${action.gradient} shadow-lg group-hover:shadow-xl transition-shadow duration-300`}>
                      <Icon size={20} className="text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 group-hover:text-gray-700 transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-gray-600 text-sm mt-1">{action.description}</p>
                    </div>
                    <ArrowUpRight size={16} className="text-gray-400 group-hover:text-gray-600 transition-colors" />
                  </div>
                </motion.div>
              </Link>
            );
          })}
        </div>
      </motion.div>

      {/* Ranking de Promotores */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg"
      >
        <div className="flex items-center space-x-2 mb-6">
          <Award className="text-yellow-600" size={24} />
          <h2 className="text-xl font-bold text-gray-900">Ranking de Promotores</h2>
        </div>
        <div className="space-y-3">
          {kpis?.ranking_promotores.slice(0, 5).map((promotor, index) => {
            const isTop3 = index < 3;
            const rankColors = ['bg-yellow-500', 'bg-gray-400', 'bg-amber-600'];
            
            return (
              <motion.div 
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                className={`flex items-center justify-between p-4 rounded-xl transition-all duration-300 ${
                  isTop3 
                    ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200/50' 
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-lg ${
                    isTop3 ? rankColors[index] : 'bg-gray-500'
                  }`}>
                    {isTop3 ? <Star size={16} /> : index + 1}
                  </div>
                  <div>
                    <p className="font-bold text-gray-900">{promotor.nome}</p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xl font-bold text-blue-600">{promotor.total}</span>
                  <p className="text-xs text-gray-500">fotos</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
