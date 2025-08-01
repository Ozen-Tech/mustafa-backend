"use client";

import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import Image from 'next/image';
import { ImageModal } from '@/components/ImageModal';
import { useAuth } from '@/contexts/AuthContext';

// Interfaces para os dados
interface FotoPromotor {
  id: number;
  url_foto: string;
  legenda: string | null;
  data_envio: string;
  nome_promotor: string; // Adicionado pelo backend
}
interface Promotor {
  id: number;
  nome: string;
}

export default function FotosPage() {
  const { user } = useAuth();
  const [fotos, setFotos] = useState<FotoPromotor[]>([]);
  const [promotores, setPromotores] = useState<Promotor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedPromotor, setSelectedPromotor] = useState('');
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [buscaLegenda, setBuscaLegenda] = useState('');

  const [modalIndex, setModalIndex] = useState<number | null>(null);

  const handleOpenModal = (index: number) => setModalIndex(index);
  const handleCloseModal = () => setModalIndex(null);
  const handleNext = () => setModalIndex((prev) => (prev! + 1) % fotos.length);
  const handlePrev = () => setModalIndex((prev) => (prev! - 1 + fotos.length) % fotos.length);

  const fetchFotos = useCallback(() => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (selectedPromotor) params.append('promotor_id', selectedPromotor);
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (buscaLegenda) params.append('busca', buscaLegenda);
    
    api.get<FotoPromotor[]>('/fotos', { params })
      .then(response => setFotos(response.data))
      .catch(() => setError("Não foi possível carregar as fotos."))
      .finally(() => setLoading(false));
  }, [selectedPromotor, dataInicio, dataFim, buscaLegenda]);

  useEffect(() => {
    api.get('/users').then(response => setPromotores(response.data)).catch(() => {});
    fetchFotos();
  }, [fetchFotos]);
  
  const handleDeleteFoto = async (fotoId: number) => {
    if (confirm("Tem certeza que deseja excluir esta foto? A ação não pode ser desfeita.")) {
      try {
        await api.delete(`/fotos/${fotoId}`);
        setFotos(prevFotos => prevFotos.filter(f => f.id !== fotoId));
        if (modalIndex !== null) handleCloseModal();
      } catch (err) {
        alert("Erro ao excluir a foto. Verifique suas permissões.");
      }
    }
  };
  
  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFotos();
  };
  
  return (
    <>
      <div>
        <h1 className="text-3xl font-bold mb-6 text-gray-800">Galeria de Fotos</h1>
        <form onSubmit={handleFilterSubmit} className="bg-white p-4 rounded-lg shadow-md mb-6 flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-[150px]"><label className="block text-sm font-medium text-gray-700">Promotor</label><select value={selectedPromotor} onChange={e => setSelectedPromotor(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800"><option value="">Todos</option>{promotores.map(p => <option key={p.id} value={p.id}>{p.nome}</option>)}</select></div>
            <div className="flex-1 min-w-[150px]"><label className="block text-sm font-medium text-gray-700">Data Início</label><input type="date" value={dataInicio} onChange={e => setDataInicio(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" /></div>
            <div className="flex-1 min-w-[150px]"><label className="block text-sm font-medium text-gray-700">Data Fim</label><input type="date" value={dataFim} onChange={e => setDataFim(e.target.value)} className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" /></div>
            <div className="flex-2 min-w-[200px]"><label className="block text-sm font-medium text-gray-700">Buscar na Legenda</label><input type="text" value={buscaLegenda} onChange={e => setBuscaLegenda(e.target.value)} placeholder="Nome da loja..." className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" /></div>
            <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">Filtrar</button>
        </form>

        {loading && <p className="text-center p-10">Carregando...</p>}
        {!loading && !error && fotos.length === 0 && <p className="text-center bg-white p-6 rounded shadow">Nenhuma foto encontrada.</p>}
        {error && <p className="text-red-500 text-center">{error}</p>}
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {fotos.map((foto, index) => (
            <div key={foto.id} className="group bg-white rounded-lg shadow-md overflow-hidden relative">
              <div onClick={() => handleOpenModal(index)} className="cursor-pointer">
                <div className="relative w-full h-48">
                  <Image src={`${process.env.NEXT_PUBLIC_API_URL}${foto.url_foto}`} alt={foto.legenda || 'Foto'} fill className="object-cover transition-transform duration-300 group-hover:scale-110"/>
                </div>
                <div className="p-4">
                  <p className="font-bold text-gray-800 truncate">{foto.nome_promotor}</p>
                  <p className="text-sm text-gray-600 truncate">{foto.legenda || 'Sem legenda'}</p>
                  <p className="text-xs text-gray-400 mt-2">{new Date(foto.data_envio).toLocaleDateString('pt-BR')}</p>
                </div>
              </div>
              {user?.perfil === 'ADMIN' && (
                <button onClick={() => handleDeleteFoto(foto.id)} className="absolute top-2 right-2 bg-red-600 text-white rounded-full h-8 w-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity" aria-label="Excluir foto">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {modalIndex !== null && (
        <ImageModal 
          isOpen={true}
          onClose={handleCloseModal}
          imageUrl={`${process.env.NEXT_PUBLIC_API_URL}${fotos[modalIndex].url_foto}`}
          altText={fotos[modalIndex].legenda || 'Foto'}
          onNext={handleNext}
          onPrev={handlePrev}
          promotorNome={fotos[modalIndex].nome_promotor}
          dataEnvio={fotos[modalIndex].data_envio}
        />
      )}
    </>
  );
}
