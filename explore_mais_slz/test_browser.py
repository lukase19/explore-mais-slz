"""Teste opcional de interface: pip install playwright; python test_browser.py.
Usa o Chrome instalado e um SQLite temporário. Não baixa outro navegador.
"""
import importlib
import os
from pathlib import Path
import tempfile
from threading import Thread
from werkzeug.serving import make_server, WSGIRequestHandler


class QuietHandler(WSGIRequestHandler):
    def log(self, *args, **kwargs):
        pass


def main():
    from playwright.sync_api import sync_playwright, expect

    with tempfile.TemporaryDirectory(prefix='explore-browser-') as directory:
        os.environ['EXPLORE_DATABASE_PATH'] = str(Path(directory) / 'browser.sqlite')
        backend = importlib.import_module('backend.app')
        server = make_server('127.0.0.1', 0, backend.app, request_handler=QuietHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        artifacts = Path('.artifacts')
        artifacts.mkdir(exist_ok=True)
        errors = []
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel='chrome', headless=True)
                context = browser.new_context(viewport={'width':1440,'height':1000}, locale='pt-BR', timezone_id='America/Fortaleza')
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: print('HTTP', response.status, response.url, flush=True) if response.status >= 400 and '/api/' in response.url else None)
                # As funcionalidades locais também devem funcionar sem o CDN do mapa.
                page.route('**.tile.openstreetmap.org/**', lambda route: route.abort())

                def loaded(path):
                    page.goto(base + path)
                    expect(page.locator('#pageBody')).to_have_attribute('aria-busy','false')

                def screenshot(name):
                    page.evaluate("scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(artifacts / name), full_page=True)

                loaded('/perfil')
                page.get_by_role('link', name='Entrar ou criar conta').click()
                expect(page.locator('#loginModal')).to_have_class('modal open')
                page.locator('#switchMode').click()
                page.locator('#switchMode').press('Tab')
                expect(page.locator('#modalClose')).to_be_focused()
                page.locator('#accountName').fill('Ana Silva')
                page.locator('#accountEmail').fill('ana@example.test')
                page.locator('#accountPassword').fill('senha-forte-123')
                page.locator('#accountSubmit').click()
                page.wait_for_url(base + '/perfil')
                expect(page.locator('#pageBody')).to_have_attribute('aria-busy','false')
                expect(page.get_by_text('Seu próximo lugar favorito', exact=True)).to_be_visible()
                screenshot('perfil-vazio.png')
                page.locator('#profileName').fill('Ana Viajante')
                page.locator('#profileInterests').fill('Praias, Cultura')
                page.get_by_role('button', name='Salvar alterações').click()
                expect(page.locator('#welcomeName')).to_have_text('Ana Viajante')
                page.reload()
                expect(page.locator('#profileName')).to_have_value('Ana Viajante')

                page.goto(base + '/explorar#explorar')
                page.wait_for_function('ExploreAccount.user !== null && ExploreAccount.csrf !== null')
                expect(page.locator('.place .fav')).to_have_count(6)
                page.locator('.place').filter(has=page.get_by_role('heading', name='Centro Histórico', exact=True)).locator('.fav').click()
                try:
                    expect(page.locator('.place').filter(has=page.get_by_role('heading', name='Centro Histórico', exact=True)).locator('.fav')).to_have_attribute('aria-pressed','true')
                except AssertionError:
                    print('Toast:', page.locator('#toast').inner_text(), 'JS:', errors, flush=True)
                    raise
                page.locator('.place[data-destination]').locator('.fav').click()
                expect(page.locator('.place[data-destination] .fav')).to_have_attribute('aria-pressed','true')
                page.locator('#destination').select_option('Raposa')
                page.locator('#budget').fill('800')
                page.locator('#days').select_option('2')
                page.locator('label.chip').filter(has=page.locator('input[name=interest][value=Natureza]')).click()
                page.locator('#tripForm button[type=submit]').click()
                page.locator('#saveTrip').click()
                expect(page.locator('#toast')).to_have_text('Roteiro salvo no seu perfil!')
                loaded('/perfil')
                expect(page.locator('.favorite-card')).to_have_count(2)
                expect(page.locator('.trip-card')).to_have_count(1)
                expect(page.locator('.activity-list li')).to_have_count(4)
                page.get_by_role('button', name='Ver detalhes').click()
                expect(page.locator('.trip-detail')).to_be_visible()
                expect(page.locator('.trip-detail')).to_contain_text('Dia 1')
                page.get_by_role('button', name='Fechar detalhes').click()
                screenshot('perfil-desktop.png')
                # A visão geral precisa preservar conteúdos seguros, mesmo com nomes HTML.
                page.locator('#profileName').fill('<img src=x onerror=alert(1)>')
                page.get_by_role('button', name='Salvar alterações').click()
                expect(page.locator('#welcomeName')).to_have_text('<img src=x onerror=alert(1)>')
                expect(page.locator('#welcomeName img')).to_have_count(0)
                page.locator('#profileName').fill('Ana Viajante')
                page.get_by_role('button', name='Salvar alterações').click()
                expect(page.locator('#welcomeName')).to_have_text('Ana Viajante')
                for width in (390, 320, 768):
                    page.set_viewport_size({'width':width,'height':844})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow: {width}'
                page.set_viewport_size({'width':390,'height':844})
                screenshot('perfil-celular.png')
                loaded('/acessibilidade')
                page.get_by_role('button', name='Alternar alto contraste').click()
                page.get_by_role('button', name='Aumentar texto').click()
                loaded('/perfil')
                expect(page.locator('body')).to_have_class('high-contrast')
                assert page.evaluate('document.documentElement.style.fontSize') == '110%'
                assert page.locator('#welcomeName').evaluate("element => getComputedStyle(element).color") == 'rgb(255, 255, 255)'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                screenshot('perfil-contraste.png')
                page.once('dialog', lambda dialog: dialog.accept())
                page.get_by_role('button', name='Excluir Roteiro').click()
                expect(page.locator('.trip-card')).to_have_count(0)
                page.locator('[data-remove-fav]').first.click()
                expect(page.locator('.favorite-card')).to_have_count(1)
                loaded('/historico')
                page.once('dialog', lambda dialog: dialog.accept())
                page.get_by_role('button', name='Limpar histórico').click()
                expect(page.locator('.activity-list')).to_have_count(0)
                page.locator('#siteMenuToggle').click()
                page.locator('#logoutBtn').click()
                page.wait_for_url(base + '/')
                loaded('/perfil')
                expect(page.get_by_role('link', name='Entrar ou criar conta')).to_be_visible()
                page.route('**/api/auth/me', lambda route: route.abort())
                loaded('/perfil')
                expect(page.get_by_role('button', name='Tentar novamente')).to_be_visible()
                page.unroute('**/api/auth/me')
                page.get_by_role('button', name='Tentar novamente').click()
                expect(page.get_by_role('link', name='Entrar ou criar conta')).to_be_visible()
                assert not errors, errors
                browser.close()
                print('OK: cadastro, perfil, favoritos, roteiro, exclusões, histórico, contraste, sessão e layouts 1440/768/390/320px; nenhum erro JavaScript.')
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()


if __name__ == '__main__':
    main()
