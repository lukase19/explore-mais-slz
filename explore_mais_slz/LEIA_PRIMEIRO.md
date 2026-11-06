# Explore+ SLZ — versão atualizada

## Como executar no Windows

1. Extraia **toda** a pasta do ZIP.
2. Instale Python 3.10+ e marque **Add Python to PATH** na instalação.
3. Dê dois cliques em `INICIAR_WINDOWS.bat`. Na primeira vez, é necessário ter internet para instalar o Flask.
4. Abra **http://127.0.0.1:5000** no navegador.

Alternativa no terminal, a partir da pasta `explore_mais_slz`:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app
```

## O que mudou

- A página inicial foi preservada; os endpoints de destinos, mapa e roteiros permanecem.
- Login, cadastro e logout reais, senhas armazenadas como hash Werkzeug.
- Rotas independentes: `/perfil`, `/historico`, `/favoritos`, `/meus-roteiros`, `/acessibilidade`, além dos endereços `/explorar` e `/planejar` que reutilizam a página inicial e suas respectivas seções.
- Histórico de pesquisas e roteiros no banco SQLite, associado ao usuário.
- Favoritos da página inicial sincronizados com a conta; roteiros gerados podem ser salvos e recuperados.
- Atualização de nome e interesses; avaliações de destinos disponíveis via API.
- Preferências locais de contraste e tamanho do texto na página de acessibilidade.
- Os dados são guardados localmente em `backend/explore_slz.db` (o banco é criado automaticamente na primeira execução).

## Observações importantes

- Este projeto é uma **versão funcional para desenvolvimento local**, não um serviço pronto para produção pública. Antes de publicar na internet, configure `EXPLORE_SECRET_KEY` com uma chave longa e persistente, HTTPS com `EXPLORE_HTTPS=1`, proteção contra tentativas excessivas de login, backups, políticas de privacidade e revisão de segurança.
- A chave de sessão temporária é gerada a cada início caso `EXPLORE_SECRET_KEY` não esteja configurada; isto faz sessões expirarem ao reiniciar.
- A interface de administração, fotos de perfil e recomendações avançadas por IA **não** foram implementadas nesta entrega.
- O mapa usa arquivos do Leaflet/OpenStreetMap e requer acesso à internet para carregar os mapas base.
- Os custos e horários do gerador são exemplos de planejamento, não valores ou disponibilidades em tempo real.
- O arquivo `.venv` original foi excluído do ZIP para evitar incompatibilidade de dependências e reduzir o tamanho.

## Onde está cada parte

- `backend/app.py`: Flask, SQLite, autenticação e APIs.
- `frontend/index.html`: página original preservada, links de acesso e login real.
- `frontend/script.js`: mapa, pesquisa, planejador e integração dos favoritos.
- `frontend/account.js`: utilitário de sessão e requisições com token CSRF.
- `frontend/painel.html`, `painel.css`, `painel.js`: páginas de conta e histórico.
