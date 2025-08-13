# Instruções de Deploy no Vercel

## Problema das Fotos não Carregando (Erro 404)

O problema das fotos não carregarem no sistema em produção está relacionado à configuração das variáveis de ambiente no Vercel.

## Solução

### 1. Configurar Variáveis de Ambiente no Vercel

No painel do Vercel, vá em:
1. **Settings** → **Environment Variables**
2. Adicione a seguinte variável:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://mustafa-backend-6ywg.onrender.com`
   - **Environments**: Marque `Production`, `Preview` e `Development`

### 2. Arquivos Criados/Modificados

- ✅ `.env.production` - Configuração para produção
- ✅ `vercel.json` - Configuração específica do Vercel
- ✅ `next.config.ts` - Atualizado para permitir imagens do localhost e Render

### 3. Fazer Redeploy

Após configurar as variáveis de ambiente no Vercel:
1. Faça um novo commit e push
2. Ou force um redeploy no painel do Vercel

### 4. Verificar se Funcionou

Após o deploy, as URLs das imagens devem apontar para:
`https://mustafa-backend-6ywg.onrender.com/fotos-promotores/[nome-do-arquivo]`

Em vez de:
`http://localhost:8000/fotos-promotores/[nome-do-arquivo]`

## Configurações Técnicas

### next.config.ts
```typescript
images: {
  remotePatterns: [
    {
      protocol: 'https', 
      hostname: 'mustafa-backend-6ywg.onrender.com',
      pathname: '/fotos-promotores/**',
    },
    {
      protocol: 'http',
      hostname: 'localhost',
      port: '8000',
      pathname: '/fotos-promotores/**',
    },
  ],
}
```

### Variáveis de Ambiente
- **Desenvolvimento**: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Produção**: `NEXT_PUBLIC_API_URL=https://mustafa-backend-6ywg.onrender.com`