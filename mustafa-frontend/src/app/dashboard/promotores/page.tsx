"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import Link from 'next/link';
import { PromotorFormModal } from '@/components/PromotorFormModal';

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
  perfil: string;
  whatsapp_number: string | null;
  is_active: boolean;
  contratos: ContratoInfo[];
}

export default function PromotoresPage() {
  const [promotores, setPromotores] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Estados para controlar o modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPromotor, setEditingPromotor] = useState<User | null>(null);

  const fetchPromotores = () => {
    setLoading(true);
    api.get('/users')
      .then(response => setPromotores(response.data))
      .catch(() => setError("Falha ao carregar promotores."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPromotores();
  }, []);

  // Funções para controlar o modal
  const handleOpenCreateModal = () => {
    setEditingPromotor(null);
    setIsModalOpen(true);
  };
  
  const handleOpenEditModal = (promotor: User) => {
    setEditingPromotor(promotor);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };
  
  const handleSave = () => {
    fetchPromotores(); // Recarrega a lista após salvar
  };

  if (loading) return <div>Carregando promotores...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <>
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Gerenciar Promotores</h1>
          <button onClick={handleOpenCreateModal} className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600">
            + Adicionar Promotor
          </button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nome</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">WhatsApp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Contratos</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {promotores.map(p => (
                <tr key={p.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{p.nome}</div>
                    <div className="text-sm text-gray-500">{p.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">{p.whatsapp_number?.replace('whatsapp:', '') || 'Não cadastrado'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {p.contratos.length > 0 ? (
                      p.contratos.map(c => (
                        <Link key={c.id} href={`${process.env.NEXT_PUBLIC_API_URL}${c.url_acesso}`} target="_blank" className="text-blue-600 hover:underline block">
                          {c.nome_arquivo_original}
                        </Link>
                      ))
                    ) : 'Nenhum'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${p.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {p.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button onClick={() => handleOpenEditModal(p)} className="text-indigo-600 hover:text-indigo-900">Editar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <PromotorFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSave={handleSave}
        promotor={editingPromotor}
      />
    </>
  );
}
