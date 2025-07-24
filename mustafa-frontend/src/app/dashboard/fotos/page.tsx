"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';

// Interfaces para os dados
interface FotoPromotor {
  id: number;
  url_foto: string;
  legenda: string | null;
  data_envio: string;
}
interface Promotor {
  id: number;
  nome: string;
}

export default function FotosPage() {
  const [fotos, setFotos] = useState<FotoPromotor[]>([]);
  const [promotores, setPromotores] = useState<Promotor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados para os filtros
  const [selectedPromotor, setSelectedPromotor] = useState('');
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [buscaLegenda, setBuscaLegenda] = useState('');

  // Busca inicial dos dados
  useEffect(() => {
    // Busca promotores para popular o dropdown de filtro
    api.get('/users')
      .then(response => {
        setPromotores(response.data);
      })
      .catch(() => {
        setError("Não foi possível carregar a lista de promotores.");
      });
    
    // Busca as fotos iniciais (sem filtro)
    fetchFotos();
  }, []);

  const fetchFotos = () => {
    setLoading(true);

    const params = new URLSearchParams();
    if (selectedPromotor) params.append('promotor_id', selectedPromotor);
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (buscaLegenda) params.append('busca', buscaLegenda);

    api.get('/fotos', { params })
      .then(response => setFotos(response.data))
      .catch(err => {
        console.error("Falha ao buscar fotos:", err);
        setError("Não foi possível carregar as fotos.");
      })
      .finally(() => setLoading(false));
  };
  
  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFotos();
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Galeria de Fotos</h1>

      {/* Seção de Filtros */}
      <form onSubmit={handleFilterSubmit} className="bg-white p-4 rounded-lg shadow-md mb-6 flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[150px]">
          <label className="block text-sm font-medium text-gray-700">Promotor</label>
          <select value={selectedPromotor} onChange={e => setSelectedPromotor(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800">
            <option value="">Todos</option>
            {promotores.map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}
          </select>
        </div>
        <div className="flex-1 min-w-[150px]">
          <label className="block text-sm font-medium text-gray-700">Data Início</label>
          <input type="date" value={dataInicio} onChange={e => setDataInicio(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" />
        </div>
        <div className="flex-1 min-w-[150px]">
          <label className="block text-sm font-medium text-gray-700">Data Fim</label>
          <input type="date" value={dataFim} onChange={e => setDataFim(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" />
        </div>
        <div className="flex-2 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700">Buscar na Legenda</label>
          <input type="text" value={buscaLegenda} onChange={e => setBuscaLegenda(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" />
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
          Filtrar
        </button>
      </form>
      
      {loading && <div className="text-center p-10">Carregando fotos...</div>}
      {error && !loading && <div className="text-red-500 text-center p-10">{error}</div>}

      {!loading && !error && (
        fotos.length === 0 ? (
          <div className="bg-white p-6 rounded-lg shadow-md text-center">
            <p className="text-gray-600">Nenhuma foto encontrada para os filtros selecionados.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {fotos.map(foto => (
              <div key={foto.id} className="bg-white rounded-lg shadow-md overflow-hidden transform hover:scale-105 transition-transform duration-300">
                <a href={`${process.env.NEXT_PUBLIC_API_URL}${foto.url_foto}`} target="_blank" rel="noopener noreferrer">
                  <img src={`${process.env.NEXT_PUBLIC_API_URL}${foto.url_foto}`} alt={foto.legenda || 'Foto de promotor'} className="w-full h-48 object-cover" />
                </a>
                <div className="p-4">
                  <p className="text-sm text-gray-800 truncate" title={foto.legenda || 'Sem legenda'}>
                    {foto.legenda || 'Sem legenda'}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">{new Date(foto.data_envio).toLocaleString('pt-BR')}</p>
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
}
