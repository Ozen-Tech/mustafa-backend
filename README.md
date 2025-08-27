# Sistema Mustafá

## 📋 Descrição

O Sistema Mustafá é uma plataforma completa de gestão de promotores e contratos, desenvolvida para automatizar e otimizar o processo de cadastro, monitoramento e análise de promotores através de integração com WhatsApp e inteligência artificial.

### 🚀 Funcionalidades Principais

- **Gestão de Promotores**: Cadastro, edição e visualização de promotores com fotos via WhatsApp
- **Gestão de Contratos**: Upload, visualização e organização de contratos em PDF
- **Integração WhatsApp**: Recebimento automático de fotos via webhook do Twilio
- **Análise com IA**: Insights inteligentes sobre promotores usando Google Gemini
- **Dashboard Interativo**: Interface moderna e responsiva para visualização de dados
- **Autenticação Segura**: Sistema de login com JWT tokens
- **Upload de Arquivos**: Suporte para fotos e documentos PDF

### 🛠️ Tecnologias Utilizadas

**Backend:**
- Python 3.11+
- FastAPI (Framework web)
- SQLAlchemy (ORM)
- PostgreSQL (Banco de dados)
- Twilio (Integração WhatsApp)
- Google Gemini AI (Análise inteligente)
- JWT (Autenticação)
- Uvicorn (Servidor ASGI)

**Frontend:**
- Next.js 14+ (React Framework)
- TypeScript
- Tailwind CSS
- Axios (Cliente HTTP)
- js-cookie (Gerenciamento de cookies)

**Infraestrutura:**
- Docker & Docker Compose
- Render (Deploy backend)
- Vercel (Deploy frontend)

## 📋 Pré-requisitos

### Software Necessário

- **Node.js**: versão 18.x ou superior
- **Python**: versão 3.11 ou superior
- **PostgreSQL**: versão 15 ou superior
- **Docker**: versão 20.x ou superior (opcional)
- **Git**: para controle de versão

### Contas e Serviços Externos

- Conta no [Twilio](https://www.twilio.com/) para integração WhatsApp
- Chave da API do [Google Gemini](https://ai.google.dev/)
- Conta no [Render](https://render.com/) para deploy do backend
- Conta no [Vercel](https://vercel.com/) para deploy do frontend

## 🚀 Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/mustafa-backend.git
cd mustafa-backend
```

### 2. Configuração do Backend

#### 2.1. Instale as Dependências Python

```bash
cd backend
pip install -r requirements.txt
```

#### 2.2. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/mustafa_db

# Segurança
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Usuário Administrador
SUPERUSER_EMAIL=admin@mustafa.com
SUPERUSER_PASSWORD=senha_admin_segura

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=seu_account_sid_twilio
TWILIO_AUTH_TOKEN=seu_auth_token_twilio

# Google Gemini AI
GOOGLE_API_KEY=sua_chave_api_google_gemini
```

#### 2.3. Configure o Banco de Dados

```bash
# Criar banco PostgreSQL
createdb mustafa_db

# Executar migrações
python -m app.prestart
python -m app.create_superuser
```

### 3. Configuração do Frontend

#### 3.1. Instale as Dependências Node.js

```bash
cd mustafa-frontend
npm install
```

#### 3.2. Configure as Variáveis de Ambiente

Crie um arquivo `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Executar com Docker (Alternativa)

```bash
# Na raiz do projeto
docker-compose up -d
```

## 💻 Uso

### Desenvolvimento Local

#### 1. Iniciar o Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

#### 2. Iniciar o Frontend

```bash
cd mustafa-frontend
npm run dev
```

O frontend estará disponível em: `http://localhost:3000`

### Acesso ao Sistema

1. **Login**: Acesse `http://localhost:3000/login`
2. **Credenciais padrão**:
   - Email: `admin@mustafa.com`
   - Senha: conforme definido no `.env`

### Funcionalidades Principais

#### Gestão de Promotores
- Acesse **Dashboard > Promotores**
- Visualize, edite e gerencie promotores
- Fotos são recebidas automaticamente via WhatsApp

#### Gestão de Contratos
- Acesse o modal de contratos através dos promotores
- Faça upload de arquivos PDF
- Visualize contratos existentes

#### Análise com IA
- Acesse **Dashboard > Insights**
- Visualize análises inteligentes dos dados
- Obtenha relatórios automatizados

### API Endpoints

#### Autenticação
```bash
POST /auth/login          # Login do usuário
GET  /auth/me             # Dados do usuário logado
```

#### Promotores
```bash
GET    /promotores        # Listar promotores
POST   /promotores        # Criar promotor
PUT    /promotores/{id}   # Atualizar promotor
DELETE /promotores/{id}   # Deletar promotor
```

#### Contratos
```bash
GET  /contratos           # Listar contratos
POST /contratos/upload    # Upload de contrato
```

## 🤝 Contribuição

### Diretrizes para Contribuidores

1. **Fork** o repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um **Pull Request**

### Padrões de Código

#### Backend (Python)
- Siga o padrão **PEP 8**
- Use **type hints** em todas as funções
- Documente funções complexas
- Mantenha funções com máximo 20 linhas

#### Frontend (TypeScript/React)
- Use **TypeScript** para tipagem estática
- Siga o padrão **ESLint** configurado
- Componentes em **PascalCase**
- Hooks customizados com prefixo **use**

### Processo de Pull Request

1. Certifique-se de que todos os testes passam
2. Atualize a documentação se necessário
3. Descreva claramente as mudanças no PR
4. Aguarde a revisão de código

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Contato

- **Email**: contato@mustafa.com
- **GitHub**: [https://github.com/seu-usuario/mustafa-backend](https://github.com/seu-usuario/mustafa-backend)
- **LinkedIn**: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

## 🗺️ Roadmap

### Versão 2.0 (Q2 2024)
- [ ] Relatórios avançados em PDF
- [ ] Integração com mais plataformas de mensagem
- [ ] Dashboard de analytics em tempo real
- [ ] API mobile para aplicativo nativo

### Versão 2.1 (Q3 2024)
- [ ] Sistema de notificações push
- [ ] Integração com CRM externo
- [ ] Backup automático na nuvem
- [ ] Suporte multi-idiomas

### Versão 3.0 (Q4 2024)
- [ ] Machine Learning para predições
- [ ] Interface de administração avançada
- [ ] API GraphQL
- [ ] Microserviços architecture

## ❓ FAQ

### Problemas Comuns

**Q: Erro "Mixed Content" no Vercel**
```bash
A: Verifique se NEXT_PUBLIC_API_URL usa HTTPS em produção
Confira o arquivo vercel.json para headers de segurança
```

**Q: Backend não conecta com PostgreSQL**
```bash
A: Verifique se o PostgreSQL está rodando
Confirme a DATABASE_URL no arquivo .env
Teste a conexão: psql $DATABASE_URL
```

**Q: WhatsApp não recebe mensagens**
```bash
A: Verifique as credenciais do Twilio
Confirme se o webhook está configurado corretamente
Teste com: curl -X POST sua-url/webhook/whatsapp
```

**Q: Erro de CORS no frontend**
```bash
A: Adicione o domínio frontend nas configurações CORS do backend
Verifique se as URLs estão corretas no .env
```

### Comandos Úteis

```bash
# Resetar banco de dados
python -m app.prestart

# Verificar logs do Docker
docker-compose logs -f

# Rebuild completo
docker-compose down -v && docker-compose up --build

# Executar testes
pytest backend/tests/
npm test --prefix mustafa-frontend
```

### Estrutura do Projeto

```
mustafa-backend/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── core/           # Configurações
│   │   ├── crud/           # Operações de banco
│   │   ├── db/             # Modelos e conexão
│   │   ├── routers/        # Endpoints da API
│   │   ├── schemas/        # Schemas Pydantic
│   │   └── services/       # Lógica de negócio
│   └── requirements.txt    # Dependências Python
├── mustafa-frontend/       # Interface Next.js
│   ├── src/
│   │   ├── app/           # Páginas e layouts
│   │   ├── components/    # Componentes React
│   │   ├── contexts/      # Contextos React
│   │   └── lib/          # Utilitários
│   └── package.json      # Dependências Node.js
├── docker-compose.yml    # Configuração Docker
└── README.md            # Este arquivo
```

---

**Desenvolvido com ❤️ pela equipe Mustafá**