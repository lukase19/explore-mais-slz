"""Migrações incrementais e cópia lógica do esquema anterior, sem dados pessoais."""
from datetime import datetime, timezone
from pathlib import Path
import json

ACCESS_FIELDS = {
 'step_free':'Acesso sem degraus', 'ramp':'Rampas', 'circulation':'Circulação para cadeira de rodas',
 'toilet':'Sanitário adaptado', 'transport':'Transporte acessível', 'signage':'Sinalização acessível',
 'braille':'Braille', 'audio_description':'Audiodescrição', 'libras':'Libras', 'captions':'Legendas',
 'sensory':'Ambiente sensorial', 'specialist':'Atendimento especializado'
}
ACCESS_GROUPS = {
 'mobility':['step_free','circulation','toilet'], 'visual':['audio_description','signage'],
 'hearing':['libras','captions'], 'cognitive':['signage','specialist'], 'sensory':['sensory']
}


def migrate(connect, database_path):
    with connect() as con:
        con.execute('BEGIN IMMEDIATE')
        con.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        if con.execute('SELECT 1 FROM schema_migrations WHERE version=2').fetchone():
            return
        schema = '\n\n'.join(row[0] + ';' for row in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type,name"))
        backup = Path(database_path).parent / 'backups'
        backup.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        (backup / f'schema_before_v2_{stamp}.sql').write_text('-- Esquema anterior à expansão 2. Não contém dados de usuários.\n' + schema, encoding='utf-8')
        existing = {row[1] for row in con.execute('PRAGMA table_info(destinos)')}
        columns = {'category':"TEXT NOT NULL DEFAULT 'Experiência'", 'address':"TEXT NOT NULL DEFAULT ''", 'source_url':"TEXT NOT NULL DEFAULT ''", 'verified_at':"TEXT", 'review_status':"TEXT NOT NULL DEFAULT 'legacy_unverified'", 'coordinates_status':"TEXT NOT NULL DEFAULT 'unverified'", 'access_json':"TEXT NOT NULL DEFAULT '{}'"}
        for column, definition in columns.items():
            if column not in existing:
                con.execute(f'ALTER TABLE destinos ADD COLUMN {column} {definition}')
        # Execute individual statements inside the same transaction; no executescript implicit commit.
        statements = [
        '''CREATE TABLE IF NOT EXISTS profiles (
          user_id INTEGER PRIMARY KEY REFERENCES usuarios(id), handle TEXT NOT NULL UNIQUE COLLATE NOCASE,
          bio TEXT NOT NULL DEFAULT '', municipality TEXT NOT NULL DEFAULT '', theme TEXT NOT NULL DEFAULT 'forest',
          is_public INTEGER NOT NULL DEFAULT 0 CHECK(is_public IN (0,1)), discoverable INTEGER NOT NULL DEFAULT 0 CHECK(discoverable IN (0,1)),
          favorites_visibility TEXT NOT NULL DEFAULT 'private' CHECK(favorites_visibility IN ('private','friends','public')),
          allow_invites INTEGER NOT NULL DEFAULT 1 CHECK(allow_invites IN (0,1)), access_preferences TEXT NOT NULL DEFAULT '[]',
          access_consent INTEGER NOT NULL DEFAULT 0 CHECK(access_consent IN (0,1)),
          avatar_x INTEGER NOT NULL DEFAULT 50, avatar_y INTEGER NOT NULL DEFAULT 50,
          cover_x INTEGER NOT NULL DEFAULT 50, cover_y INTEGER NOT NULL DEFAULT 50)''',
        '''CREATE TABLE IF NOT EXISTS media (
          token TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES usuarios(id), kind TEXT NOT NULL CHECK(kind IN ('avatar','cover')),
          data BLOB NOT NULL, mime TEXT NOT NULL DEFAULT 'image/jpeg', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(user_id,kind))''',
        '''CREATE TABLE IF NOT EXISTS friendships (
          id INTEGER PRIMARY KEY, sender_id INTEGER NOT NULL REFERENCES usuarios(id), recipient_id INTEGER NOT NULL REFERENCES usuarios(id),
          status TEXT NOT NULL CHECK(status IN ('pending','accepted','rejected','removed')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          CHECK(sender_id != recipient_id))''',
        'CREATE UNIQUE INDEX IF NOT EXISTS friendship_pair ON friendships(min(sender_id,recipient_id),max(sender_id,recipient_id))',
        '''CREATE TABLE IF NOT EXISTS blocks (
          blocker_id INTEGER NOT NULL REFERENCES usuarios(id), blocked_id INTEGER NOT NULL REFERENCES usuarios(id),
          PRIMARY KEY(blocker_id,blocked_id), CHECK(blocker_id != blocked_id))''',
        '''CREATE TABLE IF NOT EXISTS trip_invites (
          id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          sender_id INTEGER NOT NULL REFERENCES usuarios(id), recipient_id INTEGER NOT NULL REFERENCES usuarios(id),
          status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected','revoked')),
          role TEXT NOT NULL DEFAULT 'editor' CHECK(role IN ('viewer','editor')), UNIQUE(trip_id,recipient_id))''',
        '''CREATE TABLE IF NOT EXISTS trip_notes (
          id INTEGER PRIMARY KEY, trip_id INTEGER NOT NULL REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          user_id INTEGER NOT NULL REFERENCES usuarios(id), text TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE IF NOT EXISTS trip_shares (
          token TEXT PRIMARY KEY, trip_id INTEGER NOT NULL UNIQUE REFERENCES roteiros_salvos(id) ON DELETE CASCADE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        '''CREATE TABLE IF NOT EXISTS vouchers (
          id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, sender_id INTEGER NOT NULL REFERENCES usuarios(id),
          recipient_id INTEGER NOT NULL REFERENCES usuarios(id), destination_id INTEGER NOT NULL REFERENCES destinos(id),
          message TEXT NOT NULL, theme TEXT NOT NULL CHECK(theme IN ('azulejo','sol','reggae')),
          expires_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'issued'
          CHECK(status IN ('issued','sent','redeemed','expired','cancelled')),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, redeemed_at TEXT,
          CHECK(sender_id != recipient_id))''',
        '''CREATE TABLE IF NOT EXISTS accessibility_reports (
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES usuarios(id), destination_id INTEGER NOT NULL REFERENCES destinos(id),
          feature TEXT NOT NULL, proposed_status TEXT NOT NULL CHECK(proposed_status IN ('confirmed','unavailable','unverified')),
          description TEXT NOT NULL, source_url TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''',
        'CREATE INDEX IF NOT EXISTS friend_recipient ON friendships(recipient_id,status)',
        'CREATE INDEX IF NOT EXISTS invite_recipient ON trip_invites(recipient_id,status)',
        'CREATE INDEX IF NOT EXISTS voucher_recipient ON vouchers(recipient_id,status)',
        'CREATE INDEX IF NOT EXISTS dest_filters ON destinos(municipio,category)'
        ]
        for statement in statements:
            con.execute(statement)
        con.execute('INSERT INTO schema_migrations(version) VALUES (2)')


def destination_metadata(row):
    keys = set(row.keys())
    access = json.loads(row['access_json']) if 'access_json' in keys else {}
    return {**{key:row[key] for key in ('category','address','source_url','verified_at','review_status','coordinates_status') if key in keys},
            'image_url':'/destination-fallback.svg', 'image_credit':'Ilustração original Explore+ SLZ; não é fotografia do local.',
            'accessibility':{key:access.get(key, {'status':'unverified','source_url':None,'verified_at':None}) for key in ACCESS_FIELDS}}
