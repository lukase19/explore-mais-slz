const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const api = (path, options) => ExploreAccount.api(path, options);
const route = location.pathname;
const names = {
 '/perfil': ['Meu perfil', 'Suas descobertas pela Ilha, em um só lugar.'],
 '/historico': ['Histórico', 'Relembre as pesquisas e os planos que começaram por aqui.'],
 '/favoritos': ['Meus favoritos', 'Guarde os lugares que merecem fazer parte da próxima viagem.'],
 '/meus-roteiros': ['Roteiros salvos', 'Da primeira ideia ao próximo passeio. Seus planos estão aqui.'],
 '/acessibilidade': ['Acessibilidade', 'Uma experiência de navegação no seu ritmo.']
};
const money = value => Number.isFinite(Number(value)) ? Number(value).toLocaleString('pt-BR', {style:'currency',currency:'BRL'}) : 'Não informado';
function dateLabel(value) {
 if (!value) return '';
 const date = new Date(value.includes('T') ? value : value.replace(' ', 'T') + 'Z');
 return Number.isNaN(date.getTime()) ? '' : new Intl.DateTimeFormat('pt-BR', {dateStyle:'medium',timeStyle:'short'}).format(date);
}
let toastTimer;
function toast(message) {
 const element = $('#toast'); element.textContent = message; element.classList.add('show');
 clearTimeout(toastTimer); toastTimer = setTimeout(() => element.classList.remove('show'), 4000);
}
const content = html => { $('#pageBody').innerHTML = html; };
const empty = (icon, title, text, href, action) => `<div class="panel-empty"><span class="empty-icon" aria-hidden="true">${icon}</span><h3>${title}</h3><p>${text}</p><a class="btn btn-light" href="${href}">${action}</a></div>`;
const sectionHead = (title, text, href, action) => `<div class="collection-head"><div><h2>${title}</h2><p>${text}</p></div>${href ? `<a class="text-link" href="${href}">${action} <span aria-hidden="true">↗</span></a>` : ''}</div>`;
const historyList = items => items.length ? `<ol class="activity-list">${items.map(item => `<li><span class="activity-icon" aria-hidden="true">${({pesquisa:'⌕',favorito:'♡',roteiro:'▤'})[item.tipo] || '•'}</span><div><strong>${esc(item.descricao)}</strong><small>${esc(({pesquisa:'Pesquisa',favorito:'Favorito',roteiro:'Roteiro'})[item.tipo] || item.tipo)} · <time>${esc(dateLabel(item.criado_em))}</time></small></div></li>`).join('')}</ol>` : empty('⌕','Toda descoberta tem um começo','Suas pesquisas e atividades aparecerão aqui.','/explorar#explorar','Explorar a Ilha');
const favoriteList = items => items.length ? `<div class="favorite-grid">${items.map(item => `<article class="favorite-card"><div class="destination-art" aria-hidden="true">${esc(item.icon)}</div><div class="favorite-copy"><small>${esc(item.municipality)}</small><h3>${esc(item.name)}</h3><p>${esc(item.description)}</p><div class="panel-actions"><a class="text-link" href="/explorar?q=${encodeURIComponent(item.name)}#explorar">Ver no mapa ↗</a><button class="icon-button" data-remove-fav="${item.id}" aria-label="Remover ${esc(item.name)} dos favoritos" title="Remover dos favoritos">♥</button></div></div></article>`).join('')}</div>` : empty('♡','Seu próximo lugar favorito','Toque no coração de um destino para guardá-lo na sua conta.','/explorar#explorar','Encontrar destinos');
function tripList(items) {
 return items.length ? `<div class="trip-list">${items.map(item => {
 const summary = item.trip?.summary || {};
 return `<article class="trip-card"><div class="trip-top"><span class="panel-pill">${esc(summary.destination || 'Ilha de São Luís')}</span><small>${esc(dateLabel(item.created_at))}</small></div><h3>${esc(item.title)}</h3><p>${esc(summary.days ?? '—')} dia(s) · ${esc(summary.people ?? '—')} pessoa(s) · ${esc(money(summary.budget))}</p><div class="panel-actions"><button class="btn btn-light" data-view="${item.id}" aria-expanded="false" aria-controls="trip-${item.id}">Ver detalhes</button><button class="text-button" data-delete="${item.id}" aria-label="Excluir ${esc(item.title)}">Excluir</button></div><div id="trip-${item.id}" class="trip-detail" hidden></div></article>`;
 }).join('')}</div>` : empty('▤','Um plano para chamar de seu','Crie um roteiro com seus interesses e salve para consultar depois.','/planejar#roteiro','Criar meu primeiro roteiro');
}
function identity(user) {
 const initials = user.name.trim().split(/\s+/).slice(0,2).map(part => Array.from(part)[0]).join('').toUpperCase();
 $('#sideName').textContent = user.name;
 $('#sideAvatar').textContent = initials;
 const title = $('#welcomeName'); if (title) title.textContent = user.name;
 const avatar = $('#profileAvatar'); if (avatar) avatar.textContent = initials;
 const settings = ExploreAccount.profile;
 const hero = $('.profile-hero');
 if (settings && hero) {
  const stats=$('.panel-stats');
  if(stats&&!stats.querySelector('.friends-stat')){const stat=document.createElement('a');stat.className='panel-stat friends-stat';stat.href='/amigos';stat.innerHTML=`<span>◉ Amigos</span><b>${Number(settings.friend_count)||0}</b><small>Planos em companhia ↗</small>`;stats.append(stat);}
  hero.classList.add('personalized');
  if (!hero.querySelector('.profile-cover')) { const cover = document.createElement('div'); cover.className = 'profile-cover'; hero.prepend(cover); }
  const cover = hero.querySelector('.profile-cover'); cover.replaceChildren();
  if (settings.cover_url) { const image = document.createElement('img'); image.src = settings.cover_url; image.alt = ''; image.style.objectPosition = `${settings.cover_x}% ${settings.cover_y}%`; cover.append(image); }
  if (avatar && settings.avatar_url) { const image = document.createElement('img'); image.src = settings.avatar_url; image.alt = ''; image.style.objectPosition = `${settings.avatar_x}% ${settings.avatar_y}%`; avatar.replaceChildren(image); }
  let bio = hero.querySelector('.profile-bio');
  if (!bio) { bio = document.createElement('div'); bio.className = 'profile-bio'; hero.append(bio); }
  bio.replaceChildren(); const text = document.createElement('p'); text.textContent = '@' + settings.handle + (settings.municipality ? ' · ' + settings.municipality : '') + (settings.bio ? ' — ' + settings.bio : ''); bio.append(text);
  const friends = document.createElement('a'); friends.href = '/amigos'; friends.className = 'profile-stats-link'; friends.textContent = `${settings.friend_count || 0} amigo(s) · Organizar com amigos ↗`; bio.append(friends);
 }
}
function profileForm(user) {
 return `<section class="panel-card profile-settings" id="dados-perfil">${sectionHead('Do seu jeito','Atualize seus dados e conte o que gosta de explorar.')}<form id="profileForm"><div class="profile-fields"><label for="profileName">Seu nome<input class="panel-field" id="profileName" minlength="2" maxlength="100" required value="${esc(user.name)}" autocomplete="name"></label><label for="profileEmail">Seu e-mail<input class="panel-field" id="profileEmail" type="email" value="${esc(user.email)}" disabled></label><label class="full-field" for="profileInterests">Seus interesses<input class="panel-field" id="profileInterests" value="${esc((user.interests || []).join(', '))}" placeholder="História, Cultura, Praias" aria-describedby="interestsHint"><small id="interestsHint">Separe por vírgulas. Até 12 interesses de 40 caracteres.</small></label></div><div class="form-footer"><span class="panel-subtle">Preferências salvas na sua conta.</span><button class="btn btn-primary" type="submit">Salvar alterações</button></div></form></section>`;
}
async function runAction(button, action, message) {
 button.disabled = true;
 try { await action(); toast(message); await load(); }
 catch (error) { toast(error.message); }
 finally { if (button.isConnected) button.disabled = false; }
}
function bindCollections(trips = []) {
 document.querySelectorAll('[data-view]').forEach(button => { const link = document.createElement('a'); link.href = '/roteiro-compartilhado/' + button.dataset.view; link.className = 'btn btn-light'; link.textContent = 'Amigos e compartilhamento'; button.after(link); });
 document.querySelectorAll('[data-remove-fav]').forEach(button => button.onclick = () => runAction(button, () => api('/api/favoritos/' + button.dataset.removeFav, {method:'DELETE'}), 'Favorito removido.'));
 document.querySelectorAll('[data-delete]').forEach(button => button.onclick = () => {
  if (confirm('Excluir este roteiro da sua conta?')) runAction(button, () => api('/api/roteiros-salvos/' + button.dataset.delete, {method:'DELETE'}), 'Roteiro excluído.');
 });
 document.querySelectorAll('[data-view]').forEach(button => button.onclick = () => {
  const item = trips.find(trip => String(trip.id) === button.dataset.view);
  const element = $('#trip-' + item.id);
  const opening = element.hidden;
  if (opening) {
   const trip = item.trip || {};
   element.innerHTML = `${(Array.isArray(trip.days) ? trip.days : []).map(day => `<h4>${esc(day?.title)}</h4>${(Array.isArray(day?.stops) ? day.stops : []).map(stop => `<p>${esc(stop?.icon)} <b>${esc(stop?.name)}</b> — ${esc(stop?.description)}</p>`).join('')}`).join('')}${trip.special_experience ? `<h4>${esc(trip.special_experience.title)}</h4><p>${esc(trip.special_experience.name)} — ${esc(trip.special_experience.description)}</p><p>${esc(trip.special_experience.note)}</p>` : ''}<p class="panel-subtle">${esc(trip.note || 'Confirme horários, custos e acessibilidade antes de sair.')}</p>`;
  }
  element.hidden = !opening; button.setAttribute('aria-expanded', String(opening)); button.textContent = opening ? 'Fechar detalhes' : 'Ver detalhes';
 });
 const clear = $('#clearHistory');
 if (clear) clear.onclick = () => { if (confirm('Apagar todo o histórico da sua conta?')) runAction(clear, () => api('/api/historico', {method:'DELETE'}), 'Histórico apagado.'); };
}
function bindProfile() {
 const settingsLink = document.createElement('a'); settingsLink.href = '/configuracoes'; settingsLink.className = 'text-link'; settingsLink.textContent = 'Personalizar foto, capa, tema e privacidade ↗'; $('#profileForm').after(settingsLink);
 $('#profileForm').onsubmit = async event => {
  event.preventDefault();
  const name = $('#profileName').value.trim();
  const interests = $('#profileInterests').value.split(',').map(value => value.trim()).filter(Boolean);
  if (name.length < 2 || interests.length > 12 || interests.some(value => value.length > 40)) { toast('Informe um nome válido e até 12 interesses de 40 caracteres.'); return; }
  const button = event.submitter; button.disabled = true;
  try {
   await api('/api/perfil', {method:'PATCH',body:JSON.stringify({name,interests})});
   Object.assign(ExploreAccount.user, {name,interests}); identity(ExploreAccount.user); ExploreAccount.updateUI(); toast('Perfil atualizado!');
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; }
 };
}
function renderAccessibility() {
 content(`<section class="panel-card"><h2>Preferências de leitura</h2><p>Ajustes visuais aplicados neste navegador.</p><div class="panel-actions"><button class="btn btn-light" id="larger">Aumentar texto</button><button class="btn btn-light" id="smaller">Diminuir texto</button><button class="btn btn-light" id="contrast" aria-pressed="${document.body.classList.contains('high-contrast')}">Alternar alto contraste</button></div></section><section class="panel-card"><h2>Planejamento inclusivo</h2><p>Ao criar roteiros, selecione as necessidades de acessibilidade disponíveis no formulário. Confirme as condições de acesso diretamente com cada estabelecimento antes da visita.</p><a href="/planejar#roteiro" class="btn btn-primary">Planejar com acessibilidade</a></section>`);
 $('#larger').onclick = () => setSize(1); $('#smaller').onclick = () => setSize(-1);
 const links = document.createElement('div'); links.className = 'panel-card'; links.innerHTML = '<h2>Planejar com informações verificadas</h2><p>As condições são registradas por recurso como confirmadas, não disponíveis ou ainda não verificadas. Ausência de informação não comprova acessibilidade.</p><div class="panel-actions"><a class="btn btn-light" href="/catalogo">Filtrar recursos no catálogo</a><a class="btn btn-light" href="/configuracoes">Preferências privadas e consentimento</a></div>'; $('#pageBody').append(links);
 $('#contrast').onclick = event => {
  const active = document.body.classList.toggle('high-contrast');
  ExploreAccount.preference('explore-contrast', active ? '1' : '0'); event.currentTarget.setAttribute('aria-pressed', String(active));
 };
}
let loading = false;
async function load() {
 if (loading) return; loading = true;
 const [title, description] = names[route] || names['/perfil'];
 $('#pageTitle').textContent = title; $('#pageSub').textContent = description; document.title = title + ' · Explore+ SLZ';
 document.querySelectorAll('[data-nav]').forEach(link => { const active = link.getAttribute('href') === route; link.classList.toggle('current', active); if (active) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current'); });
 const user = ExploreAccount.user;
 $('#logoutBtn').hidden = !user;
 $('#pageBody').setAttribute('aria-busy','true');
 try {
  if (user) identity(user);
  if (route === '/acessibilidade') { renderAccessibility(); return; }
  if (ExploreAccount.sessionError) throw Error('Não foi possível carregar sua sessão. Verifique a conexão e tente novamente.');
  if (!user) { content(empty('◉','Seu espaço de descobertas','Entre ou cadastre-se para reunir histórico, favoritos e roteiros na sua conta.','/#entrar','Entrar ou criar conta')); return; }
  identity(user);
  if (route === '/perfil') {
   const results = await Promise.allSettled(['/api/resumo','/api/historico','/api/favoritos','/api/roteiros-salvos'].map(path => api(path)));
   const [stats, history, favorites, trips] = results.map(result => result.status === 'fulfilled' ? result.value : null);
   const unavailable = '<p class="collection-error" role="status">Não foi possível carregar esta coleção. <button class="text-button" data-retry>Tentar novamente</button></p>';
   content(`<section class="profile-hero"><div class="profile-hero-top"><div class="profile-avatar" id="profileAvatar" aria-hidden="true"></div><div><span class="hero-kicker">SEU PRÓXIMO CAPÍTULO COMEÇA AQUI</span><h2 id="welcomeName"></h2><p>${esc(user.email)}</p></div></div><div class="profile-hero-bottom"><p>Mais descobertas.<br><strong>Mais histórias para contar.</strong></p><a class="btn btn-orange" href="/planejar#roteiro">✦ Criar novo roteiro</a></div><span class="hero-decoration" aria-hidden="true">✳</span></section><div class="panel-stats"><a class="panel-stat" href="/historico"><span>⌕ Pesquisas</span><b>${stats ? stats.searches : '—'}</b><small>Suas buscas pela Ilha ↗</small></a><a class="panel-stat" href="/favoritos"><span>♡ Favoritos</span><b>${stats ? stats.favorites : '—'}</b><small>Lugares para conhecer ↗</small></a><a class="panel-stat" href="/meus-roteiros"><span>▤ Roteiros salvos</span><b>${stats ? stats.trips : '—'}</b><small>Planos para viver ↗</small></a></div>${stats ? '' : unavailable}<section class="panel-card">${sectionHead('Seus lugares favoritos','Uma seleção com a sua cara.','/favoritos','Ver todos')}${favorites ? favoriteList(favorites.results.slice(0,2)) : unavailable}</section><section class="panel-card">${sectionHead('Próximas aventuras','Retome seus planejamentos quando quiser.','/meus-roteiros','Ver roteiros')}${trips ? tripList(trips.results.slice(0,2)) : unavailable}</section><section class="panel-card">${sectionHead('Por onde você andou','Suas atividades mais recentes no Explore+.','/historico','Ver histórico')}${history ? historyList(history.results.slice(0,4)) : unavailable}</section>${profileForm(user)}`);
   identity(user); bindProfile(); bindCollections(trips?.results || []);
  } else if (route === '/historico') {
   const data = await api('/api/historico');
   content(`<section class="panel-card">${sectionHead('Atividades recentes','Até 100 atividades mais recentes da sua conta.')}<div class="collection-toolbar"><button class="btn btn-light" id="clearHistory" ${data.results.length ? '' : 'disabled'}>Limpar histórico</button></div>${historyList(data.results)}</section>`); bindCollections();
  } else if (route === '/favoritos') {
   const data = await api('/api/favoritos'); content(`<section class="panel-card">${sectionHead('Lugares salvos',`${data.results.length} destino(s) para descobrir.`)}${favoriteList(data.results)}</section>`); bindCollections();
  } else if (route === '/meus-roteiros') {
   const data = await api('/api/roteiros-salvos'); content(`<section class="panel-card">${sectionHead('Seus planejamentos','Até 100 roteiros mais recentes.','/planejar#roteiro','Criar roteiro')}${tripList(data.results)}</section>`); bindCollections(data.results);
  }
 } catch (error) { content(`<section class="panel-card"><h2>Vamos tentar de novo?</h2><p role="alert">${esc(error.message)}</p><button class="btn btn-primary" data-retry>Tentar novamente</button></section>`); }
 finally { loading = false; $('#pageBody').setAttribute('aria-busy','false'); document.querySelectorAll('[data-retry]').forEach(button => button.onclick = () => ExploreAccount.sessionError ? ExploreAccount.init() : load()); }
}
function setSize(direction) {
 const size = Math.max(85, Math.min(145, Number(ExploreAccount.preference('explore-font') || 100) + direction * 10));
 document.documentElement.style.fontSize = size + '%'; ExploreAccount.preference('explore-font', size);
}
document.addEventListener('DOMContentLoaded', () => {
 $('#logoutBtn').onclick = async () => { try { await ExploreAccount.logout(); } catch (error) { toast(error.message); } };
});
window.addEventListener('explore-login', load);
