from __future__ import annotations

import json
import sqlite3
import os
import secrets
import math
import unicodedata
from functools import wraps
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from flask import Flask, jsonify, request, send_from_directory, session, abort, redirect
try:
    from .migrations import migrate, destination_metadata, ACCESS_GROUPS, ACCESS_FIELDS
    from .expansion import install, confirmed_features
    from .catalog import seed_catalog
    from .culture import cultural_content, destination_culture, INTERESTS as CULTURAL_INTERESTS
except ImportError:
    from migrations import migrate, destination_metadata, ACCESS_GROUPS, ACCESS_FIELDS
    from expansion import install, confirmed_features
    from catalog import seed_catalog
    from culture import cultural_content, destination_culture, INTERESTS as CULTURAL_INTERESTS

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATABASE_PATH = Path(os.environ.get("EXPLORE_DATABASE_PATH") or Path(__file__).resolve().parent / "explore_slz.db")
PUBLIC_ORIGIN = os.environ.get("EXPLORE_PUBLIC_ORIGIN", "").rstrip("/")
if PUBLIC_ORIGIN:
    public_url = urlsplit(PUBLIC_ORIGIN)
    if (public_url.scheme != "https" or not public_url.netloc or public_url.username
            or public_url.password or public_url.path or public_url.query or public_url.fragment):
        raise RuntimeError("EXPLORE_PUBLIC_ORIGIN deve ser a origem HTTPS pública, sem caminho ou credenciais.")
    if len(os.environ.get("EXPLORE_SECRET_KEY", "")) < 32:
        raise RuntimeError("Configure EXPLORE_SECRET_KEY persistente com pelo menos 32 caracteres.")
    if not os.environ.get("EXPLORE_DATABASE_PATH") or not DATABASE_PATH.is_absolute() or not DATABASE_PATH.is_file():
        raise RuntimeError("Configure EXPLORE_DATABASE_PATH absoluto para o banco persistente existente; nenhum banco de produção será criado automaticamente.")
    if os.environ.get("EXPLORE_HTTPS") != "1":
        raise RuntimeError("Configure EXPLORE_HTTPS=1 para proteger a sessão pública.")
if os.environ.get("VERCEL") == "1":
    raise RuntimeError("Este backend usa SQLite persistente e deve rodar no servidor de origem, não em uma função Vercel.")

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
app.config.update(SECRET_KEY=os.environ.get("EXPLORE_SECRET_KEY") or secrets.token_hex(32), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax", MAX_CONTENT_LENGTH=6*1024*1024)
if os.environ.get("EXPLORE_HTTPS") == "1":
    app.config["SESSION_COOKIE_SECURE"] = True

@app.before_request
def protect_writes():
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and request.path.startswith("/api/"):
        if request.is_json and request.get_data() and not isinstance(request.get_json(silent=True), dict):
            return jsonify({"error": "Envie um objeto JSON válido."}), 400
        origin = request.headers.get("Origin")
        if origin and origin.rstrip("/") != (PUBLIC_ORIGIN or request.host_url.rstrip("/")):
            return jsonify({"error":"Origem não autorizada."}), 403
        if request.path not in ("/api/auth/login", "/api/auth/register") and session.get("user_id"):
            if request.headers.get("X-CSRF-Token") != session.get("csrf"):
                return jsonify({"error":"Token de segurança inválido."}), 403

def login_required(handler):
    @wraps(handler)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error":"Entre na sua conta para continuar."}), 401
        return handler(*args, **kwargs)
    return decorated


@app.after_request
def prevent_private_cache(response):
    # O proxy nunca deve compartilhar sessões, respostas da API ou mídia privada.
    if request.path.startswith(("/api/", "/media/")):
        response.headers["Cache-Control"] = "private, no-store"
    return response

def record_history(kind, label, item_id=None):
    if session.get("user_id"):
        with get_connection() as con:
            con.execute("INSERT INTO historico (usuario_id, tipo, descricao, destino_id) VALUES (?, ?, ?, ?)", (session["user_id"], kind, label[:220], item_id))


DESTINOS_INICIAIS = [
    {"name":"Centro Histórico","municipality":"São Luís","icon":"🏛️","description":"Explore os casarões, os azulejos e a arquitetura histórica.","interests":["História","Cultura"],"latitude":-2.5297,"longitude":-44.3068},
    {"name":"Casa do Maranhão","municipality":"São Luís","icon":"🎭","description":"Reserve um momento para conhecer a cultura maranhense.","interests":["História","Cultura"],"latitude":-2.5202,"longitude":-44.3017},
    {"name":"Espigão Costeiro","municipality":"São Luís","icon":"🌊","description":"Finalize o passeio apreciando a paisagem da baía.","interests":["Praias","Natureza"],"latitude":-2.4882,"longitude":-44.3235},
    {"name":"Praia do Calhau","municipality":"São Luís","icon":"🏖️","description":"Uma das praias mais conhecidas de São Luís.","interests":["Praias","Gastronomia"],"latitude":-2.4857,"longitude":-44.2457},
    {"name":"Restaurante Feijão de Corda","municipality":"São Luís","icon":"🍛","description":"Comida regional nordestina. Estimativa de R$ 52 a R$ 130 por pessoa; confirme os preços atuais.","interests":["Gastronomia"],"latitude":-2.498362,"longitude":-44.240316},
    {"name":"Santuário de São José de Ribamar","municipality":"São José de Ribamar","icon":"⛪","description":"Conheça um importante ponto de fé e cultura local.","interests":["História","Cultura","Família"],"latitude":-2.561667,"longitude":-44.055556},
    {"name":"Orla de São José de Ribamar","municipality":"São José de Ribamar","icon":"🌊","description":"Inclua uma caminhada pela região da orla.","interests":["Praias","Natureza","Família"],"latitude":-2.5615,"longitude":-44.0550},
    {"name":"Gastronomia local de Ribamar","municipality":"São José de Ribamar","icon":"🍲","description":"Pesquise restaurantes e pratos típicos da região.","interests":["Gastronomia"],"latitude":-2.5615,"longitude":-44.0550},
    {"name":"Corredor das Rendas","municipality":"Raposa","icon":"🧵","description":"Conheça o artesanato e a tradição das rendeiras.","interests":["Cultura","História"],"latitude":-2.4250,"longitude":-44.0970},
    {"name":"Passeios de barco","municipality":"Raposa","icon":"🛶","description":"Pesquise operadores e condições dos passeios pela região.","interests":["Natureza","Praias"],"latitude":-2.4250,"longitude":-44.0950},
    {"name":"Culinária regional de Raposa","municipality":"Raposa","icon":"🍤","description":"Reserve tempo para experimentar sabores locais.","interests":["Gastronomia"],"latitude":-2.4250,"longitude":-44.0950},
    {"name":"Centro de Paço do Lumiar","municipality":"Paço do Lumiar","icon":"🏘️","description":"Explore a área central e seus pontos culturais.","interests":["História","Cultura"],"latitude":-2.5230,"longitude":-44.1010},
    {"name":"Áreas naturais de Paço do Lumiar","municipality":"Paço do Lumiar","icon":"🌿","description":"Pesquise locais de natureza e confirme o acesso antes de ir.","interests":["Natureza","Família"],"latitude":-2.5100,"longitude":-44.1000},
    {"name":"Sabores de Paço do Lumiar","municipality":"Paço do Lumiar","icon":"🍲","description":"Descubra restaurantes e a culinária da região.","interests":["Gastronomia"],"latitude":-2.5230,"longitude":-44.1010},
]




@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_database() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS destinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                municipio TEXT NOT NULL,
                descricao TEXT NOT NULL,
                icone TEXT NOT NULL,
                interesses TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        """)

        count = connection.execute(
            "SELECT COUNT(*) FROM destinos"
        ).fetchone()[0]

        if count == 0:
            connection.executemany(
                """INSERT INTO destinos
                   (nome, municipio, descricao, icone, interesses, latitude, longitude)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [(
                    item["name"], item["municipality"], item["description"],
                    item["icon"],
                    json.dumps(item["interests"], ensure_ascii=False),
                    item.get("latitude"), item.get("longitude")
                ) for item in DESTINOS_INICIAIS]
            )

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE, senha_hash TEXT NOT NULL, interesses TEXT NOT NULL DEFAULT '[]', criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), tipo TEXT NOT NULL, descricao TEXT NOT NULL, destino_id INTEGER, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS favoritos (usuario_id INTEGER NOT NULL REFERENCES usuarios(id), destino_id INTEGER NOT NULL REFERENCES destinos(id), criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(usuario_id, destino_id));
            CREATE TABLE IF NOT EXISTS roteiros_salvos (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), titulo TEXT NOT NULL, conteudo TEXT NOT NULL, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS avaliacoes (id INTEGER PRIMARY KEY, usuario_id INTEGER NOT NULL REFERENCES usuarios(id), destino_id INTEGER NOT NULL REFERENCES destinos(id), nota INTEGER NOT NULL CHECK(nota BETWEEN 1 AND 5), comentario TEXT NOT NULL, criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(usuario_id,destino_id));
            CREATE INDEX IF NOT EXISTS ix_hist_user ON historico(usuario_id, criado_em);
            CREATE INDEX IF NOT EXISTS ix_trips_user ON roteiros_salvos(usuario_id, criado_em);
        """)
    # Existing null coordinates may be an operator's correction; never repopulate them at startup.
    migrate(get_connection, DATABASE_PATH)
    seed_catalog(get_connection)


def atualizar_coordenadas_iniciais():
    with get_connection() as connection:
        for item in DESTINOS_INICIAIS:
            latitude = item.get("latitude")
            longitude = item.get("longitude")

            if latitude is None or longitude is None:
                continue

            connection.execute("""
                UPDATE destinos
                SET latitude = ?, longitude = ?
                WHERE nome = ?
                AND (latitude IS NULL OR longitude IS NULL)
            """, (latitude, longitude, item["name"]))


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    valid = all(isinstance(row[key], (int,float)) and not isinstance(row[key],bool) and math.isfinite(row[key]) for key in ('latitude','longitude'))
    valid = valid and -90 <= row['latitude'] <= 90 and -180 <= row['longitude'] <= 180
    metadata = destination_metadata(row)
    verified = valid and metadata.get('coordinates_status') == 'verified'
    culture = destination_culture(row['nome'])
    return {
        "id": row["id"], "name": row["nome"], "municipality": row["municipio"],
        "description": row["descricao"], "icon": row["icone"],
        "interests": json.loads(row["interesses"]),
        "latitude": row["latitude"], "longitude": row["longitude"],
        **metadata, 'location':{'valid':valid,'verified':verified,'status':'verified' if verified else 'unverified' if valid else 'pending'},
        'culture_tags':[item['id'] for item in culture], 'culture_context':culture
    }


@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/perfil")
@app.get("/historico")
@app.get("/favoritos")
@app.get("/meus-roteiros")
@app.get("/acessibilidade")
def internal_pages():
    return send_from_directory(FRONTEND_DIR, "painel.html")

@app.get("/explorar")
def explorar_page():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/planejar")
def planejar_page():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "message": "Explore+ SLZ API funcionando."})

@app.get('/cultura')
def culture_bookmark():
    return redirect('/catalogo#cultura',code=302)

@app.get('/api/culture')
def culture_content_api():
    return jsonify(results=cultural_content(), interests=CULTURAL_INTERESTS)


@app.get("/api/destinos")
def pesquisar_destinos():
    termo = request.args.get("q", "").strip()
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM destinos ORDER BY municipio,nome").fetchall()
    def normalized(value):
        return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c))
    municipality = request.args.get('municipality', '')
    category = request.args.get('category', '')
    access = request.args.getlist('access')
    cultures = [key for key in request.args.getlist('culture') if key]
    interest = request.args.get('interest','')
    if any(key not in {item['id'] for item in cultural_content()} for key in cultures):
        return jsonify(error='Filtro cultural inválido.'),400
    fields = []
    for item in access:
        if item in ACCESS_GROUPS: fields.extend(ACCESS_GROUPS[item])
        elif item in ACCESS_FIELDS: fields.append(item)
        else: return jsonify(error='Filtro de acessibilidade inválido.'), 400
    results = [row_to_dict(row) for row in rows]
    results = [item for item in results if
               (not termo or normalized(termo) in normalized(' '.join([item['name'],item['municipality'],item['description'],*item['interests']])))
               and (not municipality or item['municipality'] == municipality)
               and (not category or item['category'] == category)
               and (not cultures or any(key in item['culture_tags'] for key in cultures))
               and (not interest or any(normalized(interest) in normalized(key) for key in item['interests']))
               and (not fields or confirmed_features(item, fields))]
    if termo and len(termo) <= 120:
        record_history("pesquisa", f"Pesquisa: {termo}")
    return jsonify({"query": termo, "total": len(results), "results": results,
                    'map':{'valid_coordinates':sum(p['location']['valid'] for p in results),'verified_coordinates':sum(p['location']['verified'] for p in results),'pending_coordinates':sum(not p['location']['verified'] for p in results)},
                    "access_note":"Os filtros de acessibilidade incluem apenas recursos confirmados com fonte e data. Ausência de resultado não significa ausência do recurso."})


@app.post("/api/roteiro")
def gerar_roteiro():
    data = request.get_json(silent=True) or {}
    try:
        destino = str(data.get("destination", "São Luís")).strip()
        dias = int(data.get("days", 1))
        orcamento = float(data.get("budget", 0))
        pessoas = str(data.get("people", "1"))
        transporte = str(data.get("transport", "Ainda não decidi"))
        interesses = data.get("interests", [])
        acessibilidade = data.get("access", [])
        if not 1 <= dias <= 30 or not math.isfinite(orcamento) or orcamento <= 0:
            return jsonify({"error": "Informe um orçamento positivo e uma quantidade de dias válida."}), 400
        if not isinstance(interesses, list) or not interesses:
            return jsonify({"error": "Escolha pelo menos um interesse."}), 400
        if (any(not isinstance(item, str) for item in interesses)
                or not isinstance(acessibilidade, list)
                or any(not isinstance(item, str) for item in acessibilidade)):
            return jsonify({"error": "Interesses e acessibilidade devem ser listas de textos."}), 400
        with get_connection() as connection:
            if destino == "Ilha de São Luís":
                rows = connection.execute("SELECT * FROM destinos WHERE municipio != 'Alcântara' ORDER BY municipio, nome").fetchall()
            else:
                rows = connection.execute("SELECT * FROM destinos WHERE municipio = ? ORDER BY nome", (destino,)).fetchall()
        lugares = [row_to_dict(row) for row in rows]
        theme = data.get('theme') or ''
        if theme not in ('','historia','reggae','sabores','popular','quilombo'):
            return jsonify(error='Tema editorial inválido.'),400
        if theme == 'reggae': lugares = [p for p in lugares if 'Reggae' in p['name']]
        elif theme == 'quilombo': lugares = [p for p in lugares if p['name'] in ('Centro de Cultura e Turismo do Quilombo Urbano','Mercado Municipal da Liberdade','Bumba Meu Boi da Floresta')]
        elif theme == 'historia': lugares = [p for p in lugares if p['category'] in ('Patrimônio','Museu','Praça')]
        elif theme == 'sabores': lugares = [p for p in lugares if 'Gastronomia' in p['interests'] or 'Gastronomia' in p['name']]
        elif theme == 'popular': lugares = [p for p in lugares if p['category'] in ('Cultura','Artesanato') or p['name']=='Casa do Maranhão']
        access_aliases = {'Mobilidade reduzida':'mobility','Deficiência visual':'visual','Deficiência auditiva':'hearing','Intelectual / cognitiva':'cognitive','Necessidades sensoriais':'sensory'}
        required_features = []
        for item in acessibilidade:
            key = access_aliases.get(item,item)
            if key in ACCESS_GROUPS: required_features.extend(ACCESS_GROUPS[key])
            elif key in ACCESS_FIELDS: required_features.append(key)
            elif key != 'Crianças':
                return jsonify(error='Necessidade de acessibilidade inválida.'), 400
        if required_features:
            lugares = [place for place in lugares if confirmed_features(place, required_features)]
            if not lugares:
                return jsonify(error='Ainda não há locais com todos os recursos selecionados confirmados. Consulte as fichas, envie sugestões de acessibilidade ou ajuste os filtros. Nenhum trajeto acessível foi validado.'), 422
        specific = [CULTURAL_INTERESTS[item] for item in interesses if item in CULTURAL_INTERESTS]
        selecionados = [place for place in lugares if any(i in interesses for i in place["interests"]) or any(key in place['culture_tags'] for key in specific)]
        if not selecionados:
            if specific:
                return jsonify(error='Ainda não há espaços associados aos interesses culturais selecionados nesta região. A tradição permanece disponível no conteúdo editorial, sem inventar local ou programação.'),422
            selecionados = lugares
        if specific:
            selecionados.sort(key=lambda p:not any(key in p['culture_tags'] for key in specific))
        if not selecionados:
            return jsonify({"error": "Não há destinos cadastrados para essa região."}), 404

        dias_resultado = []
        for index in range(dias):
            primeiro = selecionados[(index * 2) % len(selecionados)]
            segundo = selecionados[(index * 2 + 1) % len(selecionados)]
            stops = [
                {"name": primeiro["name"], "icon": primeiro["icon"], "description": primeiro["description"]}
            ]
            if segundo["name"] != primeiro["name"]:
                stops.append({"name": segundo["name"], "icon": segundo["icon"], "description": segundo["description"]})
            titulo = "Comece explorando" if index == 0 else ("Feche a viagem com boas memórias" if index == dias - 1 else "Mais descobertas pela Ilha")
            dias_resultado.append({"title": f"Dia {index + 1} · {titulo}", "stops": stops})

        special = None
        if not required_features and 1000 <= orcamento <= 2000 and any(i in interesses for i in ("Natureza", "Praias", "Família")):
            special = {
                "title": "⛵ Experiência especial · Raposa", "icon": "🛶",
                "name": "Passeio náutico pelas Fronhas Maranhenses",
                "description": "Pesquise passeios de barco pela região de Raposa, com possíveis paradas conforme maré, segurança e disponibilidade do operador.",
                "note": "A faixa de R$ 1.000 a R$ 2.000 é um critério de planejamento do projeto, não um preço oficial. Confirme o valor final, transporte, participantes e condições com o operador.",
                "url": "https://enjoymaranhao.com.br/servicos/passeio-raposa/"
            }

        per_day = orcamento / dias
        try:
            numero_pessoas = int(pessoas.split()[0])
        except (ValueError, IndexError):
            numero_pessoas = 6 if "6" in pessoas else 1
        summary = {
            "destination": destino, "days": dias, "budget": orcamento,
            "people": pessoas, "transport": transporte, "interests": interesses,
            "access": acessibilidade, "per_day": per_day,
            "per_person_day": per_day / max(numero_pessoas, 1)
        }
        plain_lines = [f"Roteiro Explore+ SLZ — {destino}, {dias} dia(s), orçamento {orcamento:.2f} BRL"]
        for day in dias_resultado:
            plain_lines.append("\n" + day["title"])
            plain_lines.extend(f"- {stop['name']}: {stop['description']}" for stop in day["stops"])
        if special:
            plain_lines.append("\n" + special["title"] + "\n" + special["name"] + ": " + special["description"])
        plain_lines.append("\nSugestão inicial: confirme horários, deslocamentos, custos e acessibilidade antes de sair.")
        record_history("roteiro", f"Roteiro gerado: {destino} · {dias} dia(s)")
        return jsonify({
            "summary": summary, "days": dias_resultado, "special_experience": special,
            "note": "Sugestão editorial baseada no catálogo local. Não há validação de trajeto, travessias, transporte ou continuidade das calçadas. Recursos de acessibilidade selecionados exigem fonte e data por local. Confirme condições, custos e horários antes de sair.",
            "plain_text": "\n".join(plain_lines)
        })
    except (TypeError, ValueError, OverflowError):
        return jsonify({"error": "Os dados enviados estão em formato inválido."}), 400


@app.get("/api/destinos/verificar")
def verificar_destinos():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT nome, municipio, latitude, longitude
            FROM destinos
            ORDER BY municipio, nome
        """).fetchall()

    return jsonify([
        dict(row) for row in rows
    ])


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not 2 <= len(name) <= 100 or not 5 <= len(email) <= 254 or "@" not in email or not 8 <= len(password) <= 128:
        return jsonify({"error":"Informe nome, e-mail válido e senha de pelo menos 8 caracteres."}), 400
    try:
        with get_connection() as con:
            cur = con.execute("INSERT INTO usuarios (nome,email,senha_hash) VALUES (?,?,?)", (name,email,generate_password_hash(password)))
            uid = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error":"Este e-mail já está cadastrado."}), 409
    session.clear(); session["user_id"] = uid; session["csrf"] = secrets.token_urlsafe(32)
    return jsonify({"user":{"id":uid,"name":name,"email":email},"csrf":session["csrf"]}), 201

@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    with get_connection() as con:
        row = con.execute("SELECT * FROM usuarios WHERE email=?",(email,)).fetchone()
    if not row or not check_password_hash(row["senha_hash"], password):
        return jsonify({"error":"E-mail ou senha incorretos."}), 401
    session.clear();session["user_id"]=row["id"];session["csrf"]=secrets.token_urlsafe(32)
    return jsonify({"user":{"id":row["id"],"name":row["nome"],"email":row["email"]},"csrf":session["csrf"]})

@app.get("/api/auth/me")
def me():
    uid=session.get("user_id")
    if not uid:
        return jsonify({"user":None})
    with get_connection() as con:
        row=con.execute("SELECT id,nome,email,interesses,criado_em FROM usuarios WHERE id=?",(uid,)).fetchone()
    if not row:
        session.clear();return jsonify({"user":None})
    return jsonify({"user":{"id":row["id"],"name":row["nome"],"email":row["email"],"interests":json.loads(row["interesses"]),"created_at":row["criado_em"]},"csrf":session.get("csrf")})

@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"ok":True})

@app.patch("/api/perfil")
@login_required
def edit_profile():
    data=request.get_json(silent=True) or {}
    name=str(data.get("name", "")).strip()
    interests=data.get("interests",[])
    if not 2<=len(name)<=100 or not isinstance(interests,list) or len(interests)>12 or any(not isinstance(v,str) or len(v)>40 for v in interests):
        return jsonify({"error":"Dados do perfil inválidos."}),400
    with get_connection() as con:
        con.execute("UPDATE usuarios SET nome=?, interesses=? WHERE id=?",(name,json.dumps(interests,ensure_ascii=False),session["user_id"]))
    return jsonify({"ok":True})

@app.get("/api/historico")
@login_required
def history():
    with get_connection() as con:
        rows=con.execute("SELECT id,tipo,descricao,criado_em FROM historico WHERE usuario_id=? ORDER BY id DESC LIMIT 100",(session["user_id"],)).fetchall()
    return jsonify({"results":[dict(x) for x in rows]})

@app.delete("/api/historico")
@login_required
def clear_history():
    with get_connection() as con:
        con.execute("DELETE FROM historico WHERE usuario_id=?",(session["user_id"],))
    return jsonify({"ok":True})

@app.get("/api/favoritos")
@login_required
def favorites():
    with get_connection() as con:
        rows=con.execute("SELECT d.* FROM favoritos f JOIN destinos d ON d.id=f.destino_id WHERE f.usuario_id=? ORDER BY f.criado_em DESC",(session["user_id"],)).fetchall()
    return jsonify({"results":[row_to_dict(x) for x in rows]})

@app.put("/api/favoritos/<int:destination_id>")
@login_required
def add_favorite(destination_id):
    with get_connection() as con:
        dest=con.execute("SELECT nome FROM destinos WHERE id=?",(destination_id,)).fetchone()
        if not dest:return jsonify({"error":"Destino não encontrado."}),404
        inserted = con.execute("INSERT OR IGNORE INTO favoritos(usuario_id,destino_id) VALUES (?,?)",(session["user_id"],destination_id)).rowcount
    if inserted:
        record_history("favorito",f"Favoritou {dest['nome']}",destination_id)
    return jsonify({"ok":True})

@app.delete("/api/favoritos/<int:destination_id>")
@login_required
def remove_favorite(destination_id):
    with get_connection() as con:
        con.execute("DELETE FROM favoritos WHERE usuario_id=? AND destino_id=?",(session["user_id"],destination_id))
    return jsonify({"ok":True})

@app.get("/api/roteiros-salvos")
@login_required
def saved_trips():
    with get_connection() as con:
        rows=con.execute("SELECT id,titulo,conteudo,criado_em FROM roteiros_salvos WHERE usuario_id=? ORDER BY id DESC LIMIT 100",(session["user_id"],)).fetchall()
    return jsonify({"results":[{"id":r["id"],"title":r["titulo"],"trip":json.loads(r["conteudo"]),"created_at":r["criado_em"]} for r in rows]})

@app.post("/api/roteiros-salvos")
@login_required
def save_trip():
    data=request.get_json(silent=True) or {}
    title=str(data.get("title", "Meu roteiro")).strip()[:120]
    trip=data.get("trip")
    if not title or not isinstance(trip,dict) or not isinstance(trip.get("summary"),dict) or not isinstance(trip.get("days"),list):
        return jsonify({"error":"Roteiro inválido."}),400
    if any(not isinstance(day, dict) or not isinstance(day.get("stops"), list)
           or any(not isinstance(stop, dict) for stop in day["stops"])
           for day in trip["days"]):
        return jsonify({"error":"Dias e paradas do roteiro inválidos."}),400
    content=json.dumps(trip,ensure_ascii=False)
    if len(content)>100000:return jsonify({"error":"Roteiro muito grande."}),400
    with get_connection() as con:
        cur=con.execute("INSERT INTO roteiros_salvos(usuario_id,titulo,conteudo) VALUES (?,?,?)",(session["user_id"],title,content))
    record_history("roteiro",f"Salvou {title}")
    return jsonify({"id":cur.lastrowid,"ok":True}),201

@app.delete("/api/roteiros-salvos/<int:trip_id>")
@login_required
def delete_trip(trip_id):
    with get_connection() as con:
        con.execute("DELETE FROM roteiros_salvos WHERE id=? AND usuario_id=?",(trip_id,session["user_id"]))
    return jsonify({"ok":True})

@app.get("/api/avaliacoes/<int:destination_id>")
def reviews(destination_id):
    with get_connection() as con:
        rows=con.execute("SELECT a.nota,a.comentario,a.criado_em,u.nome FROM avaliacoes a JOIN usuarios u ON a.usuario_id=u.id WHERE a.destino_id=? ORDER BY a.id DESC LIMIT 50",(destination_id,)).fetchall()
    return jsonify({"results":[dict(r) for r in rows]})

@app.post("/api/avaliacoes/<int:destination_id>")
@login_required
def submit_review(destination_id):
    data=request.get_json(silent=True) or {}
    try: rating=int(data.get("rating",0))
    except (ValueError,TypeError,OverflowError):rating=0
    comment=str(data.get("comment", "")).strip()
    if not 1<=rating<=5 or not 5<=len(comment)<=1000:return jsonify({"error":"Avalie de 1 a 5 e escreva entre 5 e 1000 caracteres."}),400
    with get_connection() as con:
        if not con.execute("SELECT 1 FROM destinos WHERE id=?",(destination_id,)).fetchone():return jsonify({"error":"Destino não encontrado."}),404
        con.execute("""INSERT INTO avaliacoes(usuario_id,destino_id,nota,comentario) VALUES (?,?,?,?)
            ON CONFLICT(usuario_id,destino_id) DO UPDATE SET nota=excluded.nota,comentario=excluded.comentario,criado_em=CURRENT_TIMESTAMP""",(session["user_id"],destination_id,rating,comment))
    return jsonify({"ok":True})

@app.get("/api/resumo")
@login_required
def summary_stats():
    with get_connection() as con:
        uid=session["user_id"]
        stats={"searches":con.execute("SELECT COUNT(*) FROM historico WHERE usuario_id=? AND tipo='pesquisa'",(uid,)).fetchone()[0],"favorites":con.execute("SELECT COUNT(*) FROM favoritos WHERE usuario_id=?",(uid,)).fetchone()[0],"trips":con.execute("SELECT COUNT(*) FROM roteiros_salvos WHERE usuario_id=?",(uid,)).fetchone()[0]}
    return jsonify(stats)

init_database()
install(app, get_connection, login_required, row_to_dict, FRONTEND_DIR)

if __name__ == "__main__":
    print("Explore+ SLZ disponível em http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

