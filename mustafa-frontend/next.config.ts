// --- START OF FILE next.config.ts (CORRIGIDO) ---
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configuração para permitir imagens do seu backend.
  // Sem isso, o <Image> da Next.js bloquearia as URLs.
  images: {
    remotePatterns: [
      {
        protocol: 'https', 
        hostname: 'mustafa-backend-6ywg.onrender.com',
        pathname: '/fotos-promotores/**', // Permite qualquer imagem dentro desta pasta
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/fotos-promotores/**', // Para desenvolvimento local
      },
    ],
  },
};

export default nextConfig;
// --- END OF FILE next.config.ts (CORRIGIDO) ---