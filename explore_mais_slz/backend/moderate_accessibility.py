"""Moderação local, restrita a quem administra o arquivo SQLite.
Listar: python -m backend.moderate_accessibility list
Aprovar: python -m backend.moderate_accessibility approve 1 --source https://... --date 2026-11-06 --reviewer Nome
Rejeitar: python -m backend.moderate_accessibility reject 1
"""
import argparse
from datetime import date
import json
from .app import get_connection
from .migrations import ACCESS_FIELDS


def main():
    parser=argparse.ArgumentParser(description='Revisão manual de sugestões; confirme a evidência antes de aprovar.')
    parser.add_argument('action',choices=['list','approve','reject'])
    parser.add_argument('report_id',type=int,nargs='?')
    parser.add_argument('--source')
    parser.add_argument('--date',dest='verified_date')
    parser.add_argument('--reviewer')
    args=parser.parse_args()
    with get_connection() as con:
        if args.action=='list':
            rows=con.execute("SELECT r.id,d.nome,r.feature,r.proposed_status,r.description,r.source_url FROM accessibility_reports r JOIN destinos d ON d.id=r.destination_id WHERE r.status='pending' ORDER BY r.id").fetchall()
            print(json.dumps([dict(row) for row in rows],ensure_ascii=False,indent=2));return
        row=con.execute("SELECT * FROM accessibility_reports WHERE id=? AND status='pending'",(args.report_id,)).fetchone()
        if not row:parser.error('Sugestão pendente não encontrada.')
        if args.action=='reject':
            con.execute("UPDATE accessibility_reports SET status='rejected' WHERE id=?",(row['id'],));print('Sugestão rejeitada.');return
        if not args.source or not args.source.startswith('https://') or not args.reviewer:
            parser.error('A aprovação exige fonte HTTPS e identificação do revisor.')
        try:
            verified=date.fromisoformat(args.verified_date or '')
            if verified>date.today():raise ValueError
        except ValueError:parser.error('Informe uma data válida não futura em --date.')
        if row['feature'] not in ACCESS_FIELDS:parser.error('Recurso inválido.')
        destination=con.execute('SELECT access_json FROM destinos WHERE id=?',(row['destination_id'],)).fetchone()
        data=json.loads(destination['access_json'])
        data[row['feature']]={'status':row['proposed_status'],'source_url':args.source,'verified_at':verified.isoformat(),'reviewed_by':args.reviewer}
        con.execute('UPDATE destinos SET access_json=? WHERE id=?',(json.dumps(data,ensure_ascii=False),row['destination_id']))
        con.execute("UPDATE accessibility_reports SET status='approved' WHERE id=?",(row['id'],))
        print('Sugestão aprovada. Apenas o recurso revisado foi atualizado.')


if __name__=='__main__':main()
