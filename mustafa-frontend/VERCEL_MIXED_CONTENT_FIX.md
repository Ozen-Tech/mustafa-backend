# Correção do Erro Mixed Content no Vercel

## Problema
O erro "Mixed Content" ocorre quando uma página HTTPS tenta fazer requisições HTTP, o que é bloqueado pelos navegadores por questões de segurança.

## Soluções Implementadas

### 1. Atualização do vercel.json
- Adicionado header `Content-Security-Policy: upgrade-insecure-requests`
- Configuração explícita das variáveis de ambiente
- Runtime Node.js 18.x especificado

### 2. Verificação Manual no Dashboard do Vercel

**IMPORTANTE**: Siga estes passos para garantir que as configurações estejam corretas:

1. **Acesse o Dashboard do Vercel**
   - Vá para https://vercel.com/dashboard
   - Selecione o projeto `mustafa-system`

2. **Verifique as Variáveis de Ambiente**
   - Clique na aba "Settings"
   - Vá para "Environment Variables"
   - Procure por `NEXT_PUBLIC_API_URL`

3. **Corrija se Necessário**
   - Se a variável estiver definida como `http://mustafa-backend-6ywg.onrender.com`
   - **ALTERE PARA**: `https://mustafa-backend-6ywg.onrender.com`
   - Salve as alterações

4. **Force um Novo Deploy**
   - Vá para a aba "Deployments"
   - Clique nos três pontos do último deploy
   - Selecione "Redeploy"
   - Marque "Use existing Build Cache" como **DESMARCADO**
   - Clique em "Redeploy"

### 3. Verificação Local

Para desenvolvimento local, mantenha:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Para produção, deve ser:
```bash
# Vercel (automático via vercel.json)
NEXT_PUBLIC_API_URL=https://mustafa-backend-6ywg.onrender.com
```

## Teste da Correção

Após o redeploy:
1. Acesse https://mustafa-system.vercel.app/dashboard/promotores
2. Tente criar uma conta
3. O erro Mixed Content não deve mais aparecer

## Troubleshooting

Se o problema persistir:
1. Verifique o console do navegador (F12)
2. Confirme se todas as requisições estão usando HTTPS
3. Limpe o cache do navegador (Ctrl+Shift+R)
4. Aguarde alguns minutos para propagação do CDN do Vercel