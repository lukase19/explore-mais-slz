# Explore+ SLZ — Flask, JavaScript e SQLite

Aplicativo local para explorar destinos da Ilha de São Luís, planejar viagens e organizar histórico, favoritos e roteiros por conta. A página inicial e sua identidade visual foram preservadas.

## Executar no Windows

Requer Python 3.10 ou superior. Abra esta pasta e dê dois cliques em `INICIAR_WINDOWS.bat`, ou execute:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app
```

Abra **http://127.0.0.1:5000**. O Flask serve a página e a API no mesmo endereço. Não abra o HTML diretamente nem use o Live Server. Para encerrar, pressione Ctrl+C no terminal. A primeira instalação das dependências requer internet.

## Estrutura

```text
explore_mais_slz/
├── backend/
│   ├── app.py              # Flask, SQLite, sessão e APIs
│   ├── __init__.py
│   └── explore_slz.db       # Criado automaticamente; ignorado pelo Git
├── frontend/
│   ├── index.html          # Página inicial e formulário de login/cadastro
│   ├── style.css           # Identidade visual original
│   ├── script.js           # Mapa, pesquisa, favoritos e planejador
│   ├── account.js          # Sessão, CSRF e preferências de leitura
│   ├── painel.html         # Estrutura das páginas de conta
│   ├── painel.css          # Perfil e layout responsivo
│   └── painel.js           # Coleções, edição e ações do perfil
├── test_api.py             # Regressões da API com SQLite temporário
├── test_browser.py         # Teste opcional com Chrome/Playwright
├── requirements.txt        # Dependências para executar o aplicativo
└── ANALISE_PROJETO.md      # Arquitetura, banco, correções e limitações
```

## Funcionalidades

- Cadastro, login e logout reais, com senhas em hash e sessão protegida por token CSRF nas alterações autenticadas.
- Pesquisa SQL de destinos, filtros e mapa Leaflet/OpenStreetMap.
- Geração de roteiro baseada no catálogo local, interesses, duração e orçamento; cópia e compartilhamento pelo WhatsApp.
- Histórico, favoritos e roteiros salvos no SQLite, vinculados ao usuário autenticado.
- Perfil com iniciais, contadores, prévias das coleções, detalhes de roteiros e edição de nome/interesses.
- Páginas completas de histórico, favoritos, roteiros salvos e acessibilidade; remoção de favoritos, exclusão de roteiros e limpeza do histórico.
- Avaliações de destinos pela API e nas fichas; ajustes de texto e contraste armazenados no navegador.

## Páginas e APIs

Páginas: `/`, `/explorar`, `/planejar`, `/perfil`, `/historico`, `/favoritos`, `/meus-roteiros` e `/acessibilidade`.

APIs: `/api/health`, `/api/destinos`, `/api/destinos/verificar`, `/api/roteiro`, `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`, `/api/perfil`, `/api/historico`, `/api/favoritos`, `/api/roteiros-salvos`, `/api/avaliacoes/<id>` e `/api/resumo`. Consulte as rotas em `backend/app.py` para os métodos HTTP e formatos.

## Testes

A partir desta pasta, com as dependências instaladas:

```powershell
python -m unittest -v test_api
```

A suíte conserva as verificações originais e testa autenticação, CSRF, perfil, favoritos, histórico, roteiros, isolamento entre contas, avaliações e integridade SQLite. Ela cria um banco temporário e não altera o banco usado pelo aplicativo. `python test_api.py` também executa a suíte.

Para testar os fluxos da interface no Chrome instalado, opcionalmente:

```powershell
python -m pip install playwright
python test_browser.py
```

Esse teste inicia e encerra seu próprio servidor, usa SQLite temporário e gera capturas em `.artifacts/`. Não é necessário baixar outro navegador. Playwright é opcional; Flask e Pillow são as dependências para executar o aplicativo.

## Configuração e limites

O banco padrão é `backend/explore_slz.db`. Para usar outro arquivo, defina `EXPLORE_DATABASE_PATH` antes de iniciar. Configure `EXPLORE_SECRET_KEY` com uma chave persistente para manter sessões entre reinicializações e `EXPLORE_HTTPS=1` ao servir por HTTPS.

Os 14 registros iniciais foram preservados. A expansão documenta 69 referências reais, totalizando 76 registros após considerar os nomes já existentes. Dados incompletos continuam em revisão. O gerador usa regras locais, sem IA, cotações em tempo real ou cálculo de trajetos. Confirme horários, preços e acessibilidade antes de visitar. Fontes e mapas externos dependem de internet.

O servidor iniciado diretamente é de desenvolvimento, com debug. Para a arquitetura preparada de publicação com GitHub, Vercel e Flask em disco persistente, siga [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md). A publicação depende de configurar o servidor de origem e transferir os dados com autorização.

A análise completa está em [ANALISE_PROJETO.md](ANALISE_PROJETO.md).
## Expansão 2 — cultura, acessibilidade e encontros

Consulte [RELATORIO_EXPANSAO_2.md](RELATORIO_EXPANSAO_2.md) para os recursos atuais, migrações, APIs e pendências. Essa expansão preserva a arquitetura Flask + SQLite + JavaScript e foi implementada nesta mesma pasta.

- Menu compacto compartilhado, perfil com foto/capa e configurações privadas.
- Catálogo com 69 referências documentadas em cinco municípios; coordenadas e informações ainda não verificadas ficam identificadas como pendentes.
- Cultura ludovicense e cinco seleções temáticas no planejador.
- Acessibilidade por recurso, com três estados; sugestões passam por moderação local.
- Amizades, bloqueios, convites de roteiros, contribuições e links públicos revogáveis.
- Vouchers simbólicos, sem pagamento, desconto, ingresso ou reserva.

Instale novamente as dependências para habilitar o processamento seguro de imagens:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m backend.app
```

O arquivo `INICIAR_WINDOWS.bat` também instala os requisitos. Pillow é usado exclusivamente para validar e recodificar imagens.

Ao iniciar, o aplicativo acrescenta campos e tabelas com uma migração incremental. O esquema anterior fica em `backend/backups/schema_before_v2_*.sql`. A cópia contém apenas o esquema, não os registros pessoais; faça também seus backups regulares do arquivo SQLite. O catálogo não substitui descrições, IDs, coordenadas ou correções manuais existentes.

Testes completos de API:

```powershell
.venv\Scripts\python.exe -m unittest discover -v
```

Testes opcionais com Chrome e Playwright:

```powershell
.venv\Scripts\python.exe -m pip install playwright
.venv\Scripts\python.exe test_browser.py
.venv\Scripts\python.exe browser_expansion.py
```

Ambas as verificações de navegador usam bases temporárias, encerram seus servidores e geram imagens em `.artifacts/`. Nenhum usuário demonstrativo é criado no banco normal.

### Moderação de acessibilidade

A administração é feita localmente por quem tem acesso ao arquivo SQLite. Nenhuma sugestão de usuário é publicada automaticamente.

```powershell
.venv\Scripts\python.exe -m backend.moderate_accessibility list
.venv\Scripts\python.exe -m backend.moderate_accessibility approve 1 --source https://fonte-oficial.example --date 2026-11-06 --reviewer Nome
.venv\Scripts\python.exe -m backend.moderate_accessibility reject 2
```

O endereço acima é apenas um exemplo de sintaxe. Antes de aprovar, substitua-o por uma evidência real verificada. Não há diagnóstico médico no cadastro nem nas preferências.

## Correções de integração e UX

A versão atual está descrita em [RELATORIO_CORRECOES.md](RELATORIO_CORRECOES.md). Cultura foi integrada ao catálogo e às fichas; a URL antiga redireciona para a exploração. O mapa e a lista compartilham filtros, possuem agrupamento local e distinguem coordenadas verificadas de referências legadas. O banco normal ainda tem 76 destinos, 14 pares de coordenadas válidos numericamente e nenhum classificado como verificado; não foram inventadas localizações.

Os temas usam tokens centrais em `frontend/themes.css`. Foto e capa mostram estados persistentes de seleção, envio, sucesso e erro. Para reproduzir a verificação dessas correções:

```powershell
.venv\Scripts\python.exe -m unittest discover -v
.venv\Scripts\python.exe test_browser.py
.venv\Scripts\python.exe browser_expansion.py
.venv\Scripts\python.exe browser_corrections.py
```

Os testes usam bases temporárias. Leaflet e o agrupador são servidos pelos arquivos locais em `frontend/vendor/`; só o mapa de fundo necessita do serviço externo.
