/* Antecipação visual; a sessão confirma o tema e limpa o cache ao sair. */
try{const theme=localStorage.getItem('explore-theme');if(['forest','ocean','sunset'].includes(theme))document.documentElement.dataset.theme=theme;}catch(_){}
