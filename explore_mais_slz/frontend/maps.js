/* Uma camada por conjunto filtrado. O agrupamento conserva cada destino. */
window.ExploreMap = (() => {
 const h=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function create({container,status}){
  if(!container)return null;
  if(!status){status=document.createElement('p');status.className='map-status';status.setAttribute('role','status');container.parentElement.after(status);}
  if(!window.L){container.textContent='Não foi possível iniciar o mapa. Os destinos continuam disponíveis na lista.';status.textContent='Mapa indisponível. Consulte as fichas pela lista.';return {setPlaces(){},focus(){return false;},destroy(){},snapshot(){return {ids:[],count:0,available:false};}};}
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const map=L.map(container,{scrollWheelZoom:false,maxZoom:19,zoomAnimation:!reduced}).setView([-2.53,-44.2],10);
  const emptyNote=document.createElement('div');emptyNote.className='map-empty-note';container.append(emptyNote);
  let tileFailed=false,places=[],includeUnverified=false,selected=null;
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors',maxZoom:19}).on('tileerror',()=>{if(!tileFailed){tileFailed=true;updateStatus();}}).addTo(map);
  const markers=new Map();
  const icon=(place,selected=false)=>L.divIcon({className:'destination-pin'+(place.location.verified?'':' pending-pin')+(selected?' selected-pin':''),html:`<span data-destination-id="${place.id}" aria-hidden="true">●</span>`,iconSize:[28,36],iconAnchor:[14,32]});
  const group=L.markerClusterGroup?L.markerClusterGroup({maxClusterRadius:45,showCoverageOnHover:false,removeOutsideVisibleBounds:false,spiderfyOnMaxZoom:true,animate:!reduced,iconCreateFunction:cluster=>{
   const ids=cluster.getAllChildMarkers().map(marker=>marker.options.destinationId);
   return L.divIcon({className:'map-cluster',html:`<span data-cluster-ids="${ids.join(',')}" aria-label="${ids.length} destinos agrupados">${ids.length}</span>`,iconSize:[40,40]});
  }}):L.featureGroup();
  group.addTo(map);
  function eligible(p){return p.location?.verified===true||(includeUnverified&&p.location?.valid===true);}
  function updateStatus(){
   const verified=places.filter(p=>p.location?.verified).length,legacy=places.filter(p=>p.location?.valid&&!p.location?.verified).length;
   status.textContent=`${places.length} destino(s) nos filtros · ${verified} localização(ões) verificada(s) · ${markers.size} representado(s) no mapa, incluindo agrupamentos. ${legacy} registro(s) com coordenadas legadas não verificadas; ${places.filter(p=>!p.location?.valid).length} sem coordenadas válidas.`+(includeUnverified?' Você incluiu localizações não verificadas.':' Locais pendentes continuam na lista; apenas os verificados aparecem por padrão.')+(tileFailed?' As imagens de fundo não carregaram. Os marcadores e a lista continuam disponíveis.':'');
   emptyNote.hidden=markers.size>0;
   emptyNote.textContent=places.length?(includeUnverified?'Sem coordenadas válidas nestes filtros. Os destinos continuam na lista.':'Localizações aguardando verificação. Os destinos continuam na lista.'):'Nenhum destino corresponde aos filtros.';
  }
  const controller={map,group,
   setPlaces(data,options={}){
    places=data;includeUnverified=options.includeUnverified===true;if(selected)map.removeLayer(selected);selected=null;group.clearLayers();markers.clear();
    for(const place of places){
     if(!eligible(place))continue;
     // Defesa adicional: nunca converter null, vazio, booleano ou texto em zero.
     const lat=place.latitude,lon=place.longitude;
     if(typeof lat!=='number'||typeof lon!=='number'||!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)continue;
     const marker=L.marker([lat,lon],{destinationId:place.id,title:place.name+(place.location.verified?'':' — localização não verificada'),icon:icon(place)});
     marker.bindPopup(`<strong>${h(place.name)}</strong><p>${h(place.municipality)}</p>${place.location.verified?'':'<p>Localização legada não verificada.</p>'}<a href="/destino/${place.id}">Conhecer o destino</a>`,{autoPan:false});
     group.addLayer(marker);markers.set(place.id,{marker,place});
    }
    map.invalidateSize();if(markers.size)map.fitBounds(L.latLngBounds([...markers.values()].map(item=>item.marker.getLatLng())),{padding:[35,35],maxZoom:14,animate:false});updateStatus();
   },
   focus(idOrName){
    const item=markers.get(Number(idOrName))||[...markers.values()].find(item=>item.place.name===idOrName);
    if(!item)return false;
    const reveal=()=>{
     if(selected)map.removeLayer(selected);
     // A seleção é uma camada estável, independente dos ícones recriados pelo agrupador.
     map.setView(item.marker.getLatLng(),map.getZoom(),{animate:false});
     selected=L.circleMarker(item.marker.getLatLng(),{radius:12,weight:3,className:'selected-pin selection-ring',interactive:false}).addTo(map);
     selected.bindPopup(item.marker.getPopup().getContent(),{autoPan:false}).openPopup();
    };
    if(group.zoomToShowLayer)group.zoomToShowLayer(item.marker,reveal);else{map.setView(item.marker.getLatLng(),16,{animate:!reduced});reveal();}return true;
   },
   snapshot(){return {ids:group.getLayers().map(marker=>marker.options.destinationId).sort((a,b)=>a-b),count:group.getLayers().length,available:true};},
   destroy(){resize.disconnect();map.remove();}
  };
  const resize=new ResizeObserver(()=>map.invalidateSize());resize.observe(container);
  updateStatus();return controller;
 }
 return {create};
})();
