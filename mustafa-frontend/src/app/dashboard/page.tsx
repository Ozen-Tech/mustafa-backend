
"use client";

import { useAuth } from "@/contexts/AuthContext"; 
import Link from 'next/link';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

// Tipagem para os dados que virão da API
interface KpiData {
  fotos_hoje: number;
  promotores_ativos_hoje: number;
  fotos_mes: number;
  ranking_promotores: { nome: string; total: number }[];
}

// Componente para o Card de KPI
const KpiCard = ({ title, value, loading }: { title: string; value: number | string; loading: boolean }) => (
  <div className="bg-white p-6 rounded-lg shadow-md text-center">
    <h3 className="text-gray-500 text-lg">{title}</h3>
    {loading ? (
      <div className="h-9 w-16 bg-gray-200 animate-pulse mx-auto mt-2 rounded-md"></div>
    ) : (
      <p className="text-4xl font-bold text-gray-900 mt-2">{value}</p>
    )}
  </div>
);

export default function DashboardHomePage() {
  const { user } = useAuth();
  const [kpis, setKpis] = useState<KpiData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/insights/kpis')
      .then(response => setKpis(response.data))
      .catch(error => console.error("Falha ao buscar KPIs:", error))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Painel de Controle</h1>
      
      {/* Seção de KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <KpiCard title="Fotos Recebidas Hoje" value={kpis?.fotos_hoje ?? 0} loading={loading} />
        <KpiCard title="Promotores Ativos Hoje" value={kpis?.promotores_ativos_hoje ?? 0} loading={loading} />
        <KpiCard title="Total de Fotos no Mês" value={kpis?.fotos_mes ?? 0} loading={loading} />
      </div>

      {/* Seção de Ações Rápidas e Ranking */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-4 text-gray-700">Ações Rápidas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Link href="/dashboard/fotos" className="bg-green-500 text-white p-6 rounded-lg shadow-md hover:bg-green-600 transition-colors flex flex-col justify-center">
                <h3 className="text-xl font-bold">Ver Galeria de Fotos</h3>
                <p>Filtre e visualize todas as imagens enviadas.</p>
              </Link>
              <Link href="/dashboard/contratos" className="bg-blue-500 text-white p-6 rounded-lg shadow-md hover:bg-blue-600 transition-colors flex flex-col justify-center">
                <h3 className="text-xl font-bold">Gerenciar Contratos</h3>
                <p>Visualize e adicione novos contratos.</p>
              </Link>
              <Link href="/dashboard/promotores" className="bg-indigo-500 text-white p-6 rounded-lg shadow-md hover:bg-indigo-600 transition-colors flex flex-col justify-center">
                <h3 className="text-xl font-bold">Gerenciar Promotores</h3>
                <p>Edite informações e contatos da equipe.</p>
              </Link>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-gray-700">Ranking de Promotores</h2>
            {loading ? <p>Carregando ranking...</p> : (
              <ul className="space-y-4">
                {kpis?.ranking_promotores.map((promotor, index) => (
                  <li key={index} className="flex justify-between items-center">
                    <span className="text-gray-800">{index + 1}. {promotor.nome}</span>
                    <span className="font-bold text-gray-900 bg-gray-200 px-3 py-1 rounded-full">{promotor.total} fotos</span>
                  </li>
                ))}
              </ul>
            )}
        </div>
      </div>
    </div>
  );
}
