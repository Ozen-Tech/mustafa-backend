import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // 1. Pega o token dos cookies da requisição
  const token = request.cookies.get('accessToken');

  // 2. Pega o caminho que o usuário está tentando acessar
  const { pathname } = request.nextUrl;

  // 3. Define as rotas públicas que não precisam de autenticação
  const publicPaths = ['/login'];

  const isPublicPath = publicPaths.some(path => pathname.endsWith(path));

  // Lógica de Redirecionamento
  // Se o usuário está tentando acessar uma rota protegida e NÃO tem token,
  // redirecione para o login.
  if (!token && !isPublicPath) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Se o usuário TEM um token e está tentando acessar o login,
  // redirecione-o para o dashboard, pois ele já está autenticado.
  if (token && isPublicPath) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  // Se o usuário está tentando acessar a página raiz '/', decida para onde enviá-lo
  if (pathname === '/') {
    if (token) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
    } else {
        return NextResponse.redirect(new URL('/login', request.url));
    }
  }


  // Se nenhuma das condições acima for atendida, deixe a requisição continuar.
  return NextResponse.next();
}

// O matcher define EM QUAIS ROTAS este middleware deve rodar.
// Evita rodar em arquivos de imagem, CSS, etc.
export const config = {
  matcher: [
    '/',
    '/login',
    '/dashboard/:path*', // Aplica a todas as sub-rotas de dashboard
  ],
};
