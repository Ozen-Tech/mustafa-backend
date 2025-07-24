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
        port: '',
        pathname: '/fotos-promotores/**', // Permite qualquer imagem dentro desta pasta
      },
    ],
  },
};

export default nextConfig;
// --- END OF FILE next.config.ts (CORRIGIDO) ---