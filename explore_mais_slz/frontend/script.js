
const $=s=>document.querySelector(s);
const menuToggle=$('#menuToggle'), navLinks=$('#navLinks');if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
        const opened = navLinks.classList.toggle('open');

        menuToggle.setAttribute('aria-expanded', String(opened));
        menuToggle.setAttribute(
            'aria-label',
            opened ? 'Fechar menu' : 'Abrir menu'
        );
    });

    navLinks.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            navLinks.classList.remove('open');
            menuToggle.setAttribute('aria-expanded', 'false');
            menuToggle.setAttribute('aria-label', 'Abrir menu');
        });
    });
}
function toast(msg) {
    const t = $('#toast');

    if (!t) return;

    t.textContent = msg;
    t.classList.add('show');

    setTimeout(() => t.classList.remove('show'), 3500);
}function money(n){return Number(n).toLocaleString('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0})}

$('#tripForm').addEventListener('submit', async e => {
 e.preventDefault();
 const budget=Number($('#budget').value);
 const days=Number($('#days').value);
 const destination=$('#destination').value;
 const people=$('#people').value;
 const transport=$('#transport').value;
 const interests=[...document.querySelectorAll('input[name="interest"]:checked')].map(x=>x.value);
 const access=[...document.querySelectorAll('input[name="access"]:checked')].map(x=>x.value);
 const err=$('#formError');
 if(!Number.isFinite(budget)||budget<=0||!Number.isFinite(days)||days<1||!interests.length){err.style.display='block';return;}
 err.style.display='none';
 const submitButton=$('#tripForm button[type="submit"]');
 const originalText=submitButton.textContent;
 submitButton.disabled=true; submitButton.textContent='Preparando seu roteiro...';
 try {
   const data=await ExploreAccount.api('/api/roteiro',{method:'POST',body:JSON.stringify({destination,days,budget,people,transport,interests,access,theme:new URLSearchParams(location.search).get('theme')||''})});
   const result=$('#result');
   let out=`<h3>✦ Seu roteiro inicial</h3><p class="result-summary"><b>${escapeHTML(data.summary.destination)}</b> · ${data.summary.days} ${data.summary.days===1?'dia':'dias'} · ${escapeHTML(data.summary.people)} pessoa(s) · orçamento de ${money(data.summary.budget)}.<br>Transporte: ${escapeHTML(data.summary.transport)}. Interesses: ${data.summary.interests.map(escapeHTML).join(', ')}.${data.summary.access.length?'<br>Atenção especial: '+data.summary.access.map(escapeHTML).join(', ')+'.':''}</p>`;
   out+=`<p class="result-summary">Referência de planejamento: cerca de <b>${money(data.summary.per_day)} por dia</b> para o grupo (≈ ${money(data.summary.per_person_day)} por pessoa). É uma divisão simples do orçamento informado, não uma cotação de preços.</p>`;
   data.days.forEach(day=>{
     out+=`<div class="day"><h4>${escapeHTML(day.title)}</h4>`;
     day.stops.forEach(stop=>{out+=`<div class="stop"><span class="stop-icon">${escapeHTML(stop.icon)}</span><div><b>${escapeHTML(stop.name)}</b>${escapeHTML(stop.description)}</div></div>`;});
     out+=`<div class="stop"><span class="stop-icon">🍽️</span><div><b>Pausa para comer</b>Pesquise opções próximas e confira os preços no dia.</div></div></div>`;
   });
   if(data.special_experience){
     const special=data.special_experience;
     out+=`<div class="day special-experience"><h4>${escapeHTML(special.title)}</h4><div class="stop"><span class="stop-icon">${escapeHTML(special.icon)}</span><div><b>${escapeHTML(special.name)}</b>${escapeHTML(special.description)}</div></div><p class="result-summary">${escapeHTML(special.note)}</p><a class="btn btn-light" href="${escapeHTML(special.url)}" target="_blank" rel="noopener noreferrer">Consultar passeio ↗</a></div>`;
   }
   out+=`<p class="result-summary" style="margin-top:14px">${escapeHTML(data.note)}</p><div class="actions-row"><button type="button" class="btn btn-light" id="saveTrip">♡ Salvar na minha conta</button><a class="btn btn-primary" id="waShare" target="_blank" rel="noopener noreferrer">Enviar no WhatsApp</a><button type="button" class="btn btn-light" id="copyTrip">⧉ Copiar roteiro</button></div>`;
   result.innerHTML=out; result.classList.add('show');
   const plain=data.plain_text;
   $('#waShare').href='https://wa.me/?text='+encodeURIComponent(plain);
   $('#copyTrip').addEventListener('click',()=>{(navigator.clipboard?navigator.clipboard.writeText(plain):Promise.reject()).then(()=>toast('Roteiro copiado!'),()=>toast('Não foi possível copiar.'))});
   $('#saveTrip').addEventListener('click',async()=>{if(!window.ExploreAccount.user){toast('Entre na sua conta para salvar roteiros.');openModal();return;}try{await ExploreAccount.api('/api/roteiros-salvos',{method:'POST',body:JSON.stringify({title:'Roteiro · '+data.summary.destination+' · '+data.summary.days+' dia(s)',trip:data})});toast('Roteiro salvo no seu perfil!')}catch(e){toast(e.message)}});
   result.scrollIntoView({behavior:'smooth',block:'start'});
 } catch(error) { toast(error.message||'Erro ao conversar com o servidor.'); }
 finally { submitButton.disabled=false; submitButton.textContent=originalText; }
});

function escapeHTML(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}

// Pesquisa destinos diretamente na API Python, que consulta o banco SQLite.// Pesquisa destinos diretamente na API Python.
const searchInput = $('#destinationSearch');
const searchButton = $('#destinationSearchButton');
const searchResults = $('#searchResults');
// Retoma o destino escolhido na lista de favoritos do perfil.
searchInput.value = new URLSearchParams(location.search).get('q') || '';

let searchTimer;
let activeInterest="";
let currentController = null;
async function searchDestinations() {
    if (!searchInput || !searchResults) return;

    const query = searchInput.value.trim();

    // Cancela uma pesquisa anterior.
    if (currentController) {
        currentController.abort();
    }

    currentController = new AbortController();

    searchResults.innerHTML =
        '<p class="search-status">Consultando destinos...</p>';

    try {
        const response = await fetch(
            '/api/destinos?q=' + encodeURIComponent(query) + '&interest=' + encodeURIComponent(activeInterest) + '&culture=' + encodeURIComponent(new URLSearchParams(location.search).get('culture')||''),
            { signal: currentController.signal }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Falha na pesquisa.');
        }

        window.homePlaces=data.results;
        window.homeMap?.setPlaces(data.results,{includeUnverified:$('#homeLegacy')?.checked});
        document.querySelectorAll('.place').forEach(card=>{
            const name=card.dataset.destination||card.querySelector('h3')?.textContent.trim();
            const place=data.results.find(item=>item.name===name);card.hidden=!place;
            if(place){let badge=card.querySelector('.map-availability');if(!badge){badge=document.createElement('small');badge.className='location-pending map-availability';card.querySelector('.info')?.append(badge);}badge.textContent=place.location.verified?'Localização verificada':place.location.valid?'Localização legada não verificada':'Localização pendente';}
        });
        if (!data.results.length) {
            searchResults.innerHTML =
                '<p class="search-empty">Nenhum destino encontrado. Tente outro nome ou interesse.</p>';
            return;
        }

        searchResults.innerHTML = data.results.map(place => `
<button type="button"
    class="search-result"
    data-place="${escapeHTML(place.name)}"
    data-lat="${escapeHTML(place.latitude ?? place.lat ?? '')}"
    data-lon="${escapeHTML(place.longitude ?? place.lon ?? place.lng ?? '')}">

                <span>${escapeHTML(place.icon)}</span>

                <span>
                    <strong>${escapeHTML(place.name)}</strong>

                    <small>
                        ${escapeHTML(place.municipality)}
                        ·
                        ${escapeHTML((place.interests || []).join(' · '))}
                    </small>

                    <small>
                        ${escapeHTML(place.description)}
                    </small><small>${place.location.verified?'Localiza&#231;&#227;o verificada':place.location.valid?'Localiza&#231;&#227;o legada n&#227;o verificada':'Localiza&#231;&#227;o pendente'}</small>${place.culture_context.length?`<small>${place.culture_context.map(item=>escapeHTML(item.title)).join(' &#183; ')}</small>`:''}
                </span>
            </button>
        `).join('');

    } catch (error) {
        if (error.name === 'AbortError') return;

        searchResults.innerHTML =
            `<p class="search-empty">${escapeHTML(error.message)}. Verifique se o servidor Python está ligado.</p>`;
    }
}

// Pesquisa automaticamente enquanto o usuário digita.
searchInput.addEventListener('input', () => {
    clearTimeout(searchTimer);

    searchTimer = setTimeout(searchDestinations, 250);
});

// Botão de pesquisa.
searchButton.addEventListener('click', searchDestinations);

// Pesquisa ao pressionar Enter.
searchInput.addEventListener('keydown', event => {
    if (event.key === 'Enter') {
        event.preventDefault();
        clearTimeout(searchTimer);
        searchDestinations();
    }
});

// Ao abrir a página, mostra todos os destinos.
searchDestinations();

// Ao clicar em um resultado, foca o destino no mapa.
searchResults.addEventListener('click', event => {
    const item = event.target.closest('[data-place]');

    if (!item) return;

    const name = item.dataset.place;
    const lat = item.dataset.lat;
    const lon = item.dataset.lon;

    const found = window.focusPlace &&
        window.focusPlace(name, lat, lon);

    if (found) {
        if (window.innerWidth <= 850) {
            $('#map').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
    } else {
        toast(
            'A localização está pendente de verificação ou fora dos filtros ativos. Consulte a ficha; referências legadas exigem a opção explícita no mapa.'
        );
    }
});
let isRegister=false;
const modal=$('#loginModal');
function openModal(){modal.classList.add('open');document.querySelectorAll('header, main, footer, .topbar').forEach(element=>element.inert=true);const firstField=isRegister&&$('#accountName').required?$('#accountName'):$('#accountEmail');firstField.focus()}
function closeModal(){if(!modal.classList.contains('open'))return;modal.classList.remove('open');document.querySelectorAll('header, main, footer, .topbar').forEach(element=>element.inert=false);$('#siteMenuToggle').focus()}
document.addEventListener('keydown',event=>{
 if(event.key!=='Tab'||!modal.classList.contains('open'))return;
 const fields=[...modal.querySelectorAll('button,input,a[href]')].filter(element=>!element.disabled&&element.getClientRects().length);
 const first=fields[0],last=fields[fields.length-1];
 if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
 else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
});
if(location.hash==='#entrar')openModal();
$('#loginOpen').addEventListener('click',()=>{if(ExploreAccount.user){location.href='/perfil';return;}openModal()});$('#footerLogin').addEventListener('click',e=>{e.preventDefault();openModal()});$('#modalClose').addEventListener('click',closeModal);modal.addEventListener('click',e=>{if(e.target===modal)closeModal()});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
$('#switchMode').addEventListener('click',()=>{isRegister=!isRegister;$('#modalTitle').textContent=isRegister?'Crie sua conta':'Boas-vindas!';$('#modalDesc').textContent=isRegister?'Comece a organizar suas próximas aventuras.':'Entre para organizar seus planos de viagem.';$('#accountName').style.display=isRegister?'block':'none';$('#accountName').required=isRegister;$('#accountPassword').autocomplete=isRegister?'new-password':'current-password';$('#accountSubmit').textContent=isRegister?'Criar conta':'Entrar';$('#switchMode').textContent=isRegister?'Já tem uma conta? Entrar':'Ainda não tem conta? Cadastre-se'});
$('#accountForm').addEventListener('submit',async e=>{e.preventDefault();const submit=$('#accountSubmit');submit.disabled=true;try{const payload={name:$('#accountName').value,email:$('#accountEmail').value,password:$('#accountPassword').value};await ExploreAccount.auth(isRegister?'register':'login',payload);closeModal();toast('Conta conectada com sucesso!');location.href='/perfil';}catch(err){toast(err.message)}finally{submit.disabled=false}});
const legacyLabel=document.createElement('label');legacyLabel.className='check-row';legacyLabel.innerHTML='<input id="homeLegacy" type="checkbox"> Incluir localizações legadas não verificadas';$('#map').parentElement.after(legacyLabel);
window.homeMap=ExploreMap.create({container:$('#map')});
window.focusPlace=name=>window.homeMap.focus(name);
$('#homeLegacy').onchange=()=>window.homeMap.setPlaces(window.homePlaces||[],{includeUnverified:$('#homeLegacy').checked});
(()=>{
let favs=[];async function loadFavs(){if(!ExploreAccount.user)return;try{const res=await ExploreAccount.api('/api/favoritos');favs=res.results.map(x=>x.name);document.querySelectorAll('.place .fav').forEach(b=>{const name=b.parentElement.dataset.destination||b.parentElement.querySelector('h3')?.textContent.trim();b.classList.toggle('on',favs.includes(name));b.setAttribute('aria-pressed',String(favs.includes(name)))})}catch(e){console.warn(e)}}window.addEventListener('explore-login',loadFavs);
const cards=[...document.querySelectorAll('.place')];
cards.forEach(c=>{const title = c.querySelector('h3');
const info = c.querySelector('div:not(.place-emoji)');

if (!title || !info) return;

const name = c.dataset.destination || title.textContent.trim();
info.classList.add('info');
 const b=document.createElement('button');b.type='button';b.className='fav';b.textContent='♥';
 const sync=()=>{const on=favs.includes(name);b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));b.setAttribute('aria-label',(on?'Remover dos favoritos: ':'Favoritar: ')+name)};sync();
 b.addEventListener('click',async e=>{e.stopPropagation();if(!ExploreAccount.user){toast('Entre na sua conta para favoritar.');openModal();return;}try{const res=await ExploreAccount.api('/api/destinos?q='+encodeURIComponent(name));const item=res.results.find(x=>x.name===name);if(!item)throw Error('Destino não encontrado');const active=favs.includes(name);await ExploreAccount.api('/api/favoritos/'+item.id,{method:active?'DELETE':'PUT'});favs=active?favs.filter(x=>x!==name):[...favs,name];sync();toast(active?'Removido dos favoritos':'Adicionado aos favoritos ♥')}catch(err){toast(err.message)}});
 c.appendChild(b);c.tabIndex=0;c.setAttribute('aria-label','Ver '+name+' no mapa');
 const go=()=>{if(!window.focusPlace?.(name)){toast('Localiza\u00e7\u00e3o pendente ou fora dos filtros ativos. Consulte a ficha do destino.');return;}if(innerWidth<=850)$('#map').scrollIntoView({behavior:'smooth',block:'center'})};
 c.addEventListener('click',go);c.addEventListener('keydown',e=>{if(e.target===c&&(e.key==='Enter'||e.key===' ')){e.preventDefault();go()}});
});loadFavs();const fb = $('#placeFilters');

if (fb) {
    fb.addEventListener('click', e => {
        const f = e.target.closest('.filter');

        if (!f) return;

        fb.querySelectorAll('.filter').forEach(x => {
            x.classList.toggle('active', x === f);
            x.setAttribute('aria-pressed', String(x === f));
        });

        const k = f.dataset.k;
        activeInterest=k;searchDestinations();

        cards.forEach(c => {
            const tag = c.querySelector('.tag');

            c.hidden = !!k && (
                !tag || !tag.textContent.toLowerCase().includes(k)
            );
        });
    });
}

// Observa as seções da página.
const io = new IntersectionObserver(es => {
    es.forEach(en => {
        if (en.isIntersecting) {
            document.querySelectorAll('.links a').forEach(a => {
                a.classList.toggle(
                    'active',
                    a.getAttribute('href') === '#' + en.target.id
                );
            });
        }
    });
}, {
    rootMargin: '-40% 0px -55% 0px'
});

['inicio', 'recursos', 'roteiro', 'explorar'].forEach(id => {
    const s = document.getElementById(id);

    if (s) {
        io.observe(s);
    }
});})();
/* Entradas editoriais do catálogo e preferências aplicadas somente por ação explícita. */
(() => {
 const params=new URLSearchParams(location.search), municipality=params.get('municipality');
 if(municipality && [...document.querySelector('#destination').options].some(option=>option.value===municipality)) document.querySelector('#destination').value=municipality;
 const themes={historia:'História',reggae:'Cultura',sabores:'Gastronomia',popular:'Cultura',quilombo:'Cultura'};
 const selected=themes[params.get('theme')];
 if(selected)document.querySelectorAll('input[name=interest]').forEach(input=>input.checked=input.value===selected);
 document.querySelector('#useAccessPreferences').onclick=()=>{
  const profile=ExploreAccount.profile;
  if(!profile?.access_consent){toast('Autorize suas preferências nas configurações antes de usá-las.');return;}
  const labels={mobility:'Mobilidade reduzida',visual:'Deficiência visual',hearing:'Deficiência auditiva',cognitive:'Intelectual / cognitiva',sensory:'Necessidades sensoriais'};
  document.querySelectorAll('input[name=access]').forEach(input=>{if(input.value!=='Crianças')input.checked=profile.access_preferences.some(key=>labels[key]===input.value);});
  toast('Preferências aplicadas. Os locais ainda precisam ter os recursos confirmados.');
 };
 const heading=document.querySelector('#explorar .section-head');
 if(heading){const link=document.createElement('a');link.href='/catalogo';link.className='btn btn-light';link.textContent='Ver catálogo completo ↗';heading.after(link);}
})();
