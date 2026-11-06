# Roteiros completos de fala — 5, 10 e 20 minutos

Os textos estão em primeira pessoa e podem ser lidos como fala. Os tempos incluem pequenas pausas e navegação nos pontos indicados; a velocidade de leitura varia. Ensaie com cronômetro, especialmente a versão de20 minutos. As indicações entre colchetes são ações de palco, não frases para falar. Números referem-se à análise de06/11/2026.

Nenhum texto afirma que o mapa foi resolvido, que o gerador usa IA ou que a plataforma possui certificação de acessibilidade.

## Versão A — aproximadamente 5 minutos

Bom dia, pessoal. Hoje eu vou apresentar o Explore+ SLZ, uma plataforma para descobrir lugares e organizar passeios em São Luís e em municípios próximos. A ideia é aproximar turismo, cultura e ferramentas pessoais de planejamento.

O problema que motivou a proposta é simples: encontrar o nome de um lugar não significa conseguir planejar uma visita. Muitas vezes a informação fica espalhada, a gente esquece o que encontrou e não sabe quais condições precisam ser confirmadas. Meu projeto reúne descoberta, referências culturais, favoritos e roteiros em uma mesma experiência.

[Mostrar a página inicial.]

Na entrada, eu apresento a proposta e ofereço pesquisa e planejamento. O catálogo completo permite procurar por texto, município, categoria e manifestação cultural. A base examinada tem76 destinos em São Luís, São José de Ribamar, Raposa, Paço do Lumiar e Alcântara. Esse número representa cadastros, não locais integralmente auditados.

Ao abrir uma ficha, eu encontro descrição, referência e contexto. A cultura acompanha a descoberta: o Museu do Reggae se conecta à memória musical; a Casa do Maranhão aparece ligada ao Bumba Meu Boi; o artesanato se relaciona a espaços como o Corredor das Rendas. Quando uma manifestação não tem local associado, ela permanece como informação cultural. Eu não crio um ponto artificial para preencher o mapa.

Agora vou mostrar como funciona o perfil. Depois do cadastro, a pessoa pode guardar favoritos, consultar atividades e recuperar roteiros. Também pode configurar foto, capa, tema e privacidade. A escolha de arquivo mostra uma prévia; o salvamento só acontece ao confirmar o envio. Esse detalhe evita confundir aparência local com dado realmente persistido.

[Mostrar o perfil e um roteiro salvo.]

No planejador, eu informo região, dias, orçamento e interesses. O sistema escolhe lugares do catálogo por regras programadas e distribui sugestões pelos dias. Ele não usa inteligência artificial. O orçamento é dividido por dia e por pessoa; não é uma consulta de preços. Também não há cálculo de trânsito, horário de funcionamento ou melhor caminho.

Um dos principais diferenciais do nosso projeto é a preocupação com acessibilidade. Eu separo a acessibilidade do site das condições dos lugares. A interface tem controles de contraste e texto, rótulos e operação por teclado em fluxos testados. Já os destinos possuem campos como acesso sem degraus, banheiro adaptado, audiodescrição, Libras e legendas.

Para um recurso entrar no filtro confirmado, precisa de estado, fonte e data. A base atual ainda não tem essas confirmações. Por isso uma busca pode ficar vazia, e o sistema não deve transformar ausência de evidência em promessa de passeio acessível. Eu também não afirmo conformidade integral com as WCAG sem uma auditoria adequada.

Existe uma limitação importante no mapa. Dos76 destinos,14 têm coordenadas numericamente válidas, mas nenhuma está verificada. O modo padrão exige verificação; a opção de legado permite ver os14 com aviso. Portanto, o problema de cobertura continua presente. Os testes de agrupamento passaram com pontos de teste, mas isso não valida a posição dos lugares reais.

Na parte técnica, o navegador usa HTML, CSS e JavaScript. O JavaScript conversa por uma API com Flask, em Python, e o SQLite guarda os dados. Senhas são armazenadas como hash; sessão, token CSRF e verificações de propriedade protegem ações pessoais. Há também amizades, colaboração e vouchers simbólicos, sem pagamento ou desconto comercial.

Nesta análise, os26 testes de API e os três testes de navegador passaram. Isso confirma os cenários executados, sem provar que o sistema está pronto para produção.

Eu concluo que a contribuição do Explore+ SLZ é integrar descoberta, cultura e memória de viagem. Os próximos passos são qualificar os dados, melhorar o planejamento e testar acessibilidade com usuários. O objetivo é tornar a descoberta mais útil sem esconder o que ainda precisa ser confirmado. Obrigado.

## Versão B — aproximadamente 10 minutos

Bom dia, pessoal. Eu sou responsável pela apresentação do Explore+ SLZ, um projeto de turismo que reúne descoberta de destinos, cultura e planejamento pessoal. Vou mostrar a proposta, as principais funções, como os dados circulam e quais limitações eu encontrei na versão atual.

Quando alguém quer conhecer uma cidade, costuma pesquisar lugares em páginas diferentes, salvar mensagens e tentar organizar tudo depois. Para quem precisa confirmar condições de acesso, esse processo pode ser ainda mais difícil. O nome de um lugar e uma fotografia não respondem se há entrada sem degraus, banheiro adequado ou apoio de comunicação.

Minha proposta é concentrar etapas dessa descoberta. O público pode ser um turista, um morador que quer explorar a própria região ou um grupo planejando uma saída. A plataforma não substitui a confirmação com os responsáveis pelos lugares; ela organiza informação e escolhas.

[Mostrar a página inicial e abrir o catálogo.]

A página inicial apresenta a identidade visual e os caminhos de exploração e planejamento. O catálogo é a listagem completa. Na base analisada, existem76 destinos:54 em São Luís, cinco em São José de Ribamar, seis em Raposa, quatro em Paço do Lumiar e sete em Alcântara.

Eu posso pesquisar pelo texto e combinar município, categoria e cultura. A pesquisa turística normaliza acentos e diferenças entre maiúsculas e minúsculas. O servidor devolve os resultados em JSON, e o JavaScript monta os cards. A lista e o mapa recebem a mesma coleção filtrada, mas só os destinos que atendem à regra geográfica viram marcadores.

Essa diferença é fundamental. Cadastrado não significa geolocalizado, e coordenada válida não significa coordenada confirmada. Na base atual,14 pares são numericamente válidos e zero estão verificados. Os outros62 não possuem par válido. O mapa padrão exige verificação; incluir legados é uma escolha explícita que permite visualizar os14 com aviso.

O problema de cobertura do mapa permanece. Não vou apresentar o resultado dos testes como se fosse uma vistoria geográfica. O teste de agrupamentos usa pontos controlados em banco temporário. Ele comprova que aqueles pontos não desapareceram dentro dos clusters, mas não resolve os dados dos76 destinos reais.

[Mostrar uma ficha, sem depender do fundo do mapa.]

A ficha apresenta descrição, origem da informação, contexto cultural e dados de acesso. A imagem usada atualmente nos cards é uma ilustração genérica identificada, não uma fotografia de cada lugar. Isso também precisa ser dito com clareza para não sugerir uma cobertura visual inexistente.

A cultura entra no momento da escolha. O projeto contém referências a Bumba Meu Boi, Tambor de Crioula, reggae, cacuriá, azulejaria, lendas, artesanato, gastronomia e Quilombo Cultural. As associações são explícitas. O Museu do Reggae aparece ligado ao reggae; Casa de Nhozinho e Corredor das Rendas aparecem no artesanato.

Essa relação ajuda a entender por que visitar o lugar, não apenas onde ele está. As lendas são identificadas como tradição oral. O texto sobre comunidades recomenda confirmar participação e consentimento. Já o cacuriá não tem espaço associado nesta seleção; ele permanece editorial, sem receber coordenada inventada.

Agora vou mostrar como funciona o perfil. Eu faço cadastro com nome, e-mail e senha. Depois de entrar, posso guardar destinos como favoritos e salvar roteiros. A visão geral reúne capa, foto, dados de apresentação, contadores e atividades recentes. As páginas próprias permitem rever as coleções.

[Mostrar favoritos e detalhes de um roteiro.]

Favoritos são relações entre minha conta e um destino. Repetir a marcação não cria uma segunda cópia. O histórico registra eventos específicos, como pesquisas e geração de roteiro; não é um registro de todos os cliques. Os roteiros guardam um retrato do resultado em JSON, que pode ser recuperado depois.

Nas configurações, eu altero bio, identificador, município e tema, além de foto e capa. O upload tem estados separados: arquivo selecionado, envio em andamento, salvo e erro. Escolher o arquivo ainda não altera a imagem no servidor. A imagem enviada é validada e convertida para JPEG antes de ficar no SQLite.

Também posso manter o perfil privado, permitir ou não a pesquisa de pessoas e escolher quem vê meus favoritos. Essas políticas são verificadas no backend, inclusive no endpoint de imagens. Preferências pessoais de acesso só são guardadas com consentimento e não aparecem no perfil público.

No planejamento, escolho duração, orçamento, pessoas, transporte e interesses. O algoritmo seleciona candidatos e os distribui de forma determinística. Ele não aprende com os usuários nem consulta um modelo de IA.

Um exemplo verificado foi São Luís, dois dias, R$800, duas pessoas e interesse Reggae. O resultado sugeriu o Museu do Reggae nos dois dias. Isso acontece porque havia um único espaço associado àquele interesse e a regra reutiliza candidatos. O valor diário foi R$400 e o valor por pessoa e dia foi R$200. São divisões do orçamento disponível, não preços estimados.

O resultado pode ser salvo, copiado ou aberto como texto no WhatsApp. Existe também compartilhamento por convite e link público revogável. Um convidado leitor consulta; um editor pode renomear e acrescentar notas. Não existe edição completa dos dias em tempo real.

Na parte social, a pessoa precisa optar por aparecer em pesquisa. Amizades passam por solicitação e aceitação. Bloqueio remove a relação e restringe interações. Os presentes são vouchers simbólicos: têm código, validade e estados de envio e resgate, mas não representam desconto, reserva nem pagamento.

Um dos principais diferenciais do nosso projeto é a acessibilidade, tratada em duas dimensões. Na interface, há navegação por teclado em fluxos testados, foco no modal, rótulos, estados de carregamento, alto contraste e ajuste de texto. No mundo físico, existem12 recursos independentes e cinco grupos de necessidades.

Eu não posso concluir que todo o site é acessível apenas por existir um botão de contraste. Parte dos estilos usa tamanho fixo em pixels, por exemplo, e ainda precisa de avaliação de ampliação. Também não foi feita auditoria completa com leitores de tela e participantes com deficiência.

Nos destinos, um recurso confirmado exige fonte e data. Hoje nenhum destino tem esses dados preenchidos. Um filtro vazio informa falta de evidência no cadastro, não prova que o recurso não exista na cidade. As sugestões dos usuários entram como pendentes e precisam de revisão local para alterar o dado público.

[Mostrar contraste ou a tabela de recursos.]

A arquitetura tem três partes. O frontend é HTML, CSS e JavaScript. O backend é Python com Flask. O banco é SQLite. Quando eu clico em favoritar, o navegador envia a requisição, Flask valida sessão e token CSRF, o banco grava a relação e a resposta atualiza o coração.

As senhas não são guardadas em texto: o Werkzeug gera um hash. O servidor usa o usuário da sessão para limitar cada consulta. Há cuidados de origem, tamanho e conteúdo de upload. Ainda faltam mecanismos importantes de produção, como recuperação de conta, limitação de tentativas, monitoramento e backup integral testado.

Os26 testes de API e os três testes de navegador passaram nesta execução. Foram exercitados cadastros, persistência, privacidade, relações sociais, uploads, temas e layouts pequenos. Esses resultados dão confiança nos cenários testados, mas não certificam acessibilidade física, segurança completa ou funcionamento de serviços externos.

Para concluir, o Explore+ SLZ já integra descoberta, cultura e memória pessoal em um fluxo funcional. O principal desafio agora é elevar a qualidade dos dados e do planejamento, mantendo transparência. Prefiro mostrar uma informação ainda não confirmada a prometer uma experiência que o sistema não consegue garantir. Obrigado.

## Versão C — aproximadamente 20 minutos

Bom dia, pessoal. Hoje eu vou apresentar o Explore+ SLZ e explicar tanto a experiência de quem usa quanto a estrutura que faz o sistema funcionar. Vou começar pelo problema, depois mostrar descoberta, perfil, planejamento, cultura e acessibilidade. Na parte final, vou abrir a arquitetura e os testes, incluindo o que ainda precisa ser melhorado.

A proposta parte de uma situação comum: a gente quer conhecer lugares, mas precisa reunir informação em várias fontes e depois organizar escolhas. Um morador pode nunca ter visitado um museu próximo. Um turista pode conhecer o nome do Centro Histórico, mas não compreender sua relação com arquitetura, memória e vida urbana. Uma pessoa com deficiência pode precisar confirmar condições que não aparecem em uma descrição turística comum.

O Explore+ SLZ tenta aproximar essas necessidades. Ele reúne catálogo, referências culturais e instrumentos pessoais de organização. O usuário pode pesquisar, abrir uma ficha, favoritar, gerar uma sugestão e salvar. Com isso, a descoberta deixa uma memória na conta, em vez de se perder depois que a aba é fechada.

Eu chamo isso de ferramenta de apoio ao planejamento. Não apresento como agência de viagens, sistema de reservas ou garantia operacional. Esse cuidado será importante quando falarmos de orçamento, mapa e acessibilidade.

[Mostrar a inicial e pausar para observar a identidade visual.]

A página inicial concentra a apresentação e os caminhos de uso. A identidade combina cores, cartões, tipografia e elementos ligados à proposta turística. Existe um menu compartilhado com início, exploração, planejamento e áreas pessoais. O mesmo componente é usado nas diferentes telas para manter a navegação consistente.

No navegador, abrir uma página não significa necessariamente carregar um HTML exclusivo. O projeto tem três estruturas principais: uma para início e planejamento, outra para o painel pessoal e outra para as páginas ampliadas. O JavaScript lê a rota e monta o conteúdo. Essa organização é simples para um projeto local, mas deixa clara a dependência de scripts para a experiência completa.

Agora eu vou para o catálogo. Na base examinada existem76 destinos. São54 em São Luís, cinco em São José de Ribamar, seis em Raposa, quatro em Paço do Lumiar e sete em Alcântara. Esses números são linhas cadastradas, não um levantamento de condições físicas.

A pesquisa aceita texto e pode ser combinada com município e categoria. O backend normaliza acentos e caixa para a busca textual turística. Se eu procurar por uma palavra, ele considera nome, município, descrição e interesses. Já município e categoria funcionam por correspondência exata.

[Pesquisar reggae e abrir um resultado.]

O filtro cultural acrescenta uma relação de significado. Um destino pode ser encontrado porque está associado a uma manifestação, mesmo sem representar toda a manifestação. O Museu do Reggae é um espaço concreto ligado à memória musical. Ele não é o reggae inteiro, nem uma promessa de apresentação em qualquer horário.

A ficha apresenta descrição, referência, dados de localização e contexto. A imagem genérica é identificada como ilustração original. Eu não digo que a plataforma tem uma fotografia real de todos os76 destinos, porque isso não corresponde à implementação.

As referências também precisam ser interpretadas corretamente. Sessenta e nove registros têm fonte preenchida e revisão parcial; sete permanecem como legado sem revisão. Ter um link não prova que endereço, acesso, funcionamento e preço foram confirmados. A fonte é um caminho para conferir, não um selo universal de qualidade.

Antes de avançar, quero explicar o mapa, porque ele ainda tem um problema importante. Existe diferença entre cadastro, retorno da API, coordenada válida e ponto efetivamente representado.

Todos os76 destinos aparecem na consulta sem filtro. Apenas14 têm um par de latitude e longitude numericamente válido. E nenhum desses pares está marcado como verificado. Os62 restantes não têm posição válida. O mapa padrão exige verificação; o modo legado permite os14 pontos com um aviso específico.

Isso explica uma parte central da discrepância entre muitos cards e poucos pontos. Não vou declarar o problema corrigido. Para resolvê-lo de verdade, será necessário curar coordenadas, confirmar entradas e registrar a evidência. Marcar tudo como verificado só para encher o mapa esconderia a deficiência dos dados.

O Leaflet é a biblioteca que desenha e controla o mapa. O OpenStreetMap fornece o fundo cartográfico. Uma biblioteca de clusters agrupa marcadores próximos. Se aparece um grupo com o número dez, isso pode significar dez destinos representados em uma única figura. Portanto, contar ícones não é o mesmo que contar membros.

O teste cartográfico criou40 pontos sintéticos e verificou outro ponto em um banco temporário. Depois comparou os IDs da API com os marcadores e membros dos clusters reais no navegador. Passou, inclusive sem o fundo externo. Isso comprova o mecanismo naquele cenário; não verifica a geografia do catálogo real.

[Voltar à ficha ou à seção cultural.]

A cultura é um dos eixos do projeto. Existem nove conteúdos: Bumba Meu Boi, Tambor de Crioula, reggae, cacuriá, azulejos e Centro Histórico, lendas, artesanato, gastronomia e Quilombo Cultural.

No caso do Bumba Meu Boi, o texto mostra que os sotaques envolvem maneiras de tocar, cantar, dançar e vestir. No Tambor de Crioula, destaca memória e protagonismo comunitário. O artesanato aproxima espaços como Casa de Nhozinho e Corredor das Rendas. A gastronomia aparece como saber e memória, sem vender cardápio ou preço.

As lendas são identificadas como tradição oral. Isso evita apresentá-las como fatos históricos comprovados. O conteúdo de Quilombo Cultural orienta procurar responsáveis e confirmar participação. A plataforma não presume que uma comunidade está sempre disponível para visita turística.

O cacuriá oferece outro exemplo de transparência. O texto existe, mas não há destino associado nesta seleção. Ele permanece acessível para leitura, sem criar um pin artificial. Se o usuário pedir um roteiro específico sem espaço correspondente, a API pode explicar que ainda não há candidatos.

Essa integração me parece mais natural do que separar cultura completamente da escolha. A pessoa entende por que um lugar pode interessar enquanto decide. No entanto, a curadoria ainda pode crescer com participação de artistas, comunidades e instituições locais. Essa participação não está automatizada no sistema atual.

Agora vou mostrar como funciona o perfil. Uma conta é criada com nome, e-mail e senha. O servidor valida limites e unicidade de e-mail. A senha é transformada em hash pelo Werkzeug; o texto original não é salvo. Depois do login, uma sessão mantém a identidade entre requisições.

[Mostrar o perfil autenticado.]

A visão geral reúne foto, capa, nome, identificador, bio, município, amigos e indicadores. Ela também mostra os favoritos, roteiros e atividades mais recentes. Cada coleção possui sua página para consulta. Estados vazios orientam a próxima ação.

Um favorito é uma relação entre usuário e destino. O banco impede duplicar o mesmo par. O histórico tem outro significado: ele guarda eventos que o código escolheu registrar, como pesquisa textual, geração, favorito e salvamento. Não é um sistema de rastreamento de toda navegação.

Os roteiros salvos são retratos do resultado em JSON. Se o catálogo mudar depois, o roteiro antigo não se reorganiza automaticamente. O usuário pode abrir detalhes, excluir e acessar compartilhamento. Salvar repetidamente pode criar cópias, uma limitação a tratar futuramente.

Nas configurações, a pessoa escolhe três temas e define apresentação e privacidade. A foto e a capa possuem envio independente. Selecionar um arquivo cria uma prévia local; confirmar o envio é que grava no servidor. A interface mostra os estados para que a pessoa saiba se ainda está selecionando ou se já salvou.

O servidor valida o conteúdo com Pillow, limita tamanho e resolução, corrige orientação e gera JPEG. Os bytes ficam como BLOB no SQLite. A imagem recebe um token, mas o endereço sozinho não elimina as permissões: o endpoint verifica se quem pede pode visualizar.

O perfil começa privado e fora da pesquisa de pessoas. Favoritos também começam privados. O usuário pode optar por aparecer na busca, abrir o perfil e escolher quem vê a coleção. Necessidades pessoais de acesso são guardadas apenas com consentimento.

Essa privacidade tem limites claros. Uma avaliação de destino é pública e mostra o nome de quem avaliou. E um link público de roteiro pode ser aberto por quem tiver o endereço. Portanto, perfil privado não significa anonimato em qualquer contribuição ou publicação.

[Mostrar Amigos e um roteiro já preparado.]

Na rede social, a busca exige conta e só encontra pessoas que aceitaram ser descobertas. A amizade passa por solicitação e aceitação. Recusar não é bloquear; remover não é restaurar depois. Bloquear encerra relações e restringe interações conforme as regras do backend.

Com uma amizade aceita, o dono pode convidar a outra pessoa para um roteiro. O papel de leitor permite consultar; editor permite renomear e acrescentar ideias. Não existe chat em tempo real nem edição visual completa dos dias. O recurso atual é colaboração por título e notas persistidas.

O dono também pode criar um link público de leitura e revogá-lo. Esse link não inclui as notas da colaboração. Ainda assim, antes de publicar, é preciso revisar o conteúdo do roteiro. Bloquear alguém não impede que essa pessoa acesse anonimamente um link que permaneça público.

Os presentes são outra funcionalidade social. Um voucher simbólico recebe destinatário, destino, mensagem, tema e validade. Depois pode ser enviado, cancelado ou resgatado pelo ator autorizado. A máquina de estados impede usar normalmente o mesmo convite duas vezes.

Quero reforçar a palavra simbólico. Não há pagamento, desconto negociado, reserva ou comunicação com bilheteria. O botão de enviar muda um estado interno; não envia automaticamente e-mail. É uma demonstração funcional de convite, não um produto comercial.

Agora vou para o planejador. Eu escolho região, duração, orçamento, pessoas, transporte e interesses. O servidor seleciona candidatos no catálogo, aplica condições e distribui lugares pelos dias. Não existe inteligência artificial nesse processo. O resultado é determinado pelas entradas, regras e dados.

A distribuição usa posições sucessivas e retorna ao início quando os candidatos terminam. Por isso pode repetir um lugar em dias diferentes. Um teste real com dois dias e apenas Reggae retornou o Museu do Reggae nos dois. Esse comportamento é útil para explicar a implementação, mas mostra que ainda falta melhorar a diversidade.

O orçamento total é dividido pelos dias e pelas pessoas. Com R$800, dois dias e duas pessoas, o resumo mostra R$400 por dia e R$200 por pessoa e dia. Isso é uma repartição da verba, não uma pesquisa de custos de alimentação, transporte ou ingresso.

O transporte escolhido aparece no resumo, mas não muda um cálculo de trajetos, porque esse cálculo não existe. Também não há validação de abertura, maré, travessia, clima ou continuidade de calçadas. A experiência especial de Raposa segue uma regra editorial de orçamento e interesses; não é preço oficial e pode aparecer fora do município selecionado.

[Mostrar resultado salvo, sem executar uma entrada problemática ao vivo.]

Um dos principais diferenciais do nosso projeto é a acessibilidade, mas eu preciso falar dela com precisão. Acessibilidade digital é conseguir perceber, compreender e operar a interface. Acessibilidade física é conseguir participar do passeio no lugar real. Uma não garante a outra.

Na interface, eu tenho rótulos, navegação por teclado em fluxos testados, foco controlado no modal, estados ARIA, mensagens de carregamento e erro, contraste e ajuste de texto. Há também consideração por redução de movimento e adaptação para telas pequenas.

Isso não permite dizer que o site está integralmente conforme as WCAG. Parte das fontes está definida em pixels, por exemplo, então mudar o tamanho raiz não aumenta todos os componentes de maneira igual. Não foi realizada uma auditoria completa com leitores de tela e participantes com deficiência.

No modelo físico, há12 recursos separados, como entrada sem degraus, circulação, banheiro, transporte, Braille, audiodescrição, Libras e legendas. Cinco grupos combinam parte desses campos. A combinação é uma convenção de consulta e não define toda a necessidade de uma pessoa.

Para aparecer como confirmado, um recurso exige estado, fonte e data. A base atual ainda não tem essas confirmações. Se eu selecionar condições de mobilidade, o catálogo pode retornar vazio e o planejador pode responder que não há locais com todos os requisitos confirmados.

Isso não significa que a cidade não tenha esses recursos. Significa que a plataforma não possui evidência cadastrada. A diferença é essencial para não transformar uma limitação de dados em uma afirmação sobre os lugares.

O usuário pode enviar uma sugestão na ficha. Ela entra pendente e não altera imediatamente o destino. A revisão atual é feita por comando local e exige fonte, data e revisor. A qualidade depende de uma pessoa conferir a evidência; o programa não verifica a rampa por meio de um link.

Na arquitetura, o caminho é navegador, Flask e SQLite. HTML dá estrutura, CSS cuida da apresentação e JavaScript trata eventos e comunicação. Flask recebe requisições HTTP e devolve JSON. SQLite guarda16 tabelas de aplicação, além de estruturas internas.

Quando eu favorito um destino, por exemplo, o navegador envia o ID. O servidor verifica sessão, origem e token CSRF, usa o usuário da sessão e grava a relação. Não confia num campo de formulário dizendo quem é o dono. Depois a resposta atualiza a interface.

As tabelas organizam usuários, perfis, mídias, destinos, favoritos, histórico, roteiros, avaliações, amizades, bloqueios, convites, notas, links, vouchers e relatos. Chaves e restrições ajudam a manter coerência. JSON é usado em interesses e conteúdo de roteiro; isso simplifica o retrato salvo, mas também exige validação na aplicação.

A migração cria estruturas novas sem substituir todo o banco. Ela produz uma cópia do esquema anterior. Essa cópia não contém os registros e não deve ser apresentada como backup completo. Para produção, seria necessário um plano de cópia e restauração dos dados e imagens.

A versão local usa servidor de desenvolvimento. Uma publicação pública exige outra configuração: depuração desligada, segredo estável, HTTPS, monitoramento, proteção de conta, atualização de dependências e testes de recuperação. Nem todas essas medidas estão implementadas.

Por fim, eu executei os26 testes de API e os três scripts de navegador disponíveis. Todos passaram nesta execução. Os testes usaram bancos temporários e contas fictícias. Exercitaram persistência, isolamento, CSRF, favoritos, roteiros, fotos, privacidade, amizades, convites, vouchers, temas e layouts.

Os testes também simulam ausência de tiles. Isso mostra que as funções locais podem continuar sem o fundo cartográfico. Eles não comprovam disponibilidade de todo serviço externo, segurança completa ou acessibilidade real dos destinos.

O desafio principal que identifiquei não é apenas acrescentar mais telas. É aproximar a promessa do sistema da qualidade dos dados e das verificações. Coordenadas, recursos de acesso e regras do planejador precisam evoluir com evidência.

Eu concluo que o Explore+ SLZ já oferece uma base funcional para integrar descoberta, cultura e memória de viagem. O próximo passo é aprofundar a curadoria e o teste com pessoas reais, mantendo a honestidade sobre os limites. Esse é o tipo de evolução que pode tornar a ferramenta mais útil para moradores e visitantes. Muito obrigado. Fico à disposição para as perguntas.

## Ajuste de ritmo e ensaio

Leia cada versão sem clicar e marque seu tempo natural. Depois acrescente a navegação preparada: cerca de20–30 segundos na versão curta, até1 minuto na intermediária e2–3 minutos na longa. Se ultrapassar o tempo, reduza a demonstração e alguns exemplos, preservando as ressalvas essenciais sobre mapa, acessibilidade, orçamento e vouchers.

Não preencha tempo com promessas novas. Se falar rápido, faça pausas após o retrato do catálogo, a diferença entre digital/físico e o resultado dos testes. Na versão longa, os momentos de tela são parte da apresentação e não exigem improvisar uma funcionalidade adicional.

