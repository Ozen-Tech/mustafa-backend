# 🧪 Guia de Teste do Cloudinary

## 📋 Situação Atual

**Problema identificado:** As fotos estão sendo perdidas porque o Cloudinary não está configurado corretamente no ambiente de produção.

### 📊 Estatísticas do Banco de Produção:
- **Total de fotos:** 1.661
- **URLs do Cloudinary:** 156 fotos (funcionais)
- **URLs locais:** 1.505 fotos (❌ perdidas)

## 🔧 Como Testar Localmente

### 1. Verificar Configuração Local
```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('CLOUD_NAME:', os.getenv('CLOUDINARY_CLOUD_NAME')); print('API_KEY:', os.getenv('CLOUDINARY_API_KEY')); print('SECRET configurado:', bool(os.getenv('CLOUDINARY_API_SECRET')))"
```

### 2. Executar Teste Automatizado
```bash
python test_cloudinary.py
```

### 3. Teste Manual via WhatsApp
1. Envie uma foto via WhatsApp para o sistema
2. Verifique se a URL salva no banco começa com `https://res.cloudinary.com/`
3. Acesse a URL para confirmar que a imagem está acessível

## 🚀 Configuração no Render (PRODUÇÃO)

### ⚠️ URGENTE: Configure as variáveis no Render

1. **Acesse o Dashboard do Render:**
   - Vá para: https://dashboard.render.com
   - Selecione seu serviço backend

2. **Configure as Variáveis de Ambiente:**
   - Clique em "Environment" no menu lateral
   - Adicione as seguintes variáveis:

   ```
   CLOUDINARY_CLOUD_NAME=duk91uunh
   CLOUDINARY_API_KEY=976370319645262
   CLOUDINARY_API_SECRET=g1D7j5N0VJzlCE3uiAW_Bo38PR_s
   ```

3. **Redeploy do Serviço:**
   - Clique em "Manual Deploy" > "Deploy latest commit"
   - Aguarde o deploy finalizar

## 🧪 Como Testar Após Deploy

### 1. Teste via API
```bash
# Substitua YOUR_PRODUCTION_URL pela URL do seu backend
curl -X POST "YOUR_PRODUCTION_URL/test-cloudinary" \
  -H "Content-Type: application/json"
```

### 2. Teste via WhatsApp
1. Envie uma nova foto via WhatsApp
2. Verifique no banco se a URL começa com `https://res.cloudinary.com/duk91uunh/`

### 3. Verificar no Banco de Produção
```python
# Execute este comando para verificar as últimas fotos
import psycopg2
conn = psycopg2.connect('postgresql://mustafa_postgres_user:QxeSnBvaMTDhKKX106LX9whiau27pgfM@dpg-d20psdemcj7s73e18tag-a.oregon-postgres.render.com/mustafa_postgres')
cur = conn.cursor()
cur.execute("SELECT url_foto FROM fotos_promotores ORDER BY data_envio DESC LIMIT 5")
for url in cur.fetchall():
    print(url[0])
conn.close()
```

## ✅ Sinais de Sucesso

- ✅ URLs das novas fotos começam com `https://res.cloudinary.com/duk91uunh/`
- ✅ As fotos são acessíveis via browser
- ✅ Não há mais URLs com `/fotos-promotores/` nas novas fotos
- ✅ O teste automatizado passa sem erros

## 🚨 Troubleshooting

### Erro: "Unknown API key"
- Verifique se a API key está correta no Render
- Confirme que não há espaços extras nas variáveis

### Erro: "Invalid Signature"
- Verifique se o API Secret está correto
- Confirme que todas as 3 variáveis estão configuradas

### Fotos ainda salvando localmente
- Confirme que o redeploy foi feito após configurar as variáveis
- Verifique os logs do servidor para erros do Cloudinary

## 📞 Próximos Passos

1. **Configure as variáveis no Render** (mais importante)
2. **Faça o redeploy**
3. **Teste com uma nova foto via WhatsApp**
4. **Monitore as próximas fotos para confirmar que estão sendo salvas no Cloudinary**

---

**Nota:** As 1.505 fotos já perdidas não podem ser recuperadas, mas todas as novas fotos serão salvas corretamente no Cloudinary após a configuração.