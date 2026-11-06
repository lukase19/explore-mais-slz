# Arquitetura, tecnologias, APIs, banco e código explicado

**Referência:** fonte e SQLite examinados em 06/11/2026. O apêndice de esquema é extraído de `sqlite_master` e PRAGMAs em modo somente leitura. Não contém linhas de contas reais.

## 1. Responsabilidade de cada tecnologia

| Tecnologia | O que é e para que serve | Onde e conexão no projeto | Por que faz sentido aqui |
|---|---|---|---|
| Python | Linguagem que executa regras no servidor | backend/*.py, testes e scripts | Organiza validação, consulta e regras sem compilar frontend |
| Flask | Framework HTTP Python | app.py configura app, rotas, respostas e sessão | Liga uma URL à função e serve API/arquivos; adequação inferida do uso |
| Werkzeug | Infraestrutura usada pelo Flask e utilitários | hash/check de senha, servidor de teste | Evita escrever implementação própria de hash/HTTP |
| HTML | Estrutura semântica do documento | index/painel/experiencias.html | Títulos, rótulos, formulários e pontos de montagem |
| CSS | Apresentação e adaptação | style, painel, expansion e themes.css | Mantém identidade e layouts sem biblioteca de componentes |
| JavaScript | Código no navegador | account, navigation, script, painel e controladores | Escuta eventos, faz fetch e atualiza DOM |
| SQLite | Banco relacional em arquivo | backend/explore_slz.db, via sqlite3 | Implantação local simples; limitações de concorrência devem ser consideradas |
| SQL | Linguagem de consulta | SELECT, INSERT, UPDATE, DELETE parametrizados | Relaciona contas, destinos e objetos com restrições |
| Pillow | Processamento/validação de imagens | upload_profile_media | Analisa conteúdo e normaliza foto/capa |
| Leaflet 1.9.4 | Biblioteca de mapa interativo | vendor/leaflet e maps.js | Camadas, zoom, popup e ajuste da área |
| MarkerCluster 1.5.3 | Agrupamento de marcadores Leaflet | vendor/markercluster | Mostra pontos próximos como grupos sem perder associação |
| OpenStreetMap | Fonte dos tiles cartográficos | tileLayer externo | Fornece fundo; não fornece automaticamente destinos da aplicação |
| HTTP | Protocolo requisição/resposta | Navegador ↔ Flask | Métodos e status expressam consulta, gravação e erro |
| JSON | Formato textual estruturado | Corpo e retorno das APIs; campos TEXT | Transporta objetos/listas; não substitui validação |
| Fetch / FormData | APIs do navegador | account.api e uploads | JSON para dados e multipart para imagens |
| Cookies/sessões | Mantêm identidade entre requisições | Flask session, cookie de mesma origem | Browser não precisa mandar senha em cada ação |
| localStorage | Armazenamento local do navegador | Tema em cache, contraste e fonte | Preferências locais sobrevivem ao recarregamento |
| unittest | Testes Python | test_api, test_expansion, test_corrections | Exercita API e persistência isoladamente |
| Playwright + Chrome | Automação de navegador | três scripts de browser | Executa cliques, formulários, estilos e verificações de DOM |
| pathlib/tempfile/json/math/unicodedata | Biblioteca padrão Python | Paths, isolamento, serialização, finitude e acentos | Não são serviços remotos |
| Google Fonts | Recurso externo de fontes | DM Sans e Manrope no HTML/CSS | Tipografia; sem rede há fallback de fonte |

`requirements.txt` declara Flask >=3.0,<4.0 e Pillow >=11.0,<13.0. Esses intervalos não são um lockfile de versões exatas. Playwright e Chrome são dependências adicionais dos testes de navegador. O script `scripts/vendor_maps.py` baixa versões fixadas dos assets; a aplicação não precisa executá-lo a cada abertura.

Não há React, Vue, ORM, servidor Node, API de inteligência artificial, sistema de pagamentos nem serviço de geocodificação implementado. Isso descreve a árvore encontrada, não uma recomendação geral contra essas tecnologias.

## 2. Estrutura de diretórios e ciclo de carregamento

| Local | Responsabilidade |
|---|---|
| backend/app.py | Cria app, base, sessão, destinos, planejador e CRUD pessoal |
| backend/expansion.py | Instala configurações, mídia, rede social, compartilhamento, vouchers e acessibilidade |
| backend/migrations.py | Versão do esquema, novas tabelas e metadados padrão |
| backend/catalog.py | Seleção editorial de 69 registros e seed idempotente |
| backend/culture.py + culture_content.json | Nove textos e associações por nome |
| backend/moderate_accessibility.py | Moderação por comando local |
| backend/backups | SQL do esquema anterior à migração, sem cópia de registros |
| frontend/index.html + script.js | Início/explorar/planejar e modal |
| frontend/painel.html + painel.js | Perfil, histórico, favoritos, roteiros e leitura |
| frontend/experiencias.html + experiencias.js | Shell e roteamento das páginas ampliadas |
| frontend/catalogo.js / cultura.js | Catálogo, ficha e contextos culturais |
| frontend/configuracoes.js | Preferências, foto/capa e perfil público |
| frontend/social.js | Amigos, presentes e colaboração |
| frontend/account.js / navigation.js | Sessão/API e cabeçalho compartilhados |
| frontend/maps.js | Adaptação entre destinos e Leaflet |
| frontend/theme-init.js / themes.css | Tema inicial e tokens visuais |
| frontend/style.css / painel.css / expansion.css | Estilo por conjunto de telas e responsividade |
| frontend/vendor | Bibliotecas, CSS, imagens técnicas, licenças e manifesto |
| test_*.py / browser_*.py | Verificações automatizadas |
| INICIAR_WINDOWS.bat | Inicialização local no Windows |
| README e relatórios | Instruções e histórico, não substituem fonte atual |

`theme-init.js` tenta aplicar o tema em cache cedo. `account.js` lê preferências locais, consulta sessão e, quando autenticado, configurações. O evento `explore-login` sinaliza que as telas podem renderizar. `explore-profile-updated` atualiza identidade compartilhada após alteração. O roteador de experiencias escolhe o renderizador pela URL; o painel faz seleção semelhante entre suas rotas.

Arquivos estáticos são servidos por Flask na raiz, pois `static_url_path=""`. Ex.: /maps.js, /themes.css, /vendor/leaflet/leaflet.js. Há três shells para muitas URLs; autorização privada é sempre aplicada nas APIs, mesmo quando a página HTML responde 200.

## 3. Caminho completo de uma interação

```text
Usuário aciona um coração
  → evento click no JavaScript identifica destination_id
  → ExploreAccount.api monta PUT + cookie + X-CSRF-Token
  → Flask recebe /api/favoritos/<id>
  → before_request valida origem/JSON/CSRF
  → login_required exige user_id na sessão
  → handler valida destino, abre conexão com foreign_keys=ON
  → INSERT OR IGNORE favoritos(usuario_id da sessão, destino_id)
  → se inseriu, registra histórico
  → transação confirma; conexão fecha
  → jsonify produz resposta HTTP
  → JS atualiza aria-pressed, ícone e aviso
  → consulta posterior do perfil recupera a relação persistida
```

O ID do proprietário não vem de um campo editável do formulário. O servidor usa a sessão, ponto essencial para isolamento. Alterar o HTML local não concede propriedade de outro registro.

## 4. Contrato HTTP comum

| Item | Comportamento |
|---|---|
| Consulta | GET; rotas GET também recebem HEAD/OPTIONS automáticos do framework |
| JSON de escrita | Objeto; listas escalares no topo são rejeitadas |
| Origem | Se Origin vier preenchido, precisa coincidir com host_url |
| Conta | Decorator retorna401 com error quando falta sessão |
| CSRF | Escritas API com sessão, exceto login/register, precisam header correto |
| Sucesso | Geralmente200; criações relevantes201 |
| Erro | Objeto JSON com error nas APIs tratadas |
| 400 | Formato/valor inválido |
| 401 | Precisa autenticar ou credencial incorreta |
| 403 | Origem/CSRF/papel insuficiente |
| 404 | Objeto inexistente, ocultado por privacidade ou não acessível |
| 409 | Estado em conflito, duplicação ou handle/e-mail indisponível |
| 413 | Corpo/arquivo acima do permitido |
| 422 | Pedido bem formado sem condições de dados para gerar sugestão |

Handlers HTTP e ValueError em expansion.py padronizam erros, mas isso não equivale a um monitoramento de todas as exceções. Não há contrato OpenAPI gerado. As tabelas seguintes são documentação do código atual.

## 5. Todos os endpoints de negócio

**Público** permite chamada sem sessão. **Conta** exige sessão. Escritas com conta continuam sujeitas ao CSRF comum. IDs abaixo são variáveis, não registros reais de usuários.

| Método e caminho | Entrada | Saída, efeito e validações principais |
|---|---|---|
| GET /api/health | Nenhuma | Diagnóstico de saúde simples; não auditoria de dados |
| GET /api/culture | Nenhuma | Nove contextos e mapeamento de interesses |
| GET /api/destinos | q, municipality, category, interest; culture e access repetíveis | Público; query,total,results,map,access_note; inválidos400; pode registrar pesquisa de conta |
| GET /api/destinos/verificar | Nenhuma | Público; nome, município, lat/lon; **não verifica nem atualiza** |
| GET /api/destinos/<id> | ID inteiro | Público; destino serializado ou404 |
| POST /api/roteiro | destination, days, budget, people, transport, interests[], access[], theme opcional | Público; summary,days,special_experience,note,plain_text;400/404/422 |
| POST /api/auth/register | name,email,password | Cria conta, sessão e csrf;201;400inválido/409e-mail |
| POST /api/auth/login | email,password | Sessão/user/csrf;401 incorreto |
| GET /api/auth/me | Cookie | User ou null,csrf; limpa sessão de usuário ausente |
| POST /api/auth/logout | Cookie/CSRF se houver sessão | Limpa sessão e devolve ok |
| PATCH /api/perfil | name,interests[] | Conta; atualiza nome/interesses;400 em limites |
| GET /api/historico | Cookie | Conta; últimos100 eventos próprios |
| DELETE /api/historico | Sem corpo | Conta; apaga todos os próprios eventos |
| GET /api/favoritos | Cookie | Conta; destinos favoritos por data |
| PUT /api/favoritos/<id> | Sem conteúdo obrigatório | Conta; valida destino; idempotente; histórico só na primeira inserção |
| DELETE /api/favoritos/<id> | ID | Conta; remove relação própria, idempotente |
| GET /api/roteiros-salvos | Cookie | Conta; últimos100; JSON convertido de conteudo |
| POST /api/roteiros-salvos | title,trip{summary,days} | Conta; valida estrutura básica e <=100000 caracteres serializados; título até120;201 com id |
| DELETE /api/roteiros-salvos/<id> | ID | Conta; DELETE por id E dono; retorna ok mesmo sem linha |
| GET /api/avaliacoes/<id> | Destino | Público; últimas50 avaliações com nota, comentário, data e nome |
| POST /api/avaliacoes/<id> | rating,comment | Conta; inteiro1–5, texto5–1000, destino válido; upsert do par |
| GET /api/resumo | Cookie | Conta; contadores pesquisas,favoritos,roteiros |
| GET /api/profile-settings | Cookie | Conta; profile e dicionários de acesso; cria profile lazy se ausente |
| PATCH /api/profile-settings | Campos da tabela de configurações | Conta; valida texto, enums, bools, posições e consentimento;409handle |
| POST /api/profile-media/<kind> | kind avatar/cover; multipart image | Conta; valida bytes e dimensões;201 url;400/413 |
| DELETE /api/profile-media/<kind> | kind | Conta; remove mídia própria; kind inválido404 |
| GET /media/<token> | Cookie opcional | JPEG para dono/público/amigo; bloqueio/negado404; private,no-store,nosniff |
| GET /api/people | q pelo menos2 | Conta; até30 descobríveis, sem e-mail, exclui bloqueados |
| GET /api/public-profile/<handle> | Identificador | Público condicionado à política; dados permitidos/favoritos ou404 |
| GET /api/friends | Cookie | Conta; relações pending/accepted e bloqueados próprios |
| POST /api/friends/<other> | action=request/accept/reject/remove/block/unblock | Conta; regras de par e ator;400/403/404/409 |
| POST /api/trips/<id>/invites | recipient_id,role viewer/editor | Conta/dono; amigo aceito e aceita convites;201 |
| GET /api/trip-invites | Cookie | Conta; convites enviados/recebidos pending/accepted autorizados |
| POST /api/trip-invites/<id> | action=accept/reject/revoke | Conta; destinatário pendente ou remetente conforme ação |
| GET /api/trips/<id> | Cookie | Conta; dono/convidado aceito; conteúdo, notas, owner,can_edit,share_url só dono |
| POST /api/trips/<id>/notes | text,1–1000 | Conta/dono/editor; insere nota201 |
| PATCH /api/trips/<id> | title,1–120 | Conta/dono/editor; renomeia |
| POST /api/trips/<id>/share | Sem corpo específico | Conta/dono; cria ou recupera token; url relativa |
| DELETE /api/trips/<id>/share | ID | Conta/dono; revoga token |
| GET /api/shared/<token> | Token | Público; somente title,trip;404 revogado/inexistente |
| GET /api/vouchers | Cookie | Conta; até200 enviados/recebidos visíveis, atualiza expirados |
| POST /api/vouchers | recipient_id,destination_id,message,theme,expires_at | Conta; amizade/convites/data/tema;201issued |
| POST /api/vouchers/<id>/transition | action send/cancel/redeem | Conta/papel e estado; expira antes;409 transição inválida;404 terceiro |
| GET /api/accessibility | Nenhuma | Público; campos,grupos,estados |
| GET /api/accessibility-reports | Cookie | Conta; próprios últimos100 relatos |
| POST /api/accessibility-reports | destination_id,feature,proposed_status,description,source_url | Conta;10–2000 descrição,HTTPS opcional, estado conhecido;201pending |

Os campos de avaliação são os nomes usados pelo handler, mesmo quando a interface mostra “nota” e “comentário”. Para experimentar chamadas diretas, consultar o teste correspondente e a assinatura do handler, evitando inferir chaves a partir do rótulo visual.

### Rotas HTML e comportamento do servidor

| Rotas | Arquivo/resposta |
|---|---|
| /, /explorar, /planejar | index.html |
| /perfil, /historico, /favoritos, /meus-roteiros, /acessibilidade | painel.html |
| /catalogo, /amigos, /presentes, /configuracoes | experiencias.html |
| /destino/<int:id>, /p/<handle>, /s/<token>, /roteiro-compartilhado/<int:id> | experiencias.html |
| /cultura | 302 para /catalogo#cultura |
| /<path:filename> | Rota estática Flask dentro de frontend |
| /media/<token> | Bytes JPEG após autorização, não shell |

## 6. Banco relacional: como interpretar

SQLite usa afinidade de tipos; INTEGER representa inteiros, REAL números com parte decimal, TEXT cadeias, BLOB bytes. Datas são TEXT; listas e roteiros também são TEXT contendo JSON. O banco não transforma automaticamente esses JSONs em tabelas relacionadas.

PK identifica uma linha. FK referencia outra tabela e depende de `PRAGMA foreign_keys=ON`, aplicado pela conexão da aplicação. UNIQUE impede duplicação; CHECK restringe domínio; NOT NULL impede ausência SQL. String vazia e NULL são diferentes. O padrão SQL CURRENT_TIMESTAMP usa UTC.

A tabela favoritos implementa relação muitos-para-muitos entre usuários e destinos. Avaliações também conectam os dois, com uma contribuição por par. Roteiros pertencem a usuários e convites/notas referenciam roteiros. Perfis ampliam usuários numa relação um-para-um. Mídias são no máximo duas por usuário, uma de cada tipo.

```text
usuarios ─1:1─ profiles
usuarios ─1:N─ media / historico / roteiros_salvos
usuarios ─N:N─ destinos          por favoritos e avaliacoes
usuarios ─N:N─ usuarios          por friendships e blocks
roteiros_salvos ─1:N─ trip_invites / trip_notes
roteiros_salvos ─1:0..1─ trip_shares
usuarios ─envia/recebe─ vouchers ─N:1─ destinos
usuarios ─1:N─ accessibility_reports ─N:1─ destinos
schema_migrations               controle de versão, sem dono
```

**Exceção importante:** `historico.destino_id` é INTEGER, mas não possui FK declarada. Não afirmar que todo identificador de destino do banco é protegido por integridade referencial.

### Leituras e escritas por tabela

| Tabela | Leitura | Escrita e privacidade |
|---|---|---|
| destinos | Pesquisa, ficha, planejamento, favoritos | Seed e moderação local; sem cadastro web |
| usuarios | Login/me/perfil/nomes sociais | Cadastro e nome/interesses; hash nunca vai para UI |
| profiles | Configuração, políticas, pesquisa | Criado lazy e PATCH; necessidades pessoais não públicas |
| media | Endpoint autorizado | Upload/remoção; bytes privados no arquivo SQLite |
| historico | Próprio painel/resumo | Eventos e limpeza própria |
| favoritos | Próprio painel/perfil autorizado | PUT/DELETE do dono |
| roteiros_salvos | Próprio painel/convite/link autorizado | Salvar/excluir; título editável sob permissão |
| avaliacoes | Público com nome | Upsert da própria avaliação |
| friendships | Participantes | Solicitação, aceitação, recusa, remoção |
| blocks | Ator e verificações de acesso | Bloquear/desbloquear |
| trip_invites | Participantes | Dono cria; destinatário responde; remetente revoga |
| trip_notes | Quem acessa roteiro | Dono/editor acrescenta |
| trip_shares | Dono para gerir, token para ler | Dono cria/revoga |
| vouchers | Remetente/destinatário com estado permitido | Emissão/transição/expiração |
| accessibility_reports | Próprios e CLI local | Usuário propõe; CLI decide; não autopublica |
| schema_migrations | Inicialização | Migração insere versão aplicada |

## 7. Migração e carga inicial

`init_database` cria tabelas base e, se destinos estiver vazia, insere 14 entradas antigas. Depois chama `migrate` e `seed_catalog`. Há 69 entradas editoriais adicionais no catálogo, mas sete nomes coincidem com o legado. Como nome é único, o total novo padrão é 14 + 69 − 7 = 76, não83.

A migração usa transação `BEGIN IMMEDIATE`, confere versão2, grava cópia lógica do esquema anterior, adiciona colunas ausentes e cria tabelas/índices. Executa as instruções individualmente para manter a transação prevista. Se versão2 já existe, não reaplica essas operações.

A semente usa inserção ignorando nomes já existentes e preenche metadados ainda intocados de legado conforme condições do código. Não geocodifica nem sobrescreve coordenadas para parecer completo. A função antiga de atualizar coordenadas ainda existe, mas não é chamada na inicialização. Apagar manualmente um item de semente pode fazê-lo reaparecer no início seguinte.

A associação cultural compara nomes exatos. Renomear um destino sem atualizar o JSON pode romper a associação. Uma evolução seria usar identificadores estáveis com tabela de relação.

## 8. Segurança explicada por mecanismo

| Mecanismo | O que impede/reduz | O que não prova |
|---|---|---|
| Hash de senha | Evita guardar senha legível | Não dispensa senha forte ou limite de tentativas |
| Sessão assinada | Detecta alteração do cookie sem segredo | Não criptografa conteúdo nem elimina roubo de sessão |
| HttpOnly | Dificulta leitura do cookie por JS | Não impede todas as ações via script comprometido |
| SameSite=Lax | Restringe certos envios entre sites | Não substitui CSRF e validação de origem |
| X-CSRF-Token | Exige token da sessão em escrita autenticada | Não é papel administrativo |
| Origin | Rejeita origem divergente quando header presente | Header pode estar ausente em cliente não navegador |
| SQL parametrizado | Separa valor de comando SQL | Não aplica autorização sozinho |
| Filtro por dono/papel | Restringe objeto solicitado | Precisa ser mantido em cada novo endpoint |
| Escape HTML e safeURL | Reduz injeção de marcação/URL perigosa | Não é auditoria completa de XSS/CSP |
| Pillow e limites | Rejeita formatos/cargas inadequados nos casos tratados | Não garante ausência de falha em dependência |
| Tokens aleatórios | Dificulta adivinhar mídia/link | Quem recebe link público pode redistribuir |

O código chama o hash padrão da versão instalada de Werkzeug, sem fixar método no argumento. A [documentação do Werkzeug](https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash) descreve geração e conferência; não atribuir ao projeto um algoritmo fixo eterno só porque uma versão atual usa determinado padrão.

Para produção faltam definição de implantação WSGI, segredo estável, HTTPS, política de cookies coerente, monitoramento, backup integral restaurável, gestão de atualizações, limitação de tentativas e revisão de dados/privacidade. São requisitos técnicos propostos, não recursos presentes.

## 9. Funções e módulos: explicação de execução

### Backend principal

`protect_writes()` não recebe parâmetros explícitos: lê o request corrente e pode encerrar com JSON400/403; depende de sessão e configuração Flask. `login_required(handler)` retorna uma função decorada que autoriza ou responde401. `record_history(kind,label,item_id=None)` usa a conta atual e grava texto truncado em220 caracteres.

`get_connection()` devolve uma conexão por context manager, define linhas por nome, ativa FKs, confirma ou desfaz a transação e fecha. `init_database()` tem efeito de escrita no início. `row_to_dict(row)` retorna um dicionário com JSON de interesses, metadados, localização validada e cultura, usado nas listagens e no planejador.

`pesquisar_destinos()` lê querystring e aplica normalização/filtros; helper `normalized` usa NFKD/casefold. `gerar_roteiro()` recebe JSON via request e retorna sugestão ou erro, com o algoritmo detalhado no documento01. `verificar_destinos()` apenas lista pares de coordenadas, apesar do verbo no nome.

Os handlers register/login/me/logout implementam o ciclo de conta. edit_profile altera campos básicos. history/clear_history, favorites/add_favorite/remove_favorite, saved_trips/save_trip/delete_trip, reviews/submit_review e summary_stats correspondem diretamente aos contratos da tabela de endpoints. Não há camadas de serviço/repositório separadas: regras, HTTP e SQL estão próximos.

### Expansão

`install(app,connect,login_required,serialize_destination,frontend_dir)` recebe as dependências da aplicação e registra handlers fechados sobre elas. O argumento de serialização recebe `row_to_dict` na chamada em app.py; o diretório informa de onde servir o shell. Isso evita criar uma segunda app ou conexão global distinta. Helpers `body`, `uid`, `text` e `fail` padronizam leitura, identidade, texto e erro.

`profile(con,user_id)` cria um perfil se faltar; por isso até algumas consultas podem escrever. `media_urls` monta URLs por tipo. `own_profile` converte lista de necessidades e agrega contagem de amigos. `blocked` verifica as duas direções; `friends` exige relação aceita sem bloqueio; `public_person` omite dados privados e condiciona mídia.

`trip_access(con,trip_id,editor=False)` localiza roteiro, identifica dono/convite aceito e pode exigir edição. Seus erros protegem as funções shared_trip, add_trip_note e rename_shared_trip. share_trip_link só aceita dono; public_trip_link depende de token, não amizade.

`confirmed_features(destination,fields)` retorna booleano exigindo status confirmado, fonte e data para todos. `expire_vouchers(con)` atualiza estados vencidos em lote. Os demais handlers de expansão seguem as permissões explicitadas acima; o índice de assinaturas ao final fornece os nomes e linhas exatos.

### JavaScript compartilhado

`ExploreAccount` guarda user/profile/csrf/sessionError. `init` consulta me e configurações; `auth` recebe modo e dados; `logout` encerra; `api` trata transporte; `preference` protege acesso ao localStorage; `applyTheme` valida tema; `applyPreferences` aplica contraste/fonte. Erros de sessão são guardados e o evento final ainda é emitido para a tela mostrar recuperação.

Em navigation.js, `open/close` manipulam visibilidade, foco e aria-expanded; `refreshNavigation` recebe eventos e atualiza nome/avatar. Em theme-init.js a operação é imediata no carregamento inicial, antes da confirmação da API.

### Inicial e painel

Em script.js, `toast` controla aviso temporário, `money` formata BRL, `escapeHTML` prepara texto, `searchDestinations` consulta e sincroniza resultados, `openModal/closeModal` administram foco/inert e `loadFavs` recupera estados. O submit de tripForm é handler anônimo e monta os parâmetros; o renderizador insere dias, ações e pausa alimentar.

Em painel.js, `dateLabel` apresenta data, `tripList` desenha roteiros, `identity` monta apresentação, `profileForm` monta edição, `runAction` centraliza escrita/recarga, `bindCollections` liga exclusão/detalhes e `bindProfile` salva dados básicos. `load` controla carregamento e falhas; `renderAccessibility/setSize` aplicam preferências de leitura.

### Páginas ampliadas

experiencias.js cria `ExploreFeatures`: `h` escapa texto; `safeURL` restringe links; `notice` anuncia; `heading` define título; `action` gerencia ação assíncrona; `catalogCard` e `tripHTML` são renderizadores. `F.reload` identifica rota e executa renderizador sob controle de carregamento.

catalogo.js registra `F.catalog` e `F.detail`. Helpers internos `present/search` reutilizam resultado e evitam aplicar resposta antiga. cultura.js registra `cultureContext/cultureDiscovery/culture`, reaproveitando textos e catálogo.

configuracoes.js registra `F.settings` e `F.publicProfile`; helpers `setState/revoke` atualizam status e liberam URLs blob. social.js registra `F.friends/F.gifts/F.collaborate`; `bind` liga as ações sociais aos IDs.

### Adaptador cartográfico

`ExploreMap.create(container,status)` retorna um controller. `eligible` valida elegibilidade; `updateStatus` informa contagens; `setPlaces` substitui camadas; `focus` encontra e revela marcador; `snapshot` devolve IDs para verificar representação; `destroy` libera mapa/observador. Se Leaflet faltar, retorna uma versão que comunica indisponibilidade e evita exceções por chamadas posteriores.

## 10. Referências externas de apoio

As afirmações sobre comportamento do projeto vêm dos arquivos locais. Para os conceitos de sessão e utilitários, foram consultadas as documentações primárias do [Flask](https://flask.palletsprojects.com/en/stable/quickstart/#sessions) e [Werkzeug](https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.security.generate_password_hash). Os assets do mapa têm licenças e URLs registradas no manifesto local; consulta de documentação externa não confirma que as coordenadas do catálogo sejam corretas.


## 11. Dicionário integral do esquema real

Cada coluna abaixo vem de PRAGMA table_info. “PK 1/2” indica posição em chave composta. Um INTEGER PRIMARY KEY pode aparecer com notnull=0 no PRAGMA e ainda ter semântica de identificador; o SQL exato é a referência para restrições.

### accessibility_reports

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| user_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário ou autor, conforme a tabela. |
| destination_id | INTEGER | sim | 0 | NULL/sem padrão | Destino referido. |
| feature | TEXT | sim | 0 | NULL/sem padrão | Chave do recurso de acessibilidade proposto. |
| proposed_status | TEXT | sim | 0 | NULL/sem padrão | Estado sugerido: confirmed/unavailable/unverified. |
| description | TEXT | sim | 0 | NULL/sem padrão | Justificativa do relato. |
| source_url | TEXT | sim | 0 | '' | Referência de origem/evidência; URL não é validação automática. |
| status | TEXT | sim | 0 | 'pending' | Estado da máquina de estados desta tabela; ver CHECK. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- destination_id → destinos.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- user_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE accessibility_reports (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES usuarios(id), destination_id INTEGER NOT NULL REFERENCES destinos(id),
          feature TEXT NOT NULL, proposed_status TEXT NOT NULL CHECK(proposed_status IN ('confirmed','unavailable','unverified')),
          description TEXT NOT NULL, source_url TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### avaliacoes

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| usuario_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário/autor da relação. |
| destino_id | INTEGER | sim | 0 | NULL/sem padrão | Destino referido pela relação. |
| nota | INTEGER | sim | 0 | NULL/sem padrão | Nota de avaliação entre 1 e 5. |
| comentario | TEXT | sim | 0 | NULL/sem padrão | Comentário público do usuário. |
| criado_em | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora do registro em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- destino_id → destinos.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- usuario_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE avaliacoes (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), destino_id INTEGER NOT NULL REFERENCES destinos(id), nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5), comentario TEXT NOT NULL, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(usuario_id,destino_id));
```

### blocks

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| blocker_id | INTEGER | sim | 1 | NULL/sem padrão | Usuário que aplicou bloqueio. |
| blocked_id | INTEGER | sim | 2 | NULL/sem padrão | Usuário bloqueado. |

**Chaves estrangeiras efetivamente declaradas:**

- blocked_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- blocker_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE blocks (
          blocker_id INTEGER NOT NULL REFERENCES usuarios(id), blocked_id INTEGER NOT NULL REFERENCES usuarios(id),
          PRIMARY KEY(blocker_id,blocked_id), CHECK(blocker_id != blocked_id));
```

### destinos

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| nome | TEXT | sim | 0 | NULL/sem padrão | Nome de apresentação do destino ou da pessoa. |
| municipio | TEXT | sim | 0 | NULL/sem padrão | Município do destino. |
| descricao | TEXT | sim | 0 | NULL/sem padrão | Descrição editorial ou do evento registrado. |
| icone | TEXT | sim | 0 | NULL/sem padrão | Símbolo visual do destino. |
| interesses | TEXT | sim | 0 | NULL/sem padrão | Lista JSON de interesses turísticos. |
| latitude | REAL | não | 0 | NULL/sem padrão | Coordenada norte/sul, anulável. |
| longitude | REAL | não | 0 | NULL/sem padrão | Coordenada leste/oeste, anulável. |
| category | TEXT | sim | 0 | 'Experiência' | Categoria editorial. |
| address | TEXT | sim | 0 | '' | Referência de endereço; vazio quando não informado. |
| source_url | TEXT | sim | 0 | '' | Referência de origem/evidência; URL não é validação automática. |
| verified_at | TEXT | não | 0 | NULL/sem padrão | Data editorial ou de revisão do dado. |
| review_status | TEXT | sim | 0 | 'legacy_unverified' | Estado de revisão editorial do destino. |
| coordinates_status | TEXT | sim | 0 | 'unverified' | Estado de verificação do par geográfico. |
| access_json | TEXT | sim | 0 | '{}' | Objeto JSON com recursos físicos, estado, fonte e data. |

**Chaves estrangeiras efetivamente declaradas:**

Nenhuma.


**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE destinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                municipio TEXT NOT NULL,
                descricao TEXT NOT NULL,
                icone TEXT NOT NULL,
                interesses TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            , category TEXT NOT NULL DEFAULT 'Experiência', address TEXT NOT NULL DEFAULT '', source_url TEXT NOT NULL DEFAULT '', verified_at TEXT, review_status TEXT NOT NULL DEFAULT 'legacy_unverified', coordinates_status TEXT NOT NULL DEFAULT 'unverified', access_json TEXT NOT NULL DEFAULT '{}');
```

### favoritos

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| usuario_id | INTEGER | sim | 1 | NULL/sem padrão | Usuário proprietário/autor da relação. |
| destino_id | INTEGER | sim | 2 | NULL/sem padrão | Destino referido pela relação. |
| criado_em | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora do registro em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- destino_id → destinos.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- usuario_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE favoritos (usuario_id INTEGER NOT NULL REFERENCES usuarios(id), destino_id INTEGER NOT NULL REFERENCES destinos(id), criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(usuario_id, destino_id));
```

### friendships

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| sender_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário remetente/iniciador. |
| recipient_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário destinatário. |
| status | TEXT | sim | 0 | NULL/sem padrão | Estado da máquina de estados desta tabela; ver CHECK. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- recipient_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- sender_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE friendships (
          id INTEGER PRIMARY KEY, sender_id INTEGER NOT NULL REFERENCES usuarios(id), recipient_id INTEGER NOT NULL REFERENCES usuarios(id),
          status TEXT NOT NULL CHECK(status IN ('pending','accepted','rejected','removed')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CHECK(sender_id != recipient_id));
```

### historico

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| usuario_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário/autor da relação. |
| tipo | TEXT | sim | 0 | NULL/sem padrão | Tipo de atividade de histórico. |
| descricao | TEXT | sim | 0 | NULL/sem padrão | Descrição editorial ou do evento registrado. |
| destino_id | INTEGER | não | 0 | NULL/sem padrão | Destino referido pela relação. |
| criado_em | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora do registro em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- usuario_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE historico (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), tipo TEXT NOT NULL, descricao TEXT NOT NULL, destino_id INTEGER, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### media

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| token | TEXT | não | 1 | NULL/sem padrão | Identificador aleatório opaco de imagem ou link. |
| user_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário ou autor, conforme a tabela. |
| kind | TEXT | sim | 0 | NULL/sem padrão | Tipo avatar/cover. |
| data | BLOB | sim | 0 | NULL/sem padrão | Bytes JPEG em BLOB. |
| mime | TEXT | sim | 0 | 'image/jpeg' | Tipo MIME do conteúdo de mídia. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- user_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE media (
          token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES usuarios(id), kind TEXT NOT NULL CHECK(kind IN ('avatar','cover')),
          data BLOB NOT NULL, mime TEXT NOT NULL DEFAULT 'image/jpeg', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id,kind));
```

### profiles

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| user_id | INTEGER | não | 1 | NULL/sem padrão | Usuário proprietário ou autor, conforme a tabela. |
| handle | TEXT | sim | 0 | NULL/sem padrão | Identificador legível único, usado na URL pública. |
| bio | TEXT | sim | 0 | '' | Apresentação textual do perfil. |
| municipality | TEXT | sim | 0 | '' | Município declarado no perfil, sem geolocalização automática. |
| theme | TEXT | sim | 0 | 'forest' | Tema visual enumerado. |
| is_public | INTEGER | sim | 0 | 0 | Permissão booleana para leitura pública de perfil. |
| discoverable | INTEGER | sim | 0 | 0 | Participação booleana na pesquisa de pessoas. |
| favorites_visibility | TEXT | sim | 0 | 'private' | Política private/friends/public para favoritos. |
| allow_invites | INTEGER | sim | 0 | 1 | Aceitação booleana de convites conforme regras. |
| access_preferences | TEXT | sim | 0 | '[]' | Lista JSON de grupos de necessidades consentidos. |
| access_consent | INTEGER | sim | 0 | 0 | Consentimento booleano para guardar essa lista. |
| avatar_x | INTEGER | sim | 0 | 50 | Posição horizontal percentual do recorte do avatar. |
| avatar_y | INTEGER | sim | 0 | 50 | Posição vertical percentual do recorte do avatar. |
| cover_x | INTEGER | sim | 0 | 50 | Posição horizontal percentual do recorte da capa. |
| cover_y | INTEGER | sim | 0 | 50 | Posição vertical percentual do recorte da capa. |

**Chaves estrangeiras efetivamente declaradas:**

- user_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE profiles (
          user_id INTEGER PRIMARY KEY REFERENCES usuarios(id), handle TEXT NOT NULL UNIQUE COLLATE NOCASE,
          bio TEXT NOT NULL DEFAULT '', municipality TEXT NOT NULL DEFAULT '', theme TEXT NOT NULL DEFAULT 'forest',
          is_public INTEGER NOT NULL DEFAULT 0 CHECK(is_public IN (0,1)), discoverable INTEGER NOT NULL DEFAULT 0 CHECK(discoverable IN (0,1)),
          favorites_visibility TEXT NOT NULL DEFAULT 'private' CHECK(favorites_visibility IN ('private','friends','public')),
          allow_invites INTEGER NOT NULL DEFAULT 1 CHECK(allow_invites IN (0,1)), access_preferences TEXT NOT NULL DEFAULT '[]',
          access_consent INTEGER NOT NULL DEFAULT 0 CHECK(access_consent IN (0,1)),
          avatar_x INTEGER NOT NULL DEFAULT 50, avatar_y INTEGER NOT NULL DEFAULT 50,
          cover_x INTEGER NOT NULL DEFAULT 50, cover_y INTEGER NOT NULL DEFAULT 50);
```

### roteiros_salvos

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| usuario_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário/autor da relação. |
| titulo | TEXT | sim | 0 | NULL/sem padrão | Título do roteiro. |
| conteudo | TEXT | sim | 0 | NULL/sem padrão | JSON do roteiro salvo. |
| criado_em | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora do registro em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- usuario_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE roteiros_salvos (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), titulo TEXT NOT NULL, conteudo TEXT NOT NULL, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### schema_migrations

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| version | INTEGER | não | 1 | NULL/sem padrão | Versão de migração aplicada. |
| applied_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de aplicação da migração. |

**Chaves estrangeiras efetivamente declaradas:**

Nenhuma.


**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### trip_invites

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| trip_id | INTEGER | sim | 0 | NULL/sem padrão | Roteiro relacionado. |
| sender_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário remetente/iniciador. |
| recipient_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário destinatário. |
| status | TEXT | sim | 0 | 'pending' | Estado da máquina de estados desta tabela; ver CHECK. |
| role | TEXT | sim | 0 | 'editor' | Papel viewer/editor do convidado. |

**Chaves estrangeiras efetivamente declaradas:**

- recipient_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- sender_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- trip_id → roteiros_salvos.id; ON UPDATE NO ACTION; ON DELETE CASCADE.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE trip_invites (
          id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          sender_id INTEGER NOT NULL REFERENCES usuarios(id), recipient_id INTEGER NOT NULL REFERENCES usuarios(id),
          status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected','revoked')),
          role TEXT NOT NULL DEFAULT 'editor' CHECK(role IN ('viewer','editor')), UNIQUE(trip_id,recipient_id));
```

### trip_notes

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| trip_id | INTEGER | sim | 0 | NULL/sem padrão | Roteiro relacionado. |
| user_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário proprietário ou autor, conforme a tabela. |
| text | TEXT | sim | 0 | NULL/sem padrão | Texto da nota de colaboração. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- user_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- trip_id → roteiros_salvos.id; ON UPDATE NO ACTION; ON DELETE CASCADE.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE trip_notes (
          id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          user_id INTEGER NOT NULL REFERENCES usuarios(id), text TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### trip_shares

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| token | TEXT | não | 1 | NULL/sem padrão | Identificador aleatório opaco de imagem ou link. |
| trip_id | INTEGER | sim | 0 | NULL/sem padrão | Roteiro relacionado. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

- trip_id → roteiros_salvos.id; ON UPDATE NO ACTION; ON DELETE CASCADE.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE trip_shares (
          token TEXT PRIMARY KEY, trip_id INTEGER NOT NULL UNIQUE REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### usuarios

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| nome | TEXT | sim | 0 | NULL/sem padrão | Nome de apresentação do destino ou da pessoa. |
| email | TEXT | sim | 0 | NULL/sem padrão | Identificação de login, única sem distinção de caixa. |
| senha_hash | TEXT | sim | 0 | NULL/sem padrão | Hash de senha, nunca senha original. |
| interesses | TEXT | sim | 0 | '[]' | Lista JSON de interesses turísticos. |
| criado_em | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora do registro em UTC pelo padrão SQLite. |

**Chaves estrangeiras efetivamente declaradas:**

Nenhuma.


**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE usuarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, senha_hash TEXT NOT NULL, interesses TEXT NOT NULL DEFAULT '[]', criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
```

### vouchers

| Coluna | Tipo | NOT NULL no PRAGMA | Posição PK | Padrão SQL | Significado |
|---|---|---|---:|---|---|
| id | INTEGER | não | 1 | NULL/sem padrão | Identificador da linha. |
| code | TEXT | sim | 0 | NULL/sem padrão | Código aleatório do voucher simbólico. |
| sender_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário remetente/iniciador. |
| recipient_id | INTEGER | sim | 0 | NULL/sem padrão | Usuário destinatário. |
| destination_id | INTEGER | sim | 0 | NULL/sem padrão | Destino referido. |
| message | TEXT | sim | 0 | NULL/sem padrão | Mensagem do presente. |
| theme | TEXT | sim | 0 | NULL/sem padrão | Tema visual enumerado. |
| expires_at | TEXT | sim | 0 | NULL/sem padrão | Prazo de validade do voucher, ISO com fuso UTC. |
| status | TEXT | sim | 0 | 'issued' | Estado da máquina de estados desta tabela; ver CHECK. |
| created_at | TEXT | sim | 0 | CURRENT_TIMESTAMP | Data/hora de criação em UTC pelo padrão SQLite. |
| redeemed_at | TEXT | não | 0 | NULL/sem padrão | Data/hora do resgate simbólico, ou NULL. |

**Chaves estrangeiras efetivamente declaradas:**

- destination_id → destinos.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- recipient_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.
- sender_id → usuarios.id; ON UPDATE NO ACTION; ON DELETE NO ACTION.

**DDL real — inclui CHECK, UNIQUE, DEFAULT e composição da chave:**

```sql
CREATE TABLE vouchers (
          id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, sender_id INTEGER NOT NULL REFERENCES usuarios(id),
          recipient_id INTEGER NOT NULL REFERENCES usuarios(id), destination_id INTEGER NOT NULL REFERENCES destinos(id),
          message TEXT NOT NULL, theme TEXT NOT NULL CHECK(theme IN ('azulejo','sol','reggae')),
          expires_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'issued'
          CHECK(status IN ('issued','sent','redeemed','expired','cancelled')),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, redeemed_at TEXT,
          CHECK(sender_id != recipient_id));
```

### Índices reais

Índices automáticos (sqlite_autoindex) implementam unicidade/chaves; SQL nulo não significa ausência de índice. O índice friendship_pair impede duplicar um par invertendo remetente e destinatário. Os índices de filtro não fazem a busca textual em Python virar SQL indexado.

| Índice | Definição |
|---|---|
| dest_filters | CREATE INDEX dest_filters ON destinos(municipio,category) |
| friend_recipient | CREATE INDEX friend_recipient ON friendships(recipient_id,status) |
| friendship_pair | CREATE UNIQUE INDEX friendship_pair ON friendships(min(sender_id,recipient_id),max(sender_id,recipient_id)) |
| invite_recipient | CREATE INDEX invite_recipient ON trip_invites(recipient_id,status) |
| ix_hist_user | CREATE INDEX ix_hist_user ON historico(usuario_id, criado_em) |
| ix_trips_user | CREATE INDEX ix_trips_user ON roteiros_salvos(usuario_id, criado_em) |
| sqlite_autoindex_avaliacoes_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_blocks_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_destinos_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_favoritos_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_media_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_media_2 | Automático de PK/UNIQUE |
| sqlite_autoindex_profiles_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_trip_invites_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_trip_shares_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_trip_shares_2 | Automático de PK/UNIQUE |
| sqlite_autoindex_usuarios_1 | Automático de PK/UNIQUE |
| sqlite_autoindex_vouchers_1 | Automático de PK/UNIQUE |
| voucher_recipient | CREATE INDEX voucher_recipient ON vouchers(recipient_id,status) |

### Exemplos didáticos, sem dados reais

```sql
-- Consulta de catálogo, sem dados de usuários:
SELECT id, nome, municipio, coordinates_status FROM destinos ORDER BY municipio, nome;
-- Relação: a aplicação envia os parâmetros separadamente do SQL:
SELECT d.nome FROM favoritos f JOIN destinos d ON d.id=f.destino_id
WHERE f.usuario_id=?;
-- Estes números seriam fictícios em uma explicação de quadro:
-- usuário 9001 tem favorito destino 9002; o par não pode se repetir.
```

Não executar INSERTs didáticos na base real. O exemplo de parâmetro “?” precisa de binding pela biblioteca, não substituição textual de strings.

## 12. Índice completo de funções Python e pontos de entrada

Assinaturas e linhas extraídas da AST. Helpers aninhados compartilham dependências do escopo. A responsabilidade dos handlers está no contrato HTTP; os testes têm objetivos no documento09. Bibliotecas de terceiros não são autoria do projeto.

| Arquivo:linha | Função e parâmetros |
|---|---|
| backend/app.py:37 | `protect_writes()` |
| backend/app.py:48 | `login_required(handler)` |
| backend/app.py:56 | `record_history(kind, label, item_id=None)` |
| backend/app.py:83 | `get_connection()` |
| backend/app.py:94 | `init_database()` |
| backend/app.py:140 | `atualizar_coordenadas_iniciais()` |
| backend/app.py:157 | `row_to_dict(row: sqlite3.Row)` |
| backend/app.py:174 | `home()` |
| backend/app.py:183 | `internal_pages()` |
| backend/app.py:187 | `explorar_page()` |
| backend/app.py:191 | `planejar_page()` |
| backend/app.py:195 | `health()` |
| backend/app.py:199 | `culture_bookmark()` |
| backend/app.py:203 | `culture_content_api()` |
| backend/app.py:208 | `pesquisar_destinos()` |
| backend/app.py:242 | `gerar_roteiro()` |
| backend/app.py:348 | `verificar_destinos()` |
| backend/app.py:362 | `register()` |
| backend/app.py:379 | `login()` |
| backend/app.py:391 | `me()` |
| backend/app.py:402 | `logout()` |
| backend/app.py:408 | `edit_profile()` |
| backend/app.py:420 | `history()` |
| backend/app.py:427 | `clear_history()` |
| backend/app.py:434 | `favorites()` |
| backend/app.py:441 | `add_favorite(destination_id)` |
| backend/app.py:452 | `remove_favorite(destination_id)` |
| backend/app.py:459 | `saved_trips()` |
| backend/app.py:466 | `save_trip()` |
| backend/app.py:485 | `delete_trip(trip_id)` |
| backend/app.py:491 | `reviews(destination_id)` |
| backend/app.py:498 | `submit_review(destination_id)` |
| backend/app.py:512 | `summary_stats()` |
| backend/app.py:50 | `decorated(*args, **kwargs)` |
| backend/app.py:212 | `normalized(value)` |
| backend/catalog.py:98 | `seed_catalog(connect)` |
| backend/culture.py:11 | `cultural_content()` |
| backend/culture.py:14 | `destination_culture(name)` |
| backend/expansion.py:17 | `confirmed_features(destination, fields)` |
| backend/expansion.py:23 | `install(app, connect, login_required, serialize_destination, frontend_dir)` |
| backend/expansion.py:24 | `fail(message, code=400)` |
| backend/expansion.py:27 | `body()` |
| backend/expansion.py:30 | `uid()` |
| backend/expansion.py:33 | `text(data, key, maximum, default='')` |
| backend/expansion.py:39 | `profile(con, user_id)` |
| backend/expansion.py:43 | `media_urls(con, user_id)` |
| backend/expansion.py:46 | `own_profile(con)` |
| backend/expansion.py:54 | `blocked(con, left, right)` |
| backend/expansion.py:57 | `friends(con, left, right)` |
| backend/expansion.py:60 | `public_person(con, user_id)` |
| backend/expansion.py:66 | `trip_access(con, trip_id, editor=False)` |
| backend/expansion.py:80 | `http_error(error)` |
| backend/expansion.py:87 | `invalid_data(error)` |
| backend/expansion.py:92 | `get_profile_settings()` |
| backend/expansion.py:98 | `update_profile_settings()` |
| backend/expansion.py:134 | `upload_profile_media(kind)` |
| backend/expansion.py:166 | `serve_profile_media(token)` |
| backend/expansion.py:179 | `people_search()` |
| backend/expansion.py:188 | `public_profile(handle)` |
| backend/expansion.py:203 | `list_friends()` |
| backend/expansion.py:216 | `friendship_action(other)` |
| backend/expansion.py:249 | `invite_to_trip(trip_id)` |
| backend/expansion.py:261 | `trip_invites()` |
| backend/expansion.py:268 | `respond_trip_invite(invite_id)` |
| backend/expansion.py:282 | `shared_trip(trip_id)` |
| backend/expansion.py:292 | `add_trip_note(trip_id)` |
| backend/expansion.py:302 | `rename_shared_trip(trip_id)` |
| backend/expansion.py:312 | `share_trip_link(trip_id)` |
| backend/expansion.py:324 | `public_trip_link(token)` |
| backend/expansion.py:330 | `expire_vouchers(con)` |
| backend/expansion.py:335 | `list_vouchers()` |
| backend/expansion.py:343 | `issue_voucher()` |
| backend/expansion.py:360 | `transition_voucher(voucher_id)` |
| backend/expansion.py:379 | `accessibility_metadata()` |
| backend/expansion.py:384 | `accessibility_report()` |
| backend/expansion.py:396 | `feature_page()` |
| backend/expansion.py:402 | `destination_detail(destination_id)` |
| backend/migrations.py:18 | `migrate(connect, database_path)` |
| backend/migrations.py:91 | `destination_metadata(row)` |
| backend/moderate_accessibility.py:13 | `main()` |
| browser_corrections.py:14 | `main()` |
| browser_corrections.py:37 | `go(path)` |
| browser_corrections.py:46 | `shot(name)` |
| browser_corrections.py:48 | `compare_map(query='', legacy=False, home=False)` |
| browser_corrections.py:103 | `hold(route)` |
| browser_expansion.py:13 | `main()` |
| browser_expansion.py:28 | `register(context, email, name, handle)` |
| browser_expansion.py:40 | `go(page, path)` |
| browser_expansion.py:45 | `shot(page, name)` |
| test_api.py:24 | `setUpClass(cls)` |
| test_api.py:27 | `setUp(self)` |
| test_api.py:35 | `register(self, client=None, email='ana@example.test')` |
| test_api.py:41 | `test_original_health_search_and_route(self)` |
| test_api.py:50 | `test_all_pages_and_assets(self)` |
| test_api.py:57 | `test_authentication_profile_and_persistence(self)` |
| test_api.py:71 | `test_authentication_and_csrf_guards(self)` |
| test_api.py:81 | `test_favorites_are_idempotent_and_persistent(self)` |
| test_api.py:95 | `test_saved_trips_and_user_isolation(self)` |
| test_api.py:118 | `test_invalid_payloads_return_json_errors(self)` |
| test_api.py:134 | `test_reviews_and_database_integrity(self)` |
| test_browser.py:17 | `main()` |
| test_browser.py:13 | `log(self, *args, **kwargs)` |
| test_browser.py:40 | `loaded(path)` |
| test_browser.py:44 | `screenshot(name)` |
| test_corrections.py:12 | `test_location_totals_match_the_filtered_payload(self)` |
| test_corrections.py:21 | `test_invalid_coordinates_never_become_zero_or_verified(self)` |
| test_corrections.py:32 | `test_culture_is_preserved_associated_and_filterable(self)` |
| test_corrections.py:49 | `test_planner_uses_specific_culture_without_fabricating_places(self)` |
| test_expansion.py:25 | `new_user(self, email, handle)` |
| test_expansion.py:31 | `pair(self)` |
| test_expansion.py:38 | `save(self, client, headers)` |
| test_expansion.py:42 | `test_catalog_sources_idempotency_and_filters(self)` |
| test_expansion.py:66 | `test_profile_defaults_handle_and_consent(self)` |
| test_expansion.py:84 | `test_upload_content_limits_privacy_and_removal(self)` |
| test_expansion.py:104 | `test_people_search_does_not_expose_private_data(self)` |
| test_expansion.py:115 | `test_friend_rejection_removal_block_and_unblock(self)` |
| test_expansion.py:133 | `test_favorites_visibility_and_history_privacy(self)` |
| test_expansion.py:144 | `test_trip_invitation_collaboration_and_link_revocation(self)` |
| test_expansion.py:163 | `test_viewer_permission_and_declined_invites(self)` |
| test_expansion.py:177 | `test_voucher_lifecycle_and_ownership(self)` |
| test_expansion.py:191 | `test_voucher_expiration_cancellation_and_block(self)` |
| test_expansion.py:205 | `test_accessibility_reports_do_not_self_publish(self)` |
| test_expansion.py:222 | `test_themes_and_new_pages(self)` |
| test_expansion.py:230 | `test_local_moderation_workflow(self)` |
| test_expansion.py:243 | `test_migration_preserves_legacy_data_and_backup(self)` |
| test_expansion.py:247 | `connect()` |

### Registro real de rotas Flask

Lista obtida da aplicação inicializada sobre cópia temporária; inclui rota estática e métodos automáticos. Serve para distinguir rota de página, API e asset.

| Regra | Métodos | Endpoint |
|---|---|---|
| /<path:filename> | GET, HEAD, OPTIONS | static |
| / | GET, HEAD, OPTIONS | home |
| /acessibilidade | GET, HEAD, OPTIONS | internal_pages |
| /meus-roteiros | GET, HEAD, OPTIONS | internal_pages |
| /favoritos | GET, HEAD, OPTIONS | internal_pages |
| /historico | GET, HEAD, OPTIONS | internal_pages |
| /perfil | GET, HEAD, OPTIONS | internal_pages |
| /explorar | GET, HEAD, OPTIONS | explorar_page |
| /planejar | GET, HEAD, OPTIONS | planejar_page |
| /api/health | GET, HEAD, OPTIONS | health |
| /cultura | GET, HEAD, OPTIONS | culture_bookmark |
| /api/culture | GET, HEAD, OPTIONS | culture_content_api |
| /api/destinos | GET, HEAD, OPTIONS | pesquisar_destinos |
| /api/roteiro | OPTIONS, POST | gerar_roteiro |
| /api/destinos/verificar | GET, HEAD, OPTIONS | verificar_destinos |
| /api/auth/register | OPTIONS, POST | register |
| /api/auth/login | OPTIONS, POST | login |
| /api/auth/me | GET, HEAD, OPTIONS | me |
| /api/auth/logout | OPTIONS, POST | logout |
| /api/perfil | OPTIONS, PATCH | edit_profile |
| /api/historico | GET, HEAD, OPTIONS | history |
| /api/historico | DELETE, OPTIONS | clear_history |
| /api/favoritos | GET, HEAD, OPTIONS | favorites |
| /api/favoritos/<int:destination_id> | OPTIONS, PUT | add_favorite |
| /api/favoritos/<int:destination_id> | DELETE, OPTIONS | remove_favorite |
| /api/roteiros-salvos | GET, HEAD, OPTIONS | saved_trips |
| /api/roteiros-salvos | OPTIONS, POST | save_trip |
| /api/roteiros-salvos/<int:trip_id> | DELETE, OPTIONS | delete_trip |
| /api/avaliacoes/<int:destination_id> | GET, HEAD, OPTIONS | reviews |
| /api/avaliacoes/<int:destination_id> | OPTIONS, POST | submit_review |
| /api/resumo | GET, HEAD, OPTIONS | summary_stats |
| /api/profile-settings | GET, HEAD, OPTIONS | get_profile_settings |
| /api/profile-settings | OPTIONS, PATCH | update_profile_settings |
| /api/profile-media/<kind> | DELETE, OPTIONS, POST | upload_profile_media |
| /media/<token> | GET, HEAD, OPTIONS | serve_profile_media |
| /api/people | GET, HEAD, OPTIONS | people_search |
| /api/public-profile/<handle> | GET, HEAD, OPTIONS | public_profile |
| /api/friends | GET, HEAD, OPTIONS | list_friends |
| /api/friends/<int:other> | OPTIONS, POST | friendship_action |
| /api/trips/<int:trip_id>/invites | OPTIONS, POST | invite_to_trip |
| /api/trip-invites | GET, HEAD, OPTIONS | trip_invites |
| /api/trip-invites/<int:invite_id> | OPTIONS, POST | respond_trip_invite |
| /api/trips/<int:trip_id> | GET, HEAD, OPTIONS | shared_trip |
| /api/trips/<int:trip_id>/notes | OPTIONS, POST | add_trip_note |
| /api/trips/<int:trip_id> | OPTIONS, PATCH | rename_shared_trip |
| /api/trips/<int:trip_id>/share | DELETE, OPTIONS, POST | share_trip_link |
| /api/shared/<token> | GET, HEAD, OPTIONS | public_trip_link |
| /api/vouchers | GET, HEAD, OPTIONS | list_vouchers |
| /api/vouchers | OPTIONS, POST | issue_voucher |
| /api/vouchers/<int:voucher_id>/transition | OPTIONS, POST | transition_voucher |
| /api/accessibility | GET, HEAD, OPTIONS | accessibility_metadata |
| /api/accessibility-reports | GET, HEAD, OPTIONS, POST | accessibility_report |
| /catalogo | GET, HEAD, OPTIONS | expansion_page_0 |
| /amigos | GET, HEAD, OPTIONS | expansion_page_1 |
| /presentes | GET, HEAD, OPTIONS | expansion_page_2 |
| /configuracoes | GET, HEAD, OPTIONS | expansion_page_3 |
| /destino/<int:destination_id> | GET, HEAD, OPTIONS | expansion_page_4 |
| /p/<handle> | GET, HEAD, OPTIONS | expansion_page_5 |
| /s/<token> | GET, HEAD, OPTIONS | expansion_page_6 |
| /roteiro-compartilhado/<int:trip_id> | GET, HEAD, OPTIONS | expansion_page_7 |
| /api/destinos/<int:destination_id> | GET, HEAD, OPTIONS | destination_detail |
## 13. Exemplo de roteiro efetivamente executado

Banco de trabalho: cópia temporária da base; nenhum usuário real necessário. Resultado: HTTP 200.

**Requisição:**

```json
{
  "destination": "São Luís",
  "days": 2,
  "budget": 800,
  "people": "2",
  "transport": "A pé",
  "interests": [
    "Reggae"
  ],
  "access": []
}
```

**Resposta integral:**

```json
{
  "days": [
    {
      "stops": [
        {
          "description": "Uma aproximação com a memória musical do reggae.",
          "icon": "🏛",
          "name": "Museu do Reggae"
        }
      ],
      "title": "Dia 1 · Comece explorando"
    },
    {
      "stops": [
        {
          "description": "Uma aproximação com a memória musical do reggae.",
          "icon": "🏛",
          "name": "Museu do Reggae"
        }
      ],
      "title": "Dia 2 · Feche a viagem com boas memórias"
    }
  ],
  "note": "Sugestão editorial baseada no catálogo local. Não há validação de trajeto, travessias, transporte ou continuidade das calçadas. Recursos de acessibilidade selecionados exigem fonte e data por local. Confirme condições, custos e horários antes de sair.",
  "plain_text": "Roteiro Explore+ SLZ — São Luís, 2 dia(s), orçamento 800.00 BRL\n\nDia 1 · Comece explorando\n- Museu do Reggae: Uma aproximação com a memória musical do reggae.\n\nDia 2 · Feche a viagem com boas memórias\n- Museu do Reggae: Uma aproximação com a memória musical do reggae.\n\nSugestão inicial: confirme horários, deslocamentos, custos e acessibilidade antes de sair.",
  "special_experience": null,
  "summary": {
    "access": [],
    "budget": 800.0,
    "days": 2,
    "destination": "São Luís",
    "interests": [
      "Reggae"
    ],
    "people": "2",
    "per_day": 400.0,
    "per_person_day": 200.0,
    "transport": "A pé"
  }
}
```

## 14. Localização de declarações JavaScript


O índice identifica funções nomeadas, métodos de objeto, propriedades de renderização e helpers com arrow function. Handlers anônimos são explicados pelos eventos do documento02. Linhas compactas podem conter vários símbolos.


| Arquivo:linha | Declarações |
|---|---|
| frontend/account.js:3 | applyTheme |
| frontend/account.js:8 | preference |
| frontend/account.js:12 | applyPreferences |
| frontend/account.js:17 | api |
| frontend/account.js:25 | init |
| frontend/account.js:35 | auth |
| frontend/account.js:41 | logout |
| frontend/account.js:45 | updateUI |
| frontend/catalogo.js:3 | catalog |
| frontend/catalogo.js:11 | present |
| frontend/catalogo.js:17 | search |
| frontend/catalogo.js:26 | detail |
| frontend/configuracoes.js:3 | settings |
| frontend/configuracoes.js:10 | setState |
| frontend/configuracoes.js:11 | revoke |
| frontend/configuracoes.js:52 | publicProfile |
| frontend/cultura.js:4 | cultureContext |
| frontend/cultura.js:5 | cultureDiscovery |
| frontend/cultura.js:6 | culture |
| frontend/experiencias.js:2 | $ |
| frontend/experiencias.js:3 | h |
| frontend/experiencias.js:4 | api |
| frontend/experiencias.js:5 | box |
| frontend/experiencias.js:8 | safeURL |
| frontend/experiencias.js:10 | notice |
| frontend/experiencias.js:11 | heading |
| frontend/experiencias.js:12 | check |
| frontend/experiencias.js:13 | people |
| frontend/experiencias.js:14 | action |
| frontend/experiencias.js:15 | values |
| frontend/experiencias.js:16 | date |
| frontend/experiencias.js:17 | tripHTML |
| frontend/experiencias.js:18 | catalogCard |
| frontend/experiencias.js:21 | reload |
| frontend/maps.js:3 | h |
| frontend/maps.js:4 | create |
| frontend/maps.js:14 | icon |
| frontend/maps.js:20 | eligible |
| frontend/maps.js:21 | updateStatus |
| frontend/maps.js:28 | setPlaces |
| frontend/maps.js:41 | focus |
| frontend/maps.js:44 | reveal |
| frontend/maps.js:53 | snapshot |
| frontend/maps.js:54 | destroy |
| frontend/navigation.js:6 | active |
| frontend/navigation.js:9 | close |
| frontend/navigation.js:10 | open |
| frontend/navigation.js:20 | refreshNavigation |
| frontend/painel.js:1 | $ |
| frontend/painel.js:2 | esc |
| frontend/painel.js:3 | api |
| frontend/painel.js:12 | money |
| frontend/painel.js:13 | dateLabel |
| frontend/painel.js:19 | toast |
| frontend/painel.js:23 | content |
| frontend/painel.js:24 | empty |
| frontend/painel.js:25 | sectionHead |
| frontend/painel.js:26 | historyList |
| frontend/painel.js:27 | favoriteList |
| frontend/painel.js:28 | tripList |
| frontend/painel.js:34 | identity |
| frontend/painel.js:56 | profileForm |
| frontend/painel.js:59 | runAction |
| frontend/painel.js:65 | bindCollections |
| frontend/painel.js:84 | bindProfile |
| frontend/painel.js:99 | renderAccessibility |
| frontend/painel.js:109 | load |
| frontend/painel.js:140 | setSize |
| frontend/script.js:2 | $ |
| frontend/script.js:22 | toast |
| frontend/script.js:31 | money |
| frontend/script.js:73 | escapeHTML |
| frontend/script.js:85 | searchDestinations |
| frontend/script.js:208 | openModal |
| frontend/script.js:209 | closeModal |
| frontend/script.js:226 | loadFavs |
| frontend/script.js:236 | sync |
| frontend/script.js:239 | go |
| frontend/social.js:3 | friends |
| frontend/social.js:8 | bind |
| frontend/social.js:14 | gifts |
| frontend/social.js:23 | collaborate |
