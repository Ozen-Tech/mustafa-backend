"use client";
import Image from 'next/image';

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  altText: string;
  onNext?: () => void;
  onPrev?: () => void;
  promotorNome?: string;
  dataEnvio?: string;
}

export const ImageModal = ({ isOpen, onClose, imageUrl, altText, onNext, onPrev, promotorNome, dataEnvio }: ImageModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" onClick={onClose}>
      <button className="absolute top-4 right-4 text-white text-3xl z-50">×</button>
      {onPrev && <button onClick={(e) => { e.stopPropagation(); onPrev(); }} className="absolute left-4 top-1/2 -translate-y-1/2 text-white text-4xl p-2 bg-black bg-opacity-30 rounded-full">‹</button>}
      {onNext && <button onClick={(e) => { e.stopPropagation(); onNext(); }} className="absolute right-4 top-1/2 -translate-y-1/2 text-white text-4xl p-2 bg-black bg-opacity-30 rounded-full">›</button>}
      
      <div className="relative max-w-4xl max-h-[90vh] w-full h-full" onClick={(e) => e.stopPropagation()}>
        <Image 
          src={imageUrl} 
          alt={altText} 
          fill
          style={{ objectFit: 'contain' }}
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />

        {promotorNome && (
            <div className="absolute bottom-0 left-0 w-full bg-black bg-opacity-50 text-white p-4">
                <p className="font-bold">{promotorNome}</p>
                <p className="text-sm">{new Date(dataEnvio!).toLocaleString('pt-BR')}</p>
            </div>
        )}
      </div>
    </div>
  );
};
