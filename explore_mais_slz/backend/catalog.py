"""Catálogo editorial com fontes oficiais consultadas em 06/11/2026.
Existência documental não equivale à validação de acesso, horários ou coordenadas.
Os campos desconhecidos permanecem vazios; nenhum marcador novo é estimado.
"""
import json

SITE='https://turismosaoluis.com.br/'
GROUPS=[
(SITE+'o-que-fazer/centro-historico/','São Luís','Patrimônio',[
 ('Centro Histórico','Centro Histórico','Percurso pelo patrimônio arquitetônico da cidade.'),
 ('Rua Portugal','Rua Portugal, Praia Grande','Um caminho para observar fachadas e azulejos.'),
 ('Rua do Giz','Rua do Giz, Praia Grande','Uma rua para descobrir a cidade a pé.'),
 ('Praia Grande','Praia Grande, Centro Histórico','Bairro para começar uma descoberta cultural.'),
 ('Beco Catarina Mina','Beco Catarina Mina, Praia Grande','Uma passagem para incluir no percurso histórico.'),
 ('Fonte do Ribeirão','','Uma parada para conhecer o patrimônio urbano.'),
 ('Fonte das Pedras','','Um ponto para explorar outra camada da cidade.'),
 ('Teatro João do Vale','','Espaço para pesquisar a produção cênica local.'),
 ('Praça dos Poetas','','Uma pausa para conectar paisagem e literatura.'),
 ('Casa do Maranhão','','Uma parada para conhecer expressões culturais maranhenses.')]),
(SITE+'o-que-fazer/museus/','São Luís','Museu',[
 ('Museu da Gastronomia Maranhense','Rua da Estrela, 82','Um encontro com saberes da cozinha regional.'),
 ('Museu do Reggae','Rua da Estrela, 124','Uma aproximação com a memória musical do reggae.'),
 ('Casa de Nhozinho','Rua Portugal, 185','Artesanato e memória do fazer popular.'),
 ('Museu de Artes Visuais','Rua Portugal','Um convite a conhecer a produção visual.'),
 ('Museu de Arte Sacra','Praça Pedro II, Palácio Episcopal','Um olhar sobre arte e religiosidade.'),
 ('Arquivo Público do Estado do Maranhão','Rua de Nazaré, 218','Documentos que ajudam a pesquisar a cidade.'),
 ('Museu de História Natural e Arqueologia','Rua do Giz','Uma descoberta sobre arqueologia e natureza.'),
 ('Palácio Cristo Rei','Praça Gonçalves Dias','Memória universitária em um edifício histórico.')]),
('https://turismo.ma.gov.br/programas-ou-campanhas/cidades-patrimonio-historia-e-arquitetura','São Luís','Patrimônio',[
 ('Palácio dos Leões','Avenida Pedro II','Arquitetura para observar durante um percurso histórico.'),
 ('Palácio de La Ravardière','Avenida Pedro II','Um ponto para pesquisar a história municipal.'),
 ('Teatro Arthur Azevedo','','Um espaço para conhecer a história das artes.'),
 ('Convento das Mercês','Rua Jacinto Maia, Desterro','Um convite a explorar memória e arquitetura.')]),
(SITE+'o-que-fazer/igrejas/','São Luís','Patrimônio',[
 ('Catedral da Sé','Praça Pedro II','Um ponto de encontro entre fé e patrimônio.'),
 ('Igreja Nossa Senhora do Carmo','Largo do Carmo','Uma parada no percurso de patrimônio religioso.'),
 ('Igreja de São José do Desterro','Desterro, Centro Histórico','Uma descoberta no bairro do Desterro.'),
 ('Igreja de Santo Antônio','Praça Antônio Lobo','Um lugar para conhecer história e religiosidade.'),
 ('Igreja Nossa Senhora dos Remédios','Praça Gonçalves Dias','Uma visita para observar a arquitetura religiosa.'),
 ('Igreja de São João','Rua de São João com Rua da Paz','Uma parada para explorar o patrimônio religioso.'),
 ('Igreja Nossa Senhora do Rosário dos Pretos','Rua do Egito','Um lugar para conhecer memória e fé.'),
 ('Igreja de Santana','Rua de Santana','Uma descoberta no percurso das igrejas históricas.')]),
(SITE+'o-que-fazer/pracas/','São Luís','Praça',[
 ('Praça Nauro Machado','Praia Grande','Um espaço para observar a vida da cidade.'),
 ('Praça Benedito Leite','Entre Rua de Nazaré, Palma e Beco da Sé','Uma pausa entre percursos do centro.'),
 ('Praça Gonçalves Dias','Largo dos Amores','Um mirante para uma pausa na descoberta.'),
 ('Praça João Lisboa','Centro','Um ponto para conversar sobre memória urbana.'),
 ('Praça da Faustina','Rua do Giz','Uma praça ligada às expressões culturais.'),
 ('Praça Deodoro','Centro','Um espaço público para incluir no percurso.'),
 ('Praça do Pantheon','Em frente à Biblioteca Benedito Leite','Um passeio para aproximar literatura e cidade.'),
 ('Praça Maria Aragão','Próxima à Praça Gonçalves Dias','Um lugar de memória e encontro.')]),
(SITE+'o-que-fazer/parques/','São Luís','Natureza',[
 ('Parque da Lagoa da Jansen','','Uma opção para observar a paisagem urbana.'),
 ('Parque Ecológico do Sítio do Rangedor','','Um convite ao contato com áreas verdes.'),
 ('Parque do Bom Menino','','Uma pausa verde no ritmo da cidade.'),
 ('Parque Botânico da Vale','','Uma oportunidade de conhecer ações de educação ambiental.'),
 ('Reserva do Itapiracó','','Uma paisagem para pesquisar antes do passeio.'),
 ('Parque da Juçara Rosa Mochel','','Um convite a aproximar natureza e cultura.')]),
(SITE+'o-que-fazer/praias/','São Luís','Praia',[
 ('Praia de São Marcos','Avenida Litorânea','Uma paisagem para incluir no passeio costeiro.'),
 ('Praia do Calhau','Avenida Litorânea','Um encontro com a paisagem da orla.'),
 ('Praia da Ponta d’Areia','Ponta d’Areia','Uma parada no percurso pela costa.'),
 ('Espigão Costeiro','Ponta d’Areia','Um ponto para observar a paisagem da baía.')]),
(SITE+'experiencias/roteiro-quilombo-cultural-de-sao-luis/','São Luís','Cultura',[
 ('Centro de Cultura e Turismo do Quilombo Urbano','Rua Gregório de Matos, s/n, Liberdade','Um ponto para conhecer iniciativas da comunidade.'),
 ('Mercado Municipal da Liberdade','Liberdade','Um lugar de encontro e vida comunitária.'),
 ('Bumba Meu Boi da Floresta','Liberdade','Uma referência cultural; visita depende do grupo.')]),
('https://raposa.ma.gov.br/secretario_de_turismo_acompanha_rota_turistica_em_raposa_com_casal_de_influenciadores_digitais','Raposa','Natureza',[
 ('Passeios de barco','','Experiência condicionada à maré e ao operador.'),
 ('Praia de Carimã','','Paisagem costeira; consulte condições de travessia.'),
 ('Praia dos Currais','','Uma descoberta costeira que exige planejamento.'),
 ('Praia do Garrancho','','Um encontro com a paisagem de Raposa.')]),
('https://turismo.ma.gov.br/noticias/rendeiras-da-raposa-a-arte-que-virou-patrimonio-e-orgulho-do-maranhao','Raposa','Artesanato',[
 ('Corredor das Rendas','','Um convite a conhecer o trabalho das rendeiras.')]),
('https://www.saojosederibamar.ma.gov.br/detalhe-da-materia/info/148764/sao-jose-de-ribamar-testa-roteiro-turistico-que-une-fe-gastronomia-e-tradicao-cultural-maranhense/','São José de Ribamar','Cultura',[
 ('Santuário de São José de Ribamar','','Um destino de fé e memória local.'),
 ('Casa Gamela','','Um espaço citado no roteiro cultural municipal.'),
 ('Centro de Criatividade de São José de Ribamar','','Uma referência para pesquisar a produção local.')]),
('https://www.gov.br/museus/pt-br/museus-ibram/museu-historico-de-alcantara','Alcântara','Museu',[
 ('Museu Histórico de Alcântara','Praça Gomes de Castro, 7, Matriz','Uma aproximação com a memória de Alcântara.')]),
('https://museudealcantara.museus.gov.br/wp-content/uploads/2022/06/MAPA-alcantara-A2-frente-e-verso-0704-compactado.pdf','Alcântara','Patrimônio',[
 ('Rua da Amargura','Rua da Amargura','Um percurso para observar vestígios da cidade.'),
 ('Igreja Nossa Senhora do Carmo de Alcântara','','Uma parada no patrimônio religioso de Alcântara.'),
 ('Igreja do Desterro e Sinos','','Um ponto para pesquisar a memória local.'),
 ('Pelourinho de Alcântara','Praça da Matriz','Um marco para refletir sobre história e violência.')]),
('https://turismo.ma.gov.br/programas-ou-campanhas/sao-luis-alcantara','Alcântara','Patrimônio',[
 ('Casa da Câmara e Cadeia de Alcântara','Praça da Matriz','Um encontro com a arquitetura e memória institucional.'),
 ('Casa do Divino de Alcântara','','Uma referência para pesquisar práticas culturais locais.')]),
('https://pacodolumiar.ma.gov.br/midia/Paco-do-Lumiar-inicia-comemoracoes-dos-65-anos-com-missa-solene-e-atos-civicos_348','Paço do Lumiar','Patrimônio',[
 ('Igreja Nossa Senhora da Luz','Sede de Paço do Lumiar','Uma referência de fé na sede municipal.')]),
(SITE+'eventos/feirinha-sao-luis/','São Luís','Gastronomia',[
 ('Feirinha São Luís','','Encontro de sabores e produção local; consulte programação.')]),
(SITE+'o-que-fazer/estaleiro-escola-do-maranhao/','São Luís','Cultura',[
 ('Estaleiro Escola do Maranhão','','Um espaço para conhecer saberes da construção naval.')])
]


def seed_catalog(connect):
    with connect() as con:
        for source,municipality,category,items in GROUPS:
            for name,address,description in items:
                interests=['Cultura','História'] if category in ('Patrimônio','Museu','Praça','Artesanato','Cultura') else ['Natureza','Praias'] if category in ('Praia','Natureza') else ['Gastronomia','Cultura']
                icon={'Museu':'🏛','Praia':'🌊','Natureza':'🌿','Cultura':'🥁','Gastronomia':'🍲','Artesanato':'🧵'}.get(category,'✦')
                values=(name,municipality,description,icon,json.dumps(interests,ensure_ascii=False),category,address,source,'2026-11-06','partial')
                con.execute('''INSERT OR IGNORE INTO destinos(nome,municipio,descricao,icone,interesses,category,address,source_url,verified_at,review_status)
                               VALUES (?,?,?,?,?,?,?,?,?,?)''',values)
                # Only fill untouched legacy metadata; preserve original IDs, text, coordinates and manual edits.
                con.execute('''UPDATE destinos SET category=?,address=?,source_url=?,verified_at=?,review_status='partial'
                               WHERE nome=? AND source_url='' AND category='Experiência' AND address='' AND review_status='legacy_unverified' ''',(category,address,source,'2026-11-06',name))
