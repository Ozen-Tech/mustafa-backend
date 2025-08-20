"use client";

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { PromotorFormModal } from '@/components/PromotorFormModal';
import { ImageModal } from '@/components/ImageModal';
import { 
  Users, 
  Plus, 
  Edit3, 
  FileText, 
  Eye, 
  Mail, 
  Phone,
  Search,
  Filter,
  Images
} from 'lucide-react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';

// Interfaces dos dados
interface ContratoInfo {
  id: number;
  nome_arquivo_original: string;
  url_acesso: string;
}
interface User {
  id: number;
  nome: string;
  email: string;
  perfil: 'ADMIN' | 'GESTOR' | 'OPERADOR';
  whatsapp_number: string | null;
  is_active: boolean;
  contratos: ContratoInfo[];
}

export default function PromotoresPage() {
  const router = useRouter();
  const [promotores, setPromotores] = useState<User[]>([]);
  const [filteredPromotores, setFilteredPromotores] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingPromotor, setEditingPromotor] = useState<User | null>(null);
  const [isContractModalOpen, setIsContractModalOpen] = useState(false);
  const [contractImageUrl, setContractImageUrl] = useState('');

  const fetchPromotores = () => {
    setLoading(true);
    setError(null);
    api.get<User[]>('/users')
      .then(response => {
        setPromotores(response.data);
        setFilteredPromotores(response.data);
      })
      .catch(() => setError("Falha ao carregar promotores."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPromotores();
  }, []);

  useEffect(() => {
    const filtered = promotores.filter(promotor => 
      promotor.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
      promotor.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (promotor.whatsapp_number && promotor.whatsapp_number.includes(searchTerm))
    );
    setFilteredPromotores(filtered);
  }, [searchTerm, promotores]);

  const handleOpenCreateModal = () => { setEditingPromotor(null); setIsFormModalOpen(true); };
  const handleOpenEditModal = (promotor: User) => { setEditingPromotor(promotor); setIsFormModalOpen(true); };
  const handleCloseFormModal = () => setIsFormModalOpen(false);
  const handleSave = () => {
    setIsFormModalOpen(false);
    fetchPromotores();
  };

  const handleOpenContractModal = (url: string) => { setContractImageUrl(url); setIsContractModalOpen(true); };
  const handleCloseContractModal = () => setIsContractModalOpen(false);
  
  const handleViewPhotos = (promotorId: number, promotorName: string) => {
    router.push(`/dashboard/fotos?promotor_id=${promotorId}&promotor_name=${encodeURIComponent(promotorName)}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="loading-shimmer w-12 h-12 rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Carregando promotores...</p>
        </div>
      </div>
    );
  }
  
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
            <Users className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
              Gerenciar Promotores
            </h1>
            <p className="text-gray-600 mt-1">Gerencie sua equipe de promotores</p>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleOpenCreateModal}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 shadow-lg hover:shadow-xl"
        >
          <Plus size={20} />
          <span className="font-medium">Adicionar Promotor</span>
        </motion.button>
      </div>

      {/* Search and Filter */}
      <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar por nome, email ou WhatsApp..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            />
          </div>
          <div className="flex items-center space-x-2 text-gray-600">
            <Filter size={20} />
            <span className="font-medium">{filteredPromotores.length} promotores encontrados</span>
          </div>
        </div>
      </div>

      {/* Promotores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPromotores.map((promotor, index) => (
          <motion.div
            key={promotor.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-gray-200/50 shadow-lg hover:shadow-xl transition-all duration-300 group"
          >
            {/* Header do Card */}
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-lg">
                    {promotor.nome.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{promotor.nome}</h3>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    promotor.perfil === 'ADMIN' ? 'bg-blue-100 text-blue-800' : 
                    promotor.perfil === 'GESTOR' ? 'bg-purple-100 text-purple-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {promotor.perfil}
                  </span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => handleViewPhotos(promotor.id, promotor.nome)}
                  className="p-2 bg-green-100 hover:bg-green-200 text-green-600 hover:text-green-700 rounded-lg transition-all duration-200"
                  title="Ver fotos do promotor"
                >
                  <Images size={16} />
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => handleOpenEditModal(promotor)}
                  className="p-2 bg-gray-100 hover:bg-blue-100 text-gray-600 hover:text-blue-600 rounded-lg transition-all duration-200"
                  title="Editar promotor"
                >
                  <Edit3 size={16} />
                </motion.button>
              </div>
            </div>
            
            {/* Informações de Contato */}
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3 text-gray-600">
                <Mail size={16} className="text-gray-400" />
                <span className="text-sm truncate">{promotor.email}</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-600">
                <Phone size={16} className="text-gray-400" />
                <span className="text-sm">{promotor.whatsapp_number?.replace('whatsapp:', '') || 'N/A'}</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  promotor.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {promotor.is_active ? 'Ativo' : 'Inativo'}
                </span>
              </div>
            </div>
            
            {/* Contratos */}
            {promotor.contratos && promotor.contratos.length > 0 && (
              <div className="border-t border-gray-200/50 pt-4">
                <div className="flex items-center space-x-2 mb-3">
                  <FileText size={16} className="text-blue-500" />
                  <h4 className="text-sm font-semibold text-gray-700">
                    Contratos ({promotor.contratos.length})
                  </h4>
                </div>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {promotor.contratos.map((contrato) => {
                    const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`;
                    return (
                      <div key={contrato.id} className="flex items-center justify-between p-3 bg-gray-50/80 rounded-lg hover:bg-gray-100/80 transition-colors">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-gray-700 truncate font-medium">
                            {contrato.nome_arquivo_original}
                          </p>
                        </div>
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleOpenContractModal(imageUrl)}
                          className="p-2 bg-blue-100 hover:bg-blue-200 text-blue-600 rounded-lg transition-colors ml-2"
                        >
                          <Eye size={14} />
                        </motion.button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Sem contratos */}
            {(!promotor.contratos || promotor.contratos.length === 0) && (
              <div className="border-t border-gray-200/50 pt-4">
                <div className="text-center py-4">
                  <FileText size={24} className="text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Nenhum contrato anexado</p>
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {filteredPromotores.length === 0 && !loading && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Users size={48} className="text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">
            {searchTerm ? 'Nenhum promotor encontrado' : 'Nenhum promotor cadastrado'}
          </h3>
          <p className="text-gray-500 mb-6">
            {searchTerm 
              ? 'Tente ajustar os termos de busca' 
              : 'Comece adicionando seu primeiro promotor'
            }
          </p>
          {!searchTerm && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleOpenCreateModal}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 shadow-lg"
            >
              Adicionar Primeiro Promotor
            </motion.button>
          )}
        </motion.div>
      )}

      <PromotorFormModal isOpen={isFormModalOpen} onClose={handleCloseFormModal} onSave={handleSave} promotor={editingPromotor} />
      
      <ImageModal isOpen={isContractModalOpen} onClose={handleCloseContractModal} imageUrl={contractImageUrl} altText="Visualização de Contrato"/>
    </div>
  );
}
