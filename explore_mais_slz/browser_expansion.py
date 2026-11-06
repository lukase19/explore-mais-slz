"""Teste opcional no Chrome: python browser_expansion.py. Usa apenas dados temporários."""
import importlib
import os
from pathlib import Path
from io import BytesIO
import tempfile
from threading import Thread
from datetime import datetime, timedelta, timezone
from werkzeug.serving import make_server
from test_browser import QuietHandler


def main():
    from playwright.sync_api import sync_playwright, expect
    from PIL import Image
    with tempfile.TemporaryDirectory(prefix='explore-v2-browser-') as directory:
        os.environ['EXPLORE_DATABASE_PATH']=str(Path(directory)/'browser.sqlite')
        backend=importlib.import_module('backend.app')
        server=make_server('127.0.0.1',0,backend.app,request_handler=QuietHandler)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}';artifacts=Path('.artifacts');artifacts.mkdir(exist_ok=True)
        errors=[]
        try:
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch(channel='chrome',headless=True)
                owner=browser.new_context(viewport={'width':1440,'height':1000},locale='pt-BR',timezone_id='America/Fortaleza')
                friend=browser.new_context(viewport={'width':390,'height':844},locale='pt-BR',timezone_id='America/Fortaleza')
                def register(context,email,name,handle):
                    result=context.request.post(base+'/api/auth/register',data={'email':email,'name':name,'password':'senha-forte-123'}).json()
                    headers={'X-CSRF-Token':result['csrf']}
                    response=context.request.patch(base+'/api/profile-settings',headers=headers,data={'handle':handle,'discoverable':True})
                    assert response.status==200,response.text()
                    return result,headers
                alice,ah=register(owner,'alice@example.test','Alice Viajante','alice')
                bruno,bh=register(friend,'bruno@example.test','Bruno Amigo','bruno')
                a=owner.new_page();b=friend.new_page()
                for page in (a,b):
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    page.route('**.tile.openstreetmap.org/**',lambda route:route.abort())
                def go(page,path):
                    page.goto(base+path)
                    selector='#pageBody' if path.split('?')[0] in ('/perfil','/meus-roteiros','/acessibilidade') else '#featureBody'
                    expect(page.locator(selector)).to_have_attribute('aria-busy','false')
                    assert not page.locator('[role=alert]').count(),page.locator('[role=alert]').all_text_contents()
                def shot(page,name):
                    page.evaluate("scrollTo({top:0,behavior:'instant'})")
                    page.screenshot(path=str(artifacts/name),full_page=True)
                go(a,'/catalogo');a.locator('#culturalDiscovery summary').click();expect(a.get_by_role('heading',name='Bumba Meu Boi e seus sotaques')).to_be_visible()
                menu=a.locator('#siteMenuToggle');menu.focus();menu.press('ArrowDown')
                expect(menu).to_have_attribute('aria-expanded','true')
                expect(a.locator('#siteMenu a').first).to_be_focused()
                a.keyboard.press('Escape');expect(menu).to_have_attribute('aria-expanded','false');expect(menu).to_be_focused()
                menu.click();a.locator('#featureTitle').click();expect(menu).to_have_attribute('aria-expanded','false')
                assert a.locator('#siteMenu').count()==1
                shot(a,'v2-cultura.png')
                go(a,'/configuracoes')
                a.locator('#settingsForm [name=bio]').fill('Gosto de história e cultura popular.')
                a.locator('#settingsForm [name=municipality]').fill('São Luís')
                a.locator('#settingsForm [name=theme]').select_option('ocean')
                a.locator('#settingsForm [name=access_consent]').check()
                a.locator('#settingsForm [name=access_preferences][value=visual]').check()
                a.get_by_role('button',name='Salvar configurações').click()
                expect(a.locator('#featureNotice')).to_have_text('Configurações salvas.')
                expect(a.locator('#settingsForm [name=bio]')).to_have_value('Gosto de história e cultura popular.')
                output=BytesIO();Image.new('RGB',(300,200),'#2a6654').save(output,format='PNG');png=output.getvalue()
                for kind in ('avatar','cover'):
                    a.locator(f'[data-upload={kind}] input[type=file]').set_input_files({'name':'imagem.png','mimeType':'image/png','buffer':png})
                    expect(a.locator('#preview-'+kind)).to_have_attribute('src',__import__('re').compile('blob:'))
                    a.locator(f'[data-upload={kind}] button').click()
                    expect(a.locator('#preview-'+kind)).to_have_attribute('src',__import__('re').compile('/media/'))
                a.locator('#settingsForm [name=cover_y]').focus();a.keyboard.press('End')
                a.get_by_role('button',name='Salvar configurações').click()
                expect(a.locator('#featureNotice')).to_have_text('Configurações salvas.')
                go(a,'/perfil');expect(a.locator('.profile-cover img')).to_be_visible();expect(a.locator('#profileAvatar img')).to_be_visible();shot(a,'v2-perfil.png')
                go(a,'/amigos');a.locator('#peopleSearch [name=q]').fill('bruno');a.get_by_role('button',name='Pesquisar pessoas').click();a.get_by_role('button',name='Adicionar amigo').click()
                expect(a.get_by_text('Enviada',exact=True)).to_be_visible()
                go(b,'/amigos');b.get_by_role('button',name='Aceitar',exact=True).click();expect(b.get_by_role('heading',name='Amigos · 1')).to_be_visible()
                go(a,'/amigos');expect(a.get_by_role('heading',name='Amigos · 1')).to_be_visible();shot(a,'v2-amigos.png')
                trip=owner.request.post(base+'/api/roteiro',headers=ah,data={'destination':'São Luís','days':1,'budget':500,'interests':['Cultura'],'access':[]}).json()
                saved=owner.request.post(base+'/api/roteiros-salvos',headers=ah,data={'title':'Nosso passeio','trip':trip}).json()['id']
                go(a,f'/roteiro-compartilhado/{saved}');a.get_by_role('button',name='Enviar convite de roteiro').click();expect(a.locator('#featureNotice')).to_have_text('Convite enviado.')
                go(b,'/amigos');b.get_by_role('button',name='Aceitar convite').click();b.get_by_role('link',name='Abrir roteiro').click();expect(b.locator('#featureBody')).to_have_attribute('aria-busy','false')
                b.locator('#tripNote textarea').fill('Vamos confirmar os recursos de acesso antes.');b.get_by_role('button',name='Adicionar ideia').click();expect(b.locator('.collaboration-note')).to_contain_text('Vamos confirmar')
                go(a,f'/roteiro-compartilhado/{saved}');expect(a.locator('.collaboration-note')).to_contain_text('Vamos confirmar')
                a.once('dialog',lambda dialog:dialog.accept());a.get_by_role('button',name='Criar link de leitura pública').click();expect(a.get_by_role('button',name='Desativar link público')).to_be_visible()
                link=a.locator('.share-link a').get_attribute('href');public=browser.new_context();public_page=public.new_page();public_page.goto(base+link);expect(public_page.locator('#featureBody')).to_contain_text('Dia 1')
                a.get_by_role('button',name='Desativar link público').click();expect(a.get_by_role('button',name='Criar link de leitura pública')).to_be_visible()
                go(a,'/presentes');a.locator('#voucherForm [name=message]').fill('Um convite para explorar juntos!');a.locator('#voucherForm [name=expires_at]').fill((datetime.now(timezone.utc)+timedelta(days=10)).date().isoformat());a.get_by_role('button',name='Emitir voucher simbólico').click();a.get_by_role('button',name='Enviar convite',exact=True).click();expect(a.locator('.status-pill')).to_have_text('Enviado')
                go(b,'/presentes');b.once('dialog',lambda dialog:dialog.accept());b.get_by_role('button',name='Confirmar resgate simbólico').click();expect(b.locator('.status-pill')).to_have_text('Resgatado');shot(b,'v2-voucher-celular.png')
                go(a,'/catalogo');assert a.locator('.catalog-card').count()>=60
                a.locator('#catalogFilters [name=municipality]').select_option('Alcântara');a.get_by_role('button',name='Aplicar filtros').click();expect(a.locator('#catalogResults')).to_contain_text('Alcântara')
                a.locator('#catalogFilters [name=access][value=mobility]').check();a.get_by_role('button',name='Aplicar filtros').click();expect(a.locator('#catalogResults')).to_contain_text('Nenhum local atende')
                go(a,'/destino/1');expect(a.locator('.access-table')).to_contain_text('Informação ainda não verificada')
                a.locator('#accessReport [name=description]').fill('Sugestão de teste para revisão, sem publicação automática.');a.get_by_role('button',name='Enviar para moderação').click();expect(a.locator('#featureNotice')).to_have_text('Sugestão recebida para moderação.')
                for width in (320,390,768,1440):
                    a.set_viewport_size({'width':width,'height':900})
                    for path in ('/configuracoes','/catalogo','/amigos','/presentes','/catalogo','/destino/1','/perfil'):
                        go(a,path)
                        assert a.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
                        a.locator('#siteMenuToggle').click();expect(a.locator('#siteMenu')).to_be_visible();assert a.evaluate('document.documentElement.scrollWidth<=innerWidth')
                        a.keyboard.press('Escape')
                a.set_viewport_size({'width':390,'height':844});go(a,'/configuracoes');a.get_by_role('button',name='Remover foto').click();expect(a.locator('#preview-avatar')).to_have_attribute('src','/destination-fallback.svg')
                go(a,'/amigos');a.once('dialog',lambda dialog:dialog.accept());a.get_by_role('button',name='Bloquear',exact=True).first.click();expect(a.get_by_role('button',name='Desbloquear')).to_be_visible()
                assert not errors,errors
                browser.close();print('OK: menu por teclado, fotos/capa/prévia/remoção, configurações, duas contas, amizade, colaboração, link revogável, voucher, moderação e 7 páginas em 320/390/768/1440px; sem erros JavaScript.')
        finally:
            server.shutdown();thread.join(timeout=5);server.server_close()


if __name__=='__main__':main()
