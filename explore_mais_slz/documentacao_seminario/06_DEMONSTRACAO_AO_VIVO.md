# Demonstração ao vivo — percurso, preparação e contingências

**Objetivo:** mostrar descoberta → decisão → memória pessoal → inclusão, sem depender de mapa completo nem de serviços externos. O roteiro padrão dura cerca de10–12 minutos; há recortes para5 e20 minutos.

## 1. Preparação antes de entrar em sala

Use somente contas de demonstração. Não projete dados de usuários reais, lista de e-mails ou arquivo de banco. As contas nos testes são fictícias; elas não viram contas permanentes na base normal, pois os testes usam diretórios temporários.

Confirme bateria, resolução de projeção, zoom do navegador e tamanho legível. Deixe a sessão correta aberta antes da apresentação; autenticação ao vivo pode consumir tempo e expor digitação. Prepare uma segunda janela/perfil de navegador para demonstrar o destinatário de amizade e convite, porque abas do mesmo perfil compartilham cookie.

Faça o ensaio com internet desligada pelo menos uma vez. O projeto tem JS/CSS de mapa local, mas tiles, fontes, links culturais e WhatsApp podem depender de rede. A lista e os dados locais não precisam do fundo cartográfico para serem explicados.

### Ambiente separado recomendado

Uma base nova evita apagar favoritos ou histórico pessoais durante a demonstração. O comando abaixo é uma preparação opcional e explícita, executada no PowerShell **dentro da pasta explore_mais_slz**. Ele cria um nome novo de banco a cada execução; não apaga bancos existentes.

```powershell
Set-Location 'C:\Users\felps\Downloads\Explore_Mais_SLZ_Perfil_Corrigido\explore_mais_slz'
New-Item -ItemType Directory -Path '.artifacts' -Force | Out-Null
$seminarioDbName = 'demo-' + [guid]::NewGuid().ToString('N') + '.sqlite'
$env:EXPLORE_DATABASE_PATH = Join-Path (Join-Path (Get-Location).Path '.artifacts') $seminarioDbName
$env:EXPLORE_SECRET_KEY = 'segredo-apenas-local-para-ensaio-do-seminario'
.venv/Scripts/python.exe -m flask --app backend.app run --host 127.0.0.1 --port 5000
```

O segredo acima é didático para ambiente local, não um segredo de produção. A variável de banco vale para esse processo e seus filhos. Não ativar cookie Secure em HTTP local sem entender que o navegador pode deixar de enviar a sessão. Para encerrar, Ctrl+C no terminal; não fechar durante a navegação.

O início cria/migra e abastece o banco escolhido. O catálogo novo deve ter76 registros se a semente atual for usada. Isso não importa usuários reais. Se a porta5000 estiver ocupada, use outra porta no comando e ajuste a URL do navegador.

Não é necessário reinstalar dependências durante a apresentação. Playwright serve à preparação/testes, não ao funcionamento do usuário final.

### Duas pessoas fictícias

Crie previamente, pela interface:

| Conta fictícia | Preparação |
|---|---|
| Ana Demonstração, ana.seminario@example.test | Handle ana_seminario; perfil pode ficar privado; ativar descoberta se necessário |
| Bruno Demonstração, bruno.seminario@example.test | Handle bruno_seminario; marcar descobrível e permitir convites |

Escolha senhas de ensaio fora do texto projetado. Crie a amizade e um roteiro de reserva antes da aula. Se quiser mostrar o recebimento, deixe uma solicitação ou convite pendente em vez de repetir toda a preparação.

Na primeira conta, deixe um favorito e um roteiro salvo. Use uma pequena imagem de sua autoria para upload. Não use fotografia de terceiro sem autorização. Deixe um arquivo corrompido apenas se for demonstrar validação e houver tempo.

## 2. Abas preparadas

1. Inicial: http://127.0.0.1:5000/
2. Catálogo: /catalogo, sem filtros.
3. Ficha de referência: /destino/1 na base padrão.
4. Perfil: /perfil.
5. Planejador: /planejar#roteiro.
6. Acessibilidade: /acessibilidade.
7. Configurações: /configuracoes.
8. Amigos e roteiro compartilhado já autorizado.
9. Capturas locais de contingência, claramente identificadas como testes.

Não escrever um token fictício na URL e esperar que funcione. Links públicos e IDs de roteiro precisam ser gerados no banco atual. Um ID de um ensaio anterior não é garantia de existência no próximo banco novo.

## 3. Percurso principal com fala e resultado esperado

### Passo1 — Problema e entrada, 40 segundos

**Onde:** inicial. **Ação:** mostrar proposta e menu; abrir e fechar por teclado.

**Fala:** “Eu reuni descoberta e planejamento em uma interface que também guarda escolhas. A navegação principal funciona nas telas grandes e pequenas.”

**Esperado:** menu sem links duplicados, foco visível; ArrowDown leva ao primeiro link e Escape retorna ao botão.

**Se falhar:** use a barra de endereço para abrir o catálogo; não gastar a apresentação depurando menu. Informe que a interação ao vivo falhou, sem negar o ocorrido.

### Passo2 — Catálogo completo, 1 minuto

**Onde:** /catalogo. **Ação:** mostrar contador e procurar reggae; aplicar filtros; limpar.

**Fala:** “Há76 destinos na base examinada. Eu consigo restringir a descoberta por texto, município, categoria e contexto cultural.”

**Esperado:** resultados e mapa usam a mesma coleção, mas geolocalização tem regra adicional. Reggae deve encontrar o museu no contexto cultural.

**Banco/API:** GET /api/destinos e metadados. Com conta, pesquisa textual pode registrar histórico.

**Se não houver resultado:** limpar filtros, verificar q/culture/access da URL. Evitar culpar a base antes de conferir parâmetros.

### Passo3 — Ficha e cultura, 1 minuto

**Onde:** ficha escolhida. **Ação:** ler contexto cultural e mostrar fonte.

**Fala:** “A cultura aparece ligada ao lugar. A fonte ajuda a conferir o conteúdo; a ilustração não é apresentada como foto do destino.”

**Esperado:** descrição, fonte, tabela de recursos e contexto associado.

**Se link externo não abrir:** permaneça no texto local. Diga: “A referência é externa; a navegação depende da rede, mas o contexto editorial está disponível localmente.” Não afirmar que conferiu o conteúdo externo agora.

### Passo4 — Favorito e memória, 1 minuto

**Ação:** favoritar e abrir /perfil, depois /favoritos.

**Fala:** “Essa escolha ficou vinculada à minha conta. Repetir a marcação não cria outro favorito. Meu perfil reúne o que pretendo conhecer e o que planejei.”

**Esperado:** coração ativo, card persistente e contador coerente. Recarregar uma vez é suficiente para mostrar persistência.

**Se sessão expirar:** usar conta preparada ou mostrar captura do fluxo; não projetar senha nem repetir tentativas longamente.

### Passo5 — Planejamento determinístico, 1 minuto e meio

**Entrada simples:** São Luís,1 dia, R$800,2 pessoas, interesse Cultura ou História, sem recursos físicos selecionados.

**Ação:** gerar, explicar resultado e salvar. Para demonstrar a limitação específica, usar apenas Reggae por2 dias, desmarcando interesses previamente selecionados.

**Fala:** “Eu aplico regras sobre os destinos cadastrados. A verba é dividida por dias e pessoas. Não há IA, cotação de preços ou otimização de trajetos.”

**Esperado:** resumo, um ou dois locais por dia, aviso, botões de salvar/copiar/WhatsApp. Com Reggae por2 dias, o museu pode repetir, conforme o exemplo registrado.

**Se422:** explicar a condição de dados e retirar requisitos apenas com transparência: “Agora vou gerar uma sugestão sem exigir recurso físico, porque não há confirmação cadastrada. Não estou demonstrando um roteiro acessível.”

### Passo6 — Recuperação do roteiro, 40 segundos

**Onde:** /meus-roteiros. **Ação:** abrir detalhes do roteiro salvo.

**Fala:** “O resultado fica guardado como um retrato JSON. Posso recuperá-lo; ele não é recalculado automaticamente a cada acesso.”

**Esperado:** título, data e conteúdo. Não excluir o único roteiro de reserva durante a versão curta.

### Passo7 — Acessibilidade e honestidade dos dados, 1 minuto e meio

**Onde:** /acessibilidade e ficha. **Ação:** ativar contraste, aumentar texto e navegar por teclado; mostrar recursos não verificados. No catálogo, selecionar mobilidade.

**Fala:** “Acessibilidade da interface e do destino são coisas diferentes. Os controles ajudam na leitura. Já os recursos físicos precisam de fonte e data. A busca vazia mostra uma lacuna do cadastro, não ausência de acessibilidade na cidade.”

**Esperado:** contraste aplicado; valor raiz aumenta; filtro físico pode não devolver local. Não prometer que todos os textos ampliaram na mesma proporção.

**Se layout ficar difícil na projeção:** restaurar o tamanho/contraste de ensaio; explicar que auditoria ampla ainda falta. Não usar o ajuste como certificado WCAG.

### Passo8 — Personalização e upload, 1 minuto

**Onde:** /configuracoes. **Ação:** selecionar uma imagem e mostrar estado “selecionado”; confirmar envio; recarregar; mostrar tema.

**Fala:** “A prévia ainda está no navegador. Só o envio confirma gravação. O servidor valida e normaliza a imagem. O tema é salvo na conta; contraste e tamanho ficam neste navegador.”

**Esperado:** prévia blob antes; URL /media após; imagem persiste; sucesso de configurações separado do upload.

**Se upload falhar:** mostrar mensagem; manter imagem anterior. Não clicar repetidamente. Explicar que uma seleção não equivale a sucesso; usar captura do estado salvo.

### Passo9 — Social e colaboração, 1 minuto

**Onde:** Amigos e roteiro preparado. **Ação:** mostrar amizade/convite aceito, acrescentar uma nota como editor ou dono.

**Fala:** “A colaboração exige permissão. Leitor consulta; editor acrescenta ideias e pode alterar o título. Um link público é outra forma de compartilhar, revogável pelo dono.”

**Esperado:** nota com autor; segunda janela consulta após recarregar. Não esperar atualização em tempo real.

**Se segunda conta indisponível:** mostrar relação previamente aceita e explicar o papel. Não simular uma aceitação que não ocorreu.

### Passo10 — Presente simbólico e fechamento, 50 segundos

**Onde:** /presentes, com item preparado. **Ação:** mostrar estados e validade; resgatar só se houver tempo e conta correta.

**Fala:** “Este voucher é um convite interno e simbólico. Não é desconto, pagamento ou reserva. A plataforma controla estados e quem pode agir.”

**Fechamento:** “Os testes de API e navegador passaram, mas mapa, dados físicos e auditoria assistiva permanecem como desafios concretos.”

## 4. Como apresentar o mapa sem depender dele

Não iniciar a demonstração por um pin. Primeiro mostrar a lista e os números. Em seguida dizer que o padrão exige coordenadas verificadas e, nesta base, não há nenhuma.

Se houver tempo, marcar “incluir legados” e mostrar os pontos com ressalva. A soma representa14 destinos sem filtro, podendo haver menos ícones por agrupamento. Não usar as imagens do teste com41 pontos como se fossem geolocalização real.

Se o fundo falhar, explicar a separação entre biblioteca local e tiles externos. A lista permanece como caminho principal. Uma captura pode mostrar o componente, mas deve receber a legenda “cenário de teste com dados controlados; não valida pontos reais”.

## 5. Plano de contingência por tipo de falha

| Ocorrência | Ação imediata | O que dizer | Evidência de reserva |
|---|---|---|---|
| Sem internet | Continuar em páginas locais; evitar fontes/WhatsApp | “Dados da aplicação são locais; o fundo e os links externos dependem de rede.” | Captura + API local |
| Flask parado | Ver terminal e porta; reiniciar no banco de ensaio preparado | “O serviço local parou; vou seguir pela evidência registrada.” | Documentos01/03/09 |
| API lenta/falha | Uma repetição; evitar cliques múltiplos | “A tela informa erro e permite tentar novamente.” | Captura do estado funcional |
| Conta errada | Segunda janela/contexto preparado | “Cada janela de demonstração tem uma identidade.” | Perfil de ensaio pronto |
| Sessão perdida após restart | Entrar novamente com conta fictícia | “A sessão depende da chave configurada.” | Roteiro/favorito previamente persistido |
| Filtro vazio | Limpar parâmetros ou explicar requisito | “Vazio é resposta possível, especialmente sem acessibilidade confirmada.” | Tabela dos dados |
| Clipboard/WhatsApp bloqueado | Mostrar texto do resultado sem enviar | “Integração é abertura/cópia local, não entrega garantida.” | plain_text no documento03 |
| Imagem rejeitada | Conferir tipo/tamanho; manter anterior | “O servidor não aceitou o conteúdo; seleção não garante upload.” | Capturas de upload |
| Voucher vencido | Mostrar item em estado final ou emitir antes do ensaio | “Expiração é avaliada nas consultas/transições.” | Máquina de estados |
| Link revogado | Mostrar404 como comportamento esperado | “Revogação retira a leitura por esse token.” | Roteiro ainda acessível pelo dono |

Não editar diretamente o SQLite, marcar coordenadas como verificadas ou aprovar relatos inventados durante a aula. Isso produziria uma demonstração enganosa. Fixtures são adequadas para teste e precisam ser identificadas como tal.

## 6. Material de reserva local

As capturas em .artifacts foram produzidas por scripts automatizados. Exemplos: perfil-desktop.png, perfil-celular.png, perfil-contraste.png, correcoes-configuracoes.png, correcoes-perfil.png, v2-amigos.png, v2-voucher-celular.png e correcoes-mapa.png.

Abra os arquivos antes da apresentação para confirmar conteúdo e legibilidade. Duas capturas de perfil foram inspecionadas nesta análise, em desktop e celular. Há nomes/e-mails fictícios. Evite projetar pastas que misturem dados pessoais ou segredos com esses artefatos.

A resposta integral de roteiro no documento03 pode substituir uma geração ao vivo. A tabela de mapa do documento09 pode substituir a visualização. Uma falha real deve ser assumida como falha, não encoberta por uma captura apresentada como tela ao vivo.

## 7. Recortes de duração

**Em5 minutos:** inicial, catálogo/ficha, perfil, resultado já salvo, distinção de acessibilidade e mapa. Não fazer cadastro, amizade e upload completos.

**Em10 minutos:** seguir o percurso principal com preparação de contas e itens. Presentes e colaboração podem ser mostrados em estado já pronto.

**Em20 minutos:** acrescentar troca entre as duas janelas, nota colaborativa, link público e revogação, upload e recarga, sugestão pendente e explicação do código. A moderação local deve ser explicada; não precisa aprovar informação física fictícia.

## 8. Encerramento e limpeza do ensaio

Fechar links públicos criados para demonstração quando não forem mais necessários. Não limpar histórico ou excluir roteiro da base pessoal por engano. Bases novas de ensaio ficam no diretório de artefatos para eventual revisão; sua exclusão deve ser uma ação consciente posterior.

Registre qualquer erro novo encontrado ao vivo com rota, ação, mensagem e circunstância. O fato de os testes atuais terem passado não invalida uma reprodução posterior.

