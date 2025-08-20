"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { 
  FileText, 
  Eye, 
  Download, 
  Calendar, 
  User, 
  Search, 
  Filter,
  ExternalLink,
  Upload,
  Plus
} from 'lucide-react';
import { motion } from 'framer-motion';

interface Contrato {
  id: number;
  nome_promotor: string;
  cpf_promotor: string;
  nome_arquivo_original: string;
  url_acesso: string;
  data_upload: string;
}

const ContratosPage = () => {
  const [contratos, setContratos] = useState<Contrato[]>([]);
  const [filteredContratos, setFilteredContratos] = useState<Contrato[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBy, setFilterBy] = useState<'all' | 'recent' | 'older'>('all');

  const fetchContratos = async () => {
    try {
      const response = await api.get('/contratos');
      setContratos(response.data);
      setFilteredContratos(response.data);
    } catch (err) {
      console.error('Erro ao buscar contratos:', err);
      setError('Não foi possível carregar os contratos.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContratos();
  }, []);

  useEffect(() => {
    let filtered = contratos.filter(contrato => 
      contrato.nome_promotor.toLowerCase().includes(searchTerm.toLowerCase()) ||
      contrato.cpf_promotor.includes(searchTerm) ||
      contrato.nome_arquivo_original.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Aplicar filtro de data
    if (filterBy === 'recent') {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      filtered = filtered.filter(contrato => new Date(contrato.data_upload) >= thirtyDaysAgo);
    } else if (filterBy === 'older') {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      filtered = filtered.filter(contrato => new Date(contrato.data_upload) < thirtyDaysAgo);
    }

    setFilteredContratos(filtered);
  }, [searchTerm, filterBy, contratos]);

  const getFileExtension = (filename: string) => {
    return filename.split('.').pop()?.toUpperCase() || 'FILE';
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📄';
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) return '🖼️';
    if (['doc', 'docx'].includes(ext || '')) return '📝';
    return '📁';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="loading-shimmer w-12 h-12 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando contratos...</p>
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
          <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
            <FileText className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Contratos
            </h1>
            <p className="text-gray-600 mt-1">Gerencie todos os contratos dos promotores</p>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <Plus size={20} />
          <span className="font-medium">Novo Contrato</span>
        </motion.button>
      </div>

      {/* Search and Filter */}
      <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por promotor, CPF ou nome do arquivo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
            />
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter size={20} className="text-gray-400" />
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value as 'all' | 'recent' | 'older')}
                className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
              >
                <option value="all">Todos os períodos</option>
                <option value="recent">Últimos 30 dias</option>
                <option value="older">Mais antigos</option>
              </select>
            </div>
            
            <div className="flex items-center space-x-2 text-gray-600">
              <span className="font-medium">{filteredContratos.length} contratos encontrados</span>
            </div>
          </div>
        </div>
      </div>

      {/* Contratos Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredContratos.map((contrato, index) => (
          <motion.div
            key={contrato.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg hover:shadow-xl transition-all duration-300 group"
          >
            {/* Header do Card */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
                  <span className="text-2xl">{getFileIcon(contrato.nome_arquivo_original)}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-gray-900 truncate">
                    {contrato.nome_arquivo_original}
                  </h3>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                      {getFileExtension(contrato.nome_arquivo_original)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Informações do Promotor */}
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3 text-gray-600">
                <User size={16} className="text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{contrato.nome_promotor}</p>
                  <p className="text-xs text-gray-500">CPF: {contrato.cpf_promotor}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3 text-gray-600">
                <Calendar size={16} className="text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-700">
                    {new Date(contrato.data_upload).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(contrato.data_upload).toLocaleTimeString('pt-BR', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Ações */}
            <div className="flex space-x-2 pt-4 border-t border-gray-200/50">
              <motion.a
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href={`${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-xl transition-all duration-200 font-medium"
              >
                <Eye size={16} />
                <span>Visualizar</span>
              </motion.a>
              
              <motion.a
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href={`${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`}
                download
                className="flex items-center justify-center p-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-200"
                title="Download"
              >
                <Download size={16} />
              </motion.a>
              
              <motion.a
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                href={`${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center p-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all duration-200"
                title="Abrir em nova aba"
              >
                <ExternalLink size={16} />
              </motion.a>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredContratos.length === 0 && !loading && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <FileText size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">
            {searchTerm || filterBy !== 'all' ? 'Nenhum contrato encontrado' : 'Nenhum contrato cadastrado'}
          </h3>
          <p className="text-gray-500 mb-6">
            {searchTerm || filterBy !== 'all'
              ? 'Tente ajustar os filtros de busca' 
              : 'Os contratos dos promotores aparecerão aqui'
            }
          </p>
          {!searchTerm && filterBy === 'all' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:from-green-600 hover:to-emerald-600 transition-all duration-200 shadow-lg mx-auto"
            >
              <Upload size={20} />
              <span>Fazer Upload de Contrato</span>
            </motion.button>
          )}
        </motion.div>
      )}

      {/* Stats Summary */}
      {contratos.length > 0 && (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-2xl border border-green-200/50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{contratos.length}</div>
              <div className="text-sm text-gray-600">Total de Contratos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {contratos.filter(c => {
                  const thirtyDaysAgo = new Date();
                  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
                  return new Date(c.data_upload) >= thirtyDaysAgo;
                }).length}
              </div>
              <div className="text-sm text-gray-600">Últimos 30 dias</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {new Set(contratos.map(c => c.nome_promotor)).size}
              </div>
              <div className="text-sm text-gray-600">Promotores com Contratos</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContratosPage;