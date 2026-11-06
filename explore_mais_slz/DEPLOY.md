# Colocar Explore+ SLZ no ar

Use **um serviço Render pago com disco persistente**. Ele serve o frontend e o Flask, com SQLite e imagens no mesmo volume. Vercel e Railway não são necessários. O repositório é `lukase19/explore-mais-slz`.

O plano `0.5c-512mb` custa US$ 7/mês; 1 GB de disco custa US$ 0,25/mês. Base estimada: **US$ 7,25/mês**, antes de impostos, câmbio e eventual uso adicional. Confirme o valor mostrado pelo Render antes de criar o serviço. O workspace Hobby não exige plano de equipe pago. Fontes: [compute de US$ 7](https://render.com/articles/production-rails-hosting-guide), [preços de armazenamento](https://render.com/pricing).

O Render gratuito não aceita disco persistente; arquivos locais se perdem em reinícios. PythonAnywhere tem opção gratuita com disco limitado e renovação mensal da aplicação, mas exige mais configuração manual. Para a prioridade de simplicidade e continuidade, a configuração entregue usa Render pago. Fontes: [limites do Render gratuito](https://render.com/docs/free), [conta gratuita PythonAnywhere](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/).

## 1. Enviar os ajustes de código ao GitHub

Na raiz do repositório, no PowerShell:

```powershell
Set-Location 'C:\Users\felps\Downloads\Explore_Mais_SLZ_Perfil_Corrigido'
git add -- render.yaml explore_mais_slz/backend/hosting.py explore_mais_slz/scripts/backup_database.py explore_mais_slz/scripts/prepare_vercel.py explore_mais_slz/vercel.json explore_mais_slz/test_hosting.py explore_mais_slz/test_deploy.py explore_mais_slz/README.md explore_mais_slz/.env.example explore_mais_slz/DEPLOY.md explore_mais_slz/DEPLOY_VERCEL.md
git diff --cached --stat
git diff --cached --check
git commit -m "Simplifica deploy com Render e SQLite persistente"
git push origin main
```

Não adicionar o banco nem imagens privadas ao Git. As imagens de perfil/capa já são BLOBs dentro do SQLite; não existe uma pasta de uploads a transferir separadamente. Os comandos acima não foram executados pelo assistente.

## 2. Criar um único serviço no Render

Abrir [o painel Render](https://dashboard.render.com), conectar o GitHub e selecionar **New → Blueprint → lukase19/explore-mais-slz**, com `render.yaml` da raiz. Confirmar **Create/Deploy Blueprint**.

Conferir o custo antes de confirmar. O YAML já define subpasta, Python, instalação, início, disco, banco, HTTPS e duas chaves aleatórias persistentes. Não cadastrar variáveis manualmente. Não escolher plano Free nem remover o disco.

O primeiro deploy abrirá a tela **Importar seus dados**. Isso é esperado: o serviço não cria uma base vazia e não libera cadastro antes da importação. O health check informa `waiting_for_database` nessa fase; após a importação, informa `ready`.

## 3. Gerar e enviar uma cópia consistente do SQLite

Este passo transfere uma cópia dos dados ao serviço escolhido. **Execute somente quando autorizar esse envio.** O assistente não o executou. O comando abaixo apenas cria um novo backup local, sem apagar ou migrar a origem:

```powershell
Set-Location 'C:\Users\felps\Downloads\Explore_Mais_SLZ_Perfil_Corrigido\explore_mais_slz'
py -3.12 scripts/backup_database.py
```

Ele imprime o caminho de uma nova cópia `.artifacts/explore-upload-....sqlite`. Usa a API de backup do SQLite, abre a origem em modo somente leitura, inclui as imagens e recusa substituir arquivos existentes. Não enviar o banco em uso diretamente pelo explorador de arquivos.

No painel do Render, abrir **Environment**, revelar/copiar o valor de **EXPLORE_IMPORT_TOKEN**. Abrir a URL pública `https://...onrender.com`, colar essa chave no formulário e selecionar a cópia indicada pelo comando. Clicar **Enviar cópia e abrir o site**. Não usar a chave `EXPLORE_SECRET_KEY` no formulário e não compartilhar as chaves.

O envio verifica integridade, referências e esquema existente, publica o arquivo sem sobrescrita e abre o site original. Não transforma o esquema. Ao detectar banco instalado, a entrada de importação deixa de estar disponível. Se já houver dados no disco, nenhum reenvio poderá substituí-los. Não é necessário reiniciar ou usar SSH.

Depois dessa troca, usar o site hospedado como base principal; gravações posteriores no aplicativo local não são sincronizadas automaticamente. Manter o original e o backup privado guardados.

## 4. Conferir e usar a URL do Render

Entrar com uma conta existente e conferir perfil/foto, amigos, voucher e roteiros. Em **Manual Deploy → Restart service**, reiniciar o serviço e conferir que os mesmos registros e imagens continuam disponíveis. Depois, compartilhar a URL pública do Render. O código foi testado localmente; essa confirmação em nuvem depende do serviço criado pelo usuário.

Não é necessário alterar ou excluir projetos já existentes na Vercel/Railway. Se algum serviço antigo ainda receber gravações, evitar usar duas cópias independentes como se fossem sincronizadas. Fazer backups completos periódicos fora do serviço; o volume preserva dados entre deploys, mas não substitui uma cópia independente. Não remover o disco ao atualizar o código.

### Comandos já configurados no Render

```sh
# Diretório: explore_mais_slz
pip install -r requirements.txt
python -m backend.hosting
```

`PORT` e `RENDER_EXTERNAL_URL` são fornecidos pelo Render. O app usa Waitress, sem debug. APIs, sessões, CSRF, mídia privada, mapas, cultura, personalização e as demais páginas continuam no mesmo domínio. Domínio próprio é opcional; nesse caso, configurar somente `EXPLORE_PUBLIC_ORIGIN=https://seu-dominio` e redeploy.

### Verificação e limites desta entrega

Foram aprovados 14 testes de hospedagem/configuração, incluindo envio autenticado, arquivo inválido, origem falsa, recusa de sobrescrita, backup com BLOB, ativação do site e manutenção de conta, sessão e imagem após reiniciar o processo. Os testes foram feitos em cópia isolada de código sem o banco real. O índice Git e o arquivo de nome estranho foram preservados. Não houve commit, push, publicação, cópia real de dados ou contratação.

O Flask local com recarga automática continuava aberto e reiniciou ao detectar arquivos Python editados. A carga de catálogo já existente avançou o contador interno do SQLite; o hash do banco mudou. A conferência manteve os mesmos 76 destinos, 2 usuários, 2 perfis, 2 imagens, 1 amizade, 1 voucher e 4 eventos de histórico, sem mudança da versão do esquema. Nenhum teste usou esse arquivo, nenhuma restauração foi feita e o processo local não foi encerrado. O backup para publicação deve ser gerado somente no momento da troca autorizada.

Também foi aprovado o teste da tela de importação no Chrome: envio real de formulário multipart com SQLite temporário, abertura da aplicação após o envio e ausência de erros JavaScript. Não houve envio de dados reais nesse teste.

O formulário inicial aceita cópia de até 64 MB. O banco atual é muito menor; para volumes maiores, preparar transferência administrativa separada. O disco suporta uma instância do aplicativo. Para atualizar o código, manter o mesmo serviço e disco. Os segredos gerados pelo Blueprint permanecem estáveis entre deploys. A Vercel opcional está documentada em [DEPLOY_VERCEL.md](DEPLOY_VERCEL.md).
