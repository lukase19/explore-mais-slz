"""Verifica mapa Leaflet real, temas e estados de upload. Dados só em SQLite temporário."""
import importlib
from datetime import datetime
from io import BytesIO
import json
import os
from pathlib import Path
import tempfile
from threading import Thread
from werkzeug.serving import make_server
from test_browser import QuietHandler


def main():
    from PIL import Image
    from playwright.sync_api import sync_playwright, expect
    with tempfile.TemporaryDirectory(prefix='slz-corrections-') as directory:
        os.environ['EXPLORE_DATABASE_PATH']=str(Path(directory)/'browser.sqlite')
        backend=importlib.import_module('backend.app')
        # Fixtures explicitamente de teste: não verificam nem alteram pontos da base normal.
        with backend.get_connection() as con:
            con.execute("UPDATE destinos SET coordinates_status='verified' WHERE id=1")
            for index in range(40):
                con.execute("INSERT INTO destinos(nome,municipio,descricao,icone,interesses,latitude,longitude,category,coordinates_status) VALUES (?,?,?,?,?,?,?,?,?)",(f'Ponto de teste {index:02d}','São Luís','Fixture de teste do agrupamento.','x','["História"]',-2.5297+index*0.00001,-44.3068,'Praça','verified'))
        server=make_server('127.0.0.1',0,backend.app,request_handler=QuietHandler)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}';artifacts=Path('.artifacts');artifacts.mkdir(exist_ok=True)
        errors=[]
        try:
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch(channel='chrome',headless=True)
                context=browser.new_context(viewport={'width':1440,'height':1000},locale='pt-BR',timezone_id='America/Fortaleza',reduced_motion='reduce')
                registration=context.request.post(base+'/api/auth/register',data={'name':'Pessoa de teste','email':'teste@example.test','password':'senha-forte-123'}).json()
                headers={'X-CSRF-Token':registration['csrf']}
                page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
                context.route('**.tile.openstreetmap.org/**',lambda route:route.abort())
                def go(path):
                    page.goto(base+path)
                    if path=='/' or path.startswith('/explorar'):
                        page.wait_for_function('ExploreAccount.user !== null && ExploreAccount.profile !== null')
                        expect(page.locator('#searchResults .search-status')).to_have_count(0)
                    else:
                        selector='#pageBody' if path.split('?')[0] in ('/perfil','/favoritos','/historico','/meus-roteiros','/acessibilidade') else '#featureBody'
                        expect(page.locator(selector)).to_have_attribute('aria-busy','false')
                    assert not page.locator('[role=alert]').count(),page.locator('[role=alert]').all_text_contents()
                def shot(name):
                    page.evaluate("scrollTo({top:0,behavior:'instant'})");page.screenshot(path=str(artifacts/name),full_page=True)
                def compare_map(query='',legacy=False,home=False):
                    data=context.request.get(base+'/api/destinos'+query).json()
                    expected=sorted(item['id'] for item in data['results'] if item['location']['verified'] or (legacy and item['location']['valid']))
                    variable='homeMap' if home else 'catalogMap'
                    page.wait_for_function(f'window.{variable} && window.{variable}.snapshot().count === {len(expected)}')
                    actual=page.evaluate(f'window.{variable}.snapshot().ids')
                    assert actual==expected,(query,actual,expected)
                    # Counts represented by the actual rendered cluster icons + individual icons.
                    represented=page.locator('#map' if home else '#catalogMap').evaluate('''element => [...element.querySelectorAll('[data-cluster-ids],[data-destination-id]')].flatMap(node => node.dataset.clusterIds ? node.dataset.clusterIds.split(',').map(Number) : [Number(node.dataset.destinationId)]).sort((a,b)=>a-b)''')
                    assert represented==expected,('Rendered cluster membership',query,represented,expected)
                    return data
                go('/catalogo');data=compare_map();assert data['map']['verified_coordinates']==41
                expect(page.locator('.map-cluster')).to_have_count(1)
                assert page.locator('.catalog-card').count()==data['total']
                page.locator('[data-map-id="1"]').click();expect(page.locator('.leaflet-popup')).to_contain_text('Centro Histórico')
                try:expect(page.locator('.selected-pin')).to_have_count(1)
                except AssertionError:
                    print(page.evaluate("({zoom:catalogMap.map.getZoom(),markers:catalogMap.group.getLayers().filter(m=>m.options.destinationId===1).map(m=>({cls:m.options.icon.options.className,el:!!m.getElement()})),icons:[...document.querySelectorAll('.leaflet-marker-icon')].map(e=>e.className)})"),flush=True)
                    raise
                page.locator('#catalogFilters [name=municipality]').select_option('Alcântara');page.get_by_role('button',name='Aplicar filtros').click();compare_map('?municipality=Alcântara');expect(page.locator('.catalog-card')).to_have_count(7)
                page.locator('#catalogFilters [name=municipality]').select_option('');page.locator('#catalogFilters [name=category]').select_option('Praça');page.get_by_role('button',name='Aplicar filtros').click();compare_map('?category=Praça')
                page.locator('#catalogFilters [name=category]').select_option('');page.locator('#catalogFilters [name=culture]').select_option('reggae');page.get_by_role('button',name='Aplicar filtros').click();compare_map('?culture=reggae');expect(page.locator('.catalog-card h2')).to_have_text('Museu do Reggae')
                page.locator('#culturalDiscovery summary').click();expect(page.locator('#culturalDiscovery')).to_contain_text('Memória musical')
                page.locator('#catalogFilters [name=culture]').select_option('');page.locator('#catalogFilters [name=access][value=mobility]').check();page.get_by_role('button',name='Aplicar filtros').click();compare_map('?access=mobility');expect(page.locator('.catalog-card')).to_have_count(0)
                go('/catalogo');page.locator('#includeLegacy').check();compare_map(legacy=True);shot('correcoes-explorar.png');page.locator('.catalog-mapbox').screenshot(path=str(artifacts/'correcoes-mapa.png'))
                go('/explorar');compare_map(home=True);page.locator('#homeLegacy').check();compare_map(legacy=True,home=True)
                page.locator('#placeFilters .filter[data-k=praia]').click();compare_map('?interest=praia',legacy=True,home=True)
                page.locator('#destinationSearch').fill('Raposa');page.locator('#destinationSearchButton').click();compare_map('?q=Raposa&interest=praia',legacy=True,home=True)
                # All themes, real pages and dynamic saved content.
                context.request.put(base+'/api/favoritos/1',headers=headers)
                trip=context.request.post(base+'/api/roteiro',headers=headers,data={'destination':'São Luís','days':1,'budget':500,'interests':['Cultura'],'access':[]}).json()
                context.request.post(base+'/api/roteiros-salvos',headers=headers,data={'title':'Roteiro de teste de tema','trip':trip})
                for theme,primary,footer in [('forest','#123d3a','rgb(13, 48, 45)'),('ocean','#173f55','rgb(16, 47, 67)'),('sunset','#663e34','rgb(71, 43, 37)')]:
                    go('/configuracoes');page.locator('#settingsForm [name=theme]').select_option(theme);page.get_by_role('button',name='Salvar configurações').click();expect(page.locator('#featureNotice')).to_have_text('Configurações salvas.')
                    for path in ('/','/catalogo','/destino/1','/perfil','/amigos','/presentes','/favoritos','/historico','/meus-roteiros','/configuracoes','/acessibilidade'):
                        go(path)
                        assert page.evaluate("getComputedStyle(document.body).getPropertyValue('--color-primary').trim()") == primary,(theme,path)
                        assert page.locator('footer').evaluate('e=>getComputedStyle(e).backgroundColor')==footer,(theme,path,'footer')
                        assert page.evaluate('document.documentElement.dataset.theme')==theme
                        for selector in ('.feature-card','.panel-card','.form-card'):
                            if page.locator(selector).count():assert page.locator(selector).first.evaluate('e=>getComputedStyle(e).backgroundColor')=='rgb(255, 255, 255)',(theme,path,selector)
                        if path=='/configuracoes':
                            assert page.locator('input[type=range]').first.evaluate("e=>getComputedStyle(e).accentColor===getComputedStyle(document.querySelector('header .brand')).color"),(theme,'range accent')
                    go('/');page.locator('#budget').fill('1500');page.locator('#days').select_option('1')
                    page.locator('label.chip').filter(has=page.locator('input[name=interest][value=Natureza]')).click()
                    page.locator('#tripForm button[type=submit]').click();expect(page.locator('.special-experience')).to_have_count(1)
                    assert page.locator('.special-experience').evaluate("element=>getComputedStyle(element).backgroundColor===getComputedStyle(document.querySelector('.nav-avatar')).backgroundColor"),(theme,'dynamic special experience')
                # The file selection is not a successful upload; show persistent states.
                go('/configuracoes');output=BytesIO();Image.new('RGB',(100,80),'#b17352').save(output,format='PNG');png=output.getvalue()
                saved={}
                for kind in ('avatar','cover'):
                    input=page.locator(f'[data-upload={kind}] input[type=file]');input.set_input_files({'name':kind+'-de-teste.png','mimeType':'image/png','buffer':png})
                    expect(page.locator('#state-'+kind)).to_have_attribute('data-state','selected');expect(page.locator('#filename-'+kind)).to_contain_text(kind+'-de-teste.png')
                    assert not context.request.get(base+'/api/profile-settings').json()['profile'].get(kind+'_url')
                    gate=[]
                    def hold(route):
                        if route.request.method=='POST':gate.append(route)
                        else:route.continue_()
                    context.route('**/api/profile-media/'+kind,hold)
                    page.locator(f'[data-upload={kind}] button').click();expect(page.locator('#state-'+kind)).to_have_attribute('data-state','uploading');assert len(gate)==1;gate[0].continue_()
                    expect(page.locator('#state-'+kind)).to_have_attribute('data-state','saved');expect(page.locator('#preview-'+kind)).to_have_attribute('src',__import__('re').compile('/media/'))
                    saved[kind]=page.locator('#preview-'+kind).get_attribute('src');context.unroute('**/api/profile-media/'+kind,hold)
                # A corrupt replacement is rejected; the persisted current image is untouched.
                page.locator('[data-upload=avatar] input').set_input_files({'name':'corrupta.png','mimeType':'image/png','buffer':b'not an image'})
                page.locator('[data-upload=avatar] button').click();expect(page.locator('#state-avatar')).to_have_attribute('data-state','error')
                assert context.request.get(base+'/api/profile-settings').json()['profile']['avatar_url']==saved['avatar']
                page.reload();expect(page.locator('#featureBody')).to_have_attribute('aria-busy','false')
                for kind in saved:expect(page.locator('#preview-'+kind)).to_have_attribute('src',saved[kind]);expect(page.locator('#state-'+kind)).to_have_attribute('data-state','current')
                shot('correcoes-configuracoes.png')
                go('/perfil');expect(page.locator('#profileAvatar img')).to_have_attribute('src',saved['avatar']);expect(page.locator('.profile-cover img')).to_have_attribute('src',saved['cover']);shot('correcoes-perfil.png')
                for width in (320,390,768,1440):
                    page.set_viewport_size({'width':width,'height':900})
                    for path in ('/catalogo','/configuracoes','/perfil'):
                        go(path);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
                        page.locator('#siteMenuToggle').focus();page.keyboard.press('ArrowDown');expect(page.locator('#siteMenu a').first).to_be_focused()
                        assert page.locator('#siteMenu a[href="/cultura"]').count()==0
                        labels=page.locator('#siteMenu a').all_text_contents();assert len(labels)==len(set(labels));assert not any('Atalho' in label or 'Acesso rápido' in label for label in labels)
                        page.keyboard.press('Escape');expect(page.locator('#siteMenuToggle')).to_be_focused()
                page.locator('#siteMenuToggle').click();page.locator('#logoutBtn').click();page.wait_for_url(base+'/')
                context.request.post(base+'/api/auth/login',data={'email':'teste@example.test','password':'senha-forte-123'})
                go('/perfil');expect(page.locator('#profileAvatar img')).to_have_attribute('src',saved['avatar']);expect(page.locator('.profile-cover img')).to_have_attribute('src',saved['cover'])
                go('/configuracoes')
                for kind in ('avatar','cover'):
                    page.locator('[data-remove-media='+kind+']').click();expect(page.locator('#state-'+kind)).to_have_attribute('data-state','empty');assert not context.request.get(base+'/api/profile-settings').json()['profile'].get(kind+'_url')
                assert not errors,errors
                browser.close();print('OK: contagem API versus marcadores e clusters reais; filtros e foco; 3 temas em 11 páginas; estados/persistência/erro/remoção de uploads; cultura integrada; menu em 4 larguras. Sem erros JavaScript.')
        finally:server.shutdown();thread.join(timeout=5);server.server_close()


if __name__=='__main__':main()
