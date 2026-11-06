# Preparação para GitHub e Vercel — 06/11/2026

## Resultado e arquitetura escolhida

Preparação local concluída. Não houve git add, commit, push, publicação, exclusão ou transferência de dados.
O projeto ainda depende de um servidor Flask com HTTPS e disco persistente antes de poder ser publicado com os dados atuais.

```text
Navegador → domínio público Vercel → proxy de todas as rotas → Flask/Waitress → SQLite em disco persistente
```

A escolha foi confirmada pelo usuário. O Flask continua servindo HTML, CSS, JavaScript, bibliotecas de mapas, imagens e APIs. Não há alteração visual nem mudança dos caminhos existentes. O proxy encaminha também parâmetros de busca, cookies e requisições de escrita, sem redirecionar o navegador para outro domínio.

A Vercel suporta Flask, mas seu armazenamento de funções não é um disco SQLite persistente e compartilhado. Não copie o banco para `/tmp` e não inclua o banco no Git. Referências: [SQLite e armazenamento serverless](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel), [proxy por rewrites externos](https://vercel.com/docs/routing/rewrites).

## Estrutura e dependências verificadas

- `backend/app.py`: Flask, autenticação por sessão, CSRF, catálogo, roteiros, avaliações, favoritos e histórico.
- `backend/expansion.py`: perfis, mídia, amigos/bloqueios, colaboração, compartilhamento, vouchers e sugestões de acessibilidade.
- `backend/migrations.py`, `catalog.py`, `culture.py`, `culture_content.json`: esquema, catálogo e cultura. A inicialização já executava migração incremental e carga do catálogo.
- `frontend/`: HTML/CSS/JavaScript sem etapa de compilação ou dependência npm; Leaflet e agrupador locais. O fundo do mapa usa OpenStreetMap; fontes e links externos continuam dependendo de rede.
- `requirements.txt`: Flask, Pillow e agora Waitress, servidor WSGI para produção em Linux ou Windows. Python 3.12 foi utilizado na verificação.
- Testes unitários e três roteiros Playwright/Chrome; documentação de seminário e scripts auxiliares sem função no runtime público.

## Onde estão os dados

| Local | Conteúdo e tratamento |
| --- | --- |
| `backend/explore_slz.db` | SQLite principal; persistir fora do Git, no servidor Flask. |
| Tabelas de usuários e relacionamentos | Contas, hashes de senha, perfis, preferências, consentimento, amizades, bloqueios, favoritos, histórico, avaliações, roteiros, convites e vouchers. |
| Tabela `media` | Avatar e capa como BLOB JPEG; não há pasta de uploads usada pelo aplicativo atual. Um backup completo do SQLite inclui as imagens. |
| `backend/culture_content.json` | Conteúdo cultural versionado, somente leitura; não é um arquivo gravável de usuários. |
| `backend/backups/*.sql` | Cópias de esquema feitas pela migração existente; NÃO contêm um backup dos registros dos usuários. |
| `localStorage` do navegador | Tema, fonte e contraste. Essas preferências locais não são transferidas entre domínios; tema de perfil também está no banco. |
| `.artifacts/` | Capturas, resultados e ambiente isolado de testes; não publicar. |

Inventário inicial, sem expor conteúdo pessoal: 76 destinos, 2 usuários, 2 perfis, 2 imagens, 1 amizade, 1 voucher e 4 eventos de histórico. Não foram criados usuários de teste no banco real.

O hash do arquivo SQLite mudou durante o trabalho. Foi identificado um Flask já ativo na porta 5000 com recarga automática, cujo processo filho reiniciou às 11:30:31 do relógio local da máquina após edições. A inicialização existente executa `seed_catalog`, que usa `INSERT OR IGNORE` com AUTOINCREMENT e pode avançar `sqlite_sequence` mesmo sem adicionar destinos. As contagens acima continuaram iguais na conferência final. Não é possível afirmar igualdade byte a byte com a base inicial; não restauramos, apagamos ou migramos o banco. O processo existente não foi encerrado.

### Persistência proposta, ainda não executada

1. Contratar ou configurar um servidor de aplicação com volume persistente e HTTPS; manter uma instância do Flask acessando o SQLite. Não usar disco efêmero nem escalar instâncias com bancos independentes.
2. Autorizar posteriormente uma cópia consistente do banco com a API de backup do SQLite, incluindo as imagens. Não copiar um arquivo em uso de forma ingênua, especialmente se houver WAL. Guardar o original e uma cópia privada de segurança fora do Git.
3. Restaurar a cópia no volume, por exemplo `/data/explore_slz.db`, preservando IDs, hashes, relacionamentos e mídias. Verificar integridade e contagens antes da troca pública.
4. Definir backups completos periódicos fora desse servidor e verificar uma restauração. A pasta de backups de esquema existente não substitui isso.
5. Na troca definitiva, evitar novas gravações simultâneas na base local e na cópia hospedada. Validar reinício do servidor e persistência antes de liberar uso público.

PostgreSQL externo e armazenamento de objetos continuam sendo alternativas futuras para crescimento; exigem adaptação de SQL, migração de registros/mídias e autorização própria. Não foram implementados.

## Configuração do servidor Flask

Usar a pasta `explore_mais_slz` como diretório de trabalho. Instalar `requirements.txt` em um ambiente virtual íntegro:

```sh
python -m pip install -r requirements.txt
python -m waitress --listen=0.0.0.0:8000 backend.app:app
```

Ajustar `8000` à porta exigida pelo servidor. O HTTPS deve ser terminado pelo serviço de hospedagem ou proxy confiável. Não usar `python backend/app.py` em produção, pois esse comando inicia o servidor de desenvolvimento com debug.

Configurar as variáveis no ambiente do servidor, conforme `.env.example`:

- `EXPLORE_DATABASE_PATH`: caminho absoluto do banco existente no volume persistente.
- `EXPLORE_SECRET_KEY`: chave aleatória de pelo menos 32 caracteres, estável entre reinícios e guardada como segredo. Gerar no servidor com `python -c "import secrets; print(secrets.token_hex(32))"`; não salvar a chave no Git.
- `EXPLORE_HTTPS=1`: cookie de sessão Secure.
- `EXPLORE_PUBLIC_ORIGIN`: origem HTTPS exata vista pelo visitante, por exemplo `https://seu-site.vercel.app`, sem caminho. Se houver domínio próprio, usar esse domínio e atualizar a variável.

O aplicativo não carrega `.env` automaticamente. Em modo público, a inicialização recusa chave ausente/curta, HTTP, banco ausente ou caminho relativo. Isso impede uma base vazia criada por um erro de configuração. O modo local continua com seu comportamento anterior.

A checagem de origem usa a origem pública configurada, preservando o CSRF quando o proxy altera o Host recebido pelo Flask. Não confia em `X-Forwarded-Host` enviado pelo cliente. O token CSRF continua obrigatório nas alterações autenticadas. APIs e mídia recebem `private, no-store`; o cache de rewrites foi desabilitado.

## Configuração da Vercel após preparar a origem

1. Em `vercel.json`, substituir **somente** `https://configure-backend.invalid/:path*` pela URL HTTPS real do servidor Flask, mantendo `/:path*`. Nunca usar a URL pública da própria Vercel como destino, pois isso criaria um loop.
2. Importar o repositório GitHub com **Root Directory = `explore_mais_slz`**, Framework Preset **Other**. Respeitar os comandos de build, instalação e saída definidos no `vercel.json`.
3. O build usa `python3 scripts/prepare_vercel.py`, sem instalar Flask na Vercel. O verificador usa apenas a biblioteca padrão, recusa o endereço fictício e gera uma saída estática mínima, sem página inicial. O build fica bloqueado intencionalmente até a origem real ser configurada.
4. `.vercelignore` permite apenas a configuração do proxy e seu verificador no upload. O banco, as imagens, o backend, os testes, os ambientes e os documentos não entram no pacote Vercel. O código completo continua no GitHub para ser instalado no servidor Flask.
5. Não é necessário configurar segredos do Flask na Vercel nesta arquitetura.

Previews têm domínios diferentes da origem pública configurada. Não liberar todos os domínios por CORS nem remover CSRF para fazê-los gravar. Para previews completos, usar outra origem Flask, outro banco persistente e outra configuração de origem, isolados dos dados de produção.

Após publicação autorizada, ainda será necessário validar pelo domínio público: cadastro/login, sessão após reinício, favoritos/roteiros, amigos e convites, voucher, upload/remoção de mídia privada, catálogo/cultura, mapas e personalização. O proxy externo da Vercel e a persistência do futuro servidor não foram testados em nuvem, pois não houve publicação.

## Git, segredos e arquivo de nome estranho

A raiz Git é `Explore_Mais_SLZ_Perfil_Corrigido`, um nível acima do aplicativo. A branch é `main`, ainda sem commits e sem remote. Havia arquivos previamente no staging; seu índice foi preservado.

A inspeção procurou arquivos de ambiente, bancos/dumps, chaves privadas, padrões de tokens, senhas literais e e-mails em fontes e documentos. Não foram encontrados segredos reais nos candidatos a versionamento; os e-mails encontrados são exemplos `example.test` e a documentação contém um segredo didático explicitamente local. Os dados reais estão no SQLite, que permanece ignorado. A busca por padrões não garante ausência universal de segredos.

As regras agora também abrangem arquivos laterais do SQLite, dumps, chaves, backups, uploads locais, logs, temporários, ambientes e artefatos Vercel. `.env.example` é permitido e contém apenas valores ilustrativos, com chave vazia. Nenhum segredo ou banco está no índice atual.

`../ntent .explore_mais_slzANALISE_PROJETO.md -Raw`, relativo ao aplicativo, tem 1.795 bytes e contém avisos de finais de linha e um resumo de diferenças do Git. Não é o relatório `ANALISE_PROJETO.md`, não é importado nem referenciado pelo aplicativo e aparenta ser saída de terminal salva acidentalmente. Foi preservado integralmente e ignorado pela regra da raiz; nada foi excluído.

O ZIP de documentação de seminário também foi preservado e ignorado; os documentos Markdown originais permanecem disponíveis.

## Arquivos alterados nesta tarefa

Raiz Git:

- `.gitignore` — criado para proteger também arquivos fora da subpasta do app.

Dentro de `explore_mais_slz/`:

- `.gitignore` — ampliado.
- `.env.example` — criado, sem chave real.
- `.vercelignore` — criado para limitar o pacote da Vercel.
- `vercel.json` — criado para proxy HTTPS de todas as rotas, sem cache.
- `scripts/prepare_vercel.py` — criado para validar o build.
- `backend/app.py` — configuração pública, validação de persistência/chave, origem atrás do proxy e proteção de cache.
- `requirements.txt` — adicionado Waitress.
- `test_deploy.py` — criado para regressões de deploy.
- `README.md` — atualizado com o caminho para este guia.
- `DEPLOY_VERCEL.md` — este relatório.

Frontend e funcionalidades não foram editados. Além desses arquivos de preparação, foram gerados resultados/capturas e um ambiente de testes em `.artifacts/`, ignorado. A mudança de hash do SQLite pelo processo local já ativo está explicada acima; o arquivo não será incluído no commit.

## Verificações executadas

- Suíte original e regressões iniciais: 31 testes passaram; após acrescentar a validação da saída de build, os 6 testes de deploy passaram. São **32 testes distintos aprovados**.
- `test_browser.py`, `browser_expansion.py`, `browser_corrections.py`: todos passaram com Chrome, sem erros JavaScript, em 320/390/768/1440 px. Incluem cultura, mapas/agrupamentos/filtros, três temas, fotos/capa, amigos, convites, compartilhamento, vouchers e moderação.
- Waitress via HTTP local: inicial, API health, catálogo e Leaflet responderam 200, usando banco temporário.
- `pip check`: nenhuma dependência quebrada no ambiente isolado. Versões verificadas: Python 3.12, Flask 3.1.3, Pillow 12.3.0 e Waitress 3.0.2. Playwright é dependência apenas de teste.
- Validação de build com origem fictícia: rejeitada como previsto. Com origem HTTPS de teste: saída contém apenas marcador sem dados locais.
- `git diff --check` e regras de ignore: aprovados. Nenhum banco, `.env` ou chave privada está no índice. O hash do índice Git permaneceu igual ao inicial.

O `.venv` original apresentou módulos inacessíveis sob o ambiente restrito; foi mantido. A instalação e os testes passaram em `.artifacts/deploy-venv`. Algumas tentativas iniciais foram impedidas por permissões de diretórios temporários; as execuções válidas posteriores utilizaram o mesmo código com acesso aos temporários permitido.

Uma repetição final adicional da suíte completa foi rejeitada pela revisão automática de aprovação, que apontou risco de escrita no banco real e referências ao caminho de banco nos testes. Essa repetição não foi executada nem contornada. Os resultados acima correspondem às execuções anteriores concluídas: 31 testes na suíte e 6 testes de deploy, somando 32 testes distintos, mais os três roteiros de navegador e o teste HTTP do Waitress. Não foi solicitada autorização para uma repetição desnecessária.

## Primeiro commit e envio ao GitHub — comandos para o usuário

Criar no GitHub um repositório vazio, sem README/licença/gitignore gerados pelo GitHub. Substituir `SEU_USUARIO` pelo nome correto. Os comandos abaixo ainda **não foram executados**:

```powershell
Set-Location 'C:\Users\felps\Downloads\Explore_Mais_SLZ_Perfil_Corrigido'
git status --short
git add -- .gitignore explore_mais_slz
git diff --cached --stat
git diff --cached --check
git diff --cached
# Após conferir que não há dados pessoais, banco nem segredos no diff:
git commit -m "Prepara Explore+ SLZ para Vercel com backend persistente"
git remote add origin https://github.com/SEU_USUARIO/explore-mais-slz.git
git push -u origin main
```

Se o Git solicitar identidade, configurar `git config user.name "Seu Nome"` e `git config user.email "seu-email-noreply-do-github"` antes do commit. Autenticar no GitHub pelo mecanismo habitual, sem colocar token na URL. O envio do código não transfere o SQLite. A publicação continua pendente da origem real, do volume e da cópia autorizada dos dados.
