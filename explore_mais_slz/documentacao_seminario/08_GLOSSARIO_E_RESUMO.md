# Glossário, revisão rápida e material de estudo

**Como usar:** primeiro leia a explicação geral no documento01. Depois pratique as perguntas do07 e uma fala do05. Este arquivo ajuda a recuperar conceitos, sem substituir os contratos e evidências.

## 1. Termos da arquitetura e da web

| Termo | Explicação simples | Exemplo no projeto |
|---|---|---|
| Aplicação web | Sistema usado pelo navegador e atendido por servidor | Explore+ SLZ |
| Frontend | Parte executada/apresentada no navegador | HTML, CSS, JS e Leaflet |
| Backend | Parte que recebe pedidos e aplica regras no servidor | Flask/Python |
| Cliente | Programa que faz a requisição | Chrome |
| Servidor | Processo que atende pedidos | Flask local |
| Servidor local | Serviço executado na própria máquina | 127.0.0.1:5000 |
| Loopback | Endereço para a própria máquina | 127.0.0.1 |
| Porta | Número que identifica o serviço no endereço | 5000 |
| Rota | Regra que associa endereço a uma função | /perfil |
| Endpoint | Ponto de entrada de uma operação da API | /api/favoritos/1 |
| HTTP | Protocolo de requisição/resposta | GET de destinos |
| HTTPS | HTTP protegido por conexão criptografada | Requer configuração de publicação |
| URL | Endereço completo ou relativo de recurso | /destino/1 |
| Querystring | Parâmetros após ? na URL | ?q=reggae |
| Âncora/hash | Trecho após # para referência no documento | #roteiro |
| GET | Método usado para consultar | Ler favoritos |
| POST | Método usado para criação/ação | Gerar/salvar roteiro |
| PUT | Método para intenção idempotente de atualização | Marcar favorito |
| PATCH | Método para alteração parcial | Configurações |
| DELETE | Método de remoção | Desfavoritar |
| HEAD | Consulta de cabeçalhos sem corpo | Automática em rotas GET |
| OPTIONS | Consulta de métodos disponíveis | Automática no framework |
| Status HTTP | Código do resultado da requisição | 200,401,404 |
| API | Contrato de comunicação entre partes | JavaScript ↔ Flask |
| JSON | Texto com objetos, listas e valores | Resultado do roteiro |
| Serialização | Converter estrutura para representação armazenável | json.dumps do roteiro |
| Desserialização | Reconstruir estrutura a partir do texto | json.loads de interesses |
| Fetch | Função do navegador para pedir recursos | ExploreAccount.api |
| Promise | Representação de resultado assíncrono futuro | Consulta que ainda está chegando |
| async/await | Sintaxe para trabalhar com operações assíncronas | Carregamento do perfil |
| Promise.allSettled | Espera todas as tarefas, preservando sucesso/falha individual | Blocos independentes do painel |
| AbortController | Cancela uma operação em andamento | Busca anterior da inicial |
| Debounce | Espera uma pausa antes de repetir ação | Pesquisa após250ms |
| DOM | Árvore de elementos da página | Cards montados pelo JS |
| Evento | Sinal de ação/estado no navegador | click,submit,input |
| Handler | Função que atende evento/requisição | submit de tripForm |
| Renderização | Transformar dados em interface | Mostrar favoritos |
| Shell | Estrutura inicial que recebe conteúdo dinâmico | experiencias.html |
| Asset estático | Arquivo servido sem lógica de negócio por requisição | CSS/JS/SVG |
| Vendor | Dependência de terceiro guardada no projeto | Leaflet |
| CDN | Serviço externo de entrega de arquivos | Origem de download de assets; não exigida em runtime para Leaflet |
| MIME | Tipo declarado do conteúdo | image/jpeg |
| Multipart | Formato de envio de arquivo e campos | Upload de imagem |
| FormData | Objeto navegador que monta esse envio | Campo image |
| Cache | Cópia para reutilização | Tema inicial no navegador |
| localStorage | Pequeno armazenamento persistente por origem no navegador | Contraste e fonte |
| Cookie | Dado associado à origem e enviado nas requisições | Sessão |
| Mesma origem | Mesmo esquema, host e porta | Frontend/API no Flask local |
| CORS | Política de acesso entre origens | Não há API aberta geral configurada |
| Framework | Estrutura de apoio ao desenvolvimento | Flask |
| Dependência | Biblioteca usada pelo código | Pillow |
| Ambiente virtual | Instalação isolada de Python/pacotes | .venv |
| Variável de ambiente | Configuração fora do código | EXPLORE_DATABASE_PATH |
| WSGI | Interface entre app Python web e servidor de implantação | Necessária no desenho de produção |
| Debug | Modo de diagnóstico/desenvolvimento | app.run direto |
| Headless | Navegador sem janela visível | Testes Chrome |

## 2. Banco, código e processamento

| Termo | Explicação simples | Exemplo |
|---|---|---|
| Banco relacional | Dados organizados em tabelas relacionadas | SQLite |
| Esquema | Estrutura das tabelas/regras | CREATE TABLE |
| DDL | SQL que define a estrutura | CREATE/ALTER |
| SQL | Linguagem para consultar/alterar dados | SELECT favoritos |
| Tabela | Conjunto de registros da mesma entidade | destinos |
| Linha/registro | Um item armazenado | Um destino |
| Coluna/campo | Um atributo | municipio |
| INTEGER | Afinidade de número inteiro | ID |
| REAL | Afinidade numérica com decimal | Latitude |
| TEXT | Afinidade textual | Nome e JSON |
| BLOB | Sequência de bytes | Foto processada |
| NULL | Ausência de valor SQL | Coordenada ausente |
| String vazia | Texto de comprimento zero, diferente de NULL | Endereço não preenchido |
| PK/chave primária | Identificação única de linha | usuarios.id |
| Chave composta | Identificação formada por mais de uma coluna | Favorito usuário+destino |
| FK/chave estrangeira | Referência formal a outra tabela | favoritos.destino_id |
| Integridade referencial | Coerência das referências | FK ativada por conexão |
| UNIQUE | Regra de não repetição | E-mail |
| CHECK | Regra de valores permitidos | Nota1–5 |
| DEFAULT | Valor usado quando omitido | created_at |
| COLLATE NOCASE | Comparação sem caixa para certos textos | E-mail/handle |
| Índice | Estrutura auxiliar para busca/unicidade | friendship_pair |
| JOIN | Combina tabelas por relação | Favorito com nome de destino |
| Binding/parâmetro SQL | Valor separado da instrução SQL | WHERE usuario_id=? |
| Transação | Grupo de alterações confirmado ou desfeito em conjunto | Aprovação de relato |
| Commit | Confirmar alterações | Saída normal do contexto de conexão |
| Rollback | Desfazer transação em erro | Exceção no contexto |
| Cascade | Propagação da exclusão prevista em FK | Notas quando roteiro é excluído |
| Migração | Evolução versionada do esquema | Versão2 |
| Seed/semente | Dados iniciais inseridos pelo programa | Catálogo editorial |
| Idempotência | Repetir intenção não multiplica efeito final | PUT favorito |
| Upsert | Inserir ou atualizar se já existe | Avaliação por usuário/destino |
| Backup lógico de esquema | Cópia das instruções de estrutura | schema_before_v2 |
| Backup integral | Cópia recuperável de dados e estrutura | Precisa de plano adicional |
| JSON em TEXT | Estrutura serializada numa coluna | conteudo do roteiro |
| Context manager | Controle automático de entrada/saída de recurso | get_connection |
| Decorator | Função que envolve outra para adicionar comportamento | login_required |
| Closure | Função com acesso ao escopo em que foi criada | Handlers de install |
| AST | Estrutura sintática extraída do código | Índice de funções desta auditoria |
| Determinístico | Regras/dados iguais levam ao mesmo resultado | Seleção do planejador |
| Módulo (%) | Resto que permite voltar ao começo de lista | Distribuição de paradas |
| Normalização Unicode | Padronização de texto para comparar | Busca sem acentos |
| Enum/domínio | Conjunto finito de valores aceitos | forest/ocean/sunset |
| Booleano | Valor verdadeiro/falso | is_public |
| UTC | Referência de tempo universal | Validade de voucher |
| ISO | Padrão textual de data/hora | AAAA-MM-DD |
| Lazy | Operação feita quando necessária, não antecipada | Criação de profile/expiração |
| Paginação | Dividir uma coleção em páginas | Ausente no histórico limitado |
| CLI | Interface por linha de comando | Moderação local |

## 3. Segurança e privacidade

| Termo | Explicação simples | Exemplo/limite |
|---|---|---|
| Autenticação | Confirmar a identidade | Login |
| Autorização | Decidir o que a identidade pode fazer | Editor pode adicionar nota |
| Sessão | Estado de identidade entre pedidos | user_id e csrf |
| Hash | Transformação para conferência sem guardar senha original | Werkzeug |
| Salt | Variação incorporada ao processo de hash | Tratada pela biblioteca |
| Assinatura | Forma de detectar alteração sem chave válida | Cookie Flask |
| Criptografia | Proteção de conteúdo para quem não tem chave | Não confundir com assinatura da sessão |
| Token | Valor opaco usado para checagem/referência | CSRF ou link público |
| CSRF | Requisição indevida usando sessão da vítima | Header exigido em escritas |
| Origin | Cabeçalho que indica origem do pedido | Validado quando presente |
| HttpOnly | Restringe acesso JS ao cookie | Não elimina todo XSS |
| SameSite | Política de envio do cookie entre sites | Lax |
| Secure | Cookie transmitido em contexto HTTPS | Configuração por variável |
| XSS | Injeção de script/conteúdo ativo | Escape reduz risco |
| Escape HTML | Representar texto sem torná-lo marcação | Nome com caracteres especiais |
| Injeção SQL | Entrada externa alterando comando SQL | Binding evita misturar valor/comando |
| Limite de tentativas | Controle contra automação de login | Não implementado |
| Privilégio | Capacidade concedida a um ator | Dono/editor/leitor |
| Menor exposição | Retornar apenas o necessário | Busca não devolve e-mail |
| Consentimento | Permissão explícita para um uso de dados | Guardar necessidades |
| Descoberta opt-in | Pessoa decide aparecer na busca | discoverable |
| Handle | Identificador público legível | @ana_seminario |
| Token de portador | Quem tem o endereço pode usá-lo | Link /s/token |
| Revogação | Retirar autorização/referência | Desativar link |
| Retenção | Quanto tempo se guarda informação | Política abrangente ainda ausente |
| No-store | Pedido para não armazenar resposta em cache | Mídia de perfil |
| Nosniff | Orientação para não inferir tipo diferente | Imagem servida |
| MIME falso | Tipo declarado não corresponde aos bytes | Servidor verifica com Pillow |

## 4. Imagens, mapa e acessibilidade

| Termo | Explicação simples | Projeto |
|---|---|---|
| JPEG/PNG/WebP | Formatos de imagem | Entradas aceitas; saída JPEG |
| SVG | Imagem vetorial descrita como marcação | Ilustração genérica |
| EXIF | Metadados de fotografia, incluindo orientação | Correção antes da conversão |
| Megapixel | Um milhão de pixels | Limite16MP |
| MiB | Unidade de1024×1024 bytes | Limite4MiB de arquivo |
| Blob URL | Endereço temporário local de bytes | Prévia selecionada |
| Object-fit | Regra de ajuste visual da imagem | Cobrir área de avatar/capa |
| Object-position | Posição de enquadramento | Ranges0–100 |
| Latitude | Posição norte/sul em graus | −90 a90 |
| Longitude | Posição leste/oeste em graus | −180 a180 |
| Coordenada válida | Número plausível no intervalo |14 pares atuais |
| Coordenada verificada | Par válido com confirmação marcada | Zero atuais |
| Tile | Bloco visual de mapa | OpenStreetMap externo |
| Marcador | Símbolo posicionado no mapa | Destino elegível |
| Camada | Conjunto/elemento do mapa | Marcadores, destaque |
| Cluster | Grupo visual de pontos próximos | Contador de membros |
| Spiderfy | Separação visual de pontos próximos/coincidentes | Expansão de grupo |
| Popup | Caixa de informação sobre marcador | Nome e link |
| Bounds | Limites geográficos visíveis | Ajuste aos pontos |
| Fallback | Alternativa quando recurso falha/falta | Ilustração/controller sem Leaflet |
| Responsividade | Layout adaptado a tamanhos |320 a1440px nos testes |
| Overflow | Conteúdo excede a largura disponível | Verificado nos cenários |
| Breakpoint | Largura que ativa outra regra CSS | Grades viram coluna |
| Token CSS | Variável de estilo reutilizável | Cor primária do tema |
| px | Unidade CSS de tamanho | Pode não acompanhar ajuste raiz |
| rem | Tamanho relativo à fonte raiz | Útil em ampliação coerente |
| Foco | Elemento que recebe teclado | Botão após Escape |
| Tabulação | Sequência de foco com Tab | Navegação por links/campos |
| Inert | Retira área da interação/foco | Fundo do modal |
| Modal | Janela sobreposta de tarefa | Login |
| Semântica | Significado estrutural dos elementos | Títulos/formulários |
| ARIA | Estados/nomes adicionais de acessibilidade | expanded/pressed/busy |
| Região viva | Área que anuncia atualização | Status de resultado |
| Alt | Alternativa textual de imagem | Vazia quando decorativa no contexto |
| Leitor de tela | Software que interpreta estrutura para saída assistiva | Não auditado diretamente nesta análise |
| Refluxo | Reorganização sem exigir leitura lateral inadequada | Precisa de auditoria além do overflow testado |
| Redução de movimento | Preferência por menos animação | CSS/mapa |
| WCAG | Diretrizes de acessibilidade web | Orientam auditoria; sem certificação |
| Acessibilidade digital | Acesso à interface/informação | Teclado e leitura |
| Acessibilidade física | Participação no local real | Entrada/circulação/banheiro |
| Audiodescrição | Informação falada sobre conteúdo visual | Recurso de destino |
| Libras | Língua Brasileira de Sinais | Campo de recurso, não tradutor embutido |
| Braille | Sistema tátil de leitura/escrita | Recurso específico |
| Moderação | Revisão antes da publicação | Relato pendente |

## 5. Testes e avaliação

| Termo | Explicação simples | Exemplo |
|---|---|---|
| Fixture | Dado controlado de teste |40 pontos sintéticos |
| Mock/interceptação | Simulação de condição/dependência | Abortar tiles |
| Asserção | Condição que o teste exige | IDs iguais |
| Regressão | Função antes válida passa a falhar | Quebra após alteração |
| Isolamento | Separar cenários/dados | SQLite temporário |
| Teste de API | Verifica contrato sem interação visual | unittest |
| Teste de navegador | Exercita a página real | Playwright |
| Teste de carga | Mede sob volume/concorrência | Não executado |
| Auditoria | Avaliação sistemática com critérios | WCAG futura |
| Cobertura | Medida do que o teste exercitou | Percentual de linhas não gerado |
| Evidência | Resultado ou fonte que sustenta afirmação | Resposta real de API |
| Hipótese | Explicação ainda não comprovada | Causa de falha específica de tiles |
| Causa confirmada | Fato demonstrado no caso | Falta de coordenadas válidas |
| Limitação | Restrição de comportamento/escopo | Sem roteamento |
| Bug | Defeito em comportamento esperado | Problema de cobertura documentado |
| Demonstrativo | Funciona como modelo interno, sem integração comercial | Voucher |
| Backlog | Trabalho futuro identificado | Curadoria e produção |

## 6. Revisão em dois minutos

| Conceito que preciso dominar | Frase segura |
|---|---|
| Propósito | “Integrar descoberta, cultura e memória pessoal de planejamento.” |
| Arquitetura | “Navegador com HTML/CSS/JS → Flask/Python → SQLite → JSON → interface.” |
| Catálogo | “76 destinos em cinco municípios na base examinada.” |
| Mapa | “14 pares válidos, zero verificados; problema de cobertura aberto.” |
| Padrão do mapa | “Somente verificados; legado é uma escolha com aviso.” |
| Planejador | “Regras determinísticas, sem IA e sem melhor caminho.” |
| Dinheiro | “Divisão da verba, não cotação de custos.” |
| Persistência | “Favoritos são relações; roteiros são retratos JSON.” |
| Perfil | “Foto/capa/tema com persistência e privacidade; prévia não é upload.” |
| Inclusão | “Acessibilidade digital não confirma acesso físico.” |
| Dados físicos | “Zero destinos com recursos confirmados nesta base.” |
| Moderação | “Usuário propõe; revisão local decide.” |
| Social | “Busca consentida, amizade aceita e papéis de colaboração.” |
| Voucher | “Convite simbólico, sem benefício comercial.” |
| Segurança | “Hash, sessão, CSRF, SQL parametrizado e autorização por objeto.” |
| Testes | “26 API +3 scripts de navegador passaram; não certificam tudo.” |
| Produção | “Exige implantação e operação próprias, não só abrir porta do debug.” |

## 7. Relações que costumam confundir

**Cadastro → coordenada válida → coordenada verificada → representação:** são quatro etapas. Nem todo cadastro passa pelas demais; filtros e modo de legado também interferem na última.

**Arquivo selecionado → prévia local → POST aceito → URL persistida:** são estados distintos. A imagem só existe no servidor depois do envio válido.

**Login → autorização:** estar autenticado não permite editar qualquer roteiro. É preciso ser dono ou editor aceito.

**Perfil privado → contribuição pública:** políticas têm escopo. Avaliação pública ainda mostra nome; link de roteiro é público para portadores enquanto ativo.

**Confirmado → fonte/data → filtro:** rótulo isolado não satisfaz a regra. A base precisa carregar evidência, e alguém precisa avaliar sua qualidade.

**Teste passou → produto completo:** conclusão inválida. Um cenário correto não preenche lacunas de dados e não comprova todos os requisitos.

## 8. Perguntas para praticar sem olhar

1. O que acontece entre o clique num coração e o registro no SQLite?
2. Por que76 destinos não geram76 pins?
3. O que o teste com41 pontos comprovou e o que não comprovou?
4. Como800 reais viram400 por dia e200 por pessoa?
5. Por que Reggae pode repetir o mesmo museu em dois dias?
6. O que acontece quando um recurso físico não foi verificado?
7. Quem pode alterar o título de um roteiro compartilhado?
8. Por que bloquear não impede acesso anônimo a um link público ativo?
9. Qual é a diferença entre esquema SQL e backup integral?
10. Por que a foto selecionada ainda pode não estar salva?

Respostas-base estão nos documentos01,03 e07. Se souber explicar essas relações com um exemplo, já compreenderá grande parte da estrutura sem decorar nomes de todas as funções.

## 9. Frases que não devo dizer

- “O mapa está corrigido e todos os locais estão posicionados.”
- “Nosso sistema usa inteligência artificial para achar a melhor rota.”
- “Esses valores são os preços atuais dos passeios.”
- “O botão de acessibilidade certifica o site e todos os destinos.”
- “Sem resultado significa que não existe recurso acessível na cidade.”
- “O voucher dá desconto real e confirma uma reserva.”
- “Hash é a mesma coisa que criptografar uma senha para depois recuperá-la.”
- “O backup da migração recupera todos os dados.”
- “Todos os testes passaram, então não há bugs.”
- “O perfil privado esconde o nome de qualquer contribuição pública.”

Substitua cada frase pela formulação segura da tabela de revisão. Precisão não enfraquece a apresentação; permite explicar exatamente o que foi construído e o que falta comprovar.

