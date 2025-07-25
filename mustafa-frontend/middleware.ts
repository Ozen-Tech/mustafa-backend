import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Pega o token de autenticação dos cookies
  const token = request.cookies.get('accessToken');
  const { pathname } = request.nextUrl;

  // Verifica se a rota atual é a de login ou uma rota pública que não precisa de autenticação
  const isPublicRoute = pathname.startsWith('/login');

  // REGRA 1: Se o usuário NÃO TEM token e está tentando acessar qualquer rota PROTEGIDA
  if (!token && !isPublicRoute) {
    // Redireciona para o login
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // REGRA 2: Se o usuário JÁ TEM um token e está tentando acessar a página de login
  if (token && isPublicRoute) {
    // Mande-o direto para o dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  // REGRA 3: Se o usuário acessar a raiz "/", redireciona para o dashboard.
  // A Regra 1 cuidará de enviá-lo para /login se ele não tiver token.
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Se nenhuma regra de redirecionamento foi acionada, permite que a requisição continue.
  return NextResponse.next();
}

export const config = {
  // O matcher define em quais rotas o middleware será executado.
  // Esta expressão regular executa em TODAS as rotas, exceto arquivos estáticos
  // (css, js), imagens, e rotas internas da Next.js.
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};