"use client";

import { useState } from 'react';
import api from '@/lib/api';

interface AIResponse {
  answer: string;
  question: string;
}

// Componente para um card de pergunta sugerida
const SuggestionCard = ({ question, onClick }: { question: string, onClick: (q: string) => void }) => (
  <button 
    onClick={() => onClick(question)} 
    className="bg-gray-100 hover:bg-gray-200 text-left p-4 rounded-lg border border-gray-300 transition-all text-gray-800"
  >
    <p className="font-semibold">{question}</p>
  </button>
);

export default function InsightsPage() {
  const [question, setQuestion] = useState('');
  const [history, setHistory] = useState<AIResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAskQuestion = async (q: string) => {
    if (!q.trim() || isLoading) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await api.post('/insights/ask', { question: q });
      setHistory(prev => [response.data, ...prev]);
      setQuestion(''); // Limpa o input após a pergunta
    } catch (err) {
      setError('Não foi possível obter a resposta da IA. Tente novamente.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAskQuestion(question);
  };
  
  const suggestedQuestions = [
    "Quais lojas foram visitadas esta semana? Liste em tópicos.",
    "Resuma as atividades do promotor que mais enviou fotos.",
    "Identifique se alguma legenda menciona 'ruptura' ou 'falta de produto'.",
    "Qual promotor parece focar mais em uma única rede de lojas?",
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2 text-gray-800">Assistente de Análise com IA</h1>
      <p className="mb-6 text-gray-600">Faça perguntas em linguagem natural sobre as fotos enviadas pelos promotores.</p>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSubmit} className="flex gap-4">
          <input
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ex: Quais produtos da marca X foram reportados hoje?"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-800 focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
            disabled={isLoading}
          >
            {isLoading ? 'Analisando...' : 'Perguntar'}
          </button>
        </form>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </div>

      {history.length === 0 && !isLoading && (
        <div className="text-center">
           <h2 className="text-xl font-semibold mb-4 text-gray-700">Sugestões de Perguntas</h2>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
             {suggestedQuestions.map(q => <SuggestionCard key={q} question={q} onClick={(q) => {setQuestion(q); handleAskQuestion(q);}} />)}
           </div>
        </div>
      )}

      <div className="space-y-6">
        {history.map((item, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-500 font-semibold mb-2">Você perguntou:</p>
            <p className="italic text-gray-800 mb-4">"{item.question}"</p>
            <hr className="mb-4"/>
            <p className="text-blue-600 font-semibold mb-2">Resposta da IA:</p>
            {/* Usamos prose para formatar o Markdown que vem da IA */}
            <div 
                className="prose prose-sm max-w-none text-gray-800"
                dangerouslySetInnerHTML={{ __html: item.answer.replace(/\n/g, '<br />') }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}