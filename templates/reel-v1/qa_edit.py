"""Exercise native-project edits without touching the original revision.

This tests Kdenlive's headless loader, not mouse/keyboard interaction in its UI.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from build import BASE, native_bin, write_xml


def main():
    from open import latest_project
    parser=argparse.ArgumentParser()
    parser.add_argument('source',nargs='?',type=Path)
    args=parser.parse_args()
    source=args.source.resolve() if args.source else latest_project()
    if source is None:raise FileNotFoundError('Genera prima un progetto con build.py')
    target=source.with_name(source.stem+'-verifica.kdenlive')
    if target.exists():raise FileExistsError(target)
    original=hashlib.sha256(source.read_bytes()).hexdigest()
    root=ET.parse(source).getroot()
    def properties(el):return {p.get('name'):p for p in el.findall('property')}
    changed=[]
    title_dir=BASE/'edit'/('titles-'+source.stem+'-verifica');title_dir.mkdir(exist_ok=True)
    # Both bin and timeline title instances refer to the same editable text.
    for p in root.findall('producer'):
        pr=properties(p)
        if pr.get('kdenlive:clipname') is not None and pr['kdenlive:clipname'].text=='01-narrazione-riga-1':
            title=ET.fromstring(pr['xmldata'].text)
            title.find('item/content').text='Extra Coin mi ha sorpreso.'
            titlefile=title_dir/'narrazione-riga-1.kdenlivetitle';write_xml(titlefile,title)
            pr['xmldata'].text=ET.tostring(title,encoding='unicode')
            pr['resource'].text=titlefile.relative_to(BASE/'edit').as_posix()
            changed.append(p.get('id'))
    # Replace the image with a different source, normalized to the same media box.
    replacement=BASE/'assets/qa-casa-mika.png'
    subprocess.run([str(native_bin()/'ffmpeg.exe'),'-hide_banner','-loglevel','error','-y',
                    '-i',str(BASE.parent.parent/'reels/extra-coin/assets/screenshots/casa-mika.jpg'),
                    '-vf','scale=840:473:force_original_aspect_ratio=increase,crop=840:473',
                    '-frames:v','1',str(replacement)],check=True)
    for p in root.findall('producer'):
        pr=properties(p)
        if pr.get('kdenlive:clipname') is not None and pr['kdenlive:clipname'].text=='01-narrazione-media':
            pr['resource'].text='../assets/qa-casa-mika.png'
    # Slow the first line's entrance from 8 to 18 frames.
    moved=0
    for entry in root.findall('playlist/entry'):
        if entry.get('producer') in changed:
            for f in entry.findall('filter'):
                pr=properties(f)
                if 'rect' in pr:
                    pr['rect'].text=pr['rect'].text.replace(';8=', ';18=');moved+=1
    assert len(changed)==2 and moved==1
    write_xml(target,root)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==original
    report={'original_sha256':original,'source':source.name,'variant':target.name,
            'changes':['frase sostituita','immagine sostituita','keyframe da 8 a 18'],
            'original_unchanged':True,'method':'XML nativo + loader headless di Kdenlive; UI non controllata'}
    (BASE/'dist').mkdir(exist_ok=True)
    (BASE/'dist'/f'{source.stem}-qa-edit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(target)


if __name__=='__main__':main()
