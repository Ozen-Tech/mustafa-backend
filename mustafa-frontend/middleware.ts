
import { NextResponse, type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('accessToken');
  const { pathname } = request.nextUrl;

  // A página /login é a única rota pública dentro da nossa lógica de autenticação
  const isLoginPage = pathname.startsWith('/login');

  // 1. Se o usuário NÃO tem token E está tentando acessar qualquer rota protegida
  if (!token && !isLoginPage) {
    // Redireciona para o login, mantendo a URL original como um parâmetro de 'callback'
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // 2. Se o usuário JÁ TEM um token E está tentando acessar o login
  if (token && isLoginPage) {
    // Mande-o direto para o dashboard
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  // 3. Se o usuário acessar a raiz, redireciona para o dashboard.
  // A regra #1 cuidará de enviá-lo para /login se ele não tiver token.
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Se nenhuma regra de redirecionamento foi acionada, continue para a página solicitada.
  return NextResponse.next();
}

export const config = {
  // Execute o middleware em todas as rotas, exceto arquivos estáticos
  // e rotas internas da Next.js.
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
