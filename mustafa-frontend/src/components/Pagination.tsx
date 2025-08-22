import React from 'react';
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  hasNext: boolean;
  hasPrev: boolean;
  showPageNumbers?: boolean;
  maxVisiblePages?: number;
  className?: string;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  hasNext,
  hasPrev,
  showPageNumbers = true,
  maxVisiblePages = 5,
  className = ''
}) => {
  // Calcular páginas visíveis
  const getVisiblePages = () => {
    if (totalPages <= maxVisiblePages) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    const half = Math.floor(maxVisiblePages / 2);
    let start = Math.max(currentPage - half, 1);
    const end = Math.min(start + maxVisiblePages - 1, totalPages);

    if (end - start + 1 < maxVisiblePages) {
      start = Math.max(end - maxVisiblePages + 1, 1);
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  };

  const visiblePages = getVisiblePages();
  const showStartEllipsis = visiblePages[0] > 1;
  const showEndEllipsis = visiblePages[visiblePages.length - 1] < totalPages;

  if (totalPages <= 1) {
    return null;
  }

  return (
    <div className={`flex items-center justify-center space-x-2 ${className}`}>
      {/* Botão Anterior */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!hasPrev}
        className={`
          flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
          ${hasPrev 
            ? 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 hover:text-gray-900' 
            : 'text-gray-400 bg-gray-100 border border-gray-200 cursor-not-allowed'
          }
        `}
        aria-label="Página anterior"
      >
        <ChevronLeft className="w-4 h-4 mr-1" />
        Anterior
      </button>

      {showPageNumbers && (
        <div className="flex items-center space-x-1">
          {/* Primeira página + ellipsis */}
          {showStartEllipsis && (
            <>
              <button
                onClick={() => onPageChange(1)}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-colors"
              >
                1
              </button>
              <div className="flex items-center justify-center w-8 h-8">
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </div>
            </>
          )}

          {/* Páginas visíveis */}
          {visiblePages.map((page) => (
            <button
              key={page}
              onClick={() => onPageChange(page)}
              className={`
                px-3 py-2 text-sm font-medium rounded-lg transition-colors
                ${page === currentPage
                  ? 'text-white bg-blue-600 border border-blue-600'
                  : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
              aria-label={`Página ${page}`}
              aria-current={page === currentPage ? 'page' : undefined}
            >
              {page}
            </button>
          ))}

          {/* Ellipsis + última página */}
          {showEndEllipsis && (
            <>
              <div className="flex items-center justify-center w-8 h-8">
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </div>
              <button
                onClick={() => onPageChange(totalPages)}
                className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-colors"
              >
                {totalPages}
              </button>
            </>
          )}
        </div>
      )}

      {/* Botão Próximo */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!hasNext}
        className={`
          flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors
          ${hasNext 
            ? 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 hover:text-gray-900' 
            : 'text-gray-400 bg-gray-100 border border-gray-200 cursor-not-allowed'
          }
        `}
        aria-label="Próxima página"
      >
        Próximo
        <ChevronRight className="w-4 h-4 ml-1" />
      </button>
    </div>
  );
};

// Componente para seletor de itens por página
interface PageSizeSelectorProps {
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  options?: number[];
  className?: string;
}

export const PageSizeSelector: React.FC<PageSizeSelectorProps> = ({
  pageSize,
  onPageSizeChange,
  options = [10, 20, 50, 100],
  className = ''
}) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <span className="text-sm text-gray-700">Mostrar:</span>
      <select
        value={pageSize}
        onChange={(e) => onPageSizeChange(Number(e.target.value))}
        className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <span className="text-sm text-gray-700">por página</span>
    </div>
  );
};

// Componente para informações de paginação
interface PaginationInfoProps {
  currentPage: number;
  pageSize: number;
  total: number;
  className?: string;
}

export const PaginationInfo: React.FC<PaginationInfoProps> = ({
  currentPage,
  pageSize,
  total,
  className = ''
}) => {
  const start = Math.min((currentPage - 1) * pageSize + 1, total);
  const end = Math.min(currentPage * pageSize, total);

  return (
    <div className={`text-sm text-gray-700 ${className}`}>
      Mostrando {start} a {end} de {total} resultados
    </div>
  );
};

export default Pagination;