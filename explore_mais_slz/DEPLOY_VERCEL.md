# Vercel opcional

O caminho recomendado agora usa apenas Render: siga [DEPLOY.md](DEPLOY.md).
A Vercel não hospeda o SQLite e não é necessária para colocar este projeto no ar.

## O que foi corrigido

A configuração anterior continha `https://configure-backend.invalid/:path*`; o script recusava esse destino e o build falhava. Agora o script aceita `EXPLORE_BACKEND_URL` e gera as rotas finais pela Build Output API, em `.vercel/output/config.json`. Não altera um `vercel.json` depois que suas rotas já foram processadas. Também recusa loop para os domínios conhecidos da própria implantação e mostra uma mensagem curta quando a origem não está definida.

O script não importa Flask, não abre o banco e não inclui dados ou ambientes no pacote. `vercel.json` define apenas o comando de build e desativa a detecção de framework/instalação. `.vercelignore` mantém somente esses arquivos e o verificador no upload.

## Se decidir manter a Vercel

1. Primeiro colocar o site completo no Render, incluindo a importação dos dados.
2. No projeto Vercel, usar Root Directory `explore_mais_slz`, preset **Other** e os comandos do `vercel.json`, sem overrides antigos de Output Directory.
3. Cadastrar na Vercel `EXPLORE_BACKEND_URL=https://seu-servico.onrender.com`, sem caminho ou credenciais, e executar um novo deploy. A variável precisa estar disponível no build.
4. No Render, cadastrar `EXPLORE_PUBLIC_ORIGIN=https://seu-site.vercel.app` (ou o domínio público definitivo) e reiniciar. Todas as requisições devem então usar esse domínio público; sessões são específicas do domínio.

Esse caminho acrescenta um proxy e configuração de origem. Para minimizar etapas, usar diretamente a URL Render e não executar nenhum destes passos. Não é possível executar este SQLite gravável diretamente nas funções da Vercel com persistência local confiável. Sem backend definido, o build continua recusado por segurança; não é substituído por uma página demonstrativa nem por um banco temporário.

Referências: [Build Output API](https://vercel.com/docs/build-output-api/configuration), [SQLite em funções Vercel](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel).
