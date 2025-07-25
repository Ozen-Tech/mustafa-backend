"use client";

import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import Image from 'next/image';
import { ImageModal } from '@/components/ImageModal';

// Interfaces para os tipos de dados
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

  // Modal para as fotos
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedImageUrl, setSelectedImageUrl] = useState('');

  // Funções para abrir e fechar o modal
  const handleOpenModal = (imageUrl: string) => {
    setSelectedImageUrl(imageUrl);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedImageUrl('');
  };
  

  // Envolvemos a lógica de busca em uma função `useCallback`
  // para estabilizá-la e usá-la como dependência do `useEffect` com segurança.
  const fetchFotos = useCallback(() => {
    setLoading(true);
    setError(null);

    const params = new URLSearchParams();
    if (selectedPromotor) params.append('promotor_id', selectedPromotor);
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (buscaLegenda) params.append('busca', buscaLegenda);

    api.get('/fotos', { params })
      .then(response => {
        setFotos(response.data);
      })
      .catch(err => {
        console.error("Falha ao buscar fotos:", err);
        setError("Não foi possível carregar as fotos.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [selectedPromotor, dataInicio, dataFim, buscaLegenda]); // A função só será recriada se um destes filtros mudar

  // useEffect para buscar os dados iniciais
  useEffect(() => {
    api.get('/users')
      .then(response => {
        setPromotores(response.data);
      })
      .catch(() => {
        setError("Não foi possível carregar a lista de promotores.");
      });
    
    fetchFotos();
  }, [fetchFotos]); // Este `useEffect` agora depende corretamente da função `fetchFotos`.

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFotos();
  };
  
  // O JSX para renderização continua o mesmo, com a troca de <img> para <Image>
    return (
      // <<< 3. ENVOLVER TUDO EM UM FRAGMENTO <>...</> E ADICIONAR O MODAL NO FINAL >>>
      <>
        <div>
          <h1 className="text-3xl font-bold mb-6 text-gray-800">Galeria de Fotos</h1>
  
          {/* Seção de Filtros (sem alterações) */}
          <form onSubmit={handleFilterSubmit} className="bg-white p-4 rounded-lg shadow-md mb-6 flex flex-wrap gap-4 items-end">
            {/* ...seus inputs de filtro aqui, sem alterações... */}
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
                <input type="text" value={buscaLegenda} onChange={e => setBuscaLegenda(e.target.value)} placeholder="Nome da loja..." className="mt-1 block w-full p-2 border border-gray-300 rounded-md text-gray-800" />
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
                {fotos.map(foto => {
                  const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}${foto.url_foto}`;
                  return (
                    // <<< 4. MODIFICAR O CARD DA IMAGEM >>>
                    <div 
                      key={foto.id} 
                      className="bg-white rounded-lg shadow-md overflow-hidden transform hover:scale-105 transition-transform duration-300 cursor-pointer"
                      onClick={() => handleOpenModal(imageUrl)} // Adicionar onClick aqui
                    >
                      {/* Remover o link <a> que abria em nova aba */}
                      <div className="relative w-full h-48">
                        <Image 
                          src={imageUrl} 
                          alt={foto.legenda || 'Foto de promotor'}
                          fill // fill ocupa o container pai
                          className="object-cover"
                          sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 33vw"
                        />
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-gray-800 truncate" title={foto.legenda || 'Sem legenda'}>
                          {foto.legenda || 'Sem legenda'}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">{new Date(foto.data_envio).toLocaleString('pt-BR')}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )
          )}
        </div>
  
        {/* <<< 5. RENDERIZAR O COMPONENTE MODAL AQUI >>> */}
        <ImageModal 
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          imageUrl={selectedImageUrl}
          altText="Visualização da foto do promotor"
        />
      </>
    );
  }
