# Relatório da expansão 2 — Explore+ SLZ

## Resultado e escopo

A expansão foi implementada no projeto original, mantendo Flask + SQLite + JavaScript e os recursos anteriores. Não foi criado outro aplicativo, banco substituto ou projeto de frontend. O site continua sendo executado localmente pelo Flask.

O catálogo reúne **69 referências com existência documentada em fontes oficiais**, incluindo sete nomes já presentes nos 14 registros iniciais. O banco passa a ter **76 registros**, dos quais sete registros legados, alguns genéricos, continuam identificados como não verificados. A meta numérica de referências documentadas foi atingida; a verificação completa de todas as fichas permanece pendente. Não foram inventadas coordenadas, fotografias, condições de acesso, horários, preços, avaliações, descontos ou parcerias.

## Funcionalidades entregues

| Módulo | Implementação |
| --- | --- |
| Navegação | Cabeçalho compacto com logotipo, avatar e três linhas; um dropdown compartilhado, ativo por rota, com fechamento por navegação, clique fora, saída de foco e Escape; operação por teclado e `aria-expanded`/`aria-controls` |
| Catálogo | Pesquisa sem depender de acentos, filtros combinados de nome, município, categoria e recursos de acessibilidade; fichas individuais com fonte, data, estados de revisão, avaliações, favoritos e links para mapa/planejador |
| Cultura | Página editorial com boi e sotaques, tambor de crioula, reggae, cacuriá, azulejaria, patrimônio, lendas identificadas como tradição oral, artesanato, gastronomia e Quilombo Cultural; cinco temas filtrados no planejador |
| Acessibilidade | Doze recursos independentes com estados confirmado/não disponível/não verificado; cinco grupos de necessidades; filtros conservadores; consentimento privado e revogável; sugestões pendentes e moderação administrativa local |
| Amigos | Pesquisa optativa por nome/@usuario, solicitações, aceitação, rejeição, remoção, bloqueio e desbloqueio; perfis privados por padrão, controles de favoritos e recebimento de convites |
| Roteiros compartilhados | Convites com leitura ou edição, aceite obrigatório, contribuições textuais e edição de título; revogação; links de leitura anônima criados explicitamente e revogáveis |
| Vouchers | Convites simbólicos para amigos, com lugar, mensagem, tema, validade e código aleatório único; emissão, envio, resgate, expiração e cancelamento; sem valor comercial |
| Perfil | Foto e capa com prévia, remoção e posição horizontal/vertical persistente; nome, @usuario único, biografia, município, interesses, três temas, privacidade e preferências; capa e avatar circular sobreposto; estatísticas de pesquisas, favoritos, roteiros e amigos |

A colaboração é deliberadamente básica: título e ideias do grupo. Não inclui edição simultânea do conteúdo de cada dia, chat, reserva ou contratação. Convites simbólicos podem se referir a atrações, mas não garantem visita, ingresso ou prestação de serviço.

## Migrações e preservação

A migração registrada como versão 2 em `schema_migrations` é incremental, com `BEGIN IMMEDIATE` e confirmação/rollback pela conexão. Não há comandos para apagar ou recriar tabelas com dados. As colunas existentes e IDs foram preservados. O catálogo usa inserção idempotente e só complementa metadados legados ainda vazios; descrições, nomes, coordenadas e correções manuais não são substituídos. O preenchimento automático antigo de coordenadas nulas foi retirado da inicialização para respeitar remoções manuais.

Antes da migração, o esquema é salvo em `backend/backups/schema_before_v2_<data UTC>.sql`. A cópia **não contém registros pessoais** e não substitui um backup de dados do arquivo SQLite. O diretório é ignorado pelo Git. Um teste parte de um banco legado com pessoa, destino e favorito existentes e verifica a preservação e a execução idempotente.

Campos acrescentados a `destinos`: `category`, `address`, `source_url`, `verified_at`, `review_status`, `coordinates_status` e `access_json`.

Novas tabelas: `schema_migrations`, `profiles`, `media`, `friendships`, `blocks`, `trip_invites`, `trip_notes`, `trip_shares`, `vouchers` e `accessibility_reports`. Foram adicionados índices para amizades, convites, vouchers e filtros do catálogo. Exclusões de roteiros removem apenas seus convites, ideias e links relacionados por cascata.

## Privacidade, mídia e autorização

- Perfil privado e favoritos privados por padrão; pesquisa de pessoas depende de autorização separada. Amigos aceitos podem abrir o perfil. E-mail, histórico e preferências de acessibilidade não são expostos nas APIs públicas ou sociais.
- Remover a amizade revoga convites de roteiros. Bloquear também cancela vouchers ainda pendentes entre as pessoas e impede acesso ao perfil/mídia pela conta bloqueada. Desbloquear não restaura amizades ou permissões.
- Links públicos de roteiro são uma autorização explícita de leitura para quem tiver o link, inclusive visitantes anônimos. Não incluem notas do grupo nem dados da sessão. Bloquear uma pessoa não consegue impedir que ela consulte um link público anonimamente; use “Desativar link público” para encerrar esse acesso.
- Upload exige sessão e CSRF. Até 4 MB por imagem, 16 megapixels e apenas JPEG/PNG/WebP decodificáveis. Pillow verifica o conteúdo, aplica orientação, redimensiona e recodifica para JPEG sem metadados. SVG/GIF e arquivos inválidos são recusados. Limite global de requisição: 6 MB.
- Imagens são BLOBs no SQLite, com identificadores aleatórios; nomes fornecidos pelo usuário não são usados. A rota de mídia verifica autorização e usa `nosniff` e `private, no-store`; caminhos internos não são publicados.
- A API valida os dados, utiliza parâmetros SQL, conserva hash de senha e proteção CSRF/origem. Convites, contribuições, links e vouchers têm autorização por proprietário/participante no servidor.
- Preferências de acessibilidade são apagadas ao revogar o consentimento. Só são aplicadas ao formulário do planejador ao clicar em “Usar minhas preferências autorizadas”. Não existe pedido de diagnóstico.

## Catálogo e critérios de evidência

| Município | Referências documentadas |
| --- | ---: |
| São Luís | 53 |
| São José de Ribamar | 3 |
| Raposa | 5 |
| Paço do Lumiar | 1 |
| Alcântara | 7 |
| Total | 69 |

A existência foi confirmada documentalmente em páginas oficiais, consultadas em **06/11/2026**. As descrições são editoriais e originais. `partial` significa que ainda há informações a verificar; `legacy_unverified` identifica registros anteriores sem fonte. Os endereços fornecidos são referências presentes nas fontes; quando faltam detalhes, a ficha informa que o endereço ainda não foi verificado.

**Nenhuma coordenada nova foi estimada.** Os marcadores legados foram preservados e identificados como não verificados nas fichas. Novos lugares sem coordenadas não ganham marcadores inventados. A pesquisa e os links ao mapa continuam funcionando; centralizar novos pontos depende de completar a revisão geográfica. Este é um limite material da entrega, não uma verificação concluída.

As imagens de destinos são um SVG original de azulejos identificado como ilustração, sem alegação de representar fotograficamente o local. Fotografias reais licenciadas ainda precisam ser cadastradas. Os perfis podem usar as imagens enviadas pelos próprios usuários.

Acessibilidade começa como **informação ainda não verificada** para cada recurso. Nenhum local recebeu aprovação por inferência a partir do nome, categoria ou fotografia. Filtros combinados exigem todos os recursos selecionados com estado confirmado, fonte e data. Grupos são conservadores: mobilidade exige acesso sem degraus, circulação e sanitário; visual exige audiodescrição e sinalização; auditivo exige Libras e legendas; cognitivo exige sinalização e atendimento; sensorial exige informação sensorial confirmada. Também é possível selecionar recursos individualmente.

Sem correspondências confirmadas, o planejador retorna 422 com explicação. Isso não afirma que os lugares são inacessíveis: significa que o banco ainda não possui evidências suficientes. O planejador não certifica deslocamentos, continuidade de calçadas, rampas de embarque ou travessias marítimas.

Fontes principais: [turismo municipal de São Luís](https://turismosaoluis.com.br/o-que-fazer/centro-historico/), [museus](https://turismosaoluis.com.br/o-que-fazer/museus/), [igrejas](https://turismosaoluis.com.br/o-que-fazer/igrejas/), [praças](https://turismosaoluis.com.br/o-que-fazer/pracas/), [parques](https://turismosaoluis.com.br/o-que-fazer/parques/), [Secretaria de Turismo do Maranhão](https://turismo.ma.gov.br/programas-ou-campanhas/sao-luis-alcantara), [Ibram](https://www.gov.br/museus/pt-br/museus-ibram/museu-historico-de-alcantara), [Prefeitura de Raposa](https://raposa.ma.gov.br/secretario_de_turismo_acompanha_rota_turistica_em_raposa_com_casal_de_influenciadores_digitais) e as páginas municipais de Ribamar e Paço vinculadas em `backend/catalog.py`. Cultura também referencia [Iphan](https://www.gov.br/iphan/pt-br/superintendencias/maranhao/patrimonio-imaterial) e [CNFCP](https://antigo.cnfcp.gov.br/interna.php?ID_Materia=76).

## Rotas novas

Páginas: `/catalogo`, `/destino/<id>`, `/cultura`, `/configuracoes`, `/amigos`, `/presentes`, `/p/<handle>`, `/roteiro-compartilhado/<id>` e `/s/<token>`.

| Método e API | Uso |
| --- | --- |
| GET `/api/destinos` | Mantém `q`; aceita `municipality`, `category` e `access` repetível |
| GET `/api/destinos/<id>` | Ficha com metadados e recursos |
| GET/PATCH `/api/profile-settings` | Perfil, identidade, aparência, privacidade e consentimento; PATCH também aceita nome/interesses na mesma transação |
| POST/DELETE `/api/profile-media/<avatar ou cover>` | Upload multipart no campo `image` ou remoção |
| GET `/media/<token>` | Mídia com controle de acesso |
| GET `/api/people?q=` | Pesquisa de pessoas que optaram por aparecer |
| GET `/api/public-profile/<handle>` | Perfil conforme permissões, sem e-mail ou histórico |
| GET `/api/friends` | Amigos, solicitações e bloqueios próprios |
| POST `/api/friends/<id>` | `action`: request, accept, reject, remove, block, unblock |
| POST `/api/trips/<id>/invites` | Destinatário e papel viewer/editor |
| GET `/api/trip-invites` | Convites enviados/recebidos próprios |
| POST `/api/trip-invites/<id>` | Aceitar, rejeitar ou revogar |
| GET/PATCH `/api/trips/<id>` | Conteúdo autorizado ou edição de título |
| POST `/api/trips/<id>/notes` | Contribuição de participante editor |
| POST/DELETE `/api/trips/<id>/share` | Criar ou revogar link público |
| GET `/api/shared/<token>` | Leitura pública autorizada por token |
| GET/POST `/api/vouchers` | Listar convites próprios ou emitir |
| POST `/api/vouchers/<id>/transition` | `action`: send, redeem, cancel |
| GET `/api/accessibility` | Recursos, grupos e estados |
| GET/POST `/api/accessibility-reports` | Acompanhar sugestões próprias ou enviar para moderação |

POST `/api/roteiro` mantém o contrato e aceita `theme` opcional: historia, reggae, sabores, popular ou quilombo. As demais APIs anteriores permanecem disponíveis. Requisições autenticadas que alteram dados continuam exigindo `X-CSRF-Token` obtido em `/api/auth/me`.

Vouchers seguem transições: emitido → enviado → resgatado; emitido/enviado → cancelado ou expirado. Somente o destinatário resgata, somente o emissor envia/cancela e estados finais não permitem repetição. A validade é armazenada em UTC até 23:59:59 da data escolhida. Não há saldo, desconto, provedor de pagamento ou integração comercial. Uma futura oferta paga exigirá módulos próprios de contratação, provedor, conciliação, termos e segurança; nenhuma transação foi ativada nesta expansão.

## Executar e moderar no Windows

```powershell
cd C:\Users\felps\Downloads\Explore_Mais_SLZ_Perfil_Corrigido\explore_mais_slz
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m backend.app
```

Abra `http://127.0.0.1:5000`. `INICIAR_WINDOWS.bat` continua sendo a alternativa por duplo clique. As dependências de execução são Flask e Pillow. Para testes de navegador, instale Playwright no mesmo ambiente; os testes utilizam o Chrome já instalado, sem baixar outro navegador.

A moderação está restrita à administração local do banco: `python -m backend.moderate_accessibility list`, seguido de `approve <id> --source <URL HTTPS real> --date <AAAA-MM-DD> --reviewer <nome>` ou `reject <id>`. Aprovar exige que o administrador tenha verificado a evidência. O comando atualiza somente o recurso revisado; sugestões de usuários nunca se autopublicam. Não há painel web de moderação.

## Verificação e limites

A rodada final de validação está registrada abaixo. Os testes usam SQLite temporário, incluindo testes de migração e uploads. As contas, fotos e fontes `example.test` usadas nos testes não são inseridas no banco normal.

- `python -m unittest discover -v`: suíte original e expansão, incluindo autorização entre contas, consentimento, uploads e limites, filtros, preservação de dados, moderação por CLI, colaboração e estados de vouchers.
- `python test_browser.py`: fluxos anteriores de cadastro/login, perfil, favoritos, roteiro, histórico, contraste, saída e recuperação de sessão.
- `python browser_expansion.py`: menu por teclado, foto/capa/prévia/posição/remoção, configurações, duas contas, amizade, contribuição, link revogável, voucher e envio de sugestão. Sete páginas verificadas em 320, 390, 768 e 1440 pixels, sem rolagem horizontal.
- Capturas em `.artifacts/`: `v2-perfil.png`, `v2-cultura.png`, `v2-amigos.png` e `v2-voucher-celular.png`, além das capturas anteriores.

A interface implementa práticas de acessibilidade, mas **não há certificação de conformidade integral com WCAG 2.2 AA**. Auditoria formal, testes com leitores de tela e validação com pessoas com deficiência continuam pendentes. Mapas externos e seus tiles não foram certificados pelos testes de navegador; o CDN do Leaflet foi bloqueado para também verificar o funcionamento sem ele.

Outras pendências: completar coordenadas/endereço e auditoria de acessibilidade de cada lugar; fotografias licenciadas reais; maior cobertura de Paço do Lumiar; paginação nas listagens sociais; notificações; recuperação de senha; edição colaborativa de dias; interface administrativa web; testes de carga. O servidor de desenvolvimento com debug continua destinado ao uso local. Publicação exige configuração de produção, chave persistente, HTTPS e controles operacionais.

## Arquivos desta expansão

Alterados: `backend/app.py`; `frontend/index.html`, `script.js`, `account.js`, `painel.html`, `painel.js`; `requirements.txt`; `.gitignore`; `README.md`; `ANALISE_PROJETO.md`; `test_api.py`; `test_browser.py`.

Criados: `backend/migrations.py`, `catalog.py`, `expansion.py`, `moderate_accessibility.py`; `frontend/navigation.js`, `expansion.css`, `experiencias.html`, `experiencias.js`, `configuracoes.js`, `catalogo.js`, `social.js`, `cultura.js`, `destination-fallback.svg`; `test_expansion.py`; `browser_expansion.py`; `RELATORIO_EXPANSAO_2.md`.

Gerados e ignorados pelo Git: banco SQLite local migrado, cópia do esquema em `backend/backups/` e capturas em `.artifacts/`. Alterações preexistentes no repositório não foram descartadas ou commitadas.

### Resultados executados em 06/11/2026

| Verificação | Resultado real |
| --- | --- |
| Descoberta padrão dos testes de API | 22 testes aprovados, sem erros ou avisos na última execução |
| Teste de navegador da expansão | Aprovado; dois usuários; sete páginas nas quatro larguras; nenhum erro JavaScript |
| Teste de navegador dos recursos anteriores | Aprovado; cadastro/login, perfil, histórico, favoritos, roteiros, leitura e sessão |
| `python -m pip check` | Nenhuma dependência incompatível |
| `git diff --check` | Sem problemas de whitespace |

A revisão final das capturas confirmou a capa com avatar sobreposto, estatísticas com amigos, preservação da identidade visual e formulários legíveis em celular. O login também recebeu contenção de foco por Tab/Shift+Tab e conteúdo de fundo inativo enquanto o diálogo está aberto.
