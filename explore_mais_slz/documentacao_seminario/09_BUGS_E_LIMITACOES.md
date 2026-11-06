# Bugs, limitações e resultados verificados

**Inspeção:** 06/11/2026. Este documento descreve o estado observado; não foi uma rodada de correção. Código de aplicação preservado.

## 1. Como ler o diagnóstico

“Confirmado por dados” significa consulta da base ou resposta real; “confirmado por código” significa comportamento que a implementação permite, sem necessariamente ter sido demonstrado em todos os navegadores; “hipótese” precisa de reprodução; “não reproduzido” significa que o teste atual passou, não que todo defeito possível desapareceu.

Gravidade é uma priorização para este protótipo: alta quando afeta uma promessa central ou exposição pública; média quando compromete uma tarefa ou expectativa; baixa quando afeta clareza ou acabamento.

## 2. O problema do mapa permanece

| Conjunto sem filtros | Quantidade | Evidência |
|---|---:|---|
| Destinos em SQLite | 76 | Consulta somente leitura |
| Destinos devolvidos pela API | 76 | GET real em cópia da base |
| Pares lat/lon válidos | 14 | Validação numérica e intervalos |
| Pares válidos e verificados | 0 | `coordinates_status` |
| Sem par válido | 62 | 76 menos 14 |
| Pendentes de verificação da API | 76 | Inclui os 14 legados válidos |
| Representáveis pelo mapa padrão | 0 | Elegibilidade em `maps.js` |
| Representáveis ao incluir legados | 14 | Elegibilidade em `maps.js` |

Os números de representação são consequência da regra aplicada à base examinada. A verificação visual de contagem foi feita pelos testes com fixtures, não se deve confundir as coordenadas sintéticas com verificação geográfica da base normal.

### Causas confirmadas

1. A expansão do catálogo não forneceu coordenadas verificadas para os novos locais. Há 62 registros sem par válido.
2. Os 14 pares herdados são numericamente válidos, porém não verificados. A política padrão os oculta; o usuário precisa aceitar a visualização legada.
3. Alguns registros legados compartilham coordenadas, inclusive experiências genéricas. Ícones podem se sobrepor ou formar clusters. Número de ícones e número de destinos representados são medidas diferentes.
4. Todo filtro reduz o conjunto recebido pela camada de mapa. Selecionar um local que está fora do conjunto atual não cria um marcador novo.

Evidências: `backend/app.py:157` (`row_to_dict`), `backend/app.py:208` (`pesquisar_destinos`), `frontend/maps.js` (`eligible`, `setPlaces`, `focus`), `frontend/catalogo.js` (resultado compartilhado por lista/mapa).

### O que o teste cartográfico comprovou

`browser_corrections.py` marcou apenas o destino de teste 1 como verificado e criou 40 pontos próximos sintéticos em banco temporário. Comparou IDs da API elegíveis, camadas Leaflet e membros presentes nos ícones reais de clusters/marcadores. Testou filtros, foco e ausência de tiles. Passou.

Isso sustenta que o agrupamento não descartou destinos elegíveis nos casos testados. Não resolve o cadastro geográfico real, não confirma entradas e não comprova que não existe outro defeito de renderização.

### Hipóteses que não devem ser apresentadas como diagnóstico fechado

| Hipótese | Como investigar sem inventar resultado |
|---|---|
| Tiles externos falham | Conferir requisições OpenStreetMap; separar fundo vazio de ausência de marcador |
| Filtro ficou ativo na URL | Comparar parâmetros, contador da API e checkboxes |
| Usuário conta ícones em vez de membros | Expandir clusters e somar seus membros, comparar IDs |
| Asset/plugin não carregou | Conferir rede e `window.L`; verificar fallback sem plugin |
| Contêiner sem tamanho adequado | Medir dimensão e eventos de `ResizeObserver`; não foi reproduzido no teste atual |
| Resposta de rede fora de ordem | Verificar sequência do catálogo e cancelamento da busca inicial |
| Ponto geograficamente errado apesar de válido | Conferir fonte, entrada real e posição; formato numérico não resolve isso |

### Correção futura apropriada

Curar cada local com fonte geográfica, entrada correta, data e responsável; manter locais sem evidência na lista; conservar aviso de legado; adicionar uma rotina administrável de verificação e testar mapa contra o catálogo real. Marcar todos como verificados apenas para povoar o mapa esconderia o problema.

## 3. Registro de limitações

| ID | Descrição e gravidade | Tela | Evidência / certeza | Impacto | Evolução sugerida |
|---|---|---|---|---|---|
| M01 | Cobertura cartográfica incompleta — alta | Início/catálogo | Base 76/14/0; confirmado | Mapa não representa a maioria | Curadoria geográfica auditável |
| M02 | Coordenadas repetidas e locais genéricos — média | Mapa | Legado em `DESTINOS_INICIAIS`; confirmado | Sensação de poucos pontos; precisão limitada | Separar espaço concreto de experiência regional |
| A01 | Nenhum recurso físico confirmado na base — alta | Catálogo/planejador | Todos `access_json={}`; confirmado | Filtro acessível vazio, geração 422 | Levantamento com evidência e revisão |
| A02 | Fonte ajustada no elemento raiz, estilos com px — média | Todas | `account.js`, CSS; confirmado por código | Parte do texto pode não ampliar proporcionalmente | Medir texto efetivo, preferir unidades relativas e testar zoom |
| A03 | Compatibilidade assistiva sem auditoria completa — alta como lacuna | Todas | Testes de teclado/ARIA não incluem leitor de tela real | Barreiras podem permanecer | NVDA/VoiceOver, usuários e critérios WCAG |
| P01 | Repetição de parada entre dias — média | Planejador | Módulo em `gerar_roteiro`; exemplo Reggae confirmado | Viagem pouco variada | Controlar repetição e avisar falta de candidatos |
| P02 | Experiência especial Raposa ignora região escolhida — média | Planejador | Condição usa orçamento/interesses, não município | Sugestão fora da seleção | Restringir geografia ou explicar deslocamento |
| P03 | Orçamento é divisão, não previsão de custos — média | Planejador | `per_day/per_person_day` | Usuário pode interpretar como preço calculado | Separar verba disponível de estimativa com fontes |
| P04 | Sem trajeto, horário, maré ou transporte real — alta como lacuna | Planejador | Ausência de roteamento/API externa | Não usar como orientação garantida de viagem | Integrar dados e validação operacional |
| P05 | Coerção de tipos aceita valores não estritamente inteiros — baixa | API de roteiro | `int(days)`, conversões de pessoas | Payload direto pode ter interpretação inesperada | Validar tipos e quantidade positiva explicitamente |
| R01 | Salvar repetidamente cria cópias — baixa | Resultado/roteiros | POST insere sempre; sem trava idempotente | Duplicação da lista | Estado de envio e identificação idempotente |
| R02 | Tela compartilhada não renderiza todos os blocos pessoais — média | Colaboração/link | `F.tripHTML` não mostra experiência especial/resumo completo | Apresentação parcial do conteúdo salvo | Unificar renderizador e revisar conteúdo público |
| S01 | Avaliação pública revela nome mesmo com perfil privado — média | Destino | GET avaliações inclui `usuarios.nome` | Expectativa de anonimato pode falhar | Explicar publicidade no envio ou pseudônimo |
| S02 | Link público funciona para qualquer portador — média | /s/token | Endpoint público sem login | Bloqueio social não revoga acesso anônimo | Informar alcance e oferecer revogação clara |
| S03 | Sem recuperação/troca de senha e confirmação de e-mail — média | Conta | Rotas ausentes | Perda de acesso e e-mail não comprovado | Fluxos verificados de recuperação |
| S04 | Sem limite de tentativas de login — alta se publicado | Login | Nenhum limitador encontrado | Maior exposição a automação | Limitação, monitoramento e política de conta |
| S05 | Segredo aleatório se variável ausente — média | Sessão | `app.py:32` | Logout após reinício; divergência multiprocesso | Segredo estável em ambiente seguro |
| S06 | Servidor direto em debug — alta se exposto | Operação | Final de `app.py` | Ambiente inadequado à internet pública | WSGI, debug desligado e HTTPS |
| S07 | Política de retenção/exportação/exclusão de conta ausente — média | Dados | Sem rotas correspondentes | Gestão de dados incompleta | Desenhar ciclo de vida e ferramentas |
| D01 | Backup de migração copia apenas esquema — alta para recuperação | Banco | `migrations.py:19` | Registros e imagens não recuperáveis por esse arquivo | Backup integral testado e protegido |
| D02 | Histórico/roteiros limitados a últimos 100 sem paginação — média | Painéis | SELECT LIMIT100 | Conteúdo mais antigo pode não aparecer | Paginação e busca |
| D03 | Catálogo sem paginação, filtro em memória — baixa agora | Catálogo | API lê todas as linhas | Escala limitada quando crescer | Índices/consulta paginada e busca |
| D04 | Parte dos GETs provoca escrita auxiliar — baixa técnica | Sessão/perfil/vouchers/busca | Perfil lazy, expiração, histórico | Consultas não são sempre neutras | Separar comandos e expiração planejada |
| C01 | Conteúdo tem referências, mas datas são editoriais fixas — média | Cultura/destinos | JSON/catálogo com data 2026-11-06 | Atualidade não conferida automaticamente | Revisão periódica documentada |
| C02 | Ilustração genérica no lugar de fotos de destinos — baixa | Cards/ficha | `destination_metadata` | Menor reconhecimento visual | Fotos autorizadas com autoria e alternativa |
| C03 | Cacuriá editorial sem destino associado — baixa e intencional | Cultura/planejador | `destinations=[]` | Filtro específico vazio/422 | Associar espaço real somente com evidência |
| U01 | Texto do aviso legado pode conter escapes literais — baixa | Card inicial | Trecho com dupla barra em `script.js`; inspeção de código | Aviso pode mostrar “\\u...” | Reproduzir exatamente o clique e corrigir literal numa rodada futura |
| U02 | Pesquisa social não normaliza acentos — baixa | Amigos | LIKE de nome/handle | Busca com grafia diferente pode não achar | Normalização e testes de idioma |
| V01 | Vouchers sem validade comercial — limite de escopo | Presentes | Somente transições internas | Não representam compra/desconto | Só integrar parceiros com contratos e validação |
| V02 | Expiração lazy — baixa | Presentes | `expire_vouchers` nas operações | Estado persistido pode atrasar sem consultas | Agendamento se houver necessidade comercial |

U01 é um possível defeito de apresentação derivado do literal, não uma falha declarada reproduzida em todos os cliques. Não houve alteração de código para resolvê-lo nesta tarefa.

## 4. Testes executados nesta análise

| Comando | Resultado efetivo | Alcance |
|---|---|---|
| `.venv/Scripts/python.exe -m unittest discover -v` | **26 testes, OK**, 11,474 s informados pelo runner | API e banco temporário |
| `.venv/Scripts/python.exe test_browser.py` | Saída OK, código 0 | Conta, perfil, favoritos, roteiro, exclusões, histórico, contraste, sessão e responsividade |
| `.venv/Scripts/python.exe browser_expansion.py` | Saída OK, código 0 | Menu, imagens, duas contas, amizade, colaboração, link, voucher e relato |
| `.venv/Scripts/python.exe browser_corrections.py` | Saída OK, código 0 | API × marcadores/clusters, filtros/foco, 3 temas, uploads, cultura e menu |

As quatro execuções concluíram. Os testes de navegador usaram Chrome headless via Playwright. Os scripts bloqueiam requisições de tiles em seus cenários para que o funcionamento local não dependa do serviço cartográfico. “Sem erros JavaScript” significa ausência de `pageerror` capturado; não significa ausência de toda resposta HTTP externa falha.

A interface foi exercitada em 320/390/768/1440 px conforme os loops de cada script. O teste de temas percorreu 11 telas em três temas. Não confundir isso com testar todas as combinações de estado, tela, tamanho, tema e tecnologia assistiva.

### O que não foi comprovado

- Exatidão física das coordenadas e condições reais de acesso dos 76 destinos.
- Disponibilidade atual de cada link editorial, preço, horário ou operador externo.
- Conformidade integral WCAG 2.2, leitores de tela, dispositivos físicos e usabilidade com participantes.
- Resistência a ataques por teste de intrusão ou carga.
- Recuperação integral de backup e operação multiprocesso em produção.
- Envio externo de presentes, descontos comerciais, reservas e pagamento: não existem.
- Cobertura de linhas e performance estatística: não foram medidas.
- Shells dinâmicos com dados inválidos podem responder HTML 200 e depois mostrar erro da API. Isso não prova que o recurso privado exista ou esteja autorizado.

## 5. Preservação e rastreabilidade

A inspeção de SQLite foi em modo somente leitura; consultas Flask adicionais usaram cópia temporária. Testes criam seus próprios bancos. Há evidências de auditoria em `.artifacts/seminario_audit.json` e `.artifacts/seminario_api_evidence.json`, sem exportação de contas reais. Um manifesto de hashes anterior permite conferir preservação dos arquivos de código.

Relatórios antigos na raiz são contexto histórico. Quando a linguagem antiga sugerir “mapa corrigido”, “totalmente acessível” ou “funcionalidade completa”, prevalecem os critérios e números desta análise. Não se deve apagar o histórico para harmonizar narrativas.

**Conferência final desta entrega:** 47 arquivos do manifesto anterior tiveram hashes comparados, sem alteração. Os nove Markdown foram conferidos quanto a links locais, cercas de código e caracteres inválidos. As evidências completas das execuções estão em `.artifacts/seminario_test_results.json`; os resultados de preservação e inventário estão em `.artifacts/seminario_verification.json`. Capturas de perfil desktop e celular também foram inspecionadas visualmente; isso não amplia a cobertura para todos os estados de tela.


## 6. Os 26 testes de API, individualmente

| Local | Nome | Objetivo | Resultado desta execução |
|---|---|---|---|
| test_api.py:41 | test_original_health_search_and_route | Saúde, consulta e geração original. | Passou |
| test_api.py:50 | test_all_pages_and_assets | Entrega das páginas/arquivos estáticos. | Passou |
| test_api.py:57 | test_authentication_profile_and_persistence | Cadastro, login, perfil e persistência. | Passou |
| test_api.py:71 | test_authentication_and_csrf_guards | Barreiras de sessão, origem e CSRF. | Passou |
| test_api.py:81 | test_favorites_are_idempotent_and_persistent | Unicidade e permanência dos favoritos. | Passou |
| test_api.py:95 | test_saved_trips_and_user_isolation | Salvamento, exclusão e isolamento entre contas. | Passou |
| test_api.py:118 | test_invalid_payloads_return_json_errors | Entradas inválidas e erros JSON. | Passou |
| test_api.py:134 | test_reviews_and_database_integrity | Avaliações e restrições relacionais. | Passou |
| test_corrections.py:12 | test_location_totals_match_the_filtered_payload | Contadores cartográficos correspondem ao resultado filtrado. | Passou |
| test_corrections.py:21 | test_invalid_coordinates_never_become_zero_or_verified | Ausência/invalidez não vira ponto zero ou verificado. | Passou |
| test_corrections.py:32 | test_culture_is_preserved_associated_and_filterable | Textos preservados, vínculos e filtro cultural. | Passou |
| test_corrections.py:49 | test_planner_uses_specific_culture_without_fabricating_places | Interesse cultural e resposta sem inventar local. | Passou |
| test_expansion.py:42 | test_catalog_sources_idempotency_and_filters | Seed, fontes e filtros do catálogo. | Passou |
| test_expansion.py:66 | test_profile_defaults_handle_and_consent | Padrões privados, identificador e consentimento. | Passou |
| test_expansion.py:84 | test_upload_content_limits_privacy_and_removal | Conteúdo/tamanho, autorização e remoção de imagens. | Passou |
| test_expansion.py:104 | test_people_search_does_not_expose_private_data | Busca respeita exposição de dados. | Passou |
| test_expansion.py:115 | test_friend_rejection_removal_block_and_unblock | Estados sociais e bloqueio. | Passou |
| test_expansion.py:133 | test_favorites_visibility_and_history_privacy | Visibilidade dos favoritos e isolamento do histórico. | Passou |
| test_expansion.py:144 | test_trip_invitation_collaboration_and_link_revocation | Convites, notas e link público revogável. | Passou |
| test_expansion.py:163 | test_viewer_permission_and_declined_invites | Leitor não edita e convite recusado não concede acesso. | Passou |
| test_expansion.py:177 | test_voucher_lifecycle_and_ownership | Emissão/transições e ator permitido. | Passou |
| test_expansion.py:191 | test_voucher_expiration_cancellation_and_block | Expiração, cancelamento e bloqueio. | Passou |
| test_expansion.py:205 | test_accessibility_reports_do_not_self_publish | Sugestão pendente não altera local. | Passou |
| test_expansion.py:222 | test_themes_and_new_pages | Temas e entrega de novas telas. | Passou |
| test_expansion.py:230 | test_local_moderation_workflow | Aprovação/rejeição local com evidência. | Passou |
| test_expansion.py:243 | test_migration_preserves_legacy_data_and_backup | Migração preserva dados e cria cópia de esquema. | Passou |
