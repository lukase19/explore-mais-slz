# Acessibilidade, inclusão e cultura ludovicense

**Base:** implementação local e testes de 06/11/2026. Este documento distingue uma interface com recursos de acesso, dados físicos de destinos e comprovação de uso real. Essas três coisas se relacionam, mas nenhuma substitui as outras.

## 1. Por que esses diferenciais fazem parte da proposta

Turismo envolve tomar decisões antes de sair de casa: compreender o lugar, avaliar deslocamento, prever barreiras, escolher companhia e confirmar condições. Um catálogo pode informar o nome de um museu e ainda deixar o visitante sem condições de decidir se consegue participar.

No Explore+ SLZ, cultura e acessibilidade aparecem nas escolhas: textos ajudam a compreender o destino; grupos e recursos ajudam a consultar o que se sabe sobre acesso; preferências podem ser guardadas com consentimento. A decisão de não transformar ausência de informação em promessa é parte importante do comportamento atual.

Esses recursos atendem também moradores. Uma pessoa pode conhecer o nome de uma rua e desconhecer sua relação com patrimônio e azulejaria; outra pode já conhecer o destino, mas precisar confirmar circulação ou banheiro antes de convidar alguém.

## 2. Acessibilidade digital e física

| Dimensão | Pergunta | Implementação atual | Limite |
|---|---|---|---|
| Digital | Consigo ler e operar o site? | Teclado, rótulos, contraste, fonte, estados e responsividade | Sem auditoria integral de conformidade ou uso assistivo |
| Informacional | Consigo entender o que foi confirmado? | Estado por recurso, fonte/data e aviso de incerteza | Base física ainda vazia de confirmações |
| Física | Consigo entrar, circular e usar o local? | Modelo para registrar dados e filtrá-los | O código não instala rampa nem vistoria o prédio |
| Trajeto | Consigo chegar e transitar entre as paradas? | Aviso explícito de ausência de validação | Não há análise de calçadas, travessias ou mobilidade |
| Social | Posso controlar exposição e participação? | Perfil privado, pesquisa opt-in, convites e bloqueio | Avaliações públicas e links públicos exigem atenção ao alcance |

Acessibilidade não é uma única condição binária “acessível/não acessível”. Uma entrada sem degraus não prova banheiro adaptado; uma legenda não substitui toda necessidade de uma pessoa surda; rótulos no HTML não provam que um fluxo inteiro funciona com leitor de tela.

## 3. Recursos digitais implementados

### 3.1 Estrutura e orientação

Os documentos usam títulos, áreas de navegação, conteúdo principal, formulários e rótulos. Há link para pular a navegação. Telas privadas anônimas informam a necessidade de autenticar; estados vazios sugerem uma ação; falhas possuem repetição.

Isso dá orientação visual e estrutural. Para comprovar qualidade semântica completa, ainda seria necessário conferir a árvore de acessibilidade em todos os estados, níveis de títulos e ordem de foco, incluindo conteúdo criado dinamicamente.

### 3.2 Teclado e foco

O menu de três barras abre por clique ou ArrowDown; a seta também leva foco ao primeiro link. Escape fecha e retorna ao botão. Clique externo e saída de foco também fecham. Links continuam acessíveis pela sequência normal de Tab.

O modal de login retira o fundo da interação com `inert`, foca o primeiro campo e contém Tab/Shift+Tab nos controles visíveis. Escape, botão de fechar e clique no fundo encerram. O teste verificou o ciclo de foco no cadastro.

Cards de destinos da inicial possuem interação por Enter e Espaço. Botões de favorito e detalhes usam estado. Ainda é necessário auditar todas as ações de mapa com teclado: o teste de foco de um marcador partiu de botão da lista, não de uso irrestrito do mapa sem ponte textual.

### 3.3 Leitura, cor e movimento

A tela /acessibilidade alterna alto contraste e tamanho do texto. O contraste aplica classe persistida no navegador; fonte muda percentual do elemento raiz dentro de85%–145%, por passos de10. LocalStorage indisponível é tratado sem derrubar a sessão.

Há uma limitação técnica: diversos componentes definem `font-size` em px ou limites clamp em px. Alterar o tamanho raiz não aumenta esses componentes da mesma forma que aumentaria valores em rem. O teste comprovou o valor110% no elemento raiz e cor de um texto no contraste, não a ampliação uniforme de toda a página.

Os temas forest/ocean/sunset preservam organização e alteram tokens. Não houve medição sistemática de contraste de todas as combinações, estados hover, texto sobre foto e aviso. Ser visualmente legível na captura não é um laudo de contraste.

Preferência por redução de movimento é considerada em CSS e no mapa. Isso ajuda a reduzir animação desnecessária. Não existe controle de todas as configurações do sistema operacional, nem auditoria de fotossensibilidade.

### 3.4 Leitores de tela e anúncios

Há `aria-expanded` no menu e nos detalhes, `aria-pressed` em favoritos/contraste, áreas de status, `aria-busy` no carregamento e alertas de falha. Esses atributos fornecem informações para tecnologias assistivas; a pronúncia, ordem e oportunidade dos anúncios dependem do navegador e leitor.

Fotos decorativas em certos contextos usam alternativa vazia porque o nome está ao lado. Perfil público identifica a foto pelo nome; ilustrações genéricas não devem receber alternativa que as faça parecer fotografia real do destino. O texto adjacente descreve o conteúdo turístico.

Não foi executado NVDA, JAWS ou VoiceOver nesta análise. “Preparado com semântica e estados” é uma afirmação sustentada; “totalmente compatível com todos os leitores” não é.

## 4. Diferentes necessidades, sem reduzir pessoas a rótulos

### Deficiência visual e baixa visão

A lista textual é essencial porque um mapa sozinho depende de posição visual. Nome, descrição, município e situação continuam disponíveis mesmo sem tiles. Fonte, contraste, foco e estrutura podem auxiliar baixa visão; leitura de tela demanda semântica consistente.

Para o destino físico, a base modela sinalização, Braille e audiodescrição separadamente. O grupo visual exige audiodescrição e sinalização; Braille pode ser selecionado como recurso específico. Isso é uma convenção do projeto e não uma definição completa das necessidades de toda pessoa com deficiência visual.

### Deficiência auditiva

A interface principal é textual e seus avisos não dependem apenas de som. Há campos de Libras e legendas para locais. O grupo auditivo exige os dois confirmados. Não há vídeo institucional em Libras nem tradução automática de conteúdo implementada.

Ter dados sobre intérprete em um destino não confirma disponibilidade em qualquer dia. Fonte, data, agenda e contato precisam ser verificados com o local.

### Deficiência motora ou mobilidade reduzida

Botões, links por teclado e layout responsivo ajudam diferentes maneiras de operar. O modelo físico separa acesso sem degraus, rampas, circulação, banheiro e transporte. O grupo mobilidade combina sem degraus, circulação e sanitário.

A combinação não mede inclinação de rampas, largura de portas ou capacidade de um veículo. Também não determina se a calçada entre dois pontos é contínua. A seleção de um roteiro com lugares confirmados ainda não seria uma rota integralmente acessível.

### Deficiência intelectual ou necessidades cognitivas

Rótulos objetivos, organização previsível, estados vazios e feedback ajudam a compreender ações. O grupo cognitivo exige sinalização e atendimento especializado. Não foi produzido conteúdo completo em leitura fácil, pictogramas validados ou teste de compreensão com participantes.

A interface tem muitas opções em configuração e filtros; simplificar progressivamente e testar compreensão é evolução plausível. Não se deve presumir que um tema de cores resolva barreiras cognitivas.

### Necessidades sensoriais

O modelo inclui um recurso de ambiente sensorial e grupo correspondente. Isso apenas registra uma classificação com evidência, sem medir automaticamente ruído, luminosidade, lotação ou estímulos. A preferência de redução de movimento trata um aspecto digital distinto.

A opção Crianças no planejador é contextual; não gera confirmação física específica. Não é sinônimo de acessibilidade infantil certificada.

## 5. Os 12 recursos e as cinco combinações

**Fonte exata:** `backend/migrations.py:7` e `:13`.

| Chave | Rótulo | O que representa no modelo |
|---|---|---|
| step_free | Acesso sem degraus | Informação de entrada/transposição sem degrau |
| ramp | Rampas | Existência/condição declarada desse recurso |
| circulation | Circulação para cadeira de rodas | Informação de deslocamento interno |
| toilet | Sanitário adaptado | Recurso sanitário declarado |
| transport | Transporte acessível | Informação específica de transporte |
| signage | Sinalização acessível | Orientação/sinalização |
| braille | Braille | Informação tátil escrita nesse sistema |
| audio_description | Audiodescrição | Descrição em áudio de conteúdo visual |
| libras | Libras | Recurso em Língua Brasileira de Sinais |
| captions | Legendas | Conteúdo textual associado ao audiovisual |
| sensory | Ambiente sensorial | Informação sobre condições sensoriais |
| specialist | Atendimento especializado | Informação de suporte especializado |

| Grupo | Campos exigidos por código |
|---|---|
| mobility | step_free + circulation + toilet |
| visual | audio_description + signage |
| hearing | libras + captions |
| cognitive | signage + specialist |
| sensory | sensory |

Cada recurso retorna um objeto com `status`, `source_url` e `verified_at`; após moderação pode incluir `reviewed_by`. Não verificado é o padrão para dado ausente. Indisponível indica que a informação registrada nega o recurso; confirmado indica evidência registrada. O filtro só considera confirmado com fonte e data não vazias.

**Situação real:** os 76 destinos têm access_json vazio. Nenhum recurso físico foi confirmado nesta base. O sistema devolve padrões “não verificado”; filtro de mobilidade confirmado não encontra resultado. Isso demonstra a regra de prudência, mas também a necessidade de trabalho de campo/curadoria.

## 6. Preferências consentidas e moderação

O usuário pode selecionar até cinco grupos nas configurações. A lista só é persistida se `access_consent=true`; retirar consentimento guarda lista vazia. Não são informações públicas do perfil e não são inferidas por foto ou comportamento.

No planejador, “Usar minhas preferências” é uma ação explícita de reaproveitamento. As preferências não tornam um local elegível por si mesmas; a confirmação continua sendo exigida no servidor.

O formulário da ficha cria relato com destino, recurso, estado sugerido, descrição e fonte opcional HTTPS. A API guarda status pending e responde que a contribuição não altera dados publicados. Isso impede que uma pessoa se autoconfirme como auditora apenas pelo formulário.

A CLI `backend/moderate_accessibility.py` lista pendências, rejeita ou aprova. Para aprovar exige referência HTTPS, data ISO não futura e nome do revisor. Atualiza apenas o recurso revisto em access_json e marca o relato aprovado na transação. Uma aprovação de proposta “indisponível” continua significando indisponível.

Não há autenticação de administrador web; a proteção da CLI é acesso ao ambiente/SQLite. O código verifica presença e formato de fonte/data, não se a página realmente sustenta a alegação. A responsabilidade de ler a evidência continua humana.

## 7. WCAG 2.2 como orientação, sem declaração de conformidade

A [recomendação WCAG 2.2 do W3C](https://www.w3.org/TR/WCAG22/) organiza critérios testáveis para acessibilidade web. Para orientar a próxima auditoria, são especialmente relevantes alternativas textuais (1.1.1), contraste (1.4.3), redimensionamento (1.4.4), refluxo (1.4.10), teclado (2.1.1), foco visível (2.4.7), foco não encoberto (2.4.11), tamanho de alvo (2.5.8), identificação de erro (3.3.1) e nome/papel/valor (4.1.2).

A tabela abaixo é um plano de verificação do **projeto**, não uma lista de critérios aprovados.

| Área | Evidência existente | Próxima verificação concreta |
|---|---|---|
| Alternativas de imagem | Ilustração identificada, alt em contextos | Conferir sentido em todas as fotos/estados |
| Cores | Temas e alto contraste | Medir razões de cada combinação relevante |
| Ampliação | Ajuste raiz e layouts testados | Zoom200%/400%, texto real e conteúdo sem corte |
| Teclado | Menu, modal e cards exercitados | Percorrer todos os fluxos sem mouse |
| Foco | Escape restaura e detalhes informam estado | Conferir foco após exclusão e erro dinâmico |
| Alvos | Botões reais e CSS responsivo | Medir dimensões e espaçamento |
| Formulários | Rótulos e mensagens | Associação programática de ajuda/erro e clareza |
| Conteúdo dinâmico | Status/alert/busy | Ouvir anúncios reais e evitar excesso |
| Informação física | Estados por recurso | Teste de compreensão da diferença entre incerteza e negação |

Uma auditoria também precisa de amostra representativa, combinações assistivas e participação de pessoas com deficiência. Não há base para afirmar nível A/AA/AAA alcançado.

## 8. Cultura: fonte editorial, associação e descoberta

`backend/culture_content.json` tem nove objetos com id, icon, title, kind, text, source_url, query, theme, destinations e verified_at. `cultural_content()` carrega com cache; `destination_culture(name)` faz associação explícita por nome. A API acrescenta tags/contextos ao destino.

Isso permite ao mesmo texto aparecer na descoberta e na ficha pertinente, sem transformar toda tradição em um ponto fixo do mapa. A data 2026-11-06 é editorial no arquivo; não é prova de que o link foi consultado a cada execução.

### 8.1 Bumba Meu Boi e seus sotaques

O conteúdo explica que matraca, zabumba, baixada, orquestra e costa de mão expressam formas distintas de tocar, cantar, dançar e vestir. Sua função turística é convidar à compreensão, evitando tratar a manifestação como um ritmo homogêneo.

Associações reais no código: Casa do Maranhão e Bumba Meu Boi da Floresta. O interesse específico “Bumba Meu Boi” filtra esses vínculos. A fonte editorial aponta para o CNFCP. O sistema não informa calendário de apresentações nem garante presença de grupo ao chegar.

### 8.2 Tambor de Crioula

O texto enfatiza roda, canto, tambores, memória afro-maranhense e protagonismo das comunidades. Liga-se ao Centro de Cultura e Turismo do Quilombo Urbano. A referência aponta para patrimônio imaterial do IPHAN.

Para explicar turismo responsável: o visitante deve combinar participação com responsáveis, não pressupor que uma prática comunitária está permanentemente disponível como espetáculo. O código fornece contexto, não autorização de visita.

### 8.3 Reggae maranhense

O Museu do Reggae é apresentado como ponto de partida para memória musical. A associação é um único local concreto, usado no filtro cultural e no planejador. A referência editorial é a página de museus do turismo municipal.

Esse vínculo ilustra a integração natural: a pessoa lê por que aquele espaço importa no mesmo contexto em que decide visitá-lo. Não há streaming, agenda de radiolas ou venda de ingresso.

### 8.4 Cacuriá e cultura popular

O conteúdo convida a conhecer os grupos e narrativas com respeito. A lista de destinos está vazia. Ele continua acessível como informação cultural, mas o sistema não inventa uma coordenada ou espaço para preencher o mapa.

O interesse específico pode resultar em422 no planejador por falta de associação regional. É um comportamento coerente com a base atual, não prova de que não exista cacuriá em São Luís. A referência escolhida no JSON deve ser revisada editorialmente quanto à pertinência; esta análise não verificou integralmente seu conteúdo externo.

### 8.5 Azulejos e Centro Histórico

O texto conecta fachadas, arquitetura, trabalho e transformação urbana, lembrando que o conjunto é também lugar de vida. Registra o reconhecimento mundial desde1997 como informação editorial do arquivo.

Associações: Centro Histórico, Rua Portugal e Museu de Artes Visuais. A fonte é a superintendência do IPHAN no Maranhão. Para o seminário, explicar a associação encontrada no projeto; uma pesquisa histórica independente exigiria consultar as fontes, não apenas repetir uma data do JSON como se tivesse sido auditada nesta tarefa.

### 8.6 Lendas que a cidade conta

Ana Jansen e a serpente de São Luís aparecem como tradição oral, explicitamente diferentes de acontecimentos históricos comprovados. O vínculo é Centro Histórico; fonte editorial é a página municipal de lendas.

Esse cuidado evita transformar narrativa cultural em afirmação factual. O projeto não tem áudio narrativo, realidade aumentada ou percurso geográfico completo das lendas.

### 8.7 Artesanato e artistas do fazer

O conteúdo aproxima Casa de Nhozinho, Antônio Bruno Nogueira e saberes populares; em Raposa valoriza renda de bilro e trabalho das rendeiras. Os locais associados são Casa de Nhozinho e Corredor das Rendas.

A função turística é reconhecer autoria e trabalho, não apenas mostrar produto como lembrança. Há referência da Secretaria de Turismo do Maranhão; não há loja, carrinho, catálogo de peças ou venda direta.

### 8.8 A cultura também está à mesa

Museu da Gastronomia Maranhense e Feirinha São Luís são os espaços associados. O texto chama atenção para saberes culinários e explicita que a seleção não anuncia cardápios, preços ou parceiros.

Isso deve ser distinguido de uma descrição antiga do restaurante Feijão de Corda com estimativa de preço. Nenhum desses valores é cotação atual obtida por API. A integração de gastronomia ao planejamento não calcula consumo real.

### 8.9 Quilombo Cultural

A referência territorial cita Liberdade, Camboa, Fé em Deus e Diamante no roteiro municipal. Associa Centro de Cultura e Turismo do Quilombo Urbano, Mercado Municipal da Liberdade e Bumba Meu Boi da Floresta.

O texto orienta confirmar dinâmica, participação e consentimento das comunidades. O planejamento permite tema quilombo e o backend reconhece interesse específico Quilombo Cultural; nem toda opção suportada na API possui um checkbox próprio no formulário atual.

Não existe contratação de anfitrião, sistema de autorização comunitária ou repasse financeiro. Uma evolução responsável envolveria as comunidades na autoria e na decisão sobre o que publicar.

## 9. Por que integrar ao destino ajuda

Separar totalmente “informação cultural” de “onde ir” pode obrigar o visitante a reconstruir a relação por conta própria. Os cards exibem contexto associado; a ficha aprofunda; o filtro permite descobrir locais a partir do interesse. O mesmo dado editorial atravessa as telas, reduzindo divergência textual.

Também há um limite deliberado: manifestação sem espaço associado continua editorial. Isso respeita a diferença entre prática cultural, comunidade, museu, evento e coordenada. Cultura não é um conjunto de pins intercambiáveis.

As associações atuais são pequenas e dependem de nomes exatos. O trabalho futuro inclui revisão por pessoas e instituições locais, fontes mais específicas, atualização, autorização de imagens e registro de autoria. São propostas, não funções já presentes.

## 10. O que dizer e o que evitar

| Afirmação sustentada | Afirmação a evitar |
|---|---|
| “O site possui controles de leitura e interação por teclado em fluxos testados.” | “Todas as pessoas conseguem usar sem barreiras.” |
| “Há modelo para12 recursos e filtros com evidência.” | “Todos os destinos são acessíveis.” |
| “Nenhum recurso físico está confirmado nesta base.” | “Os lugares sem resultado não têm acessibilidade.” |
| “Cultura está ligada explicitamente a espaços do catálogo.” | “Temos programação cultural em tempo real.” |
| “As lendas são apresentadas como tradição oral.” | “Essas narrativas foram comprovadas historicamente.” |
| “As WCAG orientam a próxima auditoria.” | “O projeto está certificado WCAG2.2.” |
| “Relatos entram em moderação local.” | “Qualquer usuário atualiza imediatamente o dado oficial.” |

## 11. Prioridades de evolução com evidência

Primeiro, registrar recursos de locais com inspeção, fonte, data e responsabilidade; nenhum desenho de filtro compensa banco vazio. Segundo, testar os fluxos com pessoas com deficiência e tecnologias assistivas; não basta observar o DOM. Terceiro, medir ampliação e contraste de toda a identidade visual, inclusive conteúdos personalizados.

Para cultura, priorizar curadoria participativa, atualização e autoria. Para ambos os eixos, a interface deve continuar mostrando incerteza. Uma informação não verificada apresentada com honestidade é mais útil do que uma confirmação fabricada para tornar a demonstração atraente.

