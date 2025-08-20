"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { AxiosError } from 'axios';
import { 
  X, 
  User, 
  Mail, 
  Phone, 
  Lock, 
  Save, 
  UserPlus,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Interfaces
interface User { id: number; nome: string; email: string; perfil: string; whatsapp_number: string | null; is_active: boolean; }
interface PromotorFormModalProps { isOpen: boolean; onClose: () => void; onSave: () => void; promotor: User | null; }
interface CreatePayload { nome: string; email: string; perfil: string; whatsapp_number: string; password?: string; empresa_id?: number; }
interface UpdatePayload { nome?: string; email?: string; perfil?: string; whatsapp_number?: string; }

export const PromotorFormModal = ({ isOpen, onClose, onSave, promotor }: PromotorFormModalProps) => {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [whatsapp, setWhatsapp] = useState('');
  const [perfil, setPerfil] = useState('OPERADOR');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  useEffect(() => {
    if (promotor) {
      setNome(promotor.nome);
      setEmail(promotor.email);
      setWhatsapp(promotor.whatsapp_number?.replace('whatsapp:', '') || '');
      setPerfil(promotor.perfil);
    } else {
      setNome(''); setEmail(''); setWhatsapp(''); setPerfil('OPERADOR');
    }
    setPassword(''); setError(''); setErrors({}); setSuccess(false);
  }, [promotor, isOpen]);

  if (!isOpen) return null;

  const validateForm = () => {
    const newErrors: {[key: string]: string} = {};
    
    if (!nome.trim()) {
      newErrors.nome = 'Nome é obrigatório';
    }
    
    if (!email.trim()) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Email inválido';
    }
    
    if (!promotor && !password.trim()) {
      newErrors.password = 'Senha é obrigatória';
    } else if (password && password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setError('');
    setLoading(true);
    setErrors({});

    const isCreating = !promotor;
    const url = isCreating ? '/users/' : `/users/${promotor!.id}`;
    const method = isCreating ? 'post' : 'put';
    
    const whatsappCompleto = whatsapp ? `whatsapp:${whatsapp}` : '';

    const payload: CreatePayload | UpdatePayload = { nome, email, perfil, whatsapp_number: whatsappCompleto };
    
    if (isCreating) {
      if (!password) { setError('A senha é obrigatória.'); setLoading(false); return; }
      (payload as CreatePayload).password = password;
      (payload as CreatePayload).empresa_id = 1; 
    }
    
    try {
      await api[method](url, payload);
      setSuccess(true);
      setTimeout(() => {
        onSave(); 
        onClose(); 
      }, 1000);
    } catch (err) {
      const axiosError = err as AxiosError<{ detail: string }>;
      setError(axiosError.response?.data?.detail || "Ocorreu um erro.");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string, setter: (value: string) => void) => {
    setter(value);
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.9, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.9, opacity: 0, y: 20 }}
          transition={{ type: "spring", duration: 0.3 }}
          className="bg-white/95 backdrop-blur-sm p-8 rounded-3xl shadow-2xl w-full max-w-md border border-gray-200/50"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
                {promotor ? <User className="text-white" size={20} /> : <UserPlus className="text-white" size={20} />}
              </div>
              <div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  {promotor ? 'Editar Promotor' : 'Adicionar Novo Promotor'}
                </h2>
                <p className="text-gray-600 text-sm">
                  {promotor ? 'Atualize as informações do promotor' : 'Preencha os dados do novo promotor'}
                </p>
              </div>
            </div>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onClose}
              className="p-2 bg-gray-100 hover:bg-red-100 text-gray-600 hover:text-red-600 rounded-lg transition-all duration-200"
            >
              <X size={20} />
            </motion.button>
          </div>

          {/* Success Message */}
          <AnimatePresence>
            {success && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center space-x-3"
              >
                <CheckCircle className="text-green-500" size={20} />
                <span className="text-green-700 font-medium">
                  {promotor ? 'Promotor atualizado com sucesso!' : 'Promotor criado com sucesso!'}
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-3"
              >
                <AlertCircle className="text-red-500" size={20} />
                <span className="text-red-700 font-medium">{error}</span>
              </motion.div>
            )}
          </AnimatePresence>
        
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Nome */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Nome Completo
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input 
                  type="text" 
                  value={nome} 
                  onChange={e => handleInputChange('nome', e.target.value, setNome)} 
                  required 
                  className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                    errors.nome ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white/50'
                  }`}
                  placeholder="Digite o nome completo"
                />
                {errors.nome && (
                  <motion.p 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-red-500 text-xs mt-1 flex items-center space-x-1"
                  >
                    <AlertCircle size={12} />
                    <span>{errors.nome}</span>
                  </motion.p>
                )}
              </div>
            </div>
            
            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input 
                  type="email" 
                  value={email} 
                  onChange={e => handleInputChange('email', e.target.value, setEmail)} 
                  required 
                  className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                    errors.email ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white/50'
                  }`}
                  placeholder="Digite o email"
                />
                {errors.email && (
                  <motion.p 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-red-500 text-xs mt-1 flex items-center space-x-1"
                  >
                    <AlertCircle size={12} />
                    <span>{errors.email}</span>
                  </motion.p>
                )}
              </div>
            </div>
            
            {/* WhatsApp */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Número de WhatsApp (Ex: &quot;+5511999998888&quot;)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input 
                  type="text" 
                  value={whatsapp} 
                  onChange={e => setWhatsapp(e.target.value)} 
                  placeholder="+5511999998888" 
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 bg-white/50 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>
            </div>
            
            {/* Senha */}
            {!promotor && (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input 
                    type="password" 
                    value={password} 
                    onChange={e => handleInputChange('password', e.target.value, setPassword)} 
                    required 
                    minLength={6} 
                    className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${
                      errors.password ? 'border-red-300 bg-red-50' : 'border-gray-200 bg-white/50'
                    }`}
                    placeholder="Digite a senha"
                  />
                  {errors.password && (
                    <motion.p 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-red-500 text-xs mt-1 flex items-center space-x-1"
                    >
                      <AlertCircle size={12} />
                      <span>{errors.password}</span>
                    </motion.p>
                  )}
                </div>
              </div>
            )}
            
            {/* Buttons */}
            <div className="flex justify-end space-x-3 pt-6">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="button" 
                onClick={onClose} 
                className="px-6 py-3 text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 font-medium"
              >
                Cancelar
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit" 
                disabled={loading || success}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:from-blue-600 hover:to-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-lg"
              >
                {loading ? (
                  <>
                    <div className="loading-shimmer w-4 h-4 rounded-full"></div>
                    <span>Salvando...</span>
                  </>
                ) : success ? (
                  <>
                    <CheckCircle size={18} />
                    <span>Salvo!</span>
                  </>
                ) : (
                  <>
                    <Save size={18} />
                    <span>Salvar</span>
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
