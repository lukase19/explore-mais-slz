"""Gera cópia SQLite consistente, sem importar Flask, apagar ou migrar a origem."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sqlite3


def backup(source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if source == destination or not source.is_file():
        raise ValueError('Selecione um banco de origem existente e outro caminho de destino.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Reserva exclusiva: nunca substituir backups ou bancos existentes.
    with destination.open('xb'):
        pass
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as original:
        with closing(sqlite3.connect(destination)) as copied:
            original.backup(copied)
            if copied.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
                raise ValueError('A cópia não passou na verificação de integridade. Preserve a origem.')
    return destination


def main():
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=root / 'backend' / 'explore_slz.db')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = args.output or root / '.artifacts' / f'explore-upload-{stamp}.sqlite'
    result = backup(args.source, output)
    print(f'Cópia pronta para selecionar na tela de importação: {result}')
    print(f'SHA256: {hashlib.sha256(result.read_bytes()).hexdigest()}')


if __name__ == '__main__':
    main()
