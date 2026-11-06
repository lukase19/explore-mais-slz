# Explore+ SLZ — documentação técnica e funcional para seminário

**Data da análise:** 6 de novembro de 2026. **Escopo:** implementação local encontrada nesta pasta, sem alterar funcionalidades. Os números descrevem a base examinada nesta data, não uma base futura. Exemplos de pessoas neste material são fictícios.

## Como estudar este material

Este arquivo explica o sistema como um conjunto. O [inventário de páginas e controles](02_CADA_PAGINA_E_BOTAO.md) acompanha cada ação de interface. A [arquitetura e o banco](03_ARQUITETURA_E_BANCO.md) registram contratos, colunas, relações e funções. Os [diferenciais](04_ACESSIBILIDADE_E_CULTURA.md), [falas completas](05_ROTEIROS_DE_FALA.md), [demonstração](06_DEMONSTRACAO_AO_VIVO.md), [perguntas](07_40_PERGUNTAS_E_RESPOSTAS.md), [glossário](08_GLOSSARIO_E_RESUMO.md) e [limitações](09_BUGS_E_LIMITACOES.md) complementam a preparação.

**Critério de evidência:** “implementado” significa que há um caminho de código funcional; “verificado” informa a execução realizada; “parcial” indica que uma parte existe, mas a promessa completa ainda não é atendida; “demonstrativo” significa que a operação é interna e simbólica; “futuro” indica ausência de implementação. Uma intenção de design descrita abaixo é interpretação da função do recurso, não depoimento dos autores.

## 1. O projeto em linguagem simples

Explore+ SLZ é uma plataforma local de descoberta e planejamento de passeios em São Luís e arredores. Ela aproxima uma lista de lugares, explicações culturais e ferramentas pessoais. Uma pessoa pode descobrir um museu, compreender sua ligação com o reggae, guardá-lo como favorito, gerar uma sugestão de passeio e reencontrá-la em seu perfil.

O problema tratado é a dispersão de informações: saber que um lugar existe não resolve como organizar interesses, consultar referências culturais ou guardar escolhas. O projeto reúne essas tarefas. Isso tem utilidade tanto para um turista que visita a cidade pela primeira vez quanto para um morador que quer conhecer espaços pouco explorados em sua rotina.

A cobertura atual inclui São Luís, São José de Ribamar, Raposa, Paço do Lumiar e Alcântara. O nome da opção “Ilha de São Luís” no planejador é operacional: sua consulta reúne municípios diferentes de Alcântara. Não se deve chamar todos os destinos de uma única cidade, nem prometer que deslocamentos e travessias foram calculados.

O público potencial inclui visitantes, moradores, estudantes, grupos de amigos e pessoas que precisam consultar condições de acessibilidade. Isso não significa que o sistema já garanta uma viagem acessível. Há mecanismos para registrar necessidades e exigir evidências por local, porém a base atual não tem recursos físicos confirmados.

Em relação a um catálogo simples, existem memória pessoal de atividades, favoritos, roteiros salvos, personalização, amizades, convites para roteiros e presentes simbólicos. A cultura aparece junto de espaços concretos, em vez de ficar apenas em uma página isolada. A escolha por aproximar conteúdo e destino pode ajudar o visitante a entender o significado do passeio enquanto decide.

## 2. O projeto em linguagem técnica

É uma aplicação web com backend Python/Flask, persistência SQLite e frontend HTML/CSS/JavaScript sem framework de componentes. Flask entrega arquivos estáticos e páginas de entrada; JavaScript identifica a rota, consulta endpoints JSON e monta conteúdo dinâmico. Frontend e API usam a mesma origem HTTP.

Os três documentos HTML principais são `frontend/index.html`, `frontend/painel.html` e `frontend/experiencias.html`. As diversas URLs não correspondem a um arquivo HTML independente para cada tela. Isso reduz repetição estrutural, mas torna a renderização fortemente dependente de JavaScript.

O módulo `backend/app.py` configura a aplicação, conexão, autenticação, catálogo, planejador e dados pessoais básicos. `backend/expansion.py` instala as funcionalidades sociais, configurações, imagens, compartilhamento, vouchers e relatos. `backend/migrations.py` evolui o esquema; `catalog.py` abastece o catálogo; `culture.py` associa conteúdo editorial aos nomes dos destinos.

Não há chamada a modelo de linguagem, rede neural ou serviço de IA no gerador. Ele aplica seleção, ordenação e distribuição determinísticas. Leaflet renderiza o mapa; MarkerCluster agrupa pontos; OpenStreetMap fornece os blocos visuais do mapa pela rede.

## 3. Retrato mensurável da versão examinada

| Indicador | Resultado | Significado |
|---|---:|---|
| Destinos cadastrados | 76 | Linhas reais de `destinos` |
| São Luís | 54 | Município do cadastro |
| São José de Ribamar | 5 | Município do cadastro |
| Raposa | 6 | Município do cadastro |
| Paço do Lumiar | 4 | Município do cadastro |
| Alcântara | 7 | Município do cadastro |
| Destinos com referência de origem | 69 | URL preenchida; não certificação integral |
| Revisão parcial | 69 | `review_status=partial` |
| Legado sem revisão | 7 | `legacy_unverified` |
| Coordenadas numericamente válidas | 14 | Número finito e dentro dos intervalos |
| Coordenadas verificadas | 0 | Válidas e marcadas `verified` |
| Sem par de coordenadas válido | 62 | Não elegíveis nem no modo legado |
| Sem coordenadas verificadas | 76 | Contador `pending_coordinates` da API |
| Acessibilidade preenchida em `access_json` | 0 destinos | Todas as linhas têm `{}` |
| Tabelas de aplicação | 16 | Além de `sqlite_sequence` interna |
| Integridade estrutural SQLite | `quick_check: ok` | Não verifica verdade turística ou ausência de todo erro lógico |

A API sem filtros devolveu os mesmos 76 destinos. Seu resumo de mapa devolveu 14 válidos, zero verificados e 76 pendentes. **Pendente não significa necessariamente nulo:** nesse contador também entram os 14 pares válidos ainda não verificados. Evidência: `row_to_dict` e `pesquisar_destinos` em `backend/app.py`; consulta independente em SQLite somente leitura.

## 4. Jornada de descoberta

### 4.1 Página inicial e pesquisa

A página inicial oferece identidade visual, apresentação, cards de benefícios, destaques, formulário de planejamento, pesquisa e mapa. A pesquisa envia `q` para `GET /api/destinos`. O JavaScript espera 250 ms após digitação; Enter e botão disparam a consulta imediatamente. Uma consulta nova cancela a anterior na página inicial com `AbortController`.

No servidor, texto é normalizado para comparação sem diferença de acentos e caixa. São examinados nome, município, descrição e interesses. Município e categoria usam igualdade; interesses usam correspondência textual normalizada. Portanto, pesquisar “reggae” não equivale necessariamente a selecionar qualquer lugar de uma categoria genérica.

A consulta carrega destinos e filtra em Python. Não há paginação nem limite arbitrário escondendo itens no frontend. Para o volume atual é simples de compreender; com grande crescimento deverá ser repensada. Para usuário autenticado, pesquisa textual não vazia com até 120 caracteres pode gerar histórico. Apenas abrir uma lista ou mudar um filtro sem texto não representa automaticamente uma visita registrada.

### 4.2 Catálogo completo

`/catalogo` é a tela de exploração completa. Já `/explorar` entrega a página inicial, preservando a experiência anterior. O menu atual aponta “Explorar” para o catálogo. As duas entradas existem, mas seus controles não são idênticos.

O catálogo obtém municípios e categorias a partir dos dados disponíveis, metadados de acessibilidade e nove referências culturais. O formulário combina texto, município, categoria, cultura, grupos de necessidades e recursos específicos. Filtros culturais repetidos aceitam associação a qualquer cultura escolhida; requisitos de acessibilidade exigem todos os recursos resultantes, com confirmação, fonte e data.

A mesma coleção filtrada alimenta cards e mapa. O seletor de pontos legados muda somente a elegibilidade cartográfica; não acrescenta destinos ao resultado da pesquisa. O catálogo mantém os parâmetros na URL, útil para repetir uma busca.

### 4.3 Ficha de destino

`/destino/<id>` apresenta nome, descrição, município, categoria, endereço quando disponível, referência, contexto cultural, situação cartográfica, recursos de acessibilidade, avaliações e ações pessoais. A imagem de destino atual é uma ilustração original genérica, explicitamente identificada; não uma fotografia documental de cada local.

Um visitante pode ler o conteúdo e as avaliações. Favoritar, avaliar ou propor uma correção exige conta. A avaliação recebe nota de 1 a 5 e comentário de 5 a 1.000 caracteres. Existe uma avaliação por usuário e destino: um novo envio atualiza a anterior. Não há moderação de avaliações implementada.

A sugestão de acessibilidade é diferente de avaliação turística. Ela cria um relato pendente, não altera imediatamente os dados públicos do destino e não declara o local acessível.

## 5. Mapa: funcionamento e problema ainda aberto

Latitude indica posição norte/sul e longitude indica posição leste/oeste em graus. O código aceita latitude entre −90 e 90 e longitude entre −180 e 180, rejeitando valores ausentes, não numéricos ou não finitos. Estar nesses limites só prova formato plausível. Não comprova que o ponto corresponde à entrada correta de um prédio.

`frontend/maps.js` cria um mapa Leaflet inicialmente centrado na região. Os assets Leaflet 1.9.4 e MarkerCluster 1.5.3 estão em `frontend/vendor`; os blocos de OpenStreetMap continuam externos. Falta de internet pode retirar o fundo cartográfico sem retirar os dados do catálogo.

Por padrão, um marcador exige `location.verified=true`. A opção de incluir legados admite também pares válidos não verificados, com aparência e aviso distintos. Sem filtros, a base atual permite **zero destinos representados por padrão** e **14 no modo legado**. Outros 62 permanecem sem posição válida.

MarkerCluster junta pontos próximos numa figura com contador. Um cluster de 10 não significa que nove lugares foram descartados: ele representa dez IDs. Coordenadas idênticas podem exigir expansão do agrupamento. O destaque circular de seleção é uma camada auxiliar e não um destino extra.

Ao atualizar a lista, `setPlaces` limpa as camadas anteriores, cria marcadores elegíveis e ajusta os limites. Ao selecionar um destino, `focus` procura um marcador já pertencente ao conjunto; não cria um ponto fictício para satisfazer o clique. O foco expande o cluster quando necessário, abre o popup e destaca o local.

**Situação para a apresentação:** o problema de muitos destinos cadastrados e poucos no mapa permanece. Há causa confirmada de cobertura de dados e política de verificação; não foi demonstrado desaparecimento de marcadores elegíveis nesta execução. O teste de clusters inseriu 40 pontos sintéticos e marcou um ponto de teste como verificado em SQLite temporário. Ele valida o mecanismo para 41 pontos controlados, não confirma 41 coordenadas da base normal.

Hipóteses adicionais, que precisam de investigação específica em uma ocorrência, incluem filtros ativos, zoom/agrupamento, tiles indisponíveis e falha de carregamento de assets. Não atribuir a elas uma causa já comprovada sem reproduzir o caso.

## 6. Planejador: entrada, regra, resultado e memória

O formulário recebe município/região, duração, orçamento total, pessoas, transporte, interesses e necessidades. A interface oferece durações 1, 2, 3, 4, 5 e 7; a API aceita de 1 a 30. Dias são convertidos por `int`, orçamento por `float`, e o servidor exige orçamento finito maior que zero e lista não vazia de interesses.

A consulta seleciona lugares da região. Temas editoriais opcionais restringem candidatos. Depois são exigidos os recursos de acessibilidade selecionados. A função `confirmed_features` não aceita apenas um rótulo “confirmado”: também exige fonte e data preenchidas. Na base examinada, filtros físicos confirmados tendem a retornar zero; o planejador devolve 422 quando não pode satisfazê-los.

Interesses comuns cruzam a lista de interesses do destino; interesses culturais específicos também usam as associações explícitas de `culture_content.json`. Sem correspondência cultural específica, responde 422 para não inventar um espaço. Sem correspondência genérica, pode usar os outros lugares da região.

Cada dia utiliza as posições `2 × índice do dia` e `2 × índice + 1`, com módulo pelo número de candidatos. Se ambas apontam para o mesmo nome, só aparece uma parada nesse dia. Em dias diferentes, repetições são possíveis. Não existe otimização de distância, horário de abertura, clima, trânsito, maré, custos de ingresso ou transporte.

O orçamento diário é orçamento total dividido pelos dias. O valor por pessoa/dia divide novamente pela quantidade interpretada. Transporte e pessoas aparecem no resumo; o transporte escolhido não aciona uma API de mobilidade. “6 ou mais” é tratado como seis para a conta, não como quantidade real conhecida.

Há um bloco especial de Raposa quando o orçamento está entre R$ 1.000 e R$ 2.000, há interesse Natureza, Praias ou Família e não há exigência física de acessibilidade. Essa regra editorial não está restrita ao município escolhido. Seu link externo não constitui reserva, parceria comprovada nem preço oficial.

O frontend acrescenta uma pausa genérica para alimentação ao desenho dos dias. Essa pausa não é um destino adicional devolvido em `days[].stops`. O resultado pode ser copiado, enviado como texto ao WhatsApp ou salvo mediante login. WhatsApp apenas abre um endereço `wa.me` com o texto; não existe integração de envio automático.

### Exemplo executado em cópia temporária da base

Requisição: São Luís, 2 dias, R$ 800, 2 pessoas, A pé, apenas Reggae, sem exigências físicas selecionadas.

Resultado HTTP 200: dia 1, “Comece explorando”, Museu do Reggae; dia 2, “Feche a viagem com boas memórias”, Museu do Reggae novamente. Resumo: R$ 400/dia e R$ 200/pessoa/dia; experiência especial nula. A repetição é coerente com um único espaço associado ao interesse. Uma apresentação honesta pode usar esse exemplo para mostrar tanto o vínculo cultural quanto a limitação do algoritmo.

O JSON e o texto integral efetivamente retornados estão no apêndice do documento 03. Não se está sugerindo que visitar o mesmo museu por dois dias seja a melhor viagem.

## 7. Conta, sessão e perfil pessoal

### Cadastro e entrada

O modal compartilha o formulário de login e cadastro. No cadastro, pede nome, e-mail e senha; no login, apenas e-mail e senha. O servidor exige nome de 2 a 100 caracteres, e-mail de 5 a 254 contendo “@” e senha de 8 a 128. Essa verificação de e-mail é simples: não confirma propriedade da caixa postal.

E-mail é normalizado para minúsculas e tem unicidade sem diferença de caixa no banco. A senha é transformada com `generate_password_hash` do Werkzeug e conferida por `check_password_hash`. O texto original não é gravado. Não há recuperação de senha, confirmação de e-mail, autenticação multifator ou troca de senha na interface.

Após autenticar, o servidor limpa a sessão anterior, guarda `user_id` e gera token CSRF. O cliente consulta `/api/auth/me` e `/api/profile-settings` para reconstruir estado. A sessão padrão Flask usa cookie assinado: assinatura protege integridade, não torna seu conteúdo secreto. A [documentação oficial do Flask](https://flask.palletsprojects.com/en/stable/quickstart/#sessions) explica esse comportamento.

### Visão geral

`/perfil` reúne capa, avatar ou iniciais, nome, identificador, bio, município, número de amigos, contadores, últimos favoritos, roteiros e atividades. A grade adapta sua organização conforme largura. Os estados vazios orientam a próxima descoberta em vez de esconder a seção.

As estatísticas de pesquisas contam registros de histórico do tipo pesquisa. Não são telemetria de todos os cliques ou visitas. Favoritos e roteiros contam suas tabelas. Limpar o histórico altera o contador de pesquisas, mas não exclui favoritos nem roteiros.

O painel consulta resumo, histórico, favoritos e roteiros com `Promise.allSettled`. Uma falha em um bloco pode ser apresentada com repetição local sem descartar todos os demais. Falha de sessão tem um caminho próprio de “Tentar novamente”.

O formulário básico do perfil altera nome e lista de interesses. O e-mail aparece desabilitado, porque não há alteração implementada. O perfil público é outra tela e usa permissões mais restritas.

### Favoritos, atividades e roteiros salvos

Favoritar usa `PUT /api/favoritos/<id>` com inserção ignorando duplicata. Desfavoritar é `DELETE`, limitado ao dono da sessão. Essa decisão torna a marcação idempotente: repetir PUT não multiplica o favorito.

O histórico reúne pesquisas textuais, geração de roteiro, adição de favorito e salvamento de roteiro; não toda navegação. Mostra até 100 eventos recentes. Limpar pede confirmação e elimina registros do próprio usuário. A operação não pode ser desfeita pela interface.

Roteiros salvos guardam um retrato JSON da sugestão, com título e data. Detalhes podem ser abertos/fechados; excluir pede confirmação; colaborar abre a tela específica. Salvar o mesmo resultado várias vezes pode criar múltiplos registros. Um roteiro salvo não é recalculado automaticamente quando o catálogo muda.

## 8. Personalização e upload

`/configuracoes` é a edição ampliada. Contém nome, identificador público, bio, município, interesses, três temas, posição de avatar/capa, privacidade, convites e preferências consentidas de acesso. O identificador precisa começar com letra ASCII e ter 3 a 30 caracteres entre letras, números e sublinhado. Nomes e descrições permitem texto comum, sem essa restrição de identificador.

Os temas `forest`, `ocean` e `sunset` modificam variáveis CSS. O tema persistido fica em `profiles.theme`; uma cópia no navegador ajuda a aplicá-lo antes da resposta da sessão. Após login, o valor servidor é reaplicado. Contraste e tamanho de texto são preferências locais do navegador, não campos do perfil sincronizados.

Foto e capa têm fluxos independentes do botão “Salvar configurações”. Escolher arquivo cria uma prévia `blob:` local; **não faz upload**. O usuário precisa acionar o botão de envio da respectiva imagem. Estados explícitos: nenhuma imagem, imagem atual, arquivo selecionado, enviando, salvo e erro.

O cliente verifica tamanho e MIME declarado como conveniência. O servidor verifica conteúdo com Pillow, aceita JPEG/PNG/WebP, limita arquivo a 4 MiB e imagem a 16 megapixels, corrige orientação EXIF, converte para RGB e gera JPEG. Avatar cabe em 512 × 512; capa em 1800 × 1000, preservando proporção no processamento. A exibição usa recorte visual por `object-fit/object-position`.

Os bytes ficam em BLOB na tabela `media`. Não se guarda o nome original do arquivo. Um token aleatório forma a URL `/media/<token>`. Substituir usa uma linha por usuário e tipo; remover elimina o registro. As coordenadas de enquadramento são porcentagens de 0 a 100 e precisam de “Salvar configurações”.

A URL não é autorização suficiente: o endpoint de mídia verifica dono, perfil público ou amizade, além de bloqueio. A resposta usa `private, no-store` e `nosniff`. Isso não apaga cópias que alguém já capturou enquanto podia visualizar.

Os testes atuais comprovaram persistência após recarregar e autenticar novamente, rejeição de imagem corrompida mantendo a anterior, estados de upload e remoção. Não apareceu falha reproduzida nesses cenários. Isso não comprova comportamento com todos os modelos de celular, codecs ou redes.

## 9. Privacidade e rede social

Por padrão, perfil não é público, não aparece em pesquisa e favoritos são privados. Convites são permitidos, mas uma solicitação de amizade também depende de o destinatário estar descobrível. Preferências de acessibilidade só persistem mediante consentimento; retirar consentimento esvazia a seleção.

A pesquisa de pessoas exige login e dois caracteres. Examina nome ou identificador de perfis descobríveis, exclui a própria conta e pessoas bloqueadas. Ela não normaliza acentos como a pesquisa turística. Retorna dados de apresentação, não e-mail, senha ou histórico.

Amizades usam uma única relação para cada par de usuários, com remetente, destinatário e estado. Solicitar gera pendência; só o destinatário pode aceitar ou recusar uma pendência. Remover encerra a amizade. Bloquear é direcional na tabela, mas a verificação de visibilidade considera as duas direções; remove amizade e revoga convites entre o par. Desbloquear não restaura amizade automaticamente.

O perfil público `/p/<handle>` aceita visitante anônimo apenas se público; amigos e o próprio dono têm acesso conforme regras. Favoritos podem ser privados, de amigos ou públicos. O histórico e as necessidades pessoais não aparecem no perfil público. Entretanto, avaliações públicas exibem o nome de quem avaliou mesmo quando o perfil é privado: a privacidade não é anonimato global.

## 10. Colaboração e compartilhamento

O dono de um roteiro pode convidar amigo aceito que permita convites. Escolhe leitor (`viewer`) ou editor (`editor`). O destinatário aceita ou recusa em Amigos. Um convite pendente não libera conteúdo.

O dono e editor podem renomear e acrescentar notas; leitor apenas consulta. Notas guardam autor e data. O JSON dos dias não tem um editor completo na interface. Não existem chat em tempo real, cursores simultâneos, revisão de notas ou exclusão de notas.

O dono também pode criar um link público de leitura, protegido por token aleatório. Quem obtiver esse endereço pode ver título e roteiro sem login. Revogar elimina o token e uma consulta posterior retorna 404. O link não divulga notas de colaboração; o conteúdo do roteiro deve ser revisado antes de publicar. Bloquear alguém na rede social não impede que essa pessoa use anonimamente um link que continue público.

A representação compartilhada usa os dias e a nota do roteiro; não mostra todos os elementos da versão pessoal, como a experiência especial. O dado pode continuar salvo no JSON, mas sua apresentação nesse modo é parcial.

## 11. Presentes e vouchers demonstrativos

A página `/presentes` trabalha com amigos aceitos, destinos, mensagem, tema visual e validade. Emite um código simbólico, depois permite enviar, cancelar e resgatar conforme papel. Há registro de itens enviados e recebidos; o destinatário não vê um item ainda apenas emitido.

Estados: emitido → enviado → resgatado; emitido/enviado → cancelado; emitido/enviado vencido → expirado. O resgate é uma atualização condicional do estado enviado, impedindo um segundo resgate válido na mesma lógica. A validade aceita até 366 dias e é armazenada em UTC.

A expiração é atualizada ao listar ou transicionar vouchers, não por processo de agendamento. Não existem pagamento, saldo, desconto negociado, QR code comercial, comunicação com bilheteria ou empresa, nem garantia de realização da experiência. “Enviar” significa mudar o estado interno do convite; não envia e-mail ou WhatsApp.

## 12. Inclusão com responsabilidade

Acessibilidade digital envolve conseguir perceber, compreender e operar a interface. O sistema oferece atalhos para conteúdo, rótulos, estados ARIA, foco, operação de menu por teclado, modal com contenção de foco, alto contraste, controle de fonte e redução de movimento.

Acessibilidade física envolve entrada, circulação, banheiro, transporte e outros recursos de cada destino. O catálogo distingue confirmado, indisponível e não verificado. Não verificado não equivale a inacessível; significa ausência de evidência suficiente registrada.

Os filtros agrupam necessidades, mas um grupo não substitui conhecer a pessoa. Por exemplo, mobilidade combina acesso sem degraus, circulação e sanitário; nem toda necessidade de uma pessoa com deficiência motora se resume a esses três campos. Usuário pode consultar recursos específicos.

Não foi realizada auditoria completa com leitores de tela, pessoas com deficiência, todos os critérios WCAG ou inspeção física dos lugares. O controle percentual de fonte também encontra limites em estilos com tamanho fixo em pixels. O documento 04 separa o mecanismo implementado de comprovação de usabilidade.

## 13. Segurança, dados e operação

A aplicação usa SQL com parâmetros para valores externos, validação de entradas, propriedade de registros, hash de senha, assinatura de sessão, verificação de origem e token CSRF em escritas autenticadas. Texto dinâmico é escapado nos renderizadores. Esses mecanismos reduzem riscos específicos, sem provar segurança integral.

A chave de sessão precisa vir de `EXPLORE_SECRET_KEY` em operação persistente; sem ela, é aleatória no início do processo, invalidando sessões após reinício e podendo divergir entre processos. `EXPLORE_HTTPS=1` ativa cookie Secure e requer ambiente HTTPS coerente. HttpOnly e SameSite Lax já são configurados.

A inicialização importa e cria banco/tabelas/migração/semente. Por isso a auditoria importou o backend apenas com `EXPLORE_DATABASE_PATH` apontando a uma cópia temporária. A inspeção do banco original usou conexão somente leitura. Testes também criam bancos temporários.

Não há proteção de força bruta por limite de tentativas, recuperação de conta, administração web de conteúdo, observabilidade de produção ou política automatizada de retenção. O servidor direto usa modo de depuração local; a disponibilização pública exige configuração própria de produção, HTTPS, segredo estável, backup integral, revisão de permissões e operação segura. O [Flask distingue o servidor de desenvolvimento da implantação de produção](https://flask.palletsprojects.com/en/stable/quickstart/).

O backup produzido pela migração contém **esquema SQL**, não os registros nem BLOBs. Não permite recuperar usuários, roteiros e imagens sozinho. Isso precisa ser explicado para não confundir cópia de estrutura com plano de recuperação.

## 14. Verificação efetivamente realizada

Foram executados os 26 testes descobertos por `unittest` e os três scripts de navegador existentes, com sucesso. Houve navegação automatizada em Chrome headless, contas fictícias, simulação de falhas e larguras de 320, 390, 768 e 1440 pixels nos cenários de cada script. Nenhum erro JavaScript capturado nesses percursos.

Os testes cobrem conta, CSRF, isolamento, favoritos, roteiros, avaliações, catálogo, cultura, filtros, imagens, privacidade, amizade, colaboração, links, vouchers, relatos, moderação, migração, temas e menu. Cobertura funcional não é cobertura total de linhas; não foi produzido percentual de cobertura.

Também foram conferidos SQLite, rotas Flask registradas e resposta real de catálogo, metadados, cultura e um roteiro determinístico sobre cópia temporária. Os resultados detalhados e lacunas estão no documento 09.

## 15. O que apresentar como evolução

Prioridades justificadas pelas lacunas reais: curadoria de coordenadas e acessibilidade com fontes e responsáveis; revisão das regras do planejador para reduzir repetição e respeitar região; roteiro geográfico e transporte com dados adequados; auditoria de acessibilidade com usuários; mecanismos de recuperação e proteção de conta; implantação e backups de produção.

Pagamentos, reservas, descontos comerciais e IA seriam projetos novos, com validação e custos próprios. Não devem ser incluídos entre as funções já existentes. O valor do protótipo atual está em integrar descoberta, cultura e memória pessoal e, ao mesmo tempo, tornar visível quando a informação ainda não é confiável.


## 16. Inventário dos arquivos-fonte analisados

Arquivos de aplicação, testes, configuração, assets textuais e documentação presentes no manifesto anterior. Bibliotecas vendorizadas foram identificadas por versão, manifesto, licença e uso; seu código interno é dependência externa, não regra de negócio. Arquivos binários/base64 não são reproduzidos como se fossem código textual didático.

| Caminho | Bytes | Linhas |
|---|---:|---:|
| .gitignore | 124 | 16 |
| ANALISE_PROJETO.md | 9163 | 78 |
| INICIAR_WINDOWS.bat | 352 | 17 |
| LEIA_PRIMEIRO.md | 2805 | 46 |
| README.md | 8608 | 148 |
| RELATORIO_CORRECOES.md | 12796 | 125 |
| RELATORIO_EXPANSAO_2.md | 16610 | 143 |
| backend/__init__.py | 0 | 1 |
| backend/app.py | 30192 | 525 |
| backend/catalog.py | 9891 | 110 |
| backend/culture.py | 721 | 16 |
| backend/culture_content.json | 5669 | 133 |
| backend/expansion.py | 26871 | 407 |
| backend/migrations.py | 7697 | 97 |
| backend/moderate_accessibility.py | 2743 | 45 |
| browser_corrections.py | 14352 | 138 |
| browser_expansion.py | 10817 | 111 |
| frontend/account.js | 2939 | 53 |
| frontend/catalogo.js | 10449 | 35 |
| frontend/configuracoes.js | 10842 | 57 |
| frontend/cultura.js | 987 | 8 |
| frontend/expansion.css | 15433 | 21 |
| frontend/experiencias.html | 1773 | 4 |
| frontend/experiencias.js | 5914 | 41 |
| frontend/index.html | 82061 | 109 |
| frontend/maps.js | 5674 | 61 |
| frontend/navigation.js | 3645 | 32 |
| frontend/painel.css | 11267 | 31 |
| frontend/painel.html | 2955 | 38 |
| frontend/painel.js | 18029 | 148 |
| frontend/script.js | 18703 | 307 |
| frontend/social.js | 12509 | 35 |
| frontend/style.css | 41098 | 348 |
| frontend/theme-init.js | 241 | 3 |
| frontend/themes.css | 6053 | 27 |
| frontend/vendor/leaflet/leaflet.css | 14806 | 662 |
| frontend/vendor/leaflet/leaflet.js | 147552 | 6 |
| frontend/vendor/manifest.json | 1923 | 47 |
| frontend/vendor/markercluster/MarkerCluster.Default.css | 1287 | 60 |
| frontend/vendor/markercluster/MarkerCluster.css | 872 | 15 |
| frontend/vendor/markercluster/leaflet.markercluster.js | 34136 | 2 |
| requirements.txt | 35 | 3 |
| scripts/vendor_maps.py | 1327 | 22 |
| test_api.py | 9249 | 148 |
| test_browser.py | 9039 | 149 |
| test_corrections.py | 4106 | 59 |
| test_expansion.py | 20338 | 270 |
