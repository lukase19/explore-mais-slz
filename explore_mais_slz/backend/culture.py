"""Conteúdo editorial preservado e associações explícitas com locais reais.
Uma tradição sem lugar associado permanece editorial, sem criar coordenadas.
"""
import json
from pathlib import Path
from functools import lru_cache

INTERESTS={'Reggae':'reggae','Bumba Meu Boi':'bumba','Tambor de Crioula':'tambor','Cacuriá':'cacuria','Azulejaria':'azulejos','Gastronomia maranhense':'gastronomia','Artesanato':'artesanato','Quilombo Cultural':'quilombo'}

@lru_cache(maxsize=1)
def cultural_content():
    return json.loads(Path(__file__).with_name('culture_content.json').read_text(encoding='utf-8'))

def destination_culture(name):
    return [item for item in cultural_content() if name in item['destinations']]
