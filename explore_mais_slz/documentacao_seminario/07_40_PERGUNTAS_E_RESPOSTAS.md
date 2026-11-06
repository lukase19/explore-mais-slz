# Perguntas da banca — 50 respostas fundamentadas

Respostas preparadas para a versão de06/11/2026. Use a primeira frase como resposta curta e o restante para aprofundar. Referências locais indicam onde conferir o comportamento; não são afirmações de certificação.

## Proposta, turismo e originalidade

### 1. O que é o Explore+ SLZ?

É uma plataforma local de descoberta e planejamento turístico, com cultura e memória pessoal de escolhas. A pessoa pesquisa lugares, consulta contexto, favorita e salva sugestões. Também existem relações sociais e colaboração. Não é uma agência de reservas. Evidência: index.html, catalogo.js, painel.js e rotas de app.py.

### 2. Que problema o projeto procura resolver?

A dispersão de informação e a dificuldade de organizar o que se deseja conhecer. O sistema aproxima catálogo, preferências e recuperação posterior. Essa é a leitura funcional da proposta; não foi realizado estudo quantitativo de mercado nesta análise. Não afirmar que foi comprovada uma taxa de redução de tempo.

### 3. Quem pode usar?

Moradores, turistas, estudantes e grupos podem encontrar utilidade. As páginas de descoberta e planejamento são públicas; funções pessoais precisam de conta. Pessoas com deficiência são consideradas na interface e no modelo de informação, mas a experiência completa ainda precisa de avaliação com participantes.

### 4. Qual a diferença para um catálogo comum?

Há favoritos, histórico, roteiros persistidos, perfil personalizado, políticas de privacidade, amizades e colaboração. Cultura também é associada aos lugares. Originalidade aqui é a combinação contextual implementada; não se afirma invenção mundial de cada componente ou superioridade comprovada sobre outros produtos.

### 5. Quantos destinos existem e por que não são83?

Existem76. A carga antiga tem14 e a seleção editorial tem69, mas sete nomes coincidem. Nome único e inserção idempotente impedem contar essas coincidências duas vezes:14+69−7=76. Evidência: app.py, catalog.py e consulta de destinos.

### 6. Todos os locais foram verificados pessoalmente?

Não. Sessenta e nove têm referência e revisão parcial; sete são legado sem revisão. Nenhum par geográfico está marcado como verificado e nenhum recurso físico foi confirmado na base examinada. É importante separar cadastro de levantamento em campo.

### 7. Alcântara faz parte da opção Ilha de São Luís?

No código, não. A opção “Ilha de São Luís” consulta municípios diferentes de Alcântara. Alcântara aparece como escolha própria. Isso não é um cálculo de travessia ou definição geográfica automatizada; é uma regra de seleção. Evidência: gerar_roteiro, app.py.

### 8. Como o projeto promove cultura sem transformar tudo em atração?

Os textos contextualizam memória, trabalho e protagonismo comunitário. As associações são explícitas com espaços concretos. Lendas são identificadas como tradição oral e manifestações sem espaço associado continuam editoriais. A participação comunitária mais ampla é evolução proposta, não integração já feita.

## Tecnologias e arquitetura

### 9. Qual é a diferença entre frontend e backend?

Frontend é o que o navegador apresenta e executa: estrutura, aparência, eventos e montagem de resultados. Backend recebe requisições, valida regras e acessa dados. No projeto, JavaScript chama endpoints Flask; o servidor consulta SQLite e devolve JSON. CSS não executa a regra de autorização.

### 10. Por que Python e Flask?

São a implementação encontrada para rotas, validação e acesso ao banco. Flask liga URLs a funções e serve arquivos/JSON; Python permite organizar as regras e testes. É razoável dizer que atende ao escopo local com estrutura pequena, mas não inventar uma decisão histórica dos autores que não está documentada.

### 11. O frontend usa React ou outro framework?

Não há esse framework na árvore examinada. O código usa JavaScript e DOM diretamente, dividido em controladores e helpers. Os arquivos HTML são shells compartilhados. Isso reduz dependências, mas exige disciplina para manutenção de templates e eventos manuais.

### 12. O que é uma API no projeto?

É o conjunto de endereços HTTP que permite ao frontend pedir ou alterar dados. GET /api/destinos devolve a pesquisa; PUT /api/favoritos/id registra uma relação. O contrato define método, entrada, saída e permissões. Abrir uma página visual não substitui autorização na API.

### 13. Por que JSON?

JSON representa objetos e listas de maneira que Python e JavaScript conseguem serializar e ler. Ele transporta destino, usuário e roteiro e também é salvo em alguns campos TEXT. JSON não verifica sozinho se o objeto tem summary ou days; o backend valida essa estrutura.

### 14. Toda URL tem seu próprio HTML?

Não. Inicial/explorar/planejar compartilham index.html; o painel compartilha painel.html; páginas ampliadas usam experiencias.html. O JavaScript decide o conteúdo pela rota. A API pode devolver403/404 depois de o shell já ter respondido200, preservando as permissões dos dados.

### 15. O sistema precisa de internet para tudo?

Não. Flask e SQLite funcionam localmente, e as bibliotecas do mapa estão vendorizadas. Tiles OpenStreetMap, fontes e links externos dependem de rede. Os testes bloqueiam tiles para verificar que funções locais continuam. Isso não torna a aplicação um PWA offline com sincronização.

### 16. Por que guardar as bibliotecas do mapa no repositório?

Para servir os arquivos necessários localmente, com versões identificadas e licenças preservadas. Leaflet é1.9.4 e MarkerCluster1.5.3. O manifesto registra origem e hashes. Isso reduz dependência de CDN em runtime, mas o fundo cartográfico continua externo.

## Banco e persistência

### 17. Por que SQLite?

É um banco relacional em arquivo que atende bem a instalação e ensaio locais. Não exige serviço separado. A escolha encontrada simplifica o protótipo; para escala e múltiplos escritores concorrentes seria preciso medir a carga e avaliar arquitetura. Não existe evidência de teste de carga nesta análise.

### 18. Quantas tabelas existem?

São16 tabelas de aplicação, além de sqlite_sequence interna. Elas cobrem destinos, usuários, atividades, favoritos, roteiros, avaliações, perfil, mídia, rede social, colaboração, vouchers, relatos e migrações. O dicionário completo está no documento03.

### 19. O que são chave primária e estrangeira?

A primária identifica a linha; a estrangeira referencia outra tabela. Favoritos tem chave composta de usuário e destino. As conexões ativam foreign_keys para aplicar restrições. Uma ressalva real: historico.destino_id não possui FK declarada, embora armazene um identificador de destino.

### 20. Como impedir favorito repetido?

A chave composta impede duplicar o par e o handler usa INSERT OR IGNORE. Repetir o PUT mantém um favorito. O histórico só registra a nova inserção. Isso é idempotência: repetir a mesma intenção não deve multiplicar essa relação. Evidência: add_favorite e esquema.

### 21. Onde ficam foto e capa?

Os bytes normalizados ficam em BLOB na tabela media, com dono, tipo e token. A URL não aponta para o nome original do arquivo. A relação única usuário/tipo mantém uma imagem de cada classe. A autorização é aplicada ao servir a mídia.

### 22. Um roteiro salvo acompanha futuras mudanças do catálogo?

Não automaticamente. Ele armazena um retrato JSON da sugestão. Isso preserva o resultado visto naquele momento, mas pode deixar informação desatualizada. A pessoa precisa confirmar condições e eventualmente gerar outra sugestão. Não há sincronização automática de paradas salvas com o catálogo.

### 23. A migração faz backup completo?

Não. Ela grava o SQL do esquema anterior, sem dados pessoais ou BLOBs. Isso ajuda a examinar a estrutura antiga, mas não recupera contas, imagens e roteiros. Produção precisa de cópia integral, proteção e restauração testada.

## Planejador e mapa

### 24. O gerador usa inteligência artificial?

Não. Seleciona candidatos por região, temas, interesses e requisitos, ordena e distribui por índices com módulo. Mesmas entradas e dados tendem ao mesmo resultado. Não há chamada a modelo externo ou treinamento. “Gerador” não é sinônimo de IA.

### 25. Como o orçamento é calculado?

O total é dividido pelos dias e depois pelas pessoas interpretadas. Com800 reais, dois dias e duas pessoas:400 por dia e200 por pessoa/dia. O sistema não consulta preços nem comprova que a verba paga as atrações. Transporte é informado no resumo, sem roteamento real.

### 26. Por que o mesmo museu pode aparecer em dois dias?

A distribuição volta ao início da coleção quando candidatos acabam. Remove duplicação dentro do mesmo dia, mas não entre dias. O exemplo de Reggae retornou o museu em dois dias. Melhorias possíveis são limitar repetição, avisar baixa diversidade e oferecer redução de duração.

### 27. O sistema calcula o melhor caminho?

Não. Organiza sugestões, sem otimização geográfica, horário, trânsito, maré ou travessia. Mesmo que cada parada tivesse um recurso físico confirmado, o caminho entre elas ainda não estaria validado. O próprio resultado contém esse aviso.

### 28. Por que poucos destinos aparecem no mapa?

A base tem76 cadastros,14 pares válidos e zero verificados. O mapa padrão exige verificação; o modo legado admite14 com aviso. Os outros62 não possuem par válido. Há ainda agrupamentos e coordenadas coincidentes. O problema de cobertura está aberto, não foi declarado corrigido.

### 29. Qual é a diferença entre Leaflet e OpenStreetMap?

Leaflet é a biblioteca que controla mapa, camadas e interação no navegador. OpenStreetMap fornece o fundo cartográfico usado. Os destinos vêm do SQLite da aplicação, não automaticamente do OpenStreetMap. Tiles falharem não significa que os cadastros foram apagados.

### 30. Cluster perde destinos?

Não deveria: representa vários marcadores próximos. O teste comparou membros dos agrupamentos com IDs elegíveis e passou em fixtures. Isso sustenta os casos testados, não garante ausência de qualquer defeito possível. A contagem correta soma membros de clusters e marcadores individuais.

### 31. Coordenada válida é correta?

Não necessariamente. Válida significa número finito dentro de limites plausíveis. Uma coordenada pode passar nessa validação e apontar para outra rua ou entrada. Verificação geográfica exige evidência. A flag verified separa esse conceito no modelo, embora nenhum ponto real esteja assim marcado nesta base.

## Acessibilidade e cultura

### 32. O site é acessível?

Há recursos implementados e testados em certos fluxos: teclado, foco, estados, contraste e ajustes de texto. Não foi feita auditoria completa, medição de todas as cores ou teste com leitores de tela e participantes. Portanto, a resposta correta evita conformidade integral e apresenta evidências e lacunas.

### 33. Qual a diferença entre acessibilidade digital e física?

Digital é conseguir usar a interface; física é conseguir participar no destino. Um modal acessível não comprova rampa; uma rampa não comprova que o formulário funciona com leitor de tela. O projeto trabalha com ambas, mas precisa verificá-las separadamente.

### 34. O que significa “não verificado”?

Que não existe confirmação suficiente registrada no modelo. Não é sinônimo de indisponível. O filtro confirmado exige status, fonte e data. Como a base física está vazia de confirmações, resultado zero não permite concluir que os lugares da cidade não tenham recursos.

### 35. Quais recursos físicos estão modelados?

Doze: acesso sem degraus, rampas, circulação, sanitário, transporte, sinalização, Braille, audiodescrição, Libras, legendas, ambiente sensorial e atendimento especializado. Cinco grupos combinam alguns campos. Não são uma vistoria técnica completa nem descrevem todas as necessidades individuais.

### 36. Qualquer usuário pode declarar um local acessível?

Pode propor um recurso e estado pela ficha, mas o relato fica pendente. Apenas revisão local com fonte HTTPS, data não futura e identificação do revisor atualiza o campo. O sistema não verifica automaticamente a evidência. Isso evita autopublicação, mas depende de curadoria responsável.

### 37. As preferências de acessibilidade ficam públicas?

Não. São gravadas com consentimento e não aparecem no perfil público. Retirar consentimento esvazia a lista. O botão do planejador reaproveita grupos explicitamente. Isso não autoriza inferir deficiência ou publicar informação pessoal a partir dessas preferências.

### 38. O botão de fonte resolve a leitura de toda a interface?

Não há essa comprovação. Ele altera o percentual raiz, mas muitos tamanhos estão em pixels e podem não acompanhar proporcionalmente. O teste verificou o valor aplicado, não ampliação uniforme. É uma limitação concreta para medir e melhorar.

### 39. Como as WCAG entram na avaliação?

Como referência para uma auditoria planejada, não selo obtido. Deve-se verificar contraste, teclado, foco, texto, formulários e estados com critérios e tecnologias adequados. O documento04 lista verificações do projeto e referencia a recomendação oficial do W3C.

### 40. Por que o cacuriá não vira um ponto do mapa?

Porque não há espaço associado no JSON atual. A manifestação cultural permanece no conteúdo; o programa evita inventar coordenada ou agenda. Associar um lugar real exige curadoria e contexto. Isso não significa ausência da manifestação na cidade.

## Segurança, social, testes e evolução

### 41. Como as senhas são protegidas?

O backend usa generate_password_hash e check_password_hash do Werkzeug. Guarda hash, não texto original. O método depende da versão/padrão da biblioteca e não está fixado como argumento. Isso não elimina necessidade de proteção de tentativas, recuperação e implantação segura.

### 42. O que a sessão guarda e por que há CSRF?

A sessão identifica o usuário e mantém token. O cookie padrão Flask é assinado, não um cofre criptografado. O token CSRF precisa acompanhar escritas autenticadas para reduzir requisições indevidas em nome da sessão. Ele não substitui autenticação nem verificação do dono.

### 43. Posso excluir o roteiro de outra pessoa mudando o ID?

O handler de exclusão filtra id e usuario_id da sessão. Já a colaboração exige dono ou convite aceito, com papel apropriado. Os testes verificam isolamento. Isso responde ao fluxo atual; cada endpoint futuro precisará manter o mesmo cuidado.

### 44. O upload confia na extensão do arquivo?

Não apenas. O servidor usa Pillow para verificar formato/conteúdo, tamanho e resolução, corrige orientação e regrava JPEG. O cliente verifica MIME e tamanho como ajuda. Testes rejeitaram imagem corrompida e mantiveram a anterior; não se afirma segurança universal de qualquer dependência.

### 45. Bloquear alguém apaga tudo que a pessoa já viu?

Não. Restringe consultas e relações previstas, revoga convites e cancela vouchers ativos do par. Não apaga capturas já feitas. Um link público ainda ativo pode ser aberto anonimamente, então a revogação do link é uma ação independente relevante.

### 46. Os vouchers são descontos reais?

Não. São convites simbólicos com código, mensagem, validade e estados. Não há comerciante validando, pagamento ou reserva. O resgate muda um estado interno. Uma integração comercial seria trabalho novo, com requisitos técnicos e operacionais próprios.

### 47. Quais testes foram realmente executados?

Foram26 testes unittest e três scripts de navegador, todos com sucesso nesta análise. Houve API, banco temporário e Chrome headless, incluindo responsividade nos tamanhos previstos. Não houve teste de carga, auditoria WCAG completa, inspeção física ou confirmação de todos os links externos.

### 48. Se todos os testes passaram, por que ainda há bugs?

Porque um teste prova um cenário e suas asserções, não toda promessa do produto. O mapa pode renderizar corretamente fixtures e ainda faltar coordenadas reais. Uma página pode evitar overflow nas larguras testadas e ainda ter uma barreira com leitor de tela. Teste e limitação podem coexistir.

### 49. Quanto custa colocar a plataforma no ar?

Não foi feito orçamento ou cotação nesta análise. Há custos possíveis de hospedagem, domínio, operação, backup, manutenção e curadoria. Bibliotecas utilizadas têm licenças, mas serviço de tiles também possui regras de uso; não assumir capacidade ilimitada gratuita. Qualquer valor exigiria pesquisa e definição de carga.

### 50. O que você faria primeiro na próxima versão?

Priorizaria coordenadas e acessibilidade verificáveis, melhorias de repetição/região no planejador e testes com usuários. Em paralelo, prepararia recuperação de conta, proteção de login e implantação com backup integral. Reservas, IA e benefícios comerciais seriam novas frentes, não atalhos para resolver a falta de dados confiáveis.

## Como responder sem extrapolar

Se a banca pedir uma comprovação que não foi feita, diga: “Na análise atual eu confirmei este mecanismo no código e nesses testes. Essa outra verificação ainda não foi realizada.” Depois indique a maneira concreta de verificar.

Se alguém mostrar um erro novo, registre rota e sequência. Não usar o resultado positivo dos testes para negar a ocorrência. A documentação descreve um estado e pode ser atualizada com novas evidências.

