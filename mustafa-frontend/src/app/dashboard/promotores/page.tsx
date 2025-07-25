"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { PromotorFormModal } from '@/components/PromotorFormModal';
import { ImageModal } from '@/components/ImageModal'; // Reutilizaremos o modal de imagem para ver o contrato

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
  const [promotores, setPromotores] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editingPromotor, setEditingPromotor] = useState<User | null>(null);
  
  // Estados para o modal de visualização de contrato
  const [isContractModalOpen, setIsContractModalOpen] = useState(false);
  const [contractImageUrl, setContractImageUrl] = useState('');


  const fetchPromotores = () => {
    setLoading(true);
    setError(null);
    api.get('/users')
      .then(response => setPromotores(response.data))
      .catch(() => setError("Falha ao carregar promotores."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPromotores();
  }, []);

  const handleOpenCreateModal = () => { setEditingPromotor(null); setIsFormModalOpen(true); };
  const handleOpenEditModal = (promotor: User) => { setEditingPromotor(promotor); setIsFormModalOpen(true); };
  const handleCloseFormModal = () => setIsFormModalOpen(false);
  const handleSave = () => fetchPromotores(); // Recarrega a lista após salvar

  const handleOpenContractModal = (url: string) => { setContractImageUrl(url); setIsContractModalOpen(true); };
  const handleCloseContractModal = () => setIsContractModalOpen(false);

  if (loading) return <div className="p-6">Carregando promotores...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Gerenciar Usuários</h1>
          <button onClick={handleOpenCreateModal} className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600">
            + Adicionar Usuário
          </button>
        </div>

        <div className="bg-white p-4 sm:p-6 rounded-lg shadow-md overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuário</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Perfil</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contato</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contratos</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {promotores.map(p => (
                <tr key={p.id}>
                  <td className="px-6 py-4 whitespace-nowrap"><div className="text-sm font-medium text-gray-900">{p.nome}</div><div className="text-sm text-gray-500">{p.email}</div></td>
                  <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 py-1 text-xs font-semibold rounded-full ${p.perfil === 'ADMIN' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'}`}>{p.perfil}</span></td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{p.whatsapp_number?.replace('whatsapp:', '') || 'N/A'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {p.contratos.length > 0 ? (
                      p.contratos.map(c => (
                        <button key={c.id} onClick={() => handleOpenContractModal(`${process.env.NEXT_PUBLIC_API_URL}${c.url_acesso}`)} className="text-blue-600 hover:underline block text-left">
                           📄 {c.nome_arquivo_original}
                        </button>
                      ))
                    ) : 'Nenhum'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap"><span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${p.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>{p.is_active ? 'Ativo' : 'Inativo'}</span></td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium"><button onClick={() => handleOpenEditModal(p)} className="text-indigo-600 hover:text-indigo-900">Editar</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <PromotorFormModal isOpen={isFormModalOpen} onClose={handleCloseFormModal} onSave={handleSave} promotor={editingPromotor} />
      
      {/* Reutilizando o ImageModal para visualizar contratos */}
      <ImageModal isOpen={isContractModalOpen} onClose={handleCloseContractModal} imageUrl={contractImageUrl} altText="Visualização de Contrato"/>
    </>
  );
}