"use client";

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import api from '@/lib/api';
import Image from 'next/image';
import { ImageModal } from '@/components/ImageModal';
import { useAuth } from '@/contexts/AuthContext';
import { 
  Camera, 
  Search, 
  Filter, 
  Calendar, 
  User, 
  Download,
  Eye,
  Grid3X3,
  List,
  SortAsc,
  SortDesc,
  Trash2,
  Package,
  ArrowLeft
} from 'lucide-react';
import { motion } from 'framer-motion';

// Interfaces para os dados
interface FotoPromotor {
  id: number;
  url_foto: string;
  legenda: string | null;
  data_envio: string;
  nome_promotor: string;
}

interface Promotor {
  id: number;
  nome: string;
}

type ViewMode = 'grid' | 'list';
type SortBy = 'date' | 'name';
type SortOrder = 'asc' | 'desc';

export default function FotosPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const [fotos, setFotos] = useState<FotoPromotor[]>([]);
  const [filteredFotos, setFilteredFotos] = useState<FotoPromotor[]>([]);
  const [promotores, setPromotores] = useState<Promotor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filtros originais
  const [selectedPromotor, setSelectedPromotor] = useState('');
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [buscaLegenda, setBuscaLegenda] = useState('');

  // Novos controles de UI
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState<SortBy>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterBy, setFilterBy] = useState<'all' | 'today' | 'week' | 'month'>('all');

  const [modalIndex, setModalIndex] = useState<number | null>(null);
  const [selectedPromotorName, setSelectedPromotorName] = useState<string>('');
  const [isDownloading, setIsDownloading] = useState(false);

  const handleOpenModal = (index: number) => setModalIndex(index);
  const handleCloseModal = () => setModalIndex(null);
  const handleNext = () => setModalIndex((prev) => (prev! + 1) % filteredFotos.length);
  const handlePrev = () => setModalIndex((prev) => (prev! - 1 + filteredFotos.length) % filteredFotos.length);

  const fetchFotos = useCallback(() => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (selectedPromotor) params.append('promotor_id', selectedPromotor);
    if (dataInicio) params.append('data_inicio', dataInicio);
    if (dataFim) params.append('data_fim', dataFim);
    if (buscaLegenda) params.append('busca', buscaLegenda);
    
    api.get<FotoPromotor[]>('/fotos', { params })
      .then(response => {
        setFotos(response.data);
        setFilteredFotos(response.data);
      })
      .catch((err) => {
        console.error("Falha ao buscar fotos:", err); 
        setError("Não foi possível carregar as fotos.");
      })
      .finally(() => setLoading(false));
  }, [selectedPromotor, dataInicio, dataFim, buscaLegenda]);

  useEffect(() => {
    api.get('/users').then(response => setPromotores(response.data)).catch(() => {});
    
    // Verificar se há parâmetros de URL para filtrar por promotor específico
    const promotorId = searchParams.get('promotor_id');
    const promotorName = searchParams.get('promotor_name');
    
    if (promotorId) {
      setSelectedPromotor(promotorId);
      if (promotorName) {
        setSelectedPromotorName(decodeURIComponent(promotorName));
      }
    }
    
    fetchFotos();
  }, [fetchFotos, searchParams]);

  // Aplicar filtros e ordenação locais
  useEffect(() => {
    let filtered = fotos.filter(foto => 
      foto.nome_promotor.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (foto.legenda && foto.legenda.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    // Aplicar filtro de data
    const now = new Date();
    if (filterBy === 'today') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      filtered = filtered.filter(foto => new Date(foto.data_envio) >= today);
    } else if (filterBy === 'week') {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(foto => new Date(foto.data_envio) >= weekAgo);
    } else if (filterBy === 'month') {
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(foto => new Date(foto.data_envio) >= monthAgo);
    }

    // Aplicar ordenação
    filtered.sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'date') {
        comparison = new Date(a.data_envio).getTime() - new Date(b.data_envio).getTime();
      } else if (sortBy === 'name') {
        comparison = a.nome_promotor.localeCompare(b.nome_promotor);
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    setFilteredFotos(filtered);
  }, [searchTerm, filterBy, sortBy, sortOrder, fotos]);
  
  const handleDeleteFoto = async (fotoId: number) => {
    if (confirm("Tem certeza que deseja excluir esta foto? A ação não pode ser desfeita.")) {
      try {
        await api.delete(`/fotos/${fotoId}`);
        setFotos(prevFotos => prevFotos.filter(f => f.id !== fotoId));
        if (modalIndex !== null) handleCloseModal();
      } catch {
        alert("Erro ao excluir a foto. Verifique suas permissões.");
      }
    }
  };
  
  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFotos();
  };

  const handleBulkDownload = async () => {
    if (filteredFotos.length === 0) return;
    
    setIsDownloading(true);
    try {
      // Pegar as 15 fotos mais recentes
      const fotosToDownload = filteredFotos
        .sort((a, b) => new Date(b.data_envio).getTime() - new Date(a.data_envio).getTime())
        .slice(0, 15);
      
      // Criar um zip com as fotos
      const JSZip = (await import('jszip')).default;
      const zip = new JSZip();
      
      for (let i = 0; i < fotosToDownload.length; i++) {
        const foto = fotosToDownload[i];
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${foto.url_foto}`);
          const blob = await response.blob();
          
          // Nome do arquivo com metadados
          const date = new Date(foto.data_envio).toISOString().split('T')[0];
          const fileName = `${i + 1}_${foto.nome_promotor}_${date}_${foto.legenda ? foto.legenda.substring(0, 30).replace(/[^a-zA-Z0-9]/g, '_') : 'sem_legenda'}.jpg`;
          
          zip.file(fileName, blob);
        } catch (error) {
          console.error(`Erro ao baixar foto ${foto.id}:`, error);
        }
      }
      
      // Gerar e baixar o zip
      const content = await zip.generateAsync({ type: 'blob' });
      const url = window.URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `fotos_${selectedPromotorName || 'promotor'}_${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Erro no download em lote:', error);
      alert('Erro ao fazer download das fotos. Tente novamente.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleBackToPromotores = () => {
    window.history.back();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Hoje';
    if (diffDays === 2) return 'Ontem';
    if (diffDays <= 7) return `${diffDays} dias atrás`;
    
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getImageUrl = (url: string) => {
    return url.startsWith('http') ? url : `${process.env.NEXT_PUBLIC_API_URL}${url}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="loading-shimmer w-12 h-12 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando galeria...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-center py-8">{error}</div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-3">
          {selectedPromotorName && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleBackToPromotores}
              className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-800 rounded-xl transition-all duration-200"
              title="Voltar para promotores"
            >
              <ArrowLeft size={20} />
            </motion.button>
          )}
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
            <Camera className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              {selectedPromotorName ? `Fotos de ${selectedPromotorName}` : 'Galeria de Fotos'}
            </h1>
            <p className="text-gray-600 mt-1">
              {selectedPromotorName 
                ? `Visualize todas as fotos de ${selectedPromotorName}` 
                : 'Visualize todas as fotos enviadas pelos promotores'
              }
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {selectedPromotorName && filteredFotos.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleBulkDownload}
              disabled={isDownloading}
              className={`flex items-center space-x-2 px-4 py-3 rounded-xl transition-all duration-200 ${
                isDownloading 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-green-100 hover:bg-green-200 text-green-700 hover:text-green-800'
              }`}
              title="Download das 15 fotos mais recentes"
            >
              {isDownloading ? (
                <>
                  <div className="loading-shimmer w-4 h-4 rounded-full"></div>
                  <span className="text-sm font-medium">Baixando...</span>
                </>
              ) : (
                <>
                  <Package size={16} />
                  <span className="text-sm font-medium">Download Lote</span>
                </>
              )}
            </motion.button>
          )}
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            className={`p-3 rounded-xl transition-all duration-200 ${
              viewMode === 'grid' 
                ? 'bg-purple-100 text-purple-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title={viewMode === 'grid' ? 'Visualização em lista' : 'Visualização em grade'}
          >
            {viewMode === 'grid' ? <List size={20} /> : <Grid3X3 size={20} />}
          </motion.button>
        </div>
      </div>

      {/* Advanced Filters */}
      <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg">
        <form onSubmit={handleFilterSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Promotor</label>
              <select 
                value={selectedPromotor} 
                onChange={e => setSelectedPromotor(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              >
                <option value="">Todos os promotores</option>
                {promotores.map(p => (
                  <option key={p.id} value={p.id}>{p.nome}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Início</label>
              <input 
                type="date" 
                value={dataInicio} 
                onChange={e => setDataInicio(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Fim</label>
              <input 
                type="date" 
                value={dataFim} 
                onChange={e => setDataFim(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Buscar na Legenda</label>
              <input 
                type="text" 
                value={buscaLegenda} 
                onChange={e => setBuscaLegenda(e.target.value)}
                placeholder="Nome da loja..."
                className="w-full p-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>
          
          <div className="flex justify-end">
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all duration-200 shadow-lg font-medium"
            >
              Aplicar Filtros
            </motion.button>
          </div>
        </form>
      </div>

      {/* Quick Search and Filters */}
      <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Busca rápida por promotor ou legenda..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
            />
          </div>
          
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <Filter size={20} className="text-gray-400" />
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value as 'all' | 'today' | 'week' | 'month')}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              >
                <option value="all">Todos os períodos</option>
                <option value="today">Hoje</option>
                <option value="week">Última semana</option>
                <option value="month">Último mês</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
              >
                <option value="date">Data</option>
                <option value="name">Nome</option>
              </select>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="p-3 bg-gray-100 hover:bg-gray-200 rounded-xl transition-all duration-200"
                title={sortOrder === 'asc' ? 'Ordem crescente' : 'Ordem decrescente'}
              >
                {sortOrder === 'asc' ? <SortAsc size={20} /> : <SortDesc size={20} />}
              </motion.button>
            </div>
            
            <div className="flex items-center space-x-2 text-gray-600">
              <span className="font-medium">{filteredFotos.length} fotos</span>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Section - Only show when viewing specific promotor */}
      {selectedPromotorName && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl border border-purple-200/50 shadow-lg"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Camera className="text-purple-600" size={20} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Estatísticas de {selectedPromotorName}
            </h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white/70 backdrop-blur-sm p-4 rounded-xl border border-white/50">
              <div className="flex items-center space-x-2 mb-2">
                <Camera className="text-blue-500" size={16} />
                <span className="text-sm font-medium text-gray-600">Total de Fotos</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{filteredFotos.length}</p>
            </div>
            
            <div className="bg-white/70 backdrop-blur-sm p-4 rounded-xl border border-white/50">
              <div className="flex items-center space-x-2 mb-2">
                <Calendar className="text-green-500" size={16} />
                <span className="text-sm font-medium text-gray-600">Fotos Hoje</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {filteredFotos.filter(foto => {
                  const today = new Date().toISOString().split('T')[0];
                  return foto.data_envio.split('T')[0] === today;
                }).length}
              </p>
            </div>
            
            <div className="bg-white/70 backdrop-blur-sm p-4 rounded-xl border border-white/50">
              <div className="flex items-center space-x-2 mb-2">
                <Package className="text-orange-500" size={16} />
                <span className="text-sm font-medium text-gray-600">Últimas 15</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {Math.min(filteredFotos.length, 15)}
              </p>
            </div>
            
            <div className="bg-white/70 backdrop-blur-sm p-4 rounded-xl border border-white/50">
              <div className="flex items-center space-x-2 mb-2">
                <Download className="text-purple-500" size={16} />
                <span className="text-sm font-medium text-gray-600">Disponível</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {filteredFotos.length > 0 ? "Sim" : "Não"}
              </p>
            </div>
          </div>
          
          {filteredFotos.length > 0 && (
            <div className="mt-4 p-4 bg-white/50 rounded-xl border border-white/50">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-700">Última foto enviada:</p>
                  <p className="text-sm text-gray-600">
                    {formatDate(filteredFotos[0]?.data_envio)} - {filteredFotos[0]?.legenda || "Sem legenda"}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-700">Primeira foto:</p>
                  <p className="text-sm text-gray-600">
                    {formatDate(filteredFotos[filteredFotos.length - 1]?.data_envio)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* Photos Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
          {filteredFotos.map((foto, index) => (
            <motion.div
              key={foto.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white/80 backdrop-blur-sm rounded-2xl overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300 group relative"
            >
              <div className="aspect-square relative overflow-hidden">
                <Image
                  src={getImageUrl(foto.url_foto)}
                  alt={foto.legenda || "Foto"}
                  fill
                  className="object-cover cursor-pointer transition-transform duration-300 group-hover:scale-110"
                  onClick={() => handleOpenModal(index)}
                />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center">
                  <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    whileHover={{ opacity: 1, scale: 1 }}
                    className="opacity-0 group-hover:opacity-100 transition-all duration-300"
                  >
                    <Eye className="text-white" size={32} />
                  </motion.div>
                </div>
                
                {user?.perfil === 'ADMIN' && (
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => handleDeleteFoto(foto.id)}
                    className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full h-8 w-8 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-200 shadow-lg"
                    title="Excluir foto"
                  >
                    <Trash2 size={16} />
                  </motion.button>
                )}
              </div>
              
              <div className="p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <User size={16} className="text-gray-400" />
                  <h3 className="font-semibold text-gray-900 truncate">{foto.nome_promotor}</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2 line-clamp-2">{foto.legenda || "Sem legenda"}</p>
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <Calendar size={12} />
                  <span>{formatDate(foto.data_envio)}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-lg overflow-hidden">
          <div className="divide-y divide-gray-200/50">
            {filteredFotos.map((foto, index) => (
              <motion.div
                key={foto.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="p-6 hover:bg-gray-50/50 transition-all duration-200 group relative"
              >
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 relative">
                    <Image
                      src={getImageUrl(foto.url_foto)}
                      alt={foto.legenda || "Foto"}
                      fill
                      className="object-cover cursor-pointer transition-transform duration-300 group-hover:scale-110"
                      onClick={() => handleOpenModal(index)}
                    />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <User size={16} className="text-gray-400" />
                      <h3 className="font-semibold text-gray-900">{foto.nome_promotor}</h3>
                    </div>
                    <p className="text-sm text-gray-600 mb-2 line-clamp-2">{foto.legenda || "Sem legenda"}</p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <Calendar size={12} />
                      <span>{formatDate(foto.data_envio)}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleOpenModal(index)}
                      className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-xl transition-all duration-200"
                      title="Visualizar"
                    >
                      <Eye size={16} />
                    </motion.button>
                    
                    <motion.a
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      href={getImageUrl(foto.url_foto)}
                      download
                      className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-200"
                      title="Download"
                    >
                      <Download size={16} />
                    </motion.a>
                    
                    {user?.perfil === 'ADMIN' && (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleDeleteFoto(foto.id)}
                        className="p-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-xl transition-all duration-200"
                        title="Excluir"
                      >
                        <Trash2 size={16} />
                      </motion.button>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
      
      {/* Empty State */}
      {filteredFotos.length === 0 && !loading && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Camera size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">
            {searchTerm || filterBy !== 'all' ? 'Nenhuma foto encontrada' : 'Nenhuma foto enviada ainda'}
          </h3>
          <p className="text-gray-500">
            {searchTerm || filterBy !== 'all'
              ? 'Tente ajustar os filtros de busca' 
              : 'As fotos enviadas pelos promotores aparecerão aqui'
            }
          </p>
        </motion.div>
      )}

      {/* Stats Summary */}
      {fotos.length > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-2xl border border-purple-200/50">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{fotos.length}</div>
              <div className="text-sm text-gray-600">Total de Fotos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {fotos.filter(f => {
                  const today = new Date();
                  const fotoDate = new Date(f.data_envio);
                  return fotoDate.toDateString() === today.toDateString();
                }).length}
              </div>
              <div className="text-sm text-gray-600">Hoje</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {fotos.filter(f => {
                  const weekAgo = new Date();
                  weekAgo.setDate(weekAgo.getDate() - 7);
                  return new Date(f.data_envio) >= weekAgo;
                }).length}
              </div>
              <div className="text-sm text-gray-600">Esta Semana</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {new Set(fotos.map(f => f.nome_promotor)).size}
              </div>
              <div className="text-sm text-gray-600">Promotores Ativos</div>
            </div>
          </div>
        </div>
      )}
      
      {modalIndex !== null && (
        <ImageModal 
          isOpen={true}
          onClose={handleCloseModal}
          imageUrl={getImageUrl(filteredFotos[modalIndex].url_foto)}
          altText={filteredFotos[modalIndex].legenda || "Foto"}
          onNext={handleNext}
          onPrev={handlePrev}
          promotorNome={filteredFotos[modalIndex].nome_promotor}
          dataEnvio={filteredFotos[modalIndex].data_envio}
        />
      )}
    </div>
  );
}
