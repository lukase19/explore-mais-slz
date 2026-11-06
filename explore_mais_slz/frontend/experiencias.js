window.ExploreFeatures = (() => {
 const $=s=>document.querySelector(s);
 const h=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const api=(path,method='GET',data)=>ExploreAccount.api(path,{method,...(data===undefined?{}:{body:JSON.stringify(data)})});
 const box=html=>$('#featureBody').innerHTML=html;
 const groupLabels={mobility:'Mobilidade / cadeira de rodas',visual:'Deficiência visual',hearing:'Deficiência auditiva',cognitive:'Intelectual / cognitiva',sensory:'Necessidades sensoriais'};
 const states={confirmed:'Confirmado',unavailable:'Não disponível',unverified:'Informação ainda não verificada'};
 const safeURL=value=>typeof value==='string'&&value.startsWith('https://')?value:'#';
 let noticeTimer;
 function notice(message){$('#featureNotice').textContent=message;clearTimeout(noticeTimer);noticeTimer=setTimeout(()=>$('#featureNotice').textContent='',5000);}
 function heading(title,subtitle){$('#featureTitle').textContent=title;$('#featureSubtitle').textContent=subtitle;document.title=title+' · Explore+ SLZ';}
 const check=(key,label,value=false)=>`<label class="check-row"><input type="checkbox" name="${key}" ${value?'checked':''}><span>${label}</span></label>`;
 const people=person=>`<div class="person-copy">${person.avatar_url?`<img src="${h(person.avatar_url)}" alt="" loading="lazy">`:`<span class="person-initial" aria-hidden="true">${h(Array.from(person.name)[0])}</span>`}<div><strong>${h(person.name)}</strong><small>@${h(person.handle)}</small><a class="text-link" href="/p/${encodeURIComponent(person.handle)}">Ver perfil</a></div></div>`;
 async function action(button,fn,message='Alteração salva.',refresh=true){button.disabled=true;try{await fn();notice(message);if(refresh)await F.reload();return true;}catch(error){notice(error.message);return false;}finally{if(button.isConnected)button.disabled=false;}}
 const values=form=>Object.fromEntries(new FormData(form));
 const date=value=>value?new Date(value.includes('T')?value:value.replace(' ','T')+'Z').toLocaleDateString('pt-BR'):'';
 const tripHTML=trip=>`${(Array.isArray(trip?.days)?trip.days:[]).map(day=>`<section><h3>${h(day?.title)}</h3>${(Array.isArray(day?.stops)?day.stops:[]).map(stop=>`<p><b>${h(stop?.icon)} ${h(stop?.name)}</b> — ${h(stop?.description)}</p>`).join('')}</section>`).join('')}<p class="notice">${h(trip?.note||'Confirme custos, horários e acessibilidade. Não há validação de trajeto.')}</p>`;
 const catalogCard=(place,withMap=false,legacy=false)=>`<article class="catalog-card"><img src="/destination-fallback.svg" alt="" loading="lazy"><div class="catalog-copy"><span class="eyebrow-text">${h(place.municipality)} · ${h(place.category)}</span><h2>${h(place.name)}</h2><p>${h(place.description)}</p>${place.culture_context?.length?`<div class="culture-topics">${place.culture_context.map(item=>`<span class="culture-topic">${h(item.title)}</span>`).join('')}</div><p class="culture-summary">${h(place.culture_context[0].text.slice(0,170))}…</p>`:''}<span class="location-pending">${place.location?.verified?'Localiza&#231;&#227;o verificada':place.location?.valid?'Localiza&#231;&#227;o legada ainda n&#227;o verificada':'Localiza&#231;&#227;o pendente: sem coordenadas v&#225;lidas'}</span>${withMap?`<button class="btn btn-light" type="button" data-map-id="${place.id}" ${place.location?.verified||(legacy&&place.location?.valid)?'':'disabled'}>Ver no mapa</button>`:''}<small class="review-label">${place.source_url?'Existência documentada · ficha em revisão':'Registro anterior · verificação pendente'}</small><a class="btn btn-light" href="/destino/${place.id}">Conhecer o lugar ↗</a></div></article>`;
 const F={$,h,api,box,groupLabels,states,safeURL,notice,heading,check,people,action,values,date,tripHTML,catalogCard};
 let loading=false;
 F.reload=async()=>{
  if(loading)return;loading=true;$('#featureBody').setAttribute('aria-busy','true');
  const path=location.pathname;
  try{
   const publicRoute=path==='/catalogo'||path==='/cultura'||path.startsWith('/destino/')||path.startsWith('/p/')||path.startsWith('/s/');
   if(!publicRoute&&!ExploreAccount.user){heading('Seu espaço de encontros.','Entre para organizar seus planos com privacidade.');box('<section class="feature-card"><p>Crie sua conta ou entre para continuar.</p><a class="btn btn-primary" href="/#entrar">Entrar ou criar conta</a></section>');return;}
   if(path==='/catalogo')await F.catalog();
   else if(path==='/cultura')await F.culture();
   else if(path==='/configuracoes')await F.settings();
   else if(path==='/amigos')await F.friends();
   else if(path==='/presentes')await F.gifts();
   else if(path.startsWith('/destino/'))await F.detail(Number(path.split('/')[2]));
   else if(path.startsWith('/roteiro-compartilhado/'))await F.collaborate(Number(path.split('/')[2]));
   else if(path.startsWith('/p/'))await F.publicProfile(decodeURIComponent(path.split('/')[2]));
   else if(path.startsWith('/s/')){const data=await api('/api/shared/'+encodeURIComponent(path.split('/')[2]));heading(data.title,'Leitura compartilhada pelo proprietário. Este link não autoriza alterações.');box(`<section class="feature-card">${tripHTML(data.trip)}</section><a class="btn btn-primary" href="/planejar#roteiro">Criar meu roteiro</a>`);}
  }catch(error){box(`<section class="feature-card"><h2>Não foi possível abrir este conteúdo</h2><p role="alert">${h(error.message)}</p><p>Conteúdos privados só aparecem para quem tem permissão.</p><button id="featureRetry" class="btn btn-light">Tentar novamente</button></section>`);$('#featureRetry').onclick=()=>ExploreAccount.sessionError?ExploreAccount.init():F.reload();}
  finally{loading=false;$('#featureBody').setAttribute('aria-busy','false');}
 };
 window.addEventListener('explore-login',()=>F.reload());return F;
})();
