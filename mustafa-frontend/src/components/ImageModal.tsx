"use client";

import Image from 'next/image';

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  altText?: string;
}

export const ImageModal = ({ isOpen, onClose, imageUrl, altText = 'Imagem ampliada' }: ImageModalProps) => {
  if (!isOpen || !imageUrl) {
    return null;
  }

  // Função para fechar o modal ao clicar no fundo
  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    // Fundo semi-transparente que cobre a tela inteira
    <div
      onClick={handleBackdropClick}
      className="fixed inset-0 bg-black bg-opacity-75 flex justify-center items-center z-50 p-4 transition-opacity duration-300"
    >
      {/* Container da imagem e do botão de fechar */}
      <div className="relative max-w-4xl max-h-[90vh] bg-white rounded-lg shadow-xl p-2">
        {/* Botão de Fechar */}
        <button
          onClick={onClose}
          className="absolute -top-4 -right-4 bg-white text-black rounded-full h-10 w-10 flex items-center justify-center text-2xl font-bold z-10 hover:bg-gray-200 transition-colors"
          aria-label="Fechar imagem"
        >
          ×
        </button>

        {/* A Imagem Ampliada */}
        <Image
          src={imageUrl}
          alt={altText}
          width={1200} // Valor alto para qualidade, o CSS vai limitar o tamanho
          height={800} // Valor alto para qualidade, o CSS vai limitar o tamanho
          className="object-contain w-full h-full max-h-[85vh] rounded"
          style={{ objectFit: 'contain' }} // Garante que a imagem inteira apareça
        />
      </div>
    </div>
  );
};