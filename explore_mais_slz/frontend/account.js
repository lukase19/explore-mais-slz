window.ExploreAccount = {
 user: null, profile: null, csrf: null, sessionError: false,
 applyTheme(theme) {
  const selected=['forest','ocean','sunset'].includes(theme)?theme:'forest';
  document.documentElement.dataset.theme=selected;document.body.dataset.theme=selected;
  this.preference('explore-theme',selected);
 },
 preference(key, value) {
  try { if (value !== undefined) localStorage.setItem(key, String(value)); return localStorage.getItem(key); }
  catch (_) { return null; }
 },
 applyPreferences() {
  const size = Number(this.preference('explore-font') || 100);
  document.documentElement.style.fontSize = Math.max(85, Math.min(145, Number.isFinite(size) ? size : 100)) + '%';
  document.body.classList.toggle('high-contrast', this.preference('explore-contrast') === '1');
 },
 async api(path, options = {}) {
  const headers = {...(options.body instanceof FormData ? {} : {'Content-Type':'application/json'}), ...(options.headers || {})};
  if (this.csrf && options.method && options.method !== 'GET') headers['X-CSRF-Token'] = this.csrf;
  const response = await fetch(path, {credentials:'same-origin', ...options, headers});
  const data = await response.json().catch(() => { throw Error('O servidor retornou uma resposta inválida. Tente novamente.'); });
  if (!response.ok) throw Error(data.error || 'Falha ao comunicar com o servidor.');
  return data;
 },
 async init() {
  try {
   const result = await this.api('/api/auth/me');
   this.user = result.user; this.csrf = result.csrf; this.sessionError = false;
   this.profile = this.user ? (await this.api('/api/profile-settings')).profile : null;
   this.applyTheme(this.profile?.theme || 'forest');
   this.updateUI();
  } catch (error) { this.sessionError = true; console.warn('Sessão não disponível', error); }
  finally { window.dispatchEvent(new Event('explore-login')); }
 },
 async auth(mode, payload) {
  const result = await this.api('/api/auth/' + mode, {method:'POST', body:JSON.stringify(payload)});
  this.user = result.user; this.csrf = result.csrf; this.sessionError = false;
  this.profile = (await this.api('/api/profile-settings')).profile; this.applyTheme(this.profile.theme); this.updateUI();
  window.dispatchEvent(new Event('explore-login')); return result;
 },
 async logout() {
  await this.api('/api/auth/logout', {method:'POST'});
  this.user = null; this.profile = null; this.csrf = null; this.applyTheme('forest'); this.updateUI(); location.href = '/';
 },
 updateUI() {
  const button = document.querySelector('#loginOpen');
  if (button) button.textContent = this.user ? 'Olá, ' + this.user.name.split(' ')[0] : 'Entrar';
  const shortcut = document.querySelector('#profileShortcut');
  if (shortcut) shortcut.title = this.user ? 'Abrir perfil de ' + this.user.name : 'Meu perfil (entre ou cadastre-se)';
 }
};
document.addEventListener('DOMContentLoaded', () => { ExploreAccount.applyPreferences(); ExploreAccount.init(); });
