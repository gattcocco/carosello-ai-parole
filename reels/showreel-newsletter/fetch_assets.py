"""Restore the five source images listed in assets/sources.json."""
import hashlib
import json
from pathlib import Path
import urllib.request
PROJECT=Path(__file__).resolve().parent
for item in json.loads((PROJECT/'assets/sources.json').read_text(encoding='utf-8')):
    target=(PROJECT/item['file']).resolve()
    if not target.is_relative_to((PROJECT/'assets/raw').resolve()):
        raise ValueError('Destinazione fuori assets/raw')
    if target.exists():
        print('Presente:',target.name)
        continue
    request=urllib.request.Request(item['url'],headers={'User-Agent':'CriticalInventoryReel/1.0'})
    data=urllib.request.urlopen(request,timeout=30).read()
    if hashlib.sha256(data).hexdigest()!=item['sha256']:
        raise ValueError('La sorgente è cambiata: '+target.name)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    print('Scaricato:',target.name)
