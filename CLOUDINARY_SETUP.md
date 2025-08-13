# Configuração do Cloudinary para Armazenamento de Imagens

## 🎯 Problema Resolvido

O sistema estava perdendo as fotos enviadas via WhatsApp a cada deploy no Render porque:
- O diretório `uploads/` está no `.gitignore` (correto para não versionar dados de usuários)
- O Render é um ambiente efêmero - arquivos locais são perdidos a cada deploy
- As imagens ficavam inacessíveis, causando erro 404

## ✅ Solução Implementada

Migração para **Cloudinary** - serviço de armazenamento de imagens em nuvem:
- ✅ Armazenamento persistente e confiável
- ✅ CDN global para carregamento rápido
- ✅ Otimização automática de imagens
- ✅ Plano gratuito generoso (25 GB de armazenamento, 25 GB de bandwidth)

## 🔧 Arquivos Modificados

### Backend:
- `requirements.txt` - Adicionada dependência `cloudinary`
- `app/services/cloudinary_service.py` - **NOVO** serviço de upload
- `app/routers/webhook_whatsapp.py` - Upload direto para Cloudinary
- `app/crud/foto_promotor.py` - Deleção via Cloudinary
- `app/main.py` - Removido mount de arquivos estáticos para fotos
- `start.sh` - Mantido para criar diretórios (contratos ainda usam local)

### Frontend:
- `next.config.ts` - Adicionado `res.cloudinary.com` aos domínios permitidos

## 🚀 Configuração no Render

### 1. Criar Conta no Cloudinary
1. Acesse [cloudinary.com](https://cloudinary.com)
2. Crie uma conta gratuita
3. No Dashboard, anote:
   - **Cloud Name**
   - **API Key** 
   - **API Secret**

### 2. Configurar Variáveis de Ambiente no Render

No painel do Render, vá em **Environment** e adicione:

```bash
CLOUDINARY_CLOUD_NAME=seu_cloud_name_aqui
CLOUDINARY_API_KEY=sua_api_key_aqui
CLOUDINARY_API_SECRET=seu_api_secret_aqui
```

### 3. Fazer Redeploy

Após configurar as variáveis:
1. Faça commit das mudanças no código
2. Push para o repositório
3. O Render fará o redeploy automaticamente

## 📱 Como Funciona Agora

### Fluxo de Upload (WhatsApp → Cloudinary):
1. Usuário envia foto via WhatsApp
2. Webhook recebe a mídia da Twilio
3. **NOVO**: Upload direto para Cloudinary
4. URL do Cloudinary é salva no banco de dados
5. Frontend exibe imagem do Cloudinary

### URLs das Imagens:
- **Antes**: `https://mustafa-backend-6ywg.onrender.com/fotos-promotores/arquivo.jpg`
- **Agora**: `https://res.cloudinary.com/seu-cloud-name/image/upload/v1234567890/fotos-promotores/arquivo.jpg`

## 🔍 Verificação

Para verificar se está funcionando:

1. **Teste o webhook**: Envie uma foto via WhatsApp
2. **Verifique os logs**: No Render, veja se aparece "Arquivo enviado para Cloudinary"
3. **Acesse o frontend**: As fotos devem carregar normalmente
4. **Verifique no Cloudinary**: No painel, vá em Media Library → pasta `fotos-promotores`

## 🛠️ Troubleshooting

### Erro: "Cloudinary credentials not found"
- Verifique se as 3 variáveis de ambiente estão configuradas no Render
- Certifique-se que não há espaços extras nos valores

### Erro: "Upload failed"
- Verifique se a API Key e Secret estão corretos
- Confirme se a conta Cloudinary não atingiu o limite do plano gratuito

### Imagens não carregam no frontend
- Verifique se `res.cloudinary.com` está no `next.config.ts`
- Confirme se o redeploy do frontend foi feito após a mudança

## 💡 Benefícios Adicionais

- **Performance**: CDN global do Cloudinary
- **Otimização**: Compressão automática de imagens
- **Escalabilidade**: Suporta milhares de imagens
- **Backup**: Imagens ficam seguras na nuvem
- **Análise**: Dashboard com estatísticas de uso

## 📊 Limites do Plano Gratuito

- **Armazenamento**: 25 GB
- **Bandwidth**: 25 GB/mês
- **Transformações**: 25.000/mês
- **Requests**: 1.000.000/mês

*Mais que suficiente para a maioria dos casos de uso!*