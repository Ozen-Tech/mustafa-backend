import { useState, useEffect, useCallback, useMemo } from 'react';
import api from './api';

// Interface para configuração de paginação
interface PaginationConfig {
  initialPage?: number;
  pageSize?: number;
  cacheTime?: number; // tempo em ms para manter cache
}

// Interface para dados paginados
interface PaginatedData<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

interface PaginationState {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

interface PaginatedDataActions {
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  refresh: () => void;
}

interface PaginatedDataResult<T> {
  data: T[];
  pagination: PaginationState;
  loading: boolean;
  error: string | null;
  actions: PaginatedDataActions;
}

// Interface para estado do hook
interface UsePaginatedDataState<T> {
  data: T[];
  loading: boolean;
  error: string | null;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// Cache global para dados
const dataCache = new Map<string, {
  data: UsePaginatedDataState<any>;
  timestamp: number;
  expiry: number;
}>();

// Hook para dados paginados com cache inteligente
export function usePaginatedData<T>(
  endpoint: string,
  config: PaginationConfig = {},
  dependencies: any[] = []
) {
  const {
    initialPage = 1,
    pageSize = 10,
    cacheTime = 5 * 60 * 1000 // 5 minutos por padrão
  } = config;

  const [state, setState] = useState<UsePaginatedDataState<T>>({
    data: [],
    loading: true,
    error: null,
    pagination: {
      page: initialPage,
      pageSize,
      total: 0,
      totalPages: 0,
      hasNext: false,
      hasPrev: false
    }
  });

  // Função para gerar chave do cache
  const getCacheKey = useCallback((page: number, size: number) => {
    return `${endpoint}_page_${page}_size_${size}_${JSON.stringify(dependencies)}`;
  }, [endpoint, dependencies]);

  // Função para verificar se o cache é válido
  const isCacheValid = useCallback((cacheKey: string) => {
    const cached = dataCache.get(cacheKey);
    if (!cached) return false;
    return Date.now() < cached.expiry;
  }, []);

  // Função para buscar dados
  const fetchData = useCallback(async (page: number, size: number, forceRefresh = false) => {
    const cacheKey = getCacheKey(page, size);
    
    // Verificar cache primeiro (se não for refresh forçado)
    if (!forceRefresh && isCacheValid(cacheKey)) {
      const cached = dataCache.get(cacheKey)!;
      setState(prev => ({
        ...prev,
        ...cached.data,
        loading: false,
        error: null
      }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Fazer requisição com parâmetros de paginação
      const response = await api.get(endpoint, {
        params: {
          page,
          limit: size,
          offset: (page - 1) * size
        }
      });

      let data: T[];
      let total: number;

      // Adaptar resposta baseada na estrutura da API
      if (Array.isArray(response.data)) {
        // Se a resposta é um array simples
        data = response.data as T[];
        total = response.data.length;
      } else if (response.data.items || response.data.data) {
        // Se a resposta tem estrutura paginada
        data = (response.data.items || response.data.data) as T[];
        total = response.data.total || response.data.count || data.length;
      } else {
        // Fallback
        data = response.data as T[];
        total = data.length;
      }

      const totalPages = Math.ceil(total / size);
      const hasNext = page < totalPages;
      const hasPrev = page > 1;

      const newState = {
        data,
        loading: false,
        error: null,
        pagination: {
          page,
          pageSize: size,
          total,
          totalPages,
          hasNext,
          hasPrev
        }
      };

      setState(newState);

      // Salvar no cache
      dataCache.set(cacheKey, {
        data: newState,
        timestamp: Date.now(),
        expiry: Date.now() + cacheTime
      });

    } catch (error: unknown) {
      const errorMessage = error instanceof Error 
        ? error.message 
        : (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Erro ao carregar dados';
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));
    }
  }, [endpoint, getCacheKey, isCacheValid, cacheTime]);

  // Função para ir para próxima página
  const nextPage = useCallback(() => {
    if (state.pagination.hasNext) {
      fetchData(state.pagination.page + 1, state.pagination.pageSize);
    }
  }, [state.pagination.hasNext, state.pagination.page, state.pagination.pageSize, fetchData]);

  // Função para ir para página anterior
  const prevPage = useCallback(() => {
    if (state.pagination.hasPrev) {
      fetchData(state.pagination.page - 1, state.pagination.pageSize);
    }
  }, [state.pagination.hasPrev, state.pagination.page, state.pagination.pageSize, fetchData]);

  // Função para ir para página específica
  const goToPage = useCallback((page: number) => {
    if (page >= 1 && page <= state.pagination.totalPages) {
      fetchData(page, state.pagination.pageSize);
    }
  }, [state.pagination.totalPages, state.pagination.pageSize, fetchData]);

  // Função para alterar tamanho da página
  const changePageSize = useCallback((newSize: number) => {
    fetchData(1, newSize); // Voltar para primeira página com novo tamanho
  }, [fetchData]);

  // Função para refresh dos dados
  const refresh = useCallback(() => {
    fetchData(state.pagination.page, state.pagination.pageSize, true);
  }, [state.pagination.page, state.pagination.pageSize, fetchData]);

  // Função para limpar cache
  const clearCache = useCallback(() => {
    const keysToDelete = Array.from(dataCache.keys()).filter(key => 
      key.startsWith(endpoint)
    );
    keysToDelete.forEach(key => dataCache.delete(key));
  }, [endpoint]);

  // Carregar dados iniciais
  useEffect(() => {
    fetchData(initialPage, pageSize);
  }, [fetchData, initialPage, pageSize, ...dependencies]);

  // Limpeza automática do cache expirado
  useEffect(() => {
    const interval = setInterval(() => {
      const now = Date.now();
      for (const [key, value] of dataCache.entries()) {
        if (now > value.expiry) {
          dataCache.delete(key);
        }
      }
    }, 60000); // Limpar a cada minuto

    return () => clearInterval(interval);
  }, []);

  return {
    ...state,
    actions: {
      nextPage,
      prevPage,
      goToPage,
      changePageSize,
      refresh,
      clearCache
    }
  };
}

// Hook para busca com debounce
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Hook para dados com busca paginada
export function useSearchablePaginatedData<T>(
  endpoint: string,
  config: PaginationConfig & { searchDelay?: number } = {}
) {
  const { searchDelay = 300, ...paginationConfig } = config;
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, searchDelay);

  const paginatedData = usePaginatedData<T>(
    endpoint,
    paginationConfig,
    [debouncedSearchTerm]
  );

  // Filtrar dados localmente se não houver busca no backend
  const filteredData = useMemo(() => {
    if (!debouncedSearchTerm) return paginatedData.data;
    
    return paginatedData.data.filter((item: T) => {
      const searchableFields = ['nome', 'email', 'whatsapp_number', 'title', 'description'];
      return searchableFields.some(field => {
        const value = (item as Record<string, unknown>)[field];
        return value && value.toString().toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      });
    });
  }, [paginatedData.data, debouncedSearchTerm]);

  return {
    ...paginatedData,
    data: filteredData,
    searchTerm,
    setSearchTerm,
    debouncedSearchTerm
  };
}

// Hook para lazy loading de imagens
export function useLazyImage(src: string, placeholder?: string) {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (!src) return;

    setIsLoading(true);
    setHasError(false);

    const img = new Image();
    img.onload = () => {
      setImageSrc(src);
      setIsLoading(false);
    };
    img.onerror = () => {
      setHasError(true);
      setIsLoading(false);
    };
    img.src = src;

    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [src]);

  return { imageSrc, isLoading, hasError };
}