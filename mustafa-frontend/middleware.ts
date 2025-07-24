
import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Pega o token dos cookies da requisição
  const token = request.cookies.get('accessToken');
  const { pathname } = request.nextUrl;

  // Se o usuário NÃO tem token e tenta acessar qualquer rota DENTRO do dashboard,
  // redirecione-o para a página de login.
  if (!token && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Se o usuário JÁ TEM um token e tenta acessar a página de login,
  // mande-o direto para o dashboard, pois ele já está autenticado.
  if (token && pathname === '/login') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Se o usuário tenta acessar a página raiz '/', decida para onde mandá-lo.
  // Esta regra substitui a necessidade do app/page.tsx
  if (pathname === '/') {
    if (token) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
    } else {
        return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Se nenhuma das condições acima for atendida, permita que a requisição continue.
  return NextResponse.next();
}

// O 'matcher' define EM QUAIS ROTAS este middleware deve rodar.
// Evita rodar em arquivos de imagem, CSS, etc.
export const config = {
  matcher: [
    '/',
    '/dashboard/:path*', // Aplica a TODAS as sub-rotas de dashboard
    '/login',
  ],
};
