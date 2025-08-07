"use client";

import { useState } from 'react';
import api from '@/lib/api';

export default function InsightsPage() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAsk = async () => {
    if (!question.trim()) return;
    setIsLoading(true);
    setAnswer('');
    try {
      const response = await api.post('/insights/ask', { question });
      setAnswer(response.data.answer);
    } catch (err) { // <<<< Use 'err' e defina o estado de erro
      console.error("Erro na consulta à IA:", err);
      setError('Ocorreu um erro ao consultar a IA. Tente novamente mais tarde.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Insights com IA</h1>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <label htmlFor="ai-question" className="block text-lg font-medium text-gray-700">
          Pergunte algo sobre os dados dos promotores:
        </label>
        <textarea
          id="ai-question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="mt-2 block w-full p-3 border border-gray-300 rounded-md text-gray-800"
          rows={4}
          placeholder= "Ex: Quais lojas foram mais visitadas nos últimos 7 dias?"
        />
        <button
          onClick={handleAsk}
          disabled={isLoading}
          className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
        >
          {error && <p className="text-red-500 mt-4">{error}</p>}

          {isLoading ? 'Analisando...' : 'Perguntar à IA'}
        </button>

        {answer && (
          <div className="mt-8 p-4 border-t border-gray-200">
            <h2 className="text-xl font-bold text-gray-800 mb-4">Resposta da IA:</h2>
            <div 
              className="prose max-w-none text-gray-700" 
              dangerouslySetInnerHTML={{ __html: answer.replace(/\n/g, '<br />') }}
            />
          </div>
        )}
      </div>
    </div>
  );
}