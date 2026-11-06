# Explore+ SLZ — Relatório de correções e refinamento de UX

## Resultado

As correções foram feitas no projeto existente, mantendo Flask, SQLite e JavaScript, as contas e as funcionalidades sociais e de planejamento. Não houve nova base, reconstrução do projeto, exclusão de contas ou migração de tabelas nesta rodada. As coordenadas da base normal não foram preenchidas ou marcadas como verificadas automaticamente.

## 1. Mapa e catálogo

### Causas identificadas

- A base tinha 76 registros persistidos, mas apenas 14 pares numéricos válidos de latitude/longitude. Os 62 registros restantes não possuíam coordenadas válidas; a expansão anterior deliberadamente não estimou pontos.
- Nenhum registro estava classificado como localização verificada. A API entregava coordenadas legadas sem um indicador consolidado de elegibilidade para o mapa.
- A página inicial pesquisava destinos e carregava marcadores em duas consultas diferentes. Seus filtros alteravam cartões locais, sem atualizar a camada de marcadores.
- O método de foco podia criar um marcador isolado com dados de um resultado anterior, ultrapassando o conjunto filtrado.
- Não havia agrupamento, e coordenadas coincidentes encobriam marcadores. O mapa dependia do CDN do Leaflet.

### Correções

A API agora acrescenta `location.valid`, `location.verified` e `location.status` a cada destino, além de totais `map` para o conjunto filtrado. A validação exige números finitos dentro dos intervalos geográficos; valores nulos, vazios ou textuais não viram zero.

`maps.js` é compartilhado pelo catálogo e pela pesquisa da página inicial. Cada atualização usa o mesmo conjunto retornado para a lista, substitui a camada anterior e preserva todos os destinos elegíveis, sem limite artificial. Busca, município, categoria, interesses, cultura e recursos de acessibilidade podem reduzir o conjunto conforme a tela. Respostas antigas da pesquisa não substituem resultados atuais no catálogo. Os cartões de inspiração da página inicial também respeitam a consulta retornada.

Leaflet 1.9.4 e Leaflet.markercluster 1.5.3 são servidos localmente, com licenças e hashes em `frontend/vendor/`. Somente as imagens de fundo do OpenStreetMap continuam externas. O agrupador conserva cada destino, expande pontos próximos e permite abrir a ficha pela lista. A seleção usa uma camada de destaque independente, pois os ícones do agrupador podem ser recriados ao reorganizar os pontos. O foco não cria destinos fora dos filtros.

O padrão exibe somente localizações verificadas. A opção **“Incluir localizações legadas não verificadas”** permite consultar as referências anteriores, com indicação explícita e marcadores diferenciados. Sem pontos elegíveis, o mapa apresenta uma mensagem; os lugares continuam disponíveis na lista. Esta opção não altera o estado das coordenadas no banco.

### Quantidade real da base normal

| Situação | Quantidade |
| --- | ---: |
| Destinos cadastrados e retornados pela API sem filtros | 76 |
| Latitude/longitude numéricas, finitas e dentro dos limites | 14 |
| Coordenadas válidas e classificadas como verificadas | 0 |
| Coordenadas legadas válidas, mas não verificadas | 14 |
| Sem coordenadas válidas | 62 |
| Localizações ainda pendentes de verificação | 76 |

Assim, com os dados atuais, o padrão do mapa tem **zero pontos verificados**. A consulta opcional das referências legadas representa **14 destinos**, agrupados quando próximos ou coincidentes. Não é possível transformar os outros 62 registros em pontos reais sem verificar e cadastrar suas coordenadas. Os testes do agrupador usam pontos explicitamente de teste, apenas em banco temporário.

## 2. Temas e cores

### Causas

Os temas modificavam um pequeno conjunto de variáveis, mas cabeçalhos, rodapés, sombras, formulários, cartões, alertas e componentes dinâmicos ainda usavam cores fixas. Havia definições repetidas nos arquivos CSS e pouca cobertura no alto contraste. O tema só era aplicado depois da consulta de sessão, permitindo a aparição momentânea do verde padrão.

### Correções

`themes.css` centraliza `--color-primary`, `--color-accent`, `--color-surface`, `--color-text`, `--color-border` e os demais tokens para fundos, estados, rodapés, sombras, contraste e textos sobre fundos escuros. As variáveis antigas continuam como aliases, preservando o sistema de seleção existente.

As cores fixas da interface foram substituídas pelos tokens em `style.css`, `painel.css` e `expansion.css`. Elementos dinâmicos do planejador também usam classes temáticas. Logo, fotografias/ilustrações e cores com significado funcional não são recoloridos indiscriminadamente. A marca visual original foi preservada.

O tema é confirmado pelo perfil no servidor e antecipado por `theme-init.js` a partir do cache local. O logout limpa o tema visual da sessão anterior. Verde da Ilha, Azul da baía, Pôr do sol e alto contraste continuam disponíveis. A confirmação de configurações atualiza o tema sem descartar arquivos ainda selecionados para upload.

## 3. Foto e capa

### Causas

A seleção mostrava uma prévia, mas não distinguia claramente arquivo local e imagem salva. A confirmação dependia de um aviso temporário. Depois do envio, o código recarregava a sessão e reconstruía o formulário, descartando o estado local e tornando a aplicação da imagem pouco evidente. Havia ainda risco de uma seleção pendente desaparecer ao salvar outras configurações.

### Correções

Cada componente mantém um estado visível e anunciado: sem imagem, imagem atual, selecionado/ainda não enviado, enviando, salvo e erro. O nome do arquivo e a miniatura aparecem antes do envio; **selecionar não conta como salvar**. O botão “Enviar e salvar” só é habilitado para uma seleção permitida.

Depois da confirmação real da API, a prévia passa a usar a URL persistida, o avatar do cabeçalho é atualizado e uma indicação de sucesso permanece na tela. Um link leva ao perfil. Recarregar ou entrar novamente consulta a imagem do SQLite e mostra “Imagem atual salva e exibida”. Erros de validação mantêm a mídia anterior no banco e permitem nova tentativa. Remoção também tem confirmação explícita. Os botões e o arquivo ficam protegidos contra ações concorrentes durante o envio.

As validações do servidor foram preservadas: sessão, CSRF, JPEG/PNG/WebP decodificáveis, limite de 4 MB e 16 megapixels, recodificação, retirada de metadados, identificadores aleatórios e controle de leitura conforme a privacidade. Nenhuma imagem é considerada salva apenas pela existência de um arquivo no navegador.

## 4. Menu

A versão tinha uma lista plana de 12 itens. A lista principal foi reduzida a nove entradas únicas: Início, Explorar, Planejar roteiro, Amigos, Favoritos, Histórico, Meus roteiros, Meu perfil e Configurações, além de Entrar ou Sair conforme a sessão. Não há seção de Atalhos/Acesso rápido.

Acessibilidade continua disponível nas configurações; presentes e vouchers ficam na página Amigos. As rotas e suas funcionalidades foram preservadas. A aba cultural separada foi retirada. O item Explorar também é identificado como ativo na pesquisa do mapa e nas fichas de destinos. O menu conserva teclado, foco visível, `aria-expanded`, `aria-controls`, clique fora e Escape.

## 5. Cultura integrada

O conteúdo anterior era exclusivo de `/cultura`, sem vínculo estruturado com destinos. As nove narrativas, classificações e fontes foram preservadas integralmente em `backend/culture_content.json`, com associações explícitas a espaços reais.

Agora há:

- Filtro de contexto cultural no catálogo, combinável com os outros filtros.
- Temas e pequenos contextos nos cartões; narrativas e fontes nas fichas correspondentes.
- Conteúdo editorial completo dentro da exploração, incluindo tradições que ainda não têm um espaço associado.
- Interesses no planejador para reggae, Bumba Meu Boi, Tambor de Crioula, cacuriá, azulejaria, gastronomia maranhense e artesanato.
- Priorização de locais associados aos interesses culturais específicos, sem inventar programação.

A URL antiga `/cultura` redireciona para `/catalogo#cultura`, preservando os favoritos de navegador. Cacuriá, por exemplo, continua como conteúdo editorial sem associação geográfica específica nesta base. Quando é o único interesse e não há local associado, o planejador explica a ausência de correspondências em vez de inventar um ponto.

## 6. Testes executados

| Comando / verificação | Resultado |
| --- | --- |
| `python -m unittest discover -v` | 26 testes aprovados: os 22 anteriores e quatro regressões novas |
| `python test_browser.py` | Fluxos originais aprovados, incluindo contraste e recuperação de sessão |
| `python browser_expansion.py` | Amigos, compartilhamento, vouchers, perfil e layouts da expansão aprovados |
| `python browser_corrections.py` | Mapa real, três temas em 11 páginas e estados de upload aprovados |

Os testes de navegador não apresentaram erros JavaScript. Todos usam SQLite temporário. O teste de correções compara IDs e quantidades retornados pela API com as camadas Leaflet **e com os destinos efetivamente representados pelos ícones individuais e agrupamentos renderizados**. Também testa foco de um ponto agrupado, filtros combinados, referências legadas e locais que permanecem na lista sem marcador.

A validação de cores seleciona e salva os três temas e navega por início, catálogo, ficha, perfil, amigos, presentes, favoritos, histórico, roteiros, configurações e acessibilidade. A cobertura de upload inclui seleção sem envio, estado enviando com requisição controlada, sucesso real, substituição inválida, manutenção da mídia anterior, atualização, recarga, logout/login e remoção de foto e capa.

Menu e responsividade foram verificados em 320, 390, 768 e 1440 pixels. As bibliotecas de mapa são reais e locais; os tiles externos foram bloqueados no teste para verificar a independência entre fundo cartográfico e marcadores. Isso não certifica a disponibilidade do serviço externo de mapas.

Capturas ficam em `.artifacts/`: `correcoes-configuracoes.png`, `correcoes-perfil.png`, `correcoes-explorar.png` e `correcoes-mapa.png`. São telas de uma sessão e de pontos explicitamente de teste, não dados demonstrativos cadastrados na base normal.

## 7. Arquivos desta rodada

Backend: `backend/app.py`, `backend/expansion.py`, `backend/culture.py` e `backend/culture_content.json`.

Frontend: `frontend/account.js`, `catalogo.js`, `configuracoes.js`, `cultura.js`, `experiencias.js`, `navigation.js`, `script.js`, `social.js`, `maps.js`, `theme-init.js`; `index.html`, `painel.html`, `experiencias.html`; `style.css`, `painel.css`, `expansion.css`, `themes.css`; versões fixadas, licenças e manifesto em `frontend/vendor/`.

Verificação/documentação: `test_expansion.py`, `test_corrections.py`, `test_browser.py`, `browser_expansion.py`, `browser_corrections.py`, `scripts/vendor_maps.py`, `README.md` e este relatório. Arquivos temporários de edição e capturas ficam em `.artifacts/`, ignorados pelo Git. Alterações anteriores no repositório foram preservadas.

## 8. Pendências

1. Verificar as coordenadas legadas e cadastrar posições comprovadas para os 62 registros sem coordenadas válidas. Esta rodada corrige a renderização e a sincronização; não afirma ter realizado levantamento geográfico.
2. Completar evidências de acessibilidade e fotografias licenciadas dos locais, já pendentes na expansão anterior.
3. Realizar auditoria formal com leitores de tela e pessoas com deficiência; os testes executados não equivalem a certificação WCAG integral.
4. Disponibilidade dos tiles e dados de campo continuam dependendo dos serviços e responsáveis pelos locais.

Para executar no Windows, mantenha o procedimento do README ou use `INICIAR_WINDOWS.bat`. Os scripts do mapa não requerem npm nem etapa de build. `scripts/vendor_maps.py` só é necessário para reproduzir manualmente a obtenção das versões fixadas; o servidor usa os arquivos já incluídos.

### Conferência final

A auditoria da base normal foi repetida em conexão SQLite **somente leitura**: 76 registros, 14 pares numericamente válidos, zero verificados e 62 sem coordenadas válidas. `PRAGMA quick_check` retornou `ok`. `pip check` não encontrou dependências incompatíveis e `git diff --check` passou. Os três testes de navegador terminaram com código de saída zero. A última validação das correções também confirmou controles nativos de formulário e a experiência especial criada pelo planejador nos três temas.
