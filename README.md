# 🏪 Atlas Toldos — Sistema de Gestão de Clientes

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

   ```
   atlas-toldos/
   ├── server.py
   ├── requirements.txt
   ├── render.yaml
   └── public/
       └── index.html
   ```

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
