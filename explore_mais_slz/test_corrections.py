"""Testes de regressão das correções; não alteram a base normal."""
import json
import unittest
import test_api as baseline
from backend.culture import cultural_content

backend=baseline.backend

class CorrectionsAPITest(unittest.TestCase):
    setUp=baseline.ExploreAPITest.setUp

    def test_location_totals_match_the_filtered_payload(self):
        for query in ('','?q=Raposa','?municipality=São Luís','?culture=reggae','?category=Praia','?interest=praia','?culture='):
            response=self.client.get('/api/destinos'+query);self.assertEqual(response.status_code,200,response.json)
            data=response.json
            self.assertEqual(data['total'],len(data['results']))
            self.assertEqual(data['map']['valid_coordinates'],sum(p['location']['valid'] for p in data['results']))
            self.assertEqual(data['map']['verified_coordinates'],sum(p['location']['verified'] for p in data['results']))
            self.assertEqual(data['map']['pending_coordinates'],sum(not p['location']['verified'] for p in data['results']))

    def test_invalid_coordinates_never_become_zero_or_verified(self):
        with backend.get_connection() as con:previous=tuple(con.execute('SELECT latitude,longitude,coordinates_status FROM destinos WHERE id=1').fetchone())
        try:
            for lat,lon,status,valid,verified in [(None,None,'verified',False,False),('',0,'verified',False,False),('invalid',-44,'verified',False,False),(91,-44,'verified',False,False),(-2,-181,'verified',False,False),(-2,-44,'unverified',True,False),(-2,-44,'verified',True,True)]:
                with backend.get_connection() as con:con.execute('UPDATE destinos SET latitude=?,longitude=?,coordinates_status=? WHERE id=1',(lat,lon,status))
                data=self.client.get('/api/destinos/1').json['destination']
                self.assertEqual(data['location']['valid'],valid,(lat,lon))
                self.assertEqual(data['location']['verified'],verified,(lat,lon))
        finally:
            with backend.get_connection() as con:con.execute('UPDATE destinos SET latitude=?,longitude=?,coordinates_status=? WHERE id=1',previous)

    def test_culture_is_preserved_associated_and_filterable(self):
        before=self.client.get('/api/destinos').json['total']
        content=self.client.get('/api/culture').json['results']
        self.assertEqual(len(content),9)
        self.assertEqual(content,cultural_content())
        for key in ('reggae','bumba','tambor','azulejos','gastronomia','artesanato','quilombo'):
            data=self.client.get('/api/destinos?culture='+key).json
            self.assertGreater(data['total'],0,key)
            self.assertTrue(all(key in item['culture_tags'] for item in data['results']))
        self.assertEqual(self.client.get('/api/destinos?culture=cacuria').json['total'],0)
        self.assertEqual(before,self.client.get('/api/destinos').json['total'])
        response=self.client.get('/cultura')
        self.assertEqual(response.status_code,302);self.assertEqual(response.location,'/catalogo#cultura')
        self.assertEqual(self.client.get('/api/destinos?culture=invalid').status_code,400)
        combined=self.client.get('/api/destinos?culture=reggae&municipality=São Luís&category=Museu').json
        self.assertEqual([p['name'] for p in combined['results']],['Museu do Reggae'])

    def test_planner_uses_specific_culture_without_fabricating_places(self):
        for interest in ('Reggae','Bumba Meu Boi','Tambor de Crioula','Azulejaria','Artesanato','Gastronomia maranhense'):
            response=self.client.post('/api/roteiro',json={**self.trip_input,'destination':'São Luís','interests':[interest]})
            self.assertEqual(response.status_code,200,(interest,response.json))
            if interest=='Reggae':self.assertEqual(response.json['days'][0]['stops'][0]['name'],'Museu do Reggae')
        response=self.client.post('/api/roteiro',json={**self.trip_input,'destination':'São Luís','interests':['Cacuriá']})
        self.assertEqual(response.status_code,422)


if __name__=='__main__':unittest.main(verbosity=2)
