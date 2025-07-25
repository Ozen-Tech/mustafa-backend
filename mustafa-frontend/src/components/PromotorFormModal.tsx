"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { AxiosError } from 'axios';

interface User {
  id: number;
  nome: string;
  email: string;
  perfil: 'ADMIN' | 'GESTOR' | 'OPERADOR'; // Usar os tipos do Enum
  whatsapp_number: string | null;
  is_active: boolean;
}

interface PromotorFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: () => void;
  promotor: User | null; // Se for null, é um formulário de criação
}

export const PromotorFormModal = ({ isOpen, onClose, onSave, promotor }: PromotorFormModalProps) => {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [whatsapp, setWhatsapp] = useState('');
  const [perfil, setPerfil] = useState<'ADMIN' | 'OPERADOR'>('OPERADOR');
  const [password, setPassword] = useState('');
  const [contrato, setContrato] = useState<File | null>(null); // << NOVO: Para o arquivo do contrato
  const [cpf, setCpf] = useState(''); // << NOVO: CPF do promotor para o contrato

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  const isCreating = !promotor;

  // Efeito para preencher o formulário
  useEffect(() => {
    if (promotor) {
      setNome(promotor.nome);
      setEmail(promotor.email);
      setWhatsapp(promotor.whatsapp_number?.replace('whatsapp:', '') || '');
      setPerfil(promotor.perfil as 'ADMIN' | 'OPERADOR'); // Cast para tipo correto
      setPassword('');
      setCpf(''); // Limpa CPF, pois o contrato é um novo upload
    } else {
      setNome('');
      setEmail('');
      setWhatsapp('');
      setPerfil('OPERADOR');
      setPassword('');
      setCpf('');
    }
    setError('');
    setContrato(null);
  }, [promotor, isOpen]);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setContrato(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Validação
    if (perfil === 'OPERADOR' && isCreating && !contrato) {
      setError('Para criar um promotor (Operador), o envio do contrato é obrigatório.');
      setIsLoading(false);
      return;
    }
     if (contrato && !cpf) {
      setError('O CPF é obrigatório ao enviar um contrato.');
      setIsLoading(false);
      return;
    }
    if (isCreating && !password) {
      setError('A senha é obrigatória para criar um novo usuário.');
      setIsLoading(false);
      return;
    }

    try {
      // Passo 1: Criar ou atualizar o usuário
      let userId = promotor?.id;
      if (isCreating) {
        const userPayload = { nome, email, perfil, password, whatsapp_number: whatsapp ? `whatsapp:${whatsapp}` : undefined };
        const userResponse = await api.post('/users', userPayload);
        userId = userResponse.data.id;
      } else {
        const userPayload = { nome, email, perfil, whatsapp_number: whatsapp ? `whatsapp:${whatsapp}` : undefined };
        await api.put(`/users/${userId}`, userPayload);
      }

      // Passo 2: Se houver um contrato, fazer o upload
      if (contrato && userId) {
        const formData = new FormData();
        formData.append('file', contrato);
        formData.append('nome_promotor', nome);
        formData.append('cpf_promotor', cpf);
        formData.append('usuario_id', String(userId));
        await api.post('/contratos/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      onSave();
      onClose();

    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string | string[] }>;
      const detail = axiosError.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => (d as any).msg).join(', '));
      } else {
        setError(detail || "Ocorreu um erro. Verifique os dados e tente novamente.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">{isCreating ? 'Adicionar Novo Usuário' : 'Editar Promotor'}</h2>
        {error && <p className="bg-red-100 text-red-700 p-3 rounded-md mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div><label className="block text-gray-700">Nome Completo</label><input type="text" value={nome} onChange={e => setNome(e.target.value)} required className="w-full px-3 py-2 border rounded text-gray-800" /></div>
          <div><label className="block text-gray-700">Email</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} required className="w-full px-3 py-2 border rounded text-gray-800" /></div>
          {isCreating && <div><label className="block text-gray-700">Senha</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} required={isCreating} minLength={6} className="w-full px-3 py-2 border rounded text-gray-800" /></div>}
          <div><label className="block text-gray-700">Número de WhatsApp (Ex: +5511999998888)</label><input type="text" value={whatsapp} onChange={e => setWhatsapp(e.target.value)} placeholder="+5511999998888" className="w-full px-3 py-2 border rounded text-gray-800" /></div>
          <div><label className="block text-gray-700">Perfil</label><select value={perfil} onChange={e => setPerfil(e.target.value as 'ADMIN' | 'OPERADOR')} className="w-full px-3 py-2 border rounded text-gray-800"><option value="OPERADOR">Promotor (Operador)</option><option value="ADMIN">Administrador</option></select></div>

          <hr className="my-6" />

          <h3 className="text-lg font-semibold text-gray-700">{isCreating ? 'Adicionar Contrato (Obrigatório para Promotor)' : 'Atualizar Contrato (Opcional)'}</h3>
          
          <div className='bg-gray-50 p-4 rounded-md border'>
             <div><label className="block text-gray-700">CPF do Promotor</label><input type="text" value={cpf} onChange={e => setCpf(e.target.value)} required={!!contrato} placeholder='123.456.789-00' className="w-full px-3 py-2 border rounded text-gray-800" /></div>
            <div className='mt-4'><label className="block text-gray-700">Arquivo do Contrato (.pdf, .jpg, .png)</label><input type="file" onChange={handleFileChange} accept=".pdf,.jpg,.jpeg,.png" className="w-full text-gray-800" /></div>
          </div>


          <div className="flex justify-end gap-4 pt-4">
            <button type="button" onClick={onClose} disabled={isLoading} className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 disabled:opacity-50">Cancelar</button>
            <button type="submit" disabled={isLoading} className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50">{isLoading ? 'Salvando...' : 'Salvar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};