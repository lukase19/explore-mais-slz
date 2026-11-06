(() => {
 const F=ExploreFeatures,{$,h,api,box,heading,check,action,values,notice,groupLabels}=F;
 F.settings=async()=>{
  heading('Seu jeito de explorar.','Foto, capa, privacidade e preferências. Você escolhe o que compartilhar.');
  const {profile:p}=await api('/api/profile-settings');
  box(`<section class="feature-card"><h2>Foto e capa</h2><p class="muted">JPEG, PNG ou WebP, até 4 MB e 16 megapixels. As imagens são recodificadas e os metadados removidos. Imagens privadas só aparecem para você e amigos aceitos.</p>${['avatar','cover'].map(kind=>`<div class="media-editor"><div><img id="preview-${kind}" class="media-preview ${kind==='cover'?'cover-preview':''}" src="${h(p[kind+'_url']||'/destination-fallback.svg')}" alt="Prévia ${kind==='avatar'?'da foto de perfil':'da capa'}" style="object-position:${p[kind+'_x']}% ${p[kind+'_y']}%"></div><div class="settings-column"><form class="feature-form" data-upload="${kind}"><label>${kind==='avatar'?'Trocar foto de perfil':'Trocar imagem de capa'}<input type="file" name="image" accept="image/jpeg,image/png,image/webp" aria-describedby="state-${kind} filename-${kind}" required></label><p id="filename-${kind}" class="muted">Nenhum arquivo novo selecionado.</p><p id="state-${kind}" class="media-state" data-state="${p[kind+'_url']?'current':'empty'}" role="status">${p[kind+'_url']?'Imagem atual salva e exibida.':'Nenhuma imagem salva. A ilustra&#231;&#227;o &#233; o padr&#227;o.'}</p><button class="btn btn-light" type="submit" disabled>Enviar e salvar ${kind==='avatar'?'foto':'capa'}</button><a class="text-link" href="/perfil">Conferir no meu perfil</a></form><button class="text-button" data-remove-media="${kind}" ${p[kind+'_url']?'':'disabled'}>Remover ${kind==='avatar'?'foto':'capa'}</button></div></div>`).join('<hr>')}</section><form id="settingsForm" class="feature-form"><section class="feature-card"><h2>Identidade e aparência</h2><label>Nome de exibição<input name="name" minlength="2" maxlength="100" value="${h(ExploreAccount.user.name)}" required autocomplete="name"></label><label>@usuario único<input name="handle" minlength="3" maxlength="30" pattern="[a-zA-Z][a-zA-Z0-9_]{2,29}" value="${h(p.handle)}" required></label><label>Biografia<textarea name="bio" maxlength="500">${h(p.bio)}</textarea></label><label>Município (opcional)<input name="municipality" maxlength="80" value="${h(p.municipality)}"></label><label>Interesses, separados por vírgula<input name="interests" value="${h((ExploreAccount.user.interests||[]).join(', '))}"></label><label>Tema de cores<select name="theme">${[['forest','Verde da Ilha'],['ocean','Azul da baía'],['sunset','Pôr do sol']].map(([key,label])=>`<option value="${key}" ${p.theme===key?'selected':''}>${label}</option>`).join('')}</select></label><fieldset><legend>Reposicionar imagens</legend>${['avatar','cover'].map(kind=>`<label>${kind==='avatar'?'Foto':'Capa'}: horizontal<input type="range" name="${kind}_x" min="0" max="100" value="${p[kind+'_x']}"></label><label>${kind==='avatar'?'Foto':'Capa'}: vertical<input type="range" name="${kind}_y" min="0" max="100" value="${p[kind+'_y']}"></label>`).join('')}</fieldset></section><section class="feature-card"><h2>Privacidade e amizades</h2>${check('is_public','Permitir que qualquer pessoa abra meu perfil público',p.is_public)}${check('discoverable','Permitir que usuários conectados me encontrem pelo nome ou @usuario',p.discoverable)}${check('allow_invites','Receber solicitações, convites de amigos e vouchers simbólicos',p.allow_invites)}<label>Quem vê meus favoritos?<select name="favorites_visibility">${[['private','Somente eu'],['friends','Amigos aceitos'],['public','Quem tiver acesso ao meu perfil']].map(([key,label])=>`<option value="${key}" ${p.favorites_visibility===key?'selected':''}>${label}</option>`).join('')}</select></label><p class="notice">E-mail e histórico são privados. Perfil público não publica histórico ou roteiros. Amigos aceitos podem abrir seu perfil. Links de roteiro só são publicados por ação explícita.</p></section><section class="feature-card"><h2>Preferências opcionais de acessibilidade</h2><p>Não exigimos diagnóstico. Estas preferências são privadas e nunca aparecem no perfil público.</p>${check('access_consent','Autorizo salvar e usar estas preferências para sugerir filtros e preencher o planejador quando eu solicitar.',p.access_consent)}${Object.entries(groupLabels).map(([key,label])=>`<label class="check-row"><input type="checkbox" name="access_preferences" value="${key}" ${p.access_preferences.includes(key)?'checked':''}>${label}</label>`).join('')}<p class="muted">Desmarcar a autorização apaga as preferências salvas. Dados desconhecidos nunca são tratados como acessibilidade confirmada.</p><a class="text-link" href="/acessibilidade">Ajustar texto e contraste ↗</a></section><button class="btn btn-primary" type="submit">Salvar configurações</button></form>`);
  const previews=new Map();
  document.querySelectorAll('[data-upload]').forEach(form=>{
   const kind=form.dataset.upload,input=form.elements.image,preview=$('#preview-'+kind),button=form.querySelector('button'),state=$('#state-'+kind),filename=$('#filename-'+kind);
   const setState=(value,message)=>{state.dataset.state=value;state.textContent=message;};
   const revoke=()=>{if(previews.has(kind)){URL.revokeObjectURL(previews.get(kind));previews.delete(kind);}};
   input.onchange=()=>{
    const file=input.files[0];revoke();
    if(!file){preview.src=ExploreAccount.profile[kind+'_url']||'/destination-fallback.svg';button.disabled=true;filename.textContent='Nenhum arquivo novo selecionado.';setState('current','Imagem atual exibida.');return;}
    filename.textContent=file.name;
    if(file.size>4*1024*1024||!['image/jpeg','image/png','image/webp'].includes(file.type)){preview.src=ExploreAccount.profile[kind+'_url']||'/destination-fallback.svg';button.disabled=true;setState('error','Arquivo não enviado. Use JPEG, PNG ou WebP de até 4 MB.');return;}
    const url=URL.createObjectURL(file);previews.set(kind,url);preview.src=url;button.disabled=false;setState('selected','Arquivo selecionado. A prévia ainda não foi enviada nem salva.');
   };
   form.onsubmit=async event=>{
    event.preventDefault();if(!input.files[0])return;
    const file=input.files[0],original=button.textContent,removeButton=document.querySelector('[data-remove-media="'+kind+'"]');removeButton.disabled=true;
    button.disabled=true;input.disabled=true;setState('uploading','Enviando e validando a imagem…');button.textContent='Enviando…';
    try{
     const data=new FormData();data.append('image',file);
     const result=await ExploreAccount.api('/api/profile-media/'+kind,{method:'POST',body:data});
     ExploreAccount.profile[kind+'_url']=result.url;preview.src=result.url;revoke();input.value='';
     setState('saved','Imagem salva com sucesso. Esta é a imagem atual do seu perfil.');filename.textContent='Salvo: '+file.name;
     const remove=document.querySelector('[data-remove-media="'+kind+'"]');remove.disabled=false;
     window.dispatchEvent(new Event('explore-profile-updated'));
     preview.decode().catch(()=>setState('error','Imagem salva, mas a prévia não carregou. Recarregue a página para conferir.'));
    }catch(error){setState('error','Erro ao salvar: '+error.message+' A imagem anterior foi mantida.');}
    finally{input.disabled=false;button.textContent=original;button.disabled=!input.files[0];removeButton.disabled=!ExploreAccount.profile[kind+'_url'];}
   };
  });
  document.querySelectorAll('[data-remove-media]').forEach(button=>button.onclick=async()=>{
   const kind=button.dataset.removeMedia;button.disabled=true;
   try{await api('/api/profile-media/'+kind,'DELETE');delete ExploreAccount.profile[kind+'_url'];const form=document.querySelector('[data-upload="'+kind+'"]');form.reset();form.querySelector('button').disabled=true;const url=previews.get(kind);if(url)URL.revokeObjectURL(url);previews.delete(kind);$('#preview-'+kind).src='/destination-fallback.svg';$('#filename-'+kind).textContent='Nenhum arquivo novo selecionado.';$('#state-'+kind).dataset.state='empty';$('#state-'+kind).textContent='Imagem removida. O perfil usa a imagem padrão.';window.dispatchEvent(new Event('explore-profile-updated'));}
   catch(error){$('#state-'+kind).dataset.state='error';$('#state-'+kind).textContent='Erro ao remover: '+error.message;button.disabled=false;}
  });
  window.addEventListener('pagehide',()=>{for(const url of previews.values())URL.revokeObjectURL(url);},{once:true});
  $('#settingsForm').oninput=()=>{const form=$('#settingsForm');for(const kind of ['avatar','cover'])$('#preview-'+kind).style.objectPosition=`${form.elements[kind+'_x'].value}% ${form.elements[kind+'_y'].value}%`;};
  $('#settingsForm').onsubmit=event=>{
   event.preventDefault();const form=event.target,data=values(form),interests=data.interests.split(',').map(item=>item.trim()).filter(Boolean);
   if(interests.length>12||interests.some(item=>item.length>40)){notice('Use até 12 interesses de até 40 caracteres.');return;}
   for(const key of ['is_public','discoverable','allow_invites','access_consent'])data[key]=form.elements[key].checked;
   data.access_preferences=[...form.querySelectorAll('[name=access_preferences]:checked')].map(input=>input.value);
   for(const key of ['avatar_x','avatar_y','cover_x','cover_y'])data[key]=Number(data[key]);
   data.interests=interests;
   action(event.submitter,async()=>{const result=await api('/api/profile-settings','PATCH',data);ExploreAccount.profile=result.profile;ExploreAccount.user.name=data.name.trim();ExploreAccount.user.interests=interests;ExploreAccount.applyTheme(result.profile.theme);ExploreAccount.updateUI();window.dispatchEvent(new Event('explore-profile-updated'));},'Configurações salvas.',false);
  };
 };
 F.publicProfile=async handle=>{
  const {profile:p}=await api('/api/public-profile/'+encodeURIComponent(handle));heading(p.name,'@'+p.handle+(p.municipality?' · '+p.municipality:''));
  box(`<section class="feature-card">${p.cover_url?`<div class="profile-cover"><img src="${h(p.cover_url)}" alt="" style="object-position:${p.cover_x}% ${p.cover_y}%"></div>`:''}${p.avatar_url?`<img class="public-avatar" src="${h(p.avatar_url)}" alt="Foto de ${h(p.name)}" style="object-position:${p.avatar_x}% ${p.avatar_y}%">`:''}<p>${h(p.bio||'Uma pessoa pronta para descobrir a região.')}</p><p class="notice">E-mail, histórico e preferências de acessibilidade são privados.</p></section><h2>Favoritos compartilhados</h2>${p.favorites===null?'<p>Esta pessoa mantém seus favoritos privados.</p>':`<div class="catalog-grid">${p.favorites.map(place=>F.catalogCard(place)).join('')||'<p>Nenhum favorito compartilhado.</p>'}</div>`}`);
 };
})();
