"""Obtém dependências estáticas fixadas; execução manual, não faz parte do servidor."""
from pathlib import Path
import hashlib
import json
from urllib.request import urlopen

root=Path(__file__).resolve().parents[1]/'frontend'/'vendor'
packages={
 'leaflet':('https://unpkg.com/leaflet@1.9.4/',{'dist/leaflet.js':'leaflet.js','dist/leaflet.css':'leaflet.css','LICENSE':'LICENSE','dist/images/layers.png':'images/layers.png','dist/images/layers-2x.png':'images/layers-2x.png'}),
 'markercluster':('https://unpkg.com/leaflet.markercluster@1.5.3/',{'dist/leaflet.markercluster.js':'leaflet.markercluster.js','dist/MarkerCluster.css':'MarkerCluster.css','dist/MarkerCluster.Default.css':'MarkerCluster.Default.css','MIT-LICENCE.txt':'LICENSE'})
}
manifest=[]
for package,(base,files) in packages.items():
    for source,target in files.items():
        data=urlopen(base+source,timeout=40).read()
        destination=root/package/target
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
        manifest.append({'path':str(destination.relative_to(root)).replace('\\','/'),'source':base+source,'sha256':hashlib.sha256(data).hexdigest()})
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Arquivos locais e licenças:',len(manifest))
