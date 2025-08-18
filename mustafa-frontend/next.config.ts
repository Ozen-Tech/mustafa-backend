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
        pathname: '/**', // Permite qualquer imagem do backend (incluindo proxy)
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**', // Para desenvolvimento local (incluindo proxy)
      },
      {
        protocol: 'https',
        hostname: 'res.cloudinary.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'api.twilio.com',
        pathname: '/**', // Permite URLs diretas do Twilio (caso necessário)
      },
    ],
  },
};

export default nextConfig;
// --- END OF FILE next.config.ts (CORRIGIDO) ---