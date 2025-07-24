"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { AxiosError } from 'axios';


// Interface do usuário, para ser usada como prop
interface User {
  id: number;
  nome: string;
  email: string;
  perfil: string;
  whatsapp_number: string | null;
  is_active: boolean;
}

interface PromotorFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  promotor: User | null; // Se for null, é um formulário de criação
}

interface CreatePayload {
  nome: string;
  email: string;
  perfil: string;
  whatsapp_number: string;
  password?: string;
  empresa_id?: number;
}

interface UpdatePayload {
  nome?: string;
  email?: string;
  perfil?: string;
  whatsapp_number?: string;
}

export const PromotorFormModal = ({ isOpen, onClose, onSave, promotor }: PromotorFormModalProps) => {
  // Estado para cada campo do formulário
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [whatsapp, setWhatsapp] = useState('');
  const [perfil, setPerfil] = useState('OPERADOR');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Efeito que preenche o formulário quando um promotor é passado para edição
  useEffect(() => {
    if (promotor) {
      setNome(promotor.nome);
      setEmail(promotor.email);
      setWhatsapp(promotor.whatsapp_number || '');
      setPerfil(promotor.perfil);
      setPassword(''); // Senha sempre começa vazia por segurança
    } else {
      // Limpa o formulário para criação
      setNome('');
      setEmail('');
      setWhatsapp('');
      setPerfil('OPERADOR');
      setPassword('');
    }
    setError('');
  }, [promotor, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const isCreating = !promotor;
    const url = isCreating ? '/users/' : `/users/${promotor!.id}`;
    const method = isCreating ? 'post' : 'put';
    
    // Twilio exige o prefixo "whatsapp:"
    const whatsappCompleto = whatsapp ? `whatsapp:${whatsapp}` : '';

    const payload: CreatePayload | UpdatePayload = {
      nome,
      email,
      perfil,
      whatsapp_number: whatsappCompleto,
    };
    
    if (isCreating) {
      if (!password) {
        setError('A senha é obrigatória para criar um novo promotor.');
        return;
      }
      (payload as CreatePayload).password = password;
      (payload as CreatePayload).empresa_id = 1; 
    }
    
    try {
      await api[method](url, payload);
      onSave(); 
      onClose(); 
    } catch (err) {
      // <<<<<< CORREÇÃO 2: Use a tipagem correta para o erro >>>>>>
      const axiosError = err as AxiosError<{ detail: string }>;
      setError(axiosError.response?.data?.detail || "Ocorreu um erro. Tente novamente.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">{promotor ? 'Editar Promotor' : 'Adicionar Novo Promotor'}</h2>
        
        {error && <p className="text-red-500 mb-4">{error}</p>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700">Nome Completo</label>
            <input type="text" value={nome} onChange={e => setNome(e.target.value)} required className="w-full px-3 py-2 border rounded text-gray-800" />
          </div>
          <div>
            <label className="block text-gray-700">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-3 py-2 border rounded text-gray-800" />
          </div>
          <div>
            <label className="block text-gray-700">Número de WhatsApp (Ex: +5511999998888)</label>
            <input type="text" value={whatsapp} onChange={e => setWhatsapp(e.target.value)} placeholder="+5511999998888" className="w-full px-3 py-2 border rounded text-gray-800" />
          </div>
          { !promotor && ( // Só mostra o campo de senha ao criar um novo usuário
            <div>
              <label className="block text-gray-700">Senha</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} className="w-full px-3 py-2 border rounded text-gray-800" />
            </div>
          )}

          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  );
};