/* Navegação compartilhada por todas as páginas; sem menu duplicado. */
(() => {
 const host = document.querySelector('header.nav .navinner');
 if (!host) return;
 const items = [['/','Início'],['/catalogo','Explorar'],['/planejar#roteiro','Planejar roteiro'],['/amigos','Amigos'],['/favoritos','Favoritos'],['/historico','Histórico'],['/meus-roteiros','Meus roteiros'],['/perfil','Meu perfil'],['/configuracoes','Configurações']];
 const active=href=>location.pathname===href.split('#')[0]||(href==='/catalogo'&&(location.pathname==='/explorar'||location.pathname.startsWith('/destino/')));
 host.innerHTML = `<a class="brand" href="/" aria-label="Explore+ SLZ, início"><span class="brandmark" aria-hidden="true">✳</span><span>explore+<small>SLZ · TURISMO INTELIGENTE</small></span></a><div class="compact-actions"><a id="profileShortcut" class="nav-avatar" href="/perfil" aria-label="Meu perfil"><span aria-hidden="true">◉</span></a><div class="menu-anchor"><button id="siteMenuToggle" class="hamburger" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="siteMenu"><span></span><span></span><span></span></button><nav id="siteMenu" class="site-menu" aria-label="Navegação principal" hidden>${items.map(([href,label])=>`<a href="${href}" ${active(href) ? 'aria-current="page"' : ''}>${label}</a>`).join('')}<button id="loginOpen" type="button">Entrar / criar conta</button><button id="logoutBtn" type="button" hidden>Sair</button></nav></div></div>`;
 const toggle = document.querySelector('#siteMenuToggle'), menu = document.querySelector('#siteMenu');
 function close(focus = false) { menu.hidden = true; toggle.setAttribute('aria-expanded','false'); toggle.setAttribute('aria-label','Abrir menu'); if (focus) toggle.focus(); }
 function open() { menu.hidden = false; toggle.setAttribute('aria-expanded','true'); toggle.setAttribute('aria-label','Fechar menu'); }
 toggle.onclick = () => menu.hidden ? open() : close();
 toggle.onkeydown = event => { if(event.key === 'ArrowDown') { event.preventDefault(); open(); menu.querySelector('a').focus(); } };
 document.addEventListener('click', event => { if(!event.target.closest('.menu-anchor')) close(); });
 document.addEventListener('keydown', event => { if(event.key === 'Escape' && !menu.hidden) { event.preventDefault(); close(true); } });
 document.addEventListener('focusin', event => { if(!event.target.closest('.menu-anchor')) close(); });
 menu.addEventListener('click', event => { if(event.target.closest('a,button')) close(); });
 const isHome = !!document.querySelector('#tripForm');
 if(!isHome) document.querySelector('#loginOpen').onclick = () => location.href = '/#entrar';
 document.querySelector('#logoutBtn').onclick = async () => { try { await ExploreAccount.logout(); } catch(error) { alert(error.message); } };
 function refreshNavigation() {
  const user=ExploreAccount.user, profile=ExploreAccount.profile;
  document.querySelector('#loginOpen').hidden=!!user;
  document.querySelector('#logoutBtn').hidden=!user;
  const avatar=document.querySelector('#profileShortcut');
  avatar.replaceChildren();
  if(profile?.avatar_url) { const image=document.createElement('img'); image.src=profile.avatar_url; image.alt=''; image.style.objectPosition=`${profile.avatar_x}% ${profile.avatar_y}%`; avatar.append(image); }
  else { const span=document.createElement('span'); span.textContent=user ? Array.from(user.name)[0].toUpperCase() : '◉'; avatar.append(span); }
 }
 window.addEventListener('explore-login',refreshNavigation);
 window.addEventListener('explore-profile-updated',refreshNavigation);
})();
