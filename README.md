══════════════════════════════════════════════════════════

                  STATICFORGE - MANUAL DE USO

══════════════════════════════════════════════════════════

Bem-vindo ao StaticForge!

Este programa permite criar sites estáticos (super rápidos e seguros) 
com interface gráfica simples, sem precisar saber programação avançada.

Perfeito para blogs pessoais, portfolios, sites de poemas, receitas, 
landing pages ou qualquer projeto simples que você queira colocar online.

Recursos principais:
- Criar Posts e Páginas fixas
- Adicionar imagens, tags e categorias
- Busca completa no site gerado
- Tema escuro automático
- Publicação automática no GitHub Pages (site grátis!)

══════════════════════════════════════════════════════════
REQUISITOS
══════════════════════════════════════════════════════════

- Windows 7 ou superior
- Git instalado (necessário apenas para publicar no GitHub)
  Baixe aqui: https://git-scm.com/download/win
  (Durante a instalação, marque a opção para adicionar ao PATH)

══════════════════════════════════════════════════════════
COMO USAR
══════════════════════════════════════════════════════════

1. Execute o arquivo "StaticForge.exe"

2. Crie seu conteúdo:
   - Clique em "➕ Novo Post" para criar artigos do blog
   - Clique em "📄 Nova Página" para páginas fixas (ex: Sobre, Contato)

   Preencha:
   - Título
   - Descrição (opcional)
   - Categoria (ex: poemas, receitas)
   - Tags (separadas por vírgula, ex: amor, natureza, 2025)
   - Conteúdo (pode usar HTML simples, como <b>negrito</b> ou <i>itálico</i>)
   - Adicione imagens clicando em "Adicionar Imagens"

3. Publique o conteúdo:
   - Selecione o post/página na lista
   - Clique em "🚀 Publicar"

4. Gere o site:
   - Clique no botão verde "🌐 Gerar Site"
   - Escolha:
     • "Sim" → Gera e publica automaticamente no GitHub (recomendado)
     • "Não" → Gera apenas localmente (pasta "site" será criada)

══════════════════════════════════════════════════════════
PUBLICAR NO GITHUB PAGES (SITE GRÁTIS NA INTERNET)
══════════════════════════════════════════════════════════

1. Crie uma conta gratuita no GitHub: https://github.com

2. Crie um novo repositório (público):
   - Nome exemplo: meu-site-magico
   - NÃO marque "Initialize with README"
   - Crie o repositório

3. Ative o GitHub Pages:
   - Vá em Settings → Pages
   - Source: branch "main" e pasta "/ (root)"
   - Salve

4. Gere um Personal Access Token:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Crie um token com permissão "repo"
   - Copie o token (não aparece mais depois!)

5. No StaticForge:
   - Clique em "⚙️ Configurações"
   - Aba "GitHub"
   - URL do repositório: https://github.com/SEU_USUARIO/meu-site-magico.git
   - Personal Access Token: cole o token gerado
   - Branch: main
   - Clique em "Testar Conexão GitHub"
   - Salve

6. Agora é só clicar em "Gerar Site" e escolher "Sim" → seu site fica no ar em:
   https://SEU_USUARIO.github.io/meu-site-magico/

══════════════════════════════════════════════════════════
EXEMPLO REAL
══════════════════════════════════════════════════════════

Site de poemas criado com StaticForge:
https://mestre-pogramador-ai.github.io/poemasmagico/

══════════════════════════════════════════════════════════
DICAS
══════════════════════════════════════════════════════════

- O site gerado é 100% estático → super rápido e seguro
- Você pode hospedar em qualquer lugar: GitHub Pages, Netlify, Vercel...
- Para editar o site depois, basta abrir o StaticForge novamente e gerar de novo
- Sempre faça backup da pasta do projeto (onde está o .exe e os arquivos .json)

══════════════════════════════════════════════════════════
PROBLEMAS COMUNS
══════════════════════════════════════════════════════════

- Erro "Git não encontrado"? → Instale o Git (link acima)
- Erro no push? → Verifique o token e se o repositório existe
- Site não atualiza? → Espere 1 minuto (GitHub Pages demora um pouco)

══════════════════════════════════════════════════════════
FEITO COM ❤️ POR UM DESENVOLVEDOR APAIXONADO

Se gostou, compartilhe com os amigos!
Dúvidas? Entre em contato ou deixe um comentário.

Versão: Dezembro 2025
Site exemplo: https://mestre-pogramador-ai.github.io/poemasmagico/
