# 🏪 Atlas Toldos — Sistema de Gestão de Clientes

Sistema completo para cadastro, gestão de clientes e orçamentos, com login por usuário e deploy na nuvem.

---

## 🔐 Login Padrão (ADM)

```
E-mail: admin@atlastoldos.com
Senha:  atlas2024
```

> **Troque a senha do admin assim que entrar!** Vá em Usuários → editar o Administrador.

---

## 👥 Sistema de Usuários

| Perfil | Acesso |
|--------|--------|
| **admin** | Tudo — inclui criar/editar usuários e configurações |
| **vendedor** | Dashboard, clientes, ligações e orçamentos |

O administrador pode criar quantos usuários quiser em **Usuários** na barra lateral.

---

## ✅ Funcionalidades

- **Login individual** por e-mail e senha
- **Perfis: admin e vendedor** com acesso diferenciado
- **Cadastro completo de clientes**
- **Ligações de recompra automáticas** (configurável, padrão: 3 anos)
- **Orçamentos para visitas** — tipo, dimensões, cores, mecanismo, valor
- **Dashboard** com métricas e próximas ligações
- **Sincronização com nuvem** via Supabase (gratuito)

---

## 🚀 Como Usar no PC (Windows)

1. Instale o Python em [python.org/downloads](https://python.org/downloads) — marque **"Add Python to PATH"**
2. Extraia esta pasta em qualquer lugar (ex: `C:\atlas-toldos`)
3. Clique duplo em **INICIAR.bat**
4. O navegador abrirá em `http://localhost:5000`

---

## ☁️ Como Colocar Online (Render.com — Gratuito)

### Passo 1 — Criar conta no GitHub
- Acesse [github.com](https://github.com) e crie uma conta gratuita

### Passo 2 — Criar repositório
1. Clique em **"New repository"**
2. Nome: `atlas-toldos`
3. Marque **Private** (privado)
4. Clique em **"Create repository"**

### Passo 3 — Fazer upload dos arquivos
1. Na página do repositório criado, clique **"uploading an existing file"**
2. Arraste todos os arquivos desta pasta (exceto o `.bat`)
3. Mantenha a estrutura:
   ```
   atlas-toldos/
   ├── server.py
   ├── requirements.txt
   ├── render.yaml
   └── public/
       └── index.html
   ```
4. Clique **"Commit changes"**

### Passo 4 — Conectar ao Render
1. Acesse [render.com](https://render.com) e crie conta (use o GitHub para entrar)
2. Clique **"New +"** → **"Web Service"**
3. Conecte seu repositório `atlas-toldos`
4. O Render vai detectar o `render.yaml` automaticamente
5. Clique **"Create Web Service"**
6. Aguarde ~3 minutos — o sistema estará no ar!

### Passo 5 — Acessar
- Sua URL será algo como: `https://atlas-toldos.onrender.com`
- Use o login padrão para entrar

> ⚠️ **Importante:** No plano gratuito do Render, o serviço "dorme" após 15min sem uso e demora ~30s para acordar. Para uso contínuo, considere o plano pago ($7/mês).

---

## 📁 Estrutura de Arquivos

```
atlas-toldos/
├── INICIAR.bat          ← Para usar no PC (Windows)
├── server.py            ← Servidor da aplicação (Python/Flask)
├── requirements.txt     ← Dependências Python
├── render.yaml          ← Configuração do Render
├── atlas_toldos.db      ← Banco de dados local (criado automaticamente)
├── README.md            ← Este arquivo
└── public/
    └── index.html       ← Interface do sistema
```

---

## 💡 Dicas

- **Cor vermelha** na data de ligação = ligação atrasada
- **Cor laranja** = ligação nos próximos 60 dias
- **Cor dourada** = ligação futura normal
- Use **Observações do Orçamento** para instruções ao vendedor
- Faça backup do arquivo `atlas_toldos.db` regularmente (é o banco de dados)

---

Desenvolvido para Atlas Toldos 🏪
