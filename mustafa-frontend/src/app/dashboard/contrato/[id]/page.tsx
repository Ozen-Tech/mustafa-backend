"use client";

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import api from '@/lib/api';
import { ArrowLeft, Download, FileText, Loader2, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface Contrato {
  id: number;
  nome_promotor: string;
  cpf_promotor: string;
  nome_arquivo_original: string;
  caminho_arquivo: string;
  url_acesso: string;
  data_upload: string;
  usuario_id: number;
  empresa_id: number;
}

export default function ContratoViewPage() {
  const params = useParams();
  const router = useRouter();
  const [contrato, setContrato] = useState<Contrato | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [imageError, setImageError] = useState(false);

  const contratoId = params.id as string;

  useEffect(() => {
    const fetchContrato = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/contratos/${contratoId}`);
        setContrato(response.data);
      } catch (err) {
        console.error('Erro ao buscar contrato:', err);
        setError('Erro ao carregar contrato');
      } finally {
        setLoading(false);
      }
    };

    if (contratoId) {
      fetchContrato();
    }
  }, [contratoId]);

  const handleDownload = async () => {
    if (!contrato) return;
    
    try {
      const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`;
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = contrato.nome_arquivo_original;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Erro ao baixar arquivo:', err);
    }
  };

  const handleImageError = () => {
    setImageError(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Carregando contrato...</p>
        </div>
      </div>
    );
  }

  if (error || !contrato) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Erro ao carregar contrato</h2>
          <p className="text-gray-600 mb-6">{error || 'Contrato não encontrado'}</p>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => router.back()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            Voltar
          </motion.button>
        </div>
      </div>
    );
  }

  const imageUrl = `${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`;
  const isPdf = contrato.nome_arquivo_original.toLowerCase().endsWith('.pdf');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => router.back()}
                className="p-2 bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} />
              </motion.button>
              
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {contrato.nome_arquivo_original}
                </h1>
                <p className="text-sm text-gray-600">
                  Promotor: {contrato.nome_promotor} • CPF: {contrato.cpf_promotor}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownload}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Download size={16} />
                <span>Baixar</span>
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {isPdf ? (
            <div className="h-[calc(100vh-200px)]">
              <iframe
                src={imageUrl}
                className="w-full h-full border-0"
                title={contrato.nome_arquivo_original}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center p-8">
              {imageError ? (
                <div className="text-center">
                  <FileText className="w-24 h-24 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    Não foi possível carregar a imagem
                  </h3>
                  <p className="text-gray-500 mb-4">
                    O arquivo pode estar corrompido ou em um formato não suportado
                  </p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleDownload}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors mx-auto"
                  >
                    <Download size={16} />
                    <span>Baixar arquivo</span>
                  </motion.button>
                </div>
              ) : (
                <motion.img
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                  src={imageUrl}
                  alt={contrato.nome_arquivo_original}
                  className="max-w-full max-h-[calc(100vh-200px)] object-contain rounded-lg shadow-lg"
                  onError={handleImageError}
                />
              )}
            </div>
          )}
        </div>
        
        {/* Info Card */}
        <div className="mt-6 bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200/50 shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Informações do Contrato</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Nome do Promotor</label>
              <p className="text-gray-900 font-medium">{contrato.nome_promotor}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">CPF</label>
              <p className="text-gray-900 font-medium">{contrato.cpf_promotor}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Data de Upload</label>
              <p className="text-gray-900 font-medium">
                {new Date(contrato.data_upload).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Nome do Arquivo</label>
              <p className="text-gray-900 font-medium">{contrato.nome_arquivo_original}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">Tipo</label>
              <p className="text-gray-900 font-medium">
                {isPdf ? 'Documento PDF' : 'Imagem'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}