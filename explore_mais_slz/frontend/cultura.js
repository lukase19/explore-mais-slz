/* Reutilização do conteúdo cultural nas descobertas e nas fichas. */
(() => {
 const F=ExploreFeatures,{h}=F;
 F.cultureContext=item=>`<article class="cultural-context"><span class="eyebrow-text">${h(item.kind)}</span><h3>${h(item.icon)} ${h(item.title)}</h3><p>${h(item.text)}</p><a class="text-link" href="${h(F.safeURL(item.source_url))}" target="_blank" rel="noopener noreferrer">Fonte e contexto cultural ↗</a><p class="muted">Referência editorial, sem agenda ou promessa de apresentação neste local.</p></article>`;
 F.cultureDiscovery=items=>`<section class="feature-card" id="cultura"><h2>Cultura que acompanha a descoberta</h2><p>Tradições e manifestações se conectam a espaços reais. Sem local associado, permanecem referências culturais, sem um ponto geográfico artificial.</p><details><summary>Conhecer histórias, música, gastronomia e tradições</summary>${items.map(F.cultureContext).join('')}</details></section>`;
 F.culture=()=>F.catalog();
})();
