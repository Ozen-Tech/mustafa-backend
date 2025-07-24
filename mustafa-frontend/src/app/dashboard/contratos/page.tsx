"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface Contrato {
  id: number;
  nome_promotor: string;
  cpf_promotor: string;
  nome_arquivo_original: string;
  url_acesso: string; // Ex: /arquivos-contratos/uuid.pdf
  data_upload: string;
}

export default function ContratosPage() {
  const [contratos, setContratos] = useState<Contrato[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get('/contratos') // Endpoint que lista os contratos
      .then(response => {
        setContratos(response.data);
      })
      .catch(err => {
        console.error("Falha ao buscar contratos:", err);
        setError("Não foi possível carregar os contratos.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Carregando contratos...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Contratos de Promotores</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        {contratos.length > 0 ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Promotor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPF</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Arquivo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data do Upload</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contratos.map(contrato => (
                <tr key={contrato.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-900">{contrato.nome_promotor}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">{contrato.cpf_promotor}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <a 
                      href={`${process.env.NEXT_PUBLIC_API_URL}${contrato.url_acesso}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      {contrato.nome_arquivo_original}
                    </a>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-700">
                    {new Date(contrato.data_upload).toLocaleDateString('pt-BR')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>Nenhum contrato encontrado.</p>
        )}
      </div>
    </div>
  );
}