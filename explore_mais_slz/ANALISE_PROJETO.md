# Análise técnica e melhorias — Explore+ SLZ

## Estrutura e funcionalidades

O projeto usa Flask como servidor da API e dos arquivos estáticos. O frontend é HTML, CSS e JavaScript sem etapa de build. SQLite é acessado diretamente com consultas parametrizadas; não há ORM nem framework de frontend.

| Arquivo | Responsabilidade |
| --- | --- |
| `backend/app.py` | Inicialização do catálogo, conexões SQLite, sessão, CSRF, autenticação e APIs |
| `frontend/index.html`, `style.css` | Página inicial, identidade visual, formulário de viagem, pesquisa e mapa |
| `frontend/script.js` | Leaflet/OpenStreetMap, filtros, pesquisa, geração e compartilhamento de roteiro, login/cadastro e favoritos |
| `frontend/account.js` | Sessão, chamadas HTTP, token CSRF e preferências de leitura |
| `frontend/painel.html`, `painel.css`, `painel.js` | Perfil, histórico, favoritos, roteiros salvos e acessibilidade |
| `test_api.py` | Testes de regressão do backend com SQLite temporário |
| `test_browser.py` | Teste opcional dos fluxos reais no Chrome, com Playwright e SQLite temporário |
| `INICIAR_WINDOWS.bat` | Criação do ambiente, instalação do Flask e inicialização local |

**Páginas existentes:** `/`, `/explorar`, `/planejar`, `/perfil`, `/historico`, `/favoritos`, `/meus-roteiros` e `/acessibilidade`. As páginas de conta compartilham a mesma estrutura e carregam dados conforme o endereço.

**Funcionalidades existentes:** cadastro e login reais; senhas com hash Werkzeug; logout; edição de nome e interesses; catálogo inicial de 14 destinos em quatro municípios; pesquisa SQL; mapa e filtros; geração determinística de roteiro conforme região e interesses; estimativa de divisão do orçamento; experiência especial de Raposa; cópia e compartilhamento no WhatsApp; favoritos por conta; histórico de pesquisas, favoritos e roteiros; salvamento, consulta e exclusão de roteiros; avaliações de 1 a 5 via API; ajustes de leitura.

As APIs principais são `/api/health`, `/api/destinos`, `/api/destinos/verificar`, `/api/roteiro`, `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`, `/api/perfil`, `/api/historico`, `/api/favoritos`, `/api/roteiros-salvos`, `/api/avaliacoes/<id>` e `/api/resumo`.

## Banco SQLite

O banco padrão é `backend/explore_slz.db`, criado automaticamente. Não havia banco versionado na pasta recebida. A análise do esquema e os testes foram realizados com bases criadas pelo próprio aplicativo. `EXPLORE_DATABASE_PATH` permite selecionar outra base, especialmente para testes.

| Tabela | Dados e relações |
| --- | --- |
| `destinos` | Nome único, município, descrição, ícone, interesses JSON e coordenadas |
| `usuarios` | Nome, e-mail único sem distinção de caixa, hash da senha, interesses JSON e criação |
| `historico` | Atividades associadas ao usuário, tipo, descrição e destino opcional |
| `favoritos` | Relação usuário/destino, com chave primária composta que impede duplicações |
| `roteiros_salvos` | Título, conteúdo JSON e criação, associados ao usuário |
| `avaliacoes` | Nota, comentário e data; uma avaliação por usuário/destino |

Há índices de usuário/data no histórico e nos roteiros. As leituras de histórico e roteiros retornam até 100 registros. Os contadores consideram todos os registros. As datas produzidas pelo SQLite são UTC e agora são apresentadas no horário local do navegador.

## Problemas corrigidos

- Perfil com apenas contadores e formulário: agora contém identidade do usuário, iniciais, acesso ao planejador, prévias reais de favoritos, roteiros com detalhes e linha de atividades, além da edição de dados. As páginas completas e suas ações foram preservadas.
- Ausência de fechamento explícito de conexões SQLite: o contexto anterior cuidava da transação, mas não fechava a conexão. Agora há fechamento em `finally`, inclusive em caso de erro.
- Chaves estrangeiras declaradas, mas desativadas nas conexões SQLite: `PRAGMA foreign_keys = ON` passou a ser aplicado em cada conexão.
- JSON com lista/texto/null podia provocar erro interno em endpoints que esperavam objeto: agora retorna erro JSON 400.
- Orçamentos não finitos e acessibilidade com formato incorreto eram aceitos pelo gerador: agora são rejeitados.
- Roteiros com dias/paradas malformados podiam quebrar a renderização: a API valida a estrutura e a interface tolera registros antigos incompletos.
- Repetir a inclusão do mesmo favorito duplicava atividades: o histórico é registrado somente quando há inserção efetiva.
- O cartão visual “Raposa” não correspondia ao nome de nenhum destino do banco: foi vinculado a “Passeios de barco”, preservando a apresentação.
- Favoritos levavam a uma lista genérica: agora o link preenche a pesquisa e destaca o destino no mapa quando o Leaflet está disponível.
- Falha na consulta da sessão deixava o painel carregando indefinidamente: agora há mensagem e nova tentativa. Falhas de coleções na visão geral são tratadas individualmente.
- Exclusões e logout sem tratamento de erros: agora apresentam mensagens; ações pendentes bloqueiam repetição no painel.
- Estado de visitante sem acesso direto ao login: há um link que abre o formulário na página inicial.
- Datas brutas, ausência de indicação da página ativa e limitações em telas pequenas: adicionados formatação local, `aria-current`, controles expansíveis, foco visível, atalho para o conteúdo, layouts responsivos e respeito à redução de movimento.
- README descrevia autenticação como demonstração e dados como locais do navegador: documentação atualizada para refletir o código.
- O orçamento combinava mínimo 1 e passo 50, fazendo a validação nativa rejeitar valores comuns como 500 e 800. O campo agora permite centavos com passo 0,01.

## Limitações e possíveis evoluções

- O gerador utiliza o catálogo e regras locais; não é IA, não calcula trajetos e pode repetir locais em viagens longas. Orçamento é dividido matematicamente, sem cotação ou filtragem por preço.
- Preferências de acessibilidade são incluídas no resumo; o catálogo não possui atributos para garantir locais acessíveis. Preferências de interesses do perfil são armazenadas, mas não preenchem automaticamente o planejador.
- Avaliações estão disponíveis pela API, sem interface de publicação/leitura no frontend. Não há upload de avatar, recuperação de senha nem administração.
- A busca SQLite `LIKE ... COLLATE NOCASE` não oferece normalização completa de acentos ou caixa Unicode; pesquisar versões sem acento pode omitir resultados.
- A pesquisa durante a digitação registra termos intermediários no histórico após o intervalo de 250 ms; o histórico representa eventos de consulta, não visitas presenciais nem viagens concluídas.
- A pesquisa pública pode registrar atividades por GET quando há sessão. Uma evolução é separar a consulta da gravação explícita da atividade.
- Fontes, Leaflet, mapas e compartilhamento externo dependem de conexão. O aplicativo oferece mensagem quando o mapa não carrega.
- As listas completas de histórico e roteiros têm limite de 100, sem paginação. Não há exclusão de conta; adicionar essa função exigiria definir a política das relações e dos dados relacionados.
- Sem `EXPLORE_SECRET_KEY`, reiniciar o servidor invalida sessões. O modo direto de execução usa o servidor de desenvolvimento com debug. Publicação exigiria configuração própria, limitação de tentativas de autenticação e gestão de backups.

## Verificação

A suíte original de saúde da API, pesquisa e geração de roteiro foi mantida como regressão e ampliada para oito testes, incluindo páginas/arquivos, autenticação, edição persistente, CSRF/origem, favoritos idempotentes, histórico, roteiros, isolamento entre contas, entradas inválidas, avaliações e integridade SQLite. Não usa nem altera dados de usuários no banco padrão.

O teste opcional de navegador cobre cadastro pela interface, estados vazios, edição e persistência, favoritos incluindo Raposa, geração/salvamento e expansão de roteiro, exclusões, limpeza do histórico, saída, falha/recuperação de sessão, contraste e tamanhos de tela. Capturas são gravadas em `.artifacts/` e ignoradas pelo Git.

Resultado da execução: **8 testes da API aprovados**; fluxo completo no Chrome aprovado, sem erros JavaScript, com larguras de **1440, 768, 390 e 320 pixels**. Também foram verificados alto contraste, texto a 110%, persistência após recarregar e escape de conteúdo HTML no nome. A revisão visual incluiu perfil vazio, perfil preenchido em desktop/celular e alto contraste. O CDN do Leaflet foi bloqueado nesse teste para verificar o funcionamento sem o mapa externo; carregamento de tiles e serviços externos não foi validado.

> A ampliação posterior, com catálogo enriquecido, perfil personalizável, amigos e vouchers simbólicos, está documentada em [RELATORIO_EXPANSAO_2.md](RELATORIO_EXPANSAO_2.md). Esta análise registra o estado anterior à expansão.
