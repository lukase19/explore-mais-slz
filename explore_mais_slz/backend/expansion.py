"""Recursos da expansão 2. APIs adicionais sem alterar os contratos anteriores."""
from datetime import datetime, timezone, timedelta
from io import BytesIO
import json
import re
import secrets
import sqlite3
import warnings
from flask import jsonify, request, session, send_file, send_from_directory, abort
from werkzeug.exceptions import HTTPException
try:
    from .migrations import ACCESS_FIELDS, ACCESS_GROUPS
except ImportError:
    from migrations import ACCESS_FIELDS, ACCESS_GROUPS


def confirmed_features(destination, fields):
    return all(destination.get('accessibility', {}).get(key, {}).get('status') == 'confirmed'
               and destination['accessibility'][key].get('source_url')
               and destination['accessibility'][key].get('verified_at') for key in fields)


def install(app, connect, login_required, serialize_destination, frontend_dir):
    def fail(message, code=400):
        return jsonify(error=message), code

    def body():
        return request.get_json(silent=True) or {}

    def uid():
        return session['user_id']

    def text(data, key, maximum, default=''):
        value = data.get(key, default)
        if not isinstance(value, str) or len(value.strip()) > maximum:
            raise ValueError(f'Campo {key} inválido (máximo {maximum} caracteres).')
        return value.strip()

    def profile(con, user_id):
        con.execute('INSERT OR IGNORE INTO profiles(user_id,handle) SELECT id, ? FROM usuarios WHERE id=?', (f'viajante_{user_id}_{secrets.token_hex(3)}', user_id))
        return con.execute('SELECT p.*, u.nome FROM profiles p JOIN usuarios u ON u.id=p.user_id WHERE p.user_id=?', (user_id,)).fetchone()

    def media_urls(con, user_id):
        return {row['kind'] + '_url':'/media/' + row['token'] for row in con.execute('SELECT token,kind FROM media WHERE user_id=?', (user_id,))}

    def own_profile(con):
        row = profile(con, uid())
        result = dict(row)
        result.pop('nome')
        result['access_preferences'] = json.loads(result['access_preferences'])
        result['friend_count'] = con.execute("SELECT count(*) FROM friendships WHERE status='accepted' AND (sender_id=? OR recipient_id=?)",(uid(),uid())).fetchone()[0]
        return {**result, **media_urls(con, uid())}

    def blocked(con, left, right):
        return bool(con.execute('SELECT 1 FROM blocks WHERE (blocker_id=? AND blocked_id=?) OR (blocker_id=? AND blocked_id=?)', (left,right,right,left)).fetchone())

    def friends(con, left, right):
        return not blocked(con,left,right) and bool(con.execute("SELECT 1 FROM friendships WHERE min(sender_id,recipient_id)=min(?,?) AND max(sender_id,recipient_id)=max(?,?) AND status='accepted'", (left,right,left,right)).fetchone())

    def public_person(con, user_id):
        row = profile(con,user_id)
        viewer = session.get('user_id')
        can_view = row['is_public'] or viewer == user_id or (viewer and friends(con,viewer,user_id))
        return {'id':row['user_id'],'name':row['nome'],'handle':row['handle'], **(media_urls(con,user_id) if can_view else {})}

    def trip_access(con, trip_id, editor=False):
        row = con.execute('SELECT * FROM roteiros_salvos WHERE id=?', (trip_id,)).fetchone()
        if not row:
            abort(404)
        if row['usuario_id'] == uid():
            return row
        if blocked(con,uid(),row['usuario_id']):
            abort(404)
        invite = con.execute("SELECT role FROM trip_invites WHERE trip_id=? AND recipient_id=? AND status='accepted'", (trip_id,uid())).fetchone()
        if not invite or (editor and invite['role'] != 'editor'):
            abort(403)
        return row

    @app.errorhandler(HTTPException)
    def http_error(error):
        if request.path.startswith('/api/'):
            messages = {400:'Requisição inválida.',401:'Entre para continuar.',403:'Você não tem permissão para esta ação.',404:'Não encontrado ou sem acesso.',409:'A operação conflita com o estado atual.',413:'Arquivo ou requisição acima do limite de 6 MB.'}
            return fail(messages.get(error.code, 'Não foi possível concluir a operação.'),error.code)
        return error

    @app.errorhandler(ValueError)
    def invalid_data(error):
        return fail(str(error))

    @app.get('/api/profile-settings')
    @login_required
    def get_profile_settings():
        with connect() as con:
            return jsonify(profile=own_profile(con),access_fields=ACCESS_FIELDS,access_groups=ACCESS_GROUPS)

    @app.patch('/api/profile-settings')
    @login_required
    def update_profile_settings():
        data=body()
        name = text(data,'name',100) if 'name' in data else None
        interests = data.get('interests')
        if name is not None and len(name)<2: return fail('Informe um nome de pelo menos 2 caracteres.')
        if 'interests' in data and (not isinstance(interests,list) or len(interests)>12 or any(not isinstance(item,str) or len(item)>40 for item in interests)):
            return fail('Use até 12 interesses de até 40 caracteres.')
        with connect() as con:
            current=dict(profile(con,uid()))
            values={key:text(data,key,maximum,current[key]) for key,maximum in [('handle',30),('bio',500),('municipality',80),('theme',20),('favorites_visibility',10)]}
            if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{2,29}',values['handle']):
                return fail('Use um @usuario de 3 a 30 letras, números ou sublinhado, começando por letra.')
            if values['theme'] not in ('forest','ocean','sunset') or values['favorites_visibility'] not in ('private','friends','public'):
                return fail('Tema ou visibilidade inválidos.')
            for key in ('is_public','discoverable','allow_invites','access_consent'):
                value=data.get(key,bool(current[key]))
                if not isinstance(value,bool): return fail('As opções de privacidade devem ser booleanas.')
                values[key]=int(value)
            prefs=data.get('access_preferences',json.loads(current['access_preferences']))
            if not isinstance(prefs,list) or len(prefs)>5 or any(not isinstance(v,str) or v not in ACCESS_GROUPS for v in prefs):
                return fail('Preferências de acessibilidade inválidas.')
            values['access_preferences']=json.dumps(sorted(set(prefs)) if values['access_consent'] else [])
            for key in ('avatar_x','avatar_y','cover_x','cover_y'):
                value=data.get(key,current[key])
                if isinstance(value,bool) or not isinstance(value,int) or not 0<=value<=100: return fail('Posição da imagem deve estar entre 0 e 100.')
                values[key]=value
            try:
                con.execute('UPDATE profiles SET ' + ','.join(key+'=?' for key in values) + ' WHERE user_id=?', (*values.values(),uid()))
            except sqlite3.IntegrityError:
                return fail('Este @usuario já está em uso.',409)
            if name is not None: con.execute('UPDATE usuarios SET nome=? WHERE id=?',(name,uid()))
            if interests is not None: con.execute('UPDATE usuarios SET interesses=? WHERE id=?',(json.dumps(interests,ensure_ascii=False),uid()))
            return jsonify(profile=own_profile(con))

    @app.route('/api/profile-media/<kind>', methods=['POST','DELETE'])
    @login_required
    def upload_profile_media(kind):
        if kind not in ('avatar','cover'): abort(404)
        with connect() as con:
            profile(con,uid())
            if request.method=='DELETE':
                con.execute('DELETE FROM media WHERE user_id=? AND kind=?',(uid(),kind))
                return jsonify(ok=True)
        upload=request.files.get('image')
        if not upload: return fail('Selecione uma imagem JPEG, PNG ou WebP.')
        raw=upload.read(4*1024*1024+1)
        if len(raw)>4*1024*1024: return fail('A imagem pode ter até 4 MB.',413)
        # Decode and re-encode; ignore filenames and claimed Content-Type. No SVG/GIF or embedded metadata.
        from PIL import Image, ImageOps, UnidentifiedImageError
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error',Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw)) as check:
                    if check.format not in ('JPEG','PNG','WEBP') or check.width*check.height>16_000_000:
                        return fail('Use JPEG, PNG ou WebP com até 16 megapixels.')
                    check.verify()
                with Image.open(BytesIO(raw)) as original:
                    image=ImageOps.exif_transpose(original).convert('RGB')
                    image.thumbnail((512,512) if kind=='avatar' else (1800,1000))
                    output=BytesIO(); image.save(output,format='JPEG',quality=86)
        except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError,Image.DecompressionBombWarning):
            return fail('O arquivo não contém uma imagem válida permitida.')
        token=secrets.token_hex(24)
        with connect() as con:
            con.execute('INSERT INTO media(token,user_id,kind,data) VALUES (?,?,?,?) ON CONFLICT(user_id,kind) DO UPDATE SET token=excluded.token,data=excluded.data,created_at=CURRENT_TIMESTAMP',(token,uid(),kind,output.getvalue()))
        return jsonify(url='/media/'+token),201

    @app.get('/media/<token>')
    def serve_profile_media(token):
        with connect() as con:
            row=con.execute('SELECT m.*,p.is_public FROM media m JOIN profiles p ON m.user_id=p.user_id WHERE token=?',(token,)).fetchone()
            viewer=session.get('user_id')
            if not row or (viewer and blocked(con,viewer,row['user_id'])): abort(404)
            if viewer!=row['user_id'] and not row['is_public'] and not (viewer and friends(con,viewer,row['user_id'])): abort(404)
        response=send_file(BytesIO(row['data']),mimetype='image/jpeg',download_name='imagem.jpg',max_age=0)
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Cache-Control']='private, no-store'
        return response

    @app.get('/api/people')
    @login_required
    def people_search():
        query=request.args.get('q','').strip().lstrip('@')[:80]
        if len(query)<2: return jsonify(results=[])
        with connect() as con:
            profile(con,uid())
            rows=con.execute('SELECT p.user_id FROM profiles p JOIN usuarios u ON u.id=p.user_id WHERE p.discoverable=1 AND p.user_id != ? AND (p.handle LIKE ? ESCAPE \'\\\' OR u.nome LIKE ? ESCAPE \'\\\') LIMIT 30',(uid(),'%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%','%'+query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')).fetchall()
            return jsonify(results=[public_person(con,r['user_id']) for r in rows if not blocked(con,uid(),r['user_id'])])

    @app.get('/api/public-profile/<handle>')
    def public_profile(handle):
        with connect() as con:
            row=con.execute('SELECT * FROM profiles WHERE handle=?',(handle,)).fetchone()
            viewer=session.get('user_id')
            if not row or (viewer and blocked(con,viewer,row['user_id'])): abort(404)
            is_friend=bool(viewer and friends(con,viewer,row['user_id']))
            own=viewer==row['user_id']
            if not row['is_public'] and not own and not is_friend: abort(404)
            result={**public_person(con,row['user_id']), 'bio':row['bio'],'municipality':row['municipality'],'theme':row['theme'],'cover_x':row['cover_x'],'cover_y':row['cover_y'],'avatar_x':row['avatar_x'],'avatar_y':row['avatar_y']}
            visible=own or row['favorites_visibility']=='public' or (is_friend and row['favorites_visibility']=='friends')
            result['favorites']= [serialize_destination(r) for r in con.execute('SELECT d.* FROM destinos d JOIN favoritos f ON d.id=f.destino_id WHERE f.usuario_id=?',(row['user_id'],))] if visible else None
            return jsonify(profile=result)

    @app.get('/api/friends')
    @login_required
    def list_friends():
        with connect() as con:
            profile(con,uid())
            rows=con.execute("SELECT * FROM friendships WHERE (sender_id=? OR recipient_id=?) AND status IN ('pending','accepted') ORDER BY id DESC",(uid(),uid())).fetchall()
            result=[]
            for row in rows:
                other=row['recipient_id'] if row['sender_id']==uid() else row['sender_id']
                if not blocked(con,uid(),other): result.append({**dict(row),'person':public_person(con,other),'incoming':row['recipient_id']==uid()})
            blocks=[public_person(con,r[0]) for r in con.execute('SELECT blocked_id FROM blocks WHERE blocker_id=?',(uid(),))]
            return jsonify(results=result,blocked=blocks)

    @app.post('/api/friends/<int:other>')
    @login_required
    def friendship_action(other):
        action=body().get('action')
        if other==uid(): return fail('Escolha outra pessoa.')
        with connect() as con:
            if not con.execute('SELECT 1 FROM usuarios WHERE id=?',(other,)).fetchone(): abort(404)
            target=profile(con,other)
            if action=='block':
                con.execute('INSERT OR IGNORE INTO blocks VALUES (?,?)',(uid(),other))
                con.execute("UPDATE friendships SET status='removed' WHERE min(sender_id,recipient_id)=min(?,?) AND max(sender_id,recipient_id)=max(?,?)",(uid(),other,uid(),other))
                con.execute("UPDATE trip_invites SET status='revoked' WHERE (sender_id=? AND recipient_id=?) OR (sender_id=? AND recipient_id=?)",(uid(),other,other,uid()))
                con.execute("UPDATE vouchers SET status='cancelled' WHERE status IN ('issued','sent') AND ((sender_id=? AND recipient_id=?) OR (sender_id=? AND recipient_id=?))",(uid(),other,other,uid()))
                return jsonify(ok=True)
            if action=='unblock':
                con.execute('DELETE FROM blocks WHERE blocker_id=? AND blocked_id=?',(uid(),other))
                return jsonify(ok=True)
            if blocked(con,uid(),other): abort(404)
            row=con.execute('SELECT * FROM friendships WHERE min(sender_id,recipient_id)=min(?,?) AND max(sender_id,recipient_id)=max(?,?)',(uid(),other,uid(),other)).fetchone()
            if action=='request':
                if not target['discoverable'] or not target['allow_invites']: return fail('Esta pessoa não recebe solicitações.',403)
                if row and row['status'] in ('accepted','pending'): return fail('Já existe uma amizade ou solicitação pendente.',409)
                con.execute("INSERT INTO friendships(sender_id,recipient_id,status) VALUES (?,?,'pending') ON CONFLICT DO UPDATE SET sender_id=excluded.sender_id,recipient_id=excluded.recipient_id,status='pending'",(uid(),other))
            elif action in ('accept','reject'):
                if not row or row['recipient_id']!=uid() or row['status']!='pending': return fail('Solicitação indisponível.',409)
                con.execute('UPDATE friendships SET status=? WHERE id=?',('accepted' if action=='accept' else 'rejected',row['id']))
            elif action=='remove':
                if not row: abort(404)
                con.execute("UPDATE friendships SET status='removed' WHERE id=?",(row['id'],))
                con.execute("UPDATE trip_invites SET status='revoked' WHERE (sender_id=? AND recipient_id=?) OR (sender_id=? AND recipient_id=?)",(uid(),other,other,uid()))
            else: return fail('Ação de amizade inválida.')
            return jsonify(ok=True)

    @app.post('/api/trips/<int:trip_id>/invites')
    @login_required
    def invite_to_trip(trip_id):
        data=body(); other=data.get('recipient_id'); role=data.get('role','editor')
        if not isinstance(other,int) or isinstance(other,bool) or role not in ('viewer','editor'): return fail('Convite inválido.')
        with connect() as con:
            row=trip_access(con,trip_id)
            if row['usuario_id']!=uid(): abort(403)
            if not friends(con,uid(),other) or not profile(con,other)['allow_invites']: return fail('Escolha um amigo que aceite convites.',403)
            con.execute("INSERT INTO trip_invites(trip_id,sender_id,recipient_id,role) VALUES (?,?,?,?) ON CONFLICT(trip_id,recipient_id) DO UPDATE SET status='pending',role=excluded.role",(trip_id,uid(),other,role))
            return jsonify(ok=True),201

    @app.get('/api/trip-invites')
    @login_required
    def trip_invites():
        with connect() as con:
            rows=con.execute("SELECT i.*,r.titulo FROM trip_invites i JOIN roteiros_salvos r ON r.id=i.trip_id WHERE (i.recipient_id=? OR i.sender_id=?) AND i.status IN ('pending','accepted') ORDER BY i.id DESC",(uid(),uid())).fetchall()
            return jsonify(results=[{**dict(r),'person':public_person(con,r['sender_id'] if r['recipient_id']==uid() else r['recipient_id'])} for r in rows if not blocked(con,r['sender_id'],r['recipient_id'])])

    @app.post('/api/trip-invites/<int:invite_id>')
    @login_required
    def respond_trip_invite(invite_id):
        action=body().get('action')
        with connect() as con:
            row=con.execute('SELECT * FROM trip_invites WHERE id=?',(invite_id,)).fetchone()
            if not row: abort(404)
            if action=='revoke' and row['sender_id']==uid():
                con.execute("UPDATE trip_invites SET status='revoked' WHERE id=?",(invite_id,))
            elif action in ('accept','reject') and row['recipient_id']==uid() and row['status']=='pending' and friends(con,uid(),row['sender_id']):
                con.execute('UPDATE trip_invites SET status=? WHERE id=?',('accepted' if action=='accept' else 'rejected',invite_id))
            else: return fail('Convite indisponível para esta ação.',403)
            return jsonify(ok=True)

    @app.get('/api/trips/<int:trip_id>')
    @login_required
    def shared_trip(trip_id):
        with connect() as con:
            row=trip_access(con,trip_id)
            notes=[{'id':r['id'],'text':r['text'],'created_at':r['created_at'],'person':public_person(con,r['user_id'])} for r in con.execute('SELECT * FROM trip_notes WHERE trip_id=? ORDER BY id',(trip_id,))]
            link=con.execute('SELECT token FROM trip_shares WHERE trip_id=?',(trip_id,)).fetchone() if row['usuario_id']==uid() else None
            editor = row['usuario_id']==uid() or bool(con.execute("SELECT 1 FROM trip_invites WHERE trip_id=? AND recipient_id=? AND status='accepted' AND role='editor'",(trip_id,uid())).fetchone())
            return jsonify(id=row['id'],title=row['titulo'],trip=json.loads(row['conteudo']),notes=notes,owner=row['usuario_id']==uid(),can_edit=editor,share_url='/s/'+link['token'] if link else None)

    @app.post('/api/trips/<int:trip_id>/notes')
    @login_required
    def add_trip_note(trip_id):
        note=text(body(),'text',1000)
        if not note: return fail('Escreva uma contribuição.')
        with connect() as con:
            trip_access(con,trip_id,editor=True)
            con.execute('INSERT INTO trip_notes(trip_id,user_id,text) VALUES (?,?,?)',(trip_id,uid(),note))
            return jsonify(ok=True),201

    @app.patch('/api/trips/<int:trip_id>')
    @login_required
    def rename_shared_trip(trip_id):
        title=text(body(),'title',120)
        if not title: return fail('Informe um título.')
        with connect() as con:
            trip_access(con,trip_id,editor=True)
            con.execute('UPDATE roteiros_salvos SET titulo=? WHERE id=?',(title,trip_id))
        return jsonify(ok=True)

    @app.route('/api/trips/<int:trip_id>/share',methods=['POST','DELETE'])
    @login_required
    def share_trip_link(trip_id):
        with connect() as con:
            row=trip_access(con,trip_id)
            if row['usuario_id']!=uid(): abort(403)
            if request.method=='DELETE':
                con.execute('DELETE FROM trip_shares WHERE trip_id=?',(trip_id,)); return jsonify(ok=True)
            link=con.execute('SELECT token FROM trip_shares WHERE trip_id=?',(trip_id,)).fetchone()
            token=link['token'] if link else secrets.token_urlsafe(32)
            con.execute('INSERT OR IGNORE INTO trip_shares(token,trip_id) VALUES (?,?)',(token,trip_id))
            return jsonify(url='/s/'+token)

    @app.get('/api/shared/<token>')
    def public_trip_link(token):
        with connect() as con:
            row=con.execute('SELECT r.id,r.titulo,r.conteudo FROM trip_shares s JOIN roteiros_salvos r ON r.id=s.trip_id WHERE s.token=?',(token,)).fetchone()
            if not row: abort(404)
            return jsonify(title=row['titulo'],trip=json.loads(row['conteudo']))

    def expire_vouchers(con):
        con.execute("UPDATE vouchers SET status='expired' WHERE status IN ('issued','sent') AND expires_at < ?",(datetime.now(timezone.utc).isoformat(),))

    @app.get('/api/vouchers')
    @login_required
    def list_vouchers():
        with connect() as con:
            expire_vouchers(con)
            rows=con.execute("SELECT v.*,d.nome AS destination FROM vouchers v JOIN destinos d ON d.id=v.destination_id WHERE v.sender_id=? OR (v.recipient_id=? AND v.status!='issued') ORDER BY v.id DESC LIMIT 200",(uid(),uid())).fetchall()
            return jsonify(results=[{**dict(r),'outgoing':r['sender_id']==uid(),'person':public_person(con,r['recipient_id'] if r['sender_id']==uid() else r['sender_id'])} for r in rows])

    @app.post('/api/vouchers')
    @login_required
    def issue_voucher():
        data=body(); other=data.get('recipient_id'); destination=data.get('destination_id')
        message=text(data,'message',500); theme=data.get('theme','azulejo')
        if not isinstance(other,int) or isinstance(other,bool) or not isinstance(destination,int) or theme not in ('azulejo','sol','reggae'): return fail('Voucher inválido.')
        try:
            expires=datetime.strptime(data.get('expires_at',''),'%Y-%m-%d').replace(tzinfo=timezone.utc,hour=23,minute=59,second=59)
        except (TypeError,ValueError): return fail('Informe uma validade no formato AAAA-MM-DD.')
        if not datetime.now(timezone.utc)<expires<=datetime.now(timezone.utc)+timedelta(days=366): return fail('Escolha uma validade futura em até um ano.')
        with connect() as con:
            if not friends(con,uid(),other) or not profile(con,other)['allow_invites']: return fail('Escolha um amigo que aceite convites.',403)
            if not con.execute('SELECT 1 FROM destinos WHERE id=?',(destination,)).fetchone(): abort(404)
            code=secrets.token_urlsafe(24)
            cur=con.execute('INSERT INTO vouchers(code,sender_id,recipient_id,destination_id,message,theme,expires_at) VALUES (?,?,?,?,?,?,?)',(code,uid(),other,destination,message,theme,expires.isoformat()))
            return jsonify(id=cur.lastrowid,code=code,status='issued'),201

    @app.post('/api/vouchers/<int:voucher_id>/transition')
    @login_required
    def transition_voucher(voucher_id):
        action=body().get('action')
        with connect() as con:
            expire_vouchers(con)
            row=con.execute('SELECT * FROM vouchers WHERE id=? AND (sender_id=? OR recipient_id=?)',(voucher_id,uid(),uid())).fetchone()
            if not row: abort(404)
            if action=='send' and row['sender_id']==uid() and row['status']=='issued':
                if not friends(con,uid(),row['recipient_id']) or not profile(con,row['recipient_id'])['allow_invites']: return fail('O destinatário não está disponível.',403)
                con.execute("UPDATE vouchers SET status='sent' WHERE id=? AND status='issued'",(voucher_id,))
            elif action=='cancel' and row['sender_id']==uid() and row['status'] in ('issued','sent'):
                con.execute("UPDATE vouchers SET status='cancelled' WHERE id=? AND status IN ('issued','sent')",(voucher_id,))
            elif action=='redeem' and row['recipient_id']==uid() and row['status']=='sent':
                if blocked(con,uid(),row['sender_id']): abort(403)
                changed=con.execute("UPDATE vouchers SET status='redeemed',redeemed_at=CURRENT_TIMESTAMP WHERE id=? AND status='sent'",(voucher_id,)).rowcount
                if not changed: return fail('Este convite já foi utilizado.',409)
            else: return fail('Transição indisponível para este usuário e estado.',409)
            return jsonify(ok=True)

    @app.get('/api/accessibility')
    def accessibility_metadata():
        return jsonify(fields=ACCESS_FIELDS,groups=ACCESS_GROUPS,states={'confirmed':'Confirmado','unavailable':'Não disponível','unverified':'Informação ainda não verificada'})

    @app.route('/api/accessibility-reports',methods=['GET','POST'])
    @login_required
    def accessibility_report():
        with connect() as con:
            if request.method=='GET':
                return jsonify(results=[dict(r) for r in con.execute('SELECT id,destination_id,feature,proposed_status,description,status,created_at FROM accessibility_reports WHERE user_id=? ORDER BY id DESC LIMIT 100',(uid(),))])
            data=body(); destination=data.get('destination_id'); feature=data.get('feature'); status=data.get('proposed_status')
            description=text(data,'description',2000); source=text(data,'source_url',1000)
            if not isinstance(feature,str) or feature not in ACCESS_FIELDS or status not in ('confirmed','unavailable','unverified') or len(description)<10 or not isinstance(destination,int) or isinstance(destination,bool): return fail('Informe destino, recurso e uma descrição de pelo menos 10 caracteres.')
            if source and not source.startswith('https://'): return fail('A fonte deve usar HTTPS.')
            if not con.execute('SELECT 1 FROM destinos WHERE id=?',(destination,)).fetchone(): abort(404)
            cur=con.execute('INSERT INTO accessibility_reports(user_id,destination_id,feature,proposed_status,description,source_url) VALUES (?,?,?,?,?,?)',(uid(),destination,feature,status,description,source))
            return jsonify(id=cur.lastrowid,status='pending',message='Sugestão recebida para moderação. Ela não altera os dados publicados.'),201

    def feature_page():
        return send_from_directory(frontend_dir,'experiencias.html')
    for index,path in enumerate(('/catalogo','/amigos','/presentes','/configuracoes','/destino/<int:destination_id>','/p/<handle>','/s/<token>','/roteiro-compartilhado/<int:trip_id>')):
        app.add_url_rule(path,endpoint=f'expansion_page_{index}',view_func=lambda **kwargs: feature_page())

    @app.get('/api/destinos/<int:destination_id>')
    def destination_detail(destination_id):
        with connect() as con:
            row=con.execute('SELECT * FROM destinos WHERE id=?',(destination_id,)).fetchone()
            if not row: abort(404)
            return jsonify(destination=serialize_destination(row))
