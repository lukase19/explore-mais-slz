# Cada página, botão, campo e componente

**Versão observada:** 06/11/2026. Os nomes de funções e atributos são pontos de localização no código; alguns handlers são anônimos dentro de funções de renderização. Tabelas descrevem classes de controles repetidos: cada coração de um card executa o mesmo contrato com o ID correspondente.

## 1. Convenções de interação aplicáveis às telas

`ExploreAccount.api(path, options)`, em `frontend/account.js`, centraliza fetch, cookies de mesma origem, JSON e CSRF. Métodos de escrita autenticados recebem `X-CSRF-Token`; FormData de upload não recebe Content-Type JSON, para o navegador construir o multipart. Erro HTTP gera exceção com a mensagem da API.

Botões associados a `F.action`, de `experiencias.js`, ficam desabilitados durante a ação, mostram aviso de resultado e eventualmente recarregam o conteúdo. Formulários de imagens têm tratamento próprio para preservar os estados de envio. Erros de tela dinâmica exibem alerta e repetição; não devem ser confundidos com um resultado vazio legítimo.

As páginas usam cabeçalho compartilhado, fundos claros, cartões, cor primária e detalhes amarelos/terrosos da identidade existente. Temas mudam tokens de cor; alto contraste é uma preferência adicional. Em celular, grades empilham e menus ficam contidos na largura. Isso foi verificado em percursos específicos a 320, 390, 768 e 1440 px, não em todo aparelho existente.

## 2. Cabeçalho, menu, rodapé e autenticação

**Arquivo:** `frontend/navigation.js`. O script substitui a navegação de fallback nos três HTMLs. A marca remete à entrada do site; avatar remete ao perfil. O menu é uma navegação de links, não uma aplicação do padrão ARIA de menu desktop.

| Elemento / localização | Evento e função | Dados e destino | Resultado / falha |
|---|---|---|---|
| Botão de três barras `#siteMenuToggle` | clique alterna; ArrowDown abre e foca primeiro link; handlers em navigation.js | Sem API | `aria-expanded` atualizado |
| Fechar menu | Escape, clique externo, foco saindo ou navegação | Sem API | Escape devolve foco ao botão |
| Início | link | `/` | Página inicial |
| Explorar | link | `/catalogo` | Catálogo completo |
| Planejar | link | `/planejar#roteiro` | Mesmo HTML inicial, âncora no formulário |
| Amigos | link | `/amigos` | Exige conta para dados |
| Favoritos | link | `/favoritos` | Lista pessoal |
| Histórico | link | `/historico` | Eventos pessoais |
| Meus roteiros | link | `/meus-roteiros` | Coleção pessoal |
| Meu perfil | link / avatar | `/perfil` | Visão geral pessoal |
| Configurações | link | `/configuracoes` | Personalização |
| Entrar/criar conta | abre modal nos contextos que o possuem ou encaminha à entrada | Sem API até enviar | Login visível quando anônimo |
| Sair `#logoutBtn` | `ExploreAccount.logout` | POST `/api/auth/logout` | Limpa estado, tema padrão e navega a /; erro é informado |
| Avatar do cabeçalho | `refreshNavigation` | perfil em memória | Foto autorizada ou inicial do nome |
| Links do rodapé | links/âncoras presentes no HTML | Rotas/seções locais | Rodapé não é painel administrativo |
| Pular para conteúdo | link de salto | ID do conteúdo principal | Evita repetir navegação por teclado |

Acessibilidade e Presentes existem, mas não são dois itens extras duplicados no menu principal. Acessibilidade é alcançável pelo painel/configurações e Presentes pelo contexto social. `/cultura` redireciona para `/catalogo#cultura`; não é mais uma página isolada de conteúdo.

### Modal de conta da página inicial

**Arquivos:** `frontend/index.html`, `frontend/script.js`, `account.js`.

| Controle/campo | Regra | Ação e persistência | Resposta e erros |
|---|---|---|---|
| `#accountName` | Cadastro, 2–100 caracteres no servidor | Enviado como `name` | Oculto e não obrigatório no login |
| `#accountEmail` | E-mail, 5–254 e @ no servidor | `email` normalizado; usuarios | Formato inválido 400, duplicado 409 |
| `#accountPassword` | 8–128 no cadastro | `password`; só hash é persistido | Login incorreto 401 |
| `#switchMode` | Alterna entrar/cadastrar | `isRegister` muda rótulos, autocomplete e nome | Não cria conta só por alternar |
| `#accountSubmit` | submit | `ExploreAccount.auth`: POST register ou login | Sucesso carrega perfil e vai a /perfil |
| `#modalClose` | clique | Fecha modal | Restaura conteúdo e foco |
| Fundo do modal/Escape | clique fora/Escape | Fecha | Sem chamada de API |
| Tab/Shift+Tab | teclado | Contenção nos elementos visíveis | Teste percorreu retorno ao primeiro controle |

Enquanto aberto, áreas de fundo recebem `inert`. O formulário não oferece “Esqueci minha senha”, login social ou alteração de e-mail. Mensagem “Token de segurança inválido” em ações pessoais indica falha CSRF, não necessariamente senha errada. A ação de entrar usa a mesma origem; não há serviço externo de identidade.

## 3. Início e exploração preservada — / e /explorar

**Objetivo:** apresentar a proposta, destacar espaços, pesquisar, mostrar mapa e iniciar planejamento. **HTML:** index.html. **Controlador:** script.js. **Dados:** destinos, cultura, sessão e favoritos; histórico apenas quando há conta e ação registrada.

**Elementos visuais:** hero, imagem embutida, títulos, botões de descoberta/planejamento, blocos de benefícios, cards de locais, filtros de interesses, área do mapa, cards de orçamento, formulário, resultado, rodapé e avisos.

Os blocos informativos de benefícios e faixas de orçamento não são todos controles clicáveis. Um desenho de seta ou um valor não prova existência de link. Os CTAs reais usam âncoras de navegação; os cards de destino receberam interação explícita.

| Controle | Handler / envio | Retorno visual | Erros e limites |
|---|---|---|---|
| CTA planejar | Âncora `#roteiro` | Rolagem ao formulário | Sem geração automática |
| CTA descobrir | Âncora da seção / link de catálogo | Exploração | Não é reserva |
| Campo `#destinationSearch` | input com debounce 250 ms; q | Resultados de GET /api/destinos | Cancela busca anterior; falha mostra estado |
| `#destinationSearchButton` / Enter | Dispara consulta imediata | Lista/contador/mapa sincronizados | Texto sem resultado não é pane |
| Filtros `#placeFilters .filter` | `activeInterest`; GET com interest | `aria-pressed`; cards compatíveis | Mantêm cultura da URL |
| Opções Todos, História, Cultura, Praia, Natureza, Gastronomia | `data-k` e mapeamento de interesse | Todos limpa interest | “Praia” usa busca textual, não geolocalização |
| Resultado textual `data-place` | `focusPlace` → homeMap.focus | Foco/popup se marcador elegível | Sem coordenada: aviso; não inventa ponto |
| Card estático de local | clique, Enter e Espaço | Mesmo foco cartográfico | Pode estar fora dos filtros atuais |
| Coração `.fav` | resolve destino; PUT/DELETE /api/favoritos/id | `aria-pressed`, marca visual e toast | Anônimo abre login; API falha mantém aviso |
| Link Ver catálogo | link para /catalogo | Pesquisa completa | Sem login |
| `#homeLegacy` | change → setPlaces em coleção atual | Admite pontos legados válidos | Não valida sua posição física |
| Toast `#toast` | mensagens de operações | Aviso temporário ~3,5 s | Não é histórico persistente |

Cards estáticos: Centro Histórico, Espigão Costeiro, Praia do Calhau, Casa do Maranhão, passeio de barco em Raposa e Restaurante Feijão de Corda. O nome exibido de Raposa pode usar alias para resolver o registro “Passeios de barco”. Essa grade não é uma enumeração de todos os 76 destinos.

Antes do login, pesquisa e geração funcionam; favoritos e salvamento exigem conta. Depois, os corações refletem os favoritos. O banco não registra automaticamente cada clique em card. Em telas de até aproximadamente 850 px, a ação de foco também conduz a visualização ao mapa.

**Acessibilidade:** cards operáveis por teclado, corações com estado, rótulos nos campos, modal com foco. **Limites:** a presença de um card não garante ponto no mapa; o mapa começa sem pontos verificados nesta base; imagens embutidas e blocos estáticos não são atualizados por um CMS.

## 4. Planejamento — /planejar#roteiro e seção da inicial

**Objetivo:** transformar preferências em uma sugestão organizada. A rota /planejar sozinha serve o HTML inicial; a âncora é que posiciona o usuário. **APIs:** POST /api/roteiro, POST /api/roteiros-salvos. **Persistência:** gerar pode registrar histórico; salvar cria roteiro do usuário.

### Campos e opções reais

| Campo HTML | Opções / tipo | Tratamento |
|---|---|---|
| `destination` | São Luís; São José de Ribamar; Raposa; Paço do Lumiar; Alcântara; Ilha de São Luís | Região de seleção; ilha exclui Alcântara na consulta |
| `days` | 1, 2, 3, 4, 5, 7 | Interface seleciona duração; API admite 1–30 |
| `budget` | número, mínimo 1, passo 0,01 | Orçamento total >0; finito |
| `people` | 1, 2, 3, 4, 5, “6 ou mais” | Interpretação numérica para divisão |
| `transport` | Carro; Transporte público; Aplicativo/táxi; A pé; Ainda não decidi | Informação do resumo, sem cálculo de rota |
| `interest` | História, Praias, Gastronomia, Natureza, Cultura, Família | Seleção múltipla comum |
| `interest` cultural | Reggae, Bumba Meu Boi, Tambor de Crioula, Cacuriá, Azulejaria, Gastronomia maranhense, Artesanato | Associação a conteúdo/destinos reais |
| `access` | Mobilidade reduzida; Deficiência visual; Deficiência auditiva; Intelectual/cognitiva; Necessidades sensoriais; Crianças | Grupos de campos; Crianças não exige campo físico |
| Tema da URL | historia, reggae, sabores, popular, quilombo, vazio | Entrada adicional suportada no código, não um seletor visível equivalente a todos os interesses |

### Ações do resultado

| Controle | Evento / dados | Resposta | Erro |
|---|---|---|---|
| Gerar roteiro | submit tripForm; destination/days/budget/people/transport/interests/access/theme | Botão indica preparação; dias e resumo renderizados | Falta de interesse/orçamento: validação; 400 inválido; 404 região vazia; 422 requisitos sem candidatos |
| Usar minhas preferências de acessibilidade | Lê ExploreAccount.profile, consentimento e grupos | Marca as necessidades correspondentes | Sem consentimento/dados informa limite; não ativa dados ocultos |
| Salvar roteiro `#saveTrip` | POST título automático e JSON trip | “Roteiro salvo no seu perfil!” | Anônimo recebe orientação/modal; falha informada |
| Compartilhar no WhatsApp | Link wa.me com plain_text codificado | Abre serviço externo | Não confirma entrega nem destinatário |
| Copiar roteiro | Clipboard API, plain_text | Aviso de cópia | Rejeição da área de transferência tratada |
| Links da experiência especial | URL do operador no bloco | Abre referência externa | Não verifica disponibilidade, reserva ou preço |
| Paradas e pausa de almoço | Conteúdo renderizado | Explicação do dia | A pausa genérica não representa estabelecimento cadastrado |

O orçamento exibido na página inicial usa formatação monetária sem casas decimais; a API mantém o valor decimal. O painel usa formatação com duas casas em seus próprios resumos. Essa diferença é apresentação, não alteração deliberada do orçamento salvo.

No celular, formulário e cards se reorganizam verticalmente; o usuário ainda precisa selecionar e enviar. Acessibilidade física solicitada é condição de dados, não uma declaração de rota acessível. O resultado orienta confirmar custos, horários, transporte e acesso.

## 5. Catálogo — /catalogo

**Objetivo:** listar todo o catálogo com filtros combináveis, contexto e mapa. **Arquivos:** experiencias.html, experiencias.js, catalogo.js, cultura.js, maps.js. **Login:** leitura pública; dados pessoais não são necessários para pesquisar.

| Controle/campo | Dados / função | Efeito e armazenamento | Falhas |
|---|---|---|---|
| Texto `q` | catalogFilters → query | GET /api/destinos?q=... | Resultado vazio explícito |
| Município `municipality` | Select populado pelos dados | Restringe igualdade | Sem opção: todos |
| Categoria `category` | Select com categorias existentes | Restringe igualdade | Não há administração de categorias |
| Cultura `culture` | Nove itens culturais | Filtra por association/tag | Cacuriá pode não ter local |
| Necessidades `access` | Cinco grupos | Expande campos exigidos | Todos precisam confirmação com fonte/data |
| Recursos específicos | 12 checkboxes em detalhes | Repetição de access | Interseção de requisitos, não “qualquer um” |
| Aplicar filtros | Submit, consulta sequenciada | Atualiza URL, cards e mapa | Resposta antiga é ignorada |
| Limpar | Link do catálogo sem query | Restaura coleção | Recarrega navegação |
| `#includeLegacy` | Checkbox, parâmetro legacy=1 | Recalcula mapa local | Não acrescenta dados à lista |
| Ver no mapa em card | data-map-id → catalogMap.focus | Foco e rolagem | Só habilitado para local elegível no modo atual |
| Ver detalhes em card | /destino/id | Ficha | ID inexistente gera erro na API |
| Fonte em card | URL segura, outra aba | Consulta referência | Links externos não foram revalidados nesta análise |
| Contexto cultural `#culturalDiscovery` | summary/details | Expande textos e fontes | Sem associação não cria ponto |
| Zoom, agrupamentos e popup | Leaflet | Navegação geográfica | Fundo pode falhar independentemente dos dados |

Cada card mostra ilustração, nome, município, categoria, descrição, situação de coordenadas, contexto cultural associado quando houver e fonte. Status “parcial” é de curadoria; não significa que aquele local foi fisicamente inspecionado.

O resultado é anunciado em região viva. A área de mapa informa estados; ausência de locais com todos os recursos selecionados é uma resposta correta nesta base. Em celular o mapa tem altura reduzida e filtros/cards se empilham. O catálogo depende de JavaScript para montar a tela; falha no controlador pode deixar só o shell.

## 6. Ficha — /destino/<id>

**Objetivo:** contextualizar um local e suas evidências. **APIs:** GET /api/destinos/id, GET /api/accessibility, GET /api/avaliacoes/id e GET favoritos se autenticado. **Banco:** destinos, avaliações, favoritos e relatos.

| Elemento | Dados / ação | Resposta e validação |
|---|---|---|
| Nome, categoria, descrição, endereço | Leitura do destino | Endereço ausente não é inferido |
| Ilustração e crédito | destination-fallback.svg | Declara que não é foto do lugar |
| Fonte/data/situação | Metadata | Data editorial não significa monitoramento automático |
| Favoritar / remover | PUT ou DELETE /api/favoritos/id | Estado atualizado; exige login |
| Ver no mapa | Link para catálogo com busca e legado conforme caso | Não cria coordenada |
| Planejar por município | /planejar?municipality=...#roteiro | Pré-preenche município; usuário ainda gera |
| Contextos culturais | culture_tags/context | Texto e fonte; sem promessa de espetáculo |
| Tabela de recursos | 12 campos / três estados | Exibe fonte/data quando existentes |
| `feature` do relato | Select de 12 recursos | Recurso conhecido obrigatório |
| `proposed_status` | confirmed/unavailable/unverified | Declaração proposta, não publicação |
| `description` | Texto 10–2000 | Explica o observado |
| `source_url` | Opcional, até 1000, HTTPS se preenchido | Referência do proponente |
| Enviar para moderação | POST /api/accessibility-reports com destination_id | Pendência 201, aviso e limpeza de campos |
| `rating` / nota | 1 a 5 | Inteiro validado |
| `comment` / comentário | 5–1000 caracteres | Texto público |
| Enviar avaliação | POST /api/avaliacoes/id | Cria ou atualiza a avaliação do usuário |
| Entrar para contribuir | Link/convite à autenticação | Anônimo pode ler sem esses formulários |

Erros de ID 404 aparecem no conteúdo do shell, que pode ter sido servido com HTTP 200. Listagem de avaliações é pública e inclui nome; perfil privado não torna essa contribuição anônima. Não existe denúncia/moderação de avaliação visível. A moderação de acessibilidade é uma ferramenta local separada.

## 7. Perfil pessoal — /perfil

**Objetivo:** centralizar identidade, memória de exploração e atalhos. **Arquivos:** painel.html, painel.js, painel.css. **APIs:** sessão/configurações, resumo, histórico, favoritos e roteiros salvos.

**Visual e informação:** capa horizontal, avatar, saudação, @handle, município, bio, contagem de amigos, indicadores e cards recentes. Favoritos mostram até dois na visão geral; roteiros até dois; atividades até quatro. As páginas próprias exibem a coleção consultada, sujeita ao limite da API.

| Controle | Handler / endpoint | Resultado | Erro/permissão |
|---|---|---|---|
| Entrar ou criar conta | Link abre fluxo de conta | Usuário retorna com acesso ao painel | Anônimo não recebe dados privados |
| Nome `#profileName` | Form de edição → PATCH /api/perfil | Atualiza saudação e estado | 2–100, erro exibido |
| E-mail `#profileEmail` | Desabilitado | Apenas leitura | Não há troca de e-mail |
| Interesses `#profileInterests` | CSV em lista; PATCH /api/perfil | Persiste preferências textuais | Máximo 12 itens, até 40 cada |
| Salvar alterações | Submit | Confirma e re-renderiza dados necessários | Falha não deve ser interpretada como salvo |
| Personalizar/configurações | Link /configuracoes | Edição ampliada | Exige sessão |
| Ver favoritos / histórico / roteiros | Links das seções e barra lateral | Rotas específicas | Sem duplicar dados |
| Remover favorito | data-remove-fav → DELETE | Card e contagem recarregados | Próprio usuário |
| Ver detalhes / Fechar detalhes | Toggle local com aria-expanded | Mostra JSON renderizado do roteiro | Sem API adicional obrigatória |
| Colaborar | /roteiro-compartilhado/id | Convites/notas | Permissões na API |
| Excluir roteiro | Confirmação + DELETE /api/roteiros-salvos/id | Some da coleção | Sem desfazer |
| Tentar novamente em bloco | Reexecuta consulta correspondente/load | Recupera falha parcial | allSettled preserva outras seções |
| Tentar novamente sessão | ExploreAccount.init | Reconstrói conta | Erro de rede não vira sessão falsa |

**Celular:** cabeçalho, identidade e cards ajustam colunas; nomes longos são tratados nos estilos. **Acessibilidade:** regiões com carregamento, títulos, rótulos, foco e estados. **Limites:** estatística não representa todos os eventos possíveis; não há edição de senha; o painel exige JavaScript e consulta de sessão.

## 8. Histórico — /historico

**Objetivo:** rever atividades registradas. **Visual:** título, descrição, lista cronológica com tipo, data e texto, estado vazio com CTA. **Banco:** historico do usuário. **API:** GET e DELETE /api/historico.

| Controle | Ação | Resultado / exceção |
|---|---|---|
| Limpar histórico | Confirmação nativa, DELETE sem corpo | Remove todos os eventos do dono; confirmação cancelada não envia |
| Link descobrir/planejar no vazio | Navegação local | Sugere próxima atividade |
| Sidebar | Perfil, favoritos, roteiros, acessibilidade | Mantém navegação do painel |
| Repetir consulta | load após erro | Carrega novamente se rede voltar |

Exibe até 100 itens, mais recentes primeiro. Não é um histórico completo de páginas visitadas nem registro comercial de presentes. Não há exportação, filtro por período ou exclusão seletiva. Login é obrigatório; no celular a lista empilha sem mudar as permissões. A exclusão também reduz a estatística de pesquisas.

## 9. Favoritos — /favoritos

**Objetivo:** guardar destinos para consulta posterior. **Visual:** cards com nome, contexto, município, estado vazio e CTA. **API:** GET /api/favoritos; DELETE /api/favoritos/id; adição ocorre nos cards/ficha. **Banco:** relação usuario/destino única.

| Controle | Ação | Resultado / erro |
|---|---|---|
| Remover favorito | Botão do card, sem confirmação extra | DELETE próprio, lista atualizada |
| Descobrir destinos | Link de estado vazio | /explorar ou catálogo conforme renderizador |
| Navegação lateral | Links pessoais | Não muda visibilidade pública por si só |
| Repetir | Recupera GET | Mensagem se falhar |

Favoritos são privados por padrão; configurações podem autorizar amigos ou público a vê-los em /p/handle. A página pessoal continua restrita ao dono. Não há pastas de favoritos ou ordenação manual. Layout em grade se converte em coluna em telas menores.

## 10. Meus roteiros — /meus-roteiros

**Objetivo:** recuperar retratos salvos. **Visual:** título do roteiro, município, duração, verba/resumo quando presente, data, detalhes e ações. **API:** GET /api/roteiros-salvos e DELETE /api/roteiros-salvos/id.

| Controle | Ação | Efeito |
|---|---|---|
| Ver detalhes / Fechar detalhes | Toggle local | Dias, paradas, experiência especial e nota conforme conteúdo salvo |
| Colaborar | Link com ID | Abre área compartilhada |
| Excluir roteiro | Confirmação + DELETE | Remove roteiro e dependências em cascata de convites/notas/link |
| Criar um roteiro | CTA de vazio | /planejar#roteiro |
| Tentar novamente | GET | Recuperação de rede |

A API retorna até 100, ordenados por ID decrescente. Não há edição completa dos dias aqui. Excluir usa id e dono; ID de outro usuário não causa exclusão. A interface não oferece desfazer. Visual responsivo e botões têm nomes textuais; o detalhe usa estado expandido.

## 11. Acessibilidade da interface — /acessibilidade

**Objetivo:** configurar leitura e explicar limites. **Pública:** esta tela do painel não exige conta. **Dados:** preferências no localStorage; não precisa gravar em SQLite.

| Controle | Função | Efeito |
|---|---|---|
| A− / Reduzir texto | setSize, passo −10 | Ajuste raiz entre 85% e 145% |
| A+ / Aumentar texto | setSize, passo +10 | Valor persistido neste navegador |
| Alternar alto contraste | Classe high-contrast e aria-pressed | Paleta de contraste armazenada localmente |
| Explorar/planejar | Links | Volta à atividade turística |
| Configurações | Link | Preferências pessoais consentidas quando autenticado |

O JavaScript limita os valores e trata falhas de localStorage para não impedir o uso. O ajuste percentual não comprova ampliação proporcional de fontes definidas em pixels. Não há leitor de tela embutido, tradução em Libras, audiodescrição automática ou botão que transforme um destino físico.

## 12. Configurações — /configuracoes

**Objetivo:** personalizar identidade, apresentação, privacidade e preferências. **Login:** necessário. **API:** GET/PATCH /api/profile-settings e POST/DELETE /api/profile-media/avatar ou cover. **Banco:** usuarios, profiles, media.

### Dados e preferências

| Campo | Tipo / limite | Persistência e finalidade |
|---|---|---|
| name | Texto 2–100 | usuarios.nome; apresentação |
| handle | 3–30, letra inicial ASCII, letras/números/_ | profiles.handle único sem caixa |
| bio | Texto até 500 | Descrição do perfil |
| municipality | Texto até 80 | Município declarado pelo usuário; não GPS |
| interests | CSV, até 12, 40 por item | usuarios.interesses JSON |
| theme | forest/ocean/sunset | profiles.theme e cache local |
| avatar_x, avatar_y | Range 0–100 | Enquadramento porcentual da foto |
| cover_x, cover_y | Range 0–100 | Enquadramento da capa |
| is_public | Checkbox booleano | Acesso anônimo ao perfil |
| discoverable | Checkbox booleano | Participação na pesquisa de pessoas |
| favorites_visibility | private/friends/public | Quem pode ver favoritos no perfil público |
| allow_invites | Checkbox booleano | Recebimento de amizade/roteiro/presente segundo regras |
| access_consent | Checkbox booleano | Permite guardar grupos selecionados |
| access_preferences | Até 5 grupos conhecidos | Só persiste com consentimento |

“Salvar configurações” envia todos os dados pertinentes em PATCH. O backend valida antes de atualizar; conflito de handle é 409. Sucesso mostra “Configurações salvas.”, atualiza conta em memória, tema e cabeçalho. O controlador não reconstrói a tela inteira, para preservar um arquivo selecionado ainda não enviado.

### Foto e capa: dois componentes independentes

| Controle/estado | Operação | Explicação |
|---|---|---|
| Escolher arquivo | input file JPEG/PNG/WebP | Cria prévia local e mostra nome; não grava |
| Prévia | URL blob local | Permite conferir seleção |
| Salvar foto / Salvar capa | FormData com campo image, POST do tipo | Desabilita controles durante envio |
| Abrir meu perfil | Link /perfil | Confere apresentação persistida |
| Remover foto / Remover capa | DELETE do tipo | Apaga imagem atual e usa fallback |
| Ranges de posição | input altera object-position | Prévia imediata, persistência pelo formulário de configurações |
| Estado vazio/current/selected/uploading/saved/error | Região de status | Distingue seleção de sucesso efetivo |

O cliente rejeita tamanho/MIME inadequado; o servidor analisa bytes, 4 MiB e 16 MP. Request global acima de 6 MiB também pode ser rejeitada. JPEG resultante recebe token; erro de substituição conserva a imagem anterior. Um problema de decodificação da prévia após sucesso é comunicado separadamente do salvamento.

O tema do visitante é o aplicado na tela de perfil público; a implementação recebe o tema do perfil visitado mas não o reaplica integralmente nessa renderização. Não prometer uma vitrine independente com tema do dono em todos os contextos.

## 13. Amigos — /amigos

**Objetivo:** descoberta consentida, relação social e convites. **Visual:** pesquisa, amigos, pendências, convites de colaboração, bloqueados e acesso a presentes. **APIs:** people, friends e trip-invites. **Login:** obrigatório.

| Controle | Dados / endpoint | Permissão, efeito e erro |
|---|---|---|
| Campo q | Nome ou @handle, mínimo 2 | GET /api/people?q; abaixo disso retorna lista vazia |
| Pesquisar pessoas | Submit peopleSearch | Mostra perfis descobríveis não bloqueados |
| Ver perfil | /p/handle | Pode retornar indisponível se não público/amigo |
| Adicionar amigo | POST /api/friends/id {action:request} | Destinatário descobrível e aceita convites; 409 se já há relação ativa |
| Aceitar | action:accept | Só destinatário de pendência |
| Recusar | action:reject | Só destinatário; não bloqueia |
| Remover amigo | Confirmação; action:remove | Encerra vínculo e revoga convites do par |
| Bloquear | Confirmação; action:block | Remove amizade, revoga convites e cancela vouchers ativos entre o par |
| Desbloquear | action:unblock | Remove só o bloqueio do ator; não restaura amizade |
| Aceitar convite de roteiro | POST /api/trip-invites/id {action:accept} | Ainda precisa amizade válida |
| Recusar convite | action:reject | Destinatário pendente |
| Revogar convite | action:revoke | Remetente |
| Abrir roteiro | /roteiro-compartilhado/id | Só convite aceito ou dono |
| Presentes | /presentes | Operação simbólica em outra página |

Falha de ação aparece em aviso, sem simular amizade aceita. A pesquisa não mostra e-mail; bloqueio entre qualquer direção exclui visibilidade. Não há mensagens privadas ou notificações push. Os convites são vistos quando a página consulta os dados. O layout social foi exercitado em múltiplas larguras e com duas contas isoladas.

## 14. Perfil visível a terceiros — /p/<handle>

**Objetivo:** mostrar apresentação autorizada. **API:** GET /api/public-profile/handle. **Elementos:** capa, foto, nome, @handle, bio, município e favoritos conforme permissão.

Dono, amigo aceito ou visitante de perfil público podem acessar segundo regras; bloqueio retorna 404. Perfil inexistente ou privado para aquele visitante também aparece indisponível. O shell pode ser HTTP200 antes da resposta JSON de erro.

| Elemento/controle | Ação |
|---|---|
| Foto/capa | Carrega /media/token com checagem de permissão |
| Favoritos visíveis | Cards do conteúdo autorizado |
| Aviso de favoritos privados | Não exibe lista se a política negar |
| Links de navegação e detalhes | Rotas compartilhadas |
| Repetição após erro | Reconsulta dados |

Não expõe e-mail, senha, histórico ou preferências de acesso. Não é uma edição do próprio perfil. Bio vazia usa texto de apresentação genérico; isso não foi escrito pelo titular. A imagem não é identificador secreto: a autorização é checada no endpoint.

## 15. Roteiro compartilhado autenticado — /roteiro-compartilhado/<id>

**Objetivo:** consultar conteúdo e reunir ideias. **Visual:** título, dias, notas com autor/data, formulários e área de compartilhamento do dono. **APIs:** /api/trips/id, /notes, /invites, /share.

| Controle/campo | Dados | Permissão / resultado |
|---|---|---|
| Título + salvar | PATCH /api/trips/id {title} 1–120 | Dono/editor; altera título, não dias |
| Texto da ideia | POST /notes {text} até1000, não vazio | Dono/editor; adiciona nota |
| Amigo do convite | Select de amigos aceitos | Dono; recipient_id |
| Papel | viewer/editor | Dono; define futura capacidade |
| Enviar convite de roteiro | POST /invites {recipient_id,role} | Pendência criada/renovada; ainda sem acesso |
| Criar link de leitura pública | Confirmação + POST /share | Só dono; token público revogável |
| Link gerado | /s/token | Abre leitura sem login |
| Desativar link público | DELETE /share | Revoga; não apaga roteiro |
| Leitura das notas | GET do roteiro | Dono e convidados aceitos |
| Voltar/navegar | Links gerais | Permissão segue API |

Leitor não recebe controles de edição. Não há edição simultânea em tempo real, exclusão de notas, anexos ou reorganização de paradas. Não confundir as notas com histórico pessoal. Em celular, formulários empilham. Mensagens de API 403/404 preservam restrições mesmo se alguém digitar o endereço manualmente.

## 16. Link público — /s/<token>

**Objetivo:** consulta anônima de roteiro por endereço. **API:** GET /api/shared/token. **Visual:** título e dias renderizados, aviso; navegação geral.

Não possui formulário de notas nem convites. Não precisa estar na lista de amigos. Token inválido/revogado retorna 404 no conteúdo. O link continua público até revogação ou exclusão do roteiro. Notas de colaboração não são incluídas. Experiência especial e resumo completo não são renderizados por esse componente atual, embora possam constar do JSON salvo.

## 17. Presentes e vouchers — /presentes

**Objetivo:** convite simbólico associado a destino e amizade. **Visual:** formulário e cards de presentes com tema, mensagem, código, validade, estado e ações. **APIs:** GET/POST /api/vouchers, GET /api/friends e /api/destinos, POST /api/vouchers/id/transition.

| Campo/controle | Dados / validação | Resultado e permissões |
|---|---|---|
| Destinatário | Amigo aceito, recipient_id inteiro | Sem amigos: orientação/CTA |
| Experiência/destino | destination_id existente | Inclui destinos de catálogo, não produto comercial |
| Mensagem | Até500 caracteres | Guardada no voucher |
| Tema | azulejo/sol/reggae | Aparência do card |
| Validade | Data, futura até366 dias | Backend usa fim do dia UTC |
| Emitir voucher simbólico | POST dos campos | 201, estado issued e código aleatório |
| Enviar convite | transition {action:send} | Remetente, issued, amizade e convites válidos → sent |
| Cancelar | action:cancel | Remetente, issued/sent → cancelled |
| Confirmar resgate simbólico | Confirmação + action:redeem | Destinatário, sent, não bloqueado → redeemed |
| Código e histórico de cards | Leitura | Destinatário não vê issued; lista até200 |
| Estado expirado | Atualização nas consultas/operações | Não há job independente de expiração |

A mensagem de sucesso indica estado no banco, não envio externo. Uma transição repetida ou inválida resulta 409; terceiro recebe404. A página não cobra, gera desconto, reserva ou valida presença no destino. Não há PDF/QR do voucher nem integração com comerciante. Isso deve ser dito antes de demonstrar “resgate”.

## 18. Cultura — /cultura → /catalogo#cultura

**Objetivo:** preservar o endereço antigo e incorporar cultura à descoberta. O Flask responde302. A seção contém nove contextos, textos, títulos, tipo de informação e links de fonte. `details/summary` expande leitura; a query cultural filtra locais associados. Esse é conteúdo editorial servido de JSON, não agenda ao vivo.

O visitante não precisa autenticar; nenhum cadastro cultural é criado por abrir a seção. Links externos abrem com proteção de nova aba. No celular o texto acompanha a coluna de leitura. Cacuriá permanece sem ponto associado: não há geolocalização artificial de uma tradição.

## 19. Controles internos do mapa

| Controle | Função | Dados / resultado | Acessibilidade e limite |
|---|---|---|---|
| + / − | Zoom Leaflet | Modifica escala | Sem alterar API |
| Arrastar | Navegação do mapa | Centro visual | Lista oferece acesso textual alternativo |
| Marcador | Popup com nome/link | ID elegível | Não equivale a acessibilidade física |
| Cluster com contador | Zoom/expansão/spiderfy | Representa vários IDs | Somar membros, não contar somente figuras |
| Nome “Ver no mapa” | focus(id) | Abre cluster/popup e destaca | Só busca no conjunto atual |
| Inclusão de legado | setPlaces com includeUnverified | Pontos válidos não verificados | Aviso explícito |
| Créditos OpenStreetMap | Link de atribuição | Fonte cartográfica | Externo |
| Falha de tiles | Handler de tileerror | Aviso; dados/lista continuam | Fundo não é catálogo |
| Ausência de Leaflet | Controller fallback | Mensagem de indisponibilidade | Sem mapa; catálogo permanece possível |

Roda do mouse não aumenta zoom por padrão, evitando captura involuntária da rolagem da página. Redução de movimento diminui animações. `ResizeObserver` invalida tamanho ao mudar o contêiner; `destroy` remove mapa e observador em nova renderização.

## 20. Telas técnicas e o que não é uma página de produto

`/api/health` é uma resposta JSON de diagnóstico; `/api/destinos/verificar` lista nomes, municípios e pares lat/lon, sem marcar nada como verificado. `/api/accessibility` e `/api/culture` são dados consumidos pelas telas. `/media/token` entrega imagem autorizada. Arquivos CSS/JS/vendor/SVG são estáticos.

Não existem páginas comprovadas de administração, pagamento, reserva, recuperação de conta, cadastro manual de destinos ou auditoria física. O arquivo `backend/moderate_accessibility.py` é uma ferramenta de linha de comando para revisão local, não um painel web.

## 21. Evidências de interface e limites da verificação

Os scripts existentes percorreram /, /explorar, /catalogo, /destino/1, /perfil, /historico, /favoritos, /meus-roteiros, /acessibilidade, /configuracoes, /amigos, /presentes e URLs dinâmicas de colaboração/link criadas nos testes. A rota /planejar compartilha o HTML inicial e foi confirmada no código/teste de páginas; /cultura é redirecionamento confirmado. Perfil público e permissões foram conferidos em API, não se afirma auditoria visual completa de todas as combinações de /p/handle.

Capturas produzidas pelos scripts ficam em `.artifacts`: perfil vazio/desktop/celular/contraste, cultura, configurações, mapa/exploração, amigos e voucher. São cenários com contas fictícias e, no teste de correções cartográficas, pontos sintéticos. Não apresentar essas imagens como levantamento físico ou como número de pontos reais verificados.


## 22. Inventário literal dos controles nos HTMLs de entrada

Complementa os controles criados por JavaScript descritos acima. O cabeçalho fallback é substituído por navigation.js; um link estático antigo não implica duplicação do menu final. Campos dinâmicos não aparecem nesta lista de HTML, mas estão nas seções correspondentes.

### experiencias.html

| Linha | Tag | id | name | type | value | Destino/ação | aria-label |
|---:|---|---|---|---|---|---|---|
| 3 | a |  |  |  |  | #featureTitle |  |
| 3 | a |  |  |  |  | / |  |
### index.html

| Linha | Tag | id | name | type | value | Destino/ação | aria-label |
|---:|---|---|---|---|---|---|---|
| 17 | a |  |  |  |  | #inicio |  |
| 21 | a |  |  |  |  | /#inicio |  |
| 22 | button | menuToggle |  | button |  |  | Abrir menu |
| 23 | a |  |  |  |  | /#inicio |  |
| 23 | a |  |  |  |  | #explorar |  |
| 23 | a |  |  |  |  | #roteiro |  |
| 23 | a |  |  |  |  | #recursos |  |
| 23 | a |  |  |  |  | /perfil |  |
| 23 | a |  |  |  |  | /historico |  |
| 24 | a |  |  |  |  | /favoritos |  |
| 24 | a | profileShortcut |  |  |  | /perfil | Abrir meu perfil |
| 24 | button | loginOpen |  |  |  |  |  |
| 24 | a |  |  |  |  | #roteiro |  |
| 29 | a |  |  |  |  | #roteiro |  |
| 29 | a |  |  |  |  | #explorar |  |
| 44 | form | tripForm |  |  |  |  |  |
| 45 | select | destination |  |  |  |  |  |
| 46 | select | days |  |  |  |  |  |
| 47 | input | budget |  | number |  |  |  |
| 48 | select | people |  |  |  |  |  |
| 49 | select | transport |  |  |  |  |  |
| 51 | input |  | interest | checkbox | História |  |  |
| 52 | input |  | interest | checkbox | Praias |  |  |
| 53 | input |  | interest | checkbox | Gastronomia |  |  |
| 54 | input |  | interest | checkbox | Natureza |  |  |
| 55 | input |  | interest | checkbox | Cultura |  |  |
| 56 | input |  | interest | checkbox | Reggae |  |  |
| 57 | input |  | interest | checkbox | Bumba Meu Boi |  |  |
| 58 | input |  | interest | checkbox | Tambor de Crioula |  |  |
| 59 | input |  | interest | checkbox | Cacuriá |  |  |
| 60 | input |  | interest | checkbox | Azulejaria |  |  |
| 61 | input |  | interest | checkbox | Gastronomia maranhense |  |  |
| 62 | input |  | interest | checkbox | Artesanato |  |  |
| 63 | input |  | interest | checkbox | Família |  |  |
| 66 | input |  | access | checkbox | Mobilidade reduzida |  |  |
| 67 | input |  | access | checkbox | Deficiência visual |  |  |
| 68 | input |  | access | checkbox | Deficiência auditiva |  |  |
| 69 | input |  | access | checkbox | Intelectual / cognitiva |  |  |
| 70 | input |  | access | checkbox | Necessidades sensoriais |  |  |
| 71 | input |  | access | checkbox | Crianças |  |  |
| 72 | a |  |  |  |  | /catalogo |  |
| 72 | button | useAccessPreferences |  | button |  |  |  |
| 73 | button |  |  | submit |  |  |  |
| 82 | input | destinationSearch |  | search |  |  |  |
| 83 | button | destinationSearchButton |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 87 | button |  |  | button |  |  |  |
| 100 | a |  |  |  |  | #roteiro |  |
| 102 | a |  |  |  |  | /#inicio |  |
| 102 | a |  |  |  |  | #explorar |  |
| 102 | a |  |  |  |  | #roteiro |  |
| 102 | a |  |  |  |  | #recursos |  |
| 102 | a | footerLogin |  |  |  | # |  |
| 103 | button | modalClose |  |  |  |  | Fechar |
| 103 | form | accountForm |  |  |  |  |  |
| 103 | input | accountName |  |  |  |  | Nome |
| 103 | input | accountEmail |  | email |  |  | E-mail |
| 103 | input | accountPassword |  | password |  |  | Senha |
| 103 | button | accountSubmit |  | submit |  |  |  |
| 103 | button | switchMode |  | button |  |  |  |
### painel.html

| Linha | Tag | id | name | type | value | Destino/ação | aria-label |
|---:|---|---|---|---|---|---|---|
| 10 | a |  |  |  |  | #pageTitle |  |
| 12 | a |  |  |  |  | / | Explore+ SLZ, início |
| 13 | a |  |  |  |  | / |  |
| 13 | a |  |  |  |  | /explorar#explorar |  |
| 13 | a |  |  |  |  | /planejar#roteiro |  |
| 14 | a |  |  |  |  | / |  |
| 14 | button | logoutBtn |  |  |  |  |  |
| 20 | a |  |  |  |  | /perfil |  |
| 21 | a |  |  |  |  | /historico |  |
| 22 | a |  |  |  |  | /favoritos |  |
| 23 | a |  |  |  |  | /meus-roteiros |  |
| 24 | a |  |  |  |  | /acessibilidade |  |
| 26 | a |  |  |  |  | /explorar#explorar |  |
