#!/usr/bin/env python3
"""Generate native title clips, animated MLT/Kdenlive project and editorial SRT.

Python standard library only. Rendering uses the bundled Kdenlive/MLT engine.
Each invocation creates a fresh revision; manual projects are never overwritten.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import uuid
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent


def props(element, **values):
    for name, value in values.items():
        ET.SubElement(element, 'property', name=name).text = str(value)


def write_xml(path, element):
    ET.indent(element, space='  ')
    ET.ElementTree(element).write(path, encoding='utf-8', xml_declaration=True)


def native_bin():
    candidates = []
    configured = os.environ.get('KDENLIVE_BIN')
    if configured:
        candidates.append(Path(configured))
    candidates.extend(p.parent for p in sorted((BASE / '.cache/kdenlive').glob('*/bin/melt.exe')))
    installed = shutil.which('kdenlive.exe')
    if installed:
        candidates.append(Path(installed).parent)
    candidates.append(Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'kdenlive/bin')
    for directory in candidates:
        if all((directory/name).is_file() for name in ('kdenlive.exe', 'melt.exe', 'ffmpeg.exe', 'ffprobe.exe')):
            return directory
    raise RuntimeError('Kdenlive non trovato. Imposta KDENLIVE_BIN alla cartella bin: vedi README.md.')


def qcolor(hex_value):
    h = hex_value.lstrip('#')
    return ','.join(str(int(h[i:i+2], 16)) for i in (0,2,4)) + ',255'


def title_document(items, frames, width, height):
    root = ET.Element('kdenlivetitle', width=str(width), height=str(height),
                      out=str(frames-1), duration=str(frames), LC_NUMERIC='C')
    for index, item in enumerate(items):
        is_rect = 'rect' in item
        el = ET.SubElement(root, 'item', {'z-index': str(index), 'type': 'QGraphicsRectItem' if is_rect else 'QGraphicsTextItem'})
        pos = ET.SubElement(el, 'position', x=str(item['x']), y=str(item['y']))
        ET.SubElement(pos, 'transform').text = f'{item.get("scale_x",1)},0,0,0,1,0,0,0,1'
        if is_rect:
            w,h = item['rect']
            ET.SubElement(el, 'content', rect=f'0,0,{w},{h}', pencolor=qcolor(item['color']),
                          penwidth=str(item.get('stroke',0)), brushcolor=qcolor(item['color']) if not item.get('stroke') else '0,0,0,0')
        else:
            attrs = {'font': item['font'], 'font-weight': str(item.get('weight',600)),
                     'font-pixel-size':str(item['size']), 'font-italic':'0', 'font-underline':'0',
                     'font-color':qcolor(item['color']), 'font-outline':'0',
                     'font-outline-color':'0,0,0,0', 'alignment':'1',
                     'letter-spacing':'0', 'line-spacing':'0', 'shadow':'0;#000000;0;0;0',
                     'typewriter':'0;0;0;0'}
            ET.SubElement(el, 'content', attrs).text = item['text']
    for name in ('startviewport','endviewport'):
        ET.SubElement(root,name,rect=f'0,0,{width},{height}')
    ET.SubElement(root,'background',color='0,0,0,0')
    return root


class Builder:
    def __init__(self, model, revision, base=None, prefix="prova"):
        self.base=Path(base) if base is not None else BASE
        self.model=model
        self.w,self.h,self.fps = model['width'],model['height'],model['fps']
        self.duration=sum(s['frames'] for s in model['scenes'])
        self.edit=self.base/'edit'; self.edit.mkdir(parents=True,exist_ok=True)
        self.tag=f'{prefix}-v{revision:03}'
        self.titles=self.edit/f'titles-v{revision:03}'; self.titles.mkdir()
        self.root=ET.Element('mlt',LC_NUMERIC='C',version='7.36.0',producer='main_bin',root=self.edit.as_posix())
        ET.SubElement(self.root,'profile',description='Critical Inventory 1080x1920 30fps',
                      width=str(self.w),height=str(self.h),frame_rate_num=str(self.fps),frame_rate_den='1',
                      progressive='1',sample_aspect_num='1',sample_aspect_den='1',
                      display_aspect_num='9',display_aspect_den='16',colorspace='709')
        self.layers=[[] for _ in range(8)]
        self.bin_entries=[]; self.count=0; self.manifest=[]

    def producer(self, name, frames, service, values, layer, start, motion=None):
        self.count+=1; bin_id=str(self.count+1)
        base_id=f'bin{self.count}'; clip_id=f'clip{self.count}'
        base=ET.SubElement(self.root,'producer',id=base_id,**{'in':'0','out':str(frames-1)})
        props(base, **{'length':frames,'eof':'pause','mlt_service':service,
                       'kdenlive:id':bin_id,'kdenlive:clipname':name,'kdenlive:folderid':'-1',
                       'set.test_audio':'1',**values})
        clip=copy.deepcopy(base);clip.set('id',clip_id)
        if motion:
            filt=ET.SubElement(clip,'filter',**{'in':'0','out':str(frames-1)})
            props(filt,**{'mlt_service':'qtblend','kdenlive_id':'qtblend','kdenlive:ix':'1','version':'4',
                          'kdenlive:sync_in_out':'1','kdenlive:effectName':'Transform',
                          'kdenlive:collapsed':'0','kdenlive:enabled':'1',
                          'rect':motion,'distort':'0','compositing':'0','rotation':'0'})
        self.root.append(clip)
        self.bin_entries.append((base_id,frames))
        self.layers[layer].append((start,frames,clip_id,bin_id))
        self.manifest.append({'name':name,'producer':clip_id,'layer':layer,'start':start,'frames':frames,'animated':bool(motion)})

    def text(self, text, x,y,size,color, role='body',weight=600):
        return dict(text=text,x=x,y=y,size=size,color=color,font=self.model['fonts'][role],weight=weight)

    def title(self,name,items,frames,layer,start,delay=None):
        xml=title_document(items,frames,self.w,self.h)
        path=self.titles/f'{name}.kdenlivetitle';write_xml(path,xml)
        motion=None
        if delay is not None:
            m=self.model['motion']; end=delay+m['enter_frames'];rise=m['rise_px']
            keys={0:(rise,0),delay:(rise,0),end:(0,1),frames-1:(0,1)}
            motion=';'.join(f'{f}=0 {dy} {self.w} {self.h} {alpha}' for f,(dy,alpha) in sorted(keys.items()))
        self.producer(name,frames,'kdenlivetitle',{'xmldata':ET.tostring(xml,encoding='unicode'),
                      'resource':path.relative_to(self.edit).as_posix(),'kdenlive:clip_type':'6',
                      'kdenlive:duration':frames,'aspect_ratio':'1','force_reload':'0'},layer,start,motion)

    def media(self,name,media,frames,start):
        assets=self.base/self.model.get('media_cache','assets');assets.mkdir(parents=True,exist_ok=True)
        src=(self.base/media['source']).resolve()
        # MP4 derivato ignorato da Git: sul clone nuovo usa la GIF sorgente.
        if not src.is_file() and src.suffix.lower()=='.mp4' and src.with_suffix('.gif').is_file():
            src=src.with_suffix('.gif')
        if not src.is_file():raise FileNotFoundError(src)
        x,y,w,h=media['box']
        fingerprint=hashlib.sha256(src.read_bytes()+json.dumps(media,sort_keys=True).encode()+str(frames).encode()).hexdigest()[:12]
        out=assets/(name+'-'+fingerprint+('.png' if media['kind']=='image' else '.mp4'))
        if not out.exists():
            command=[str(native_bin()/'ffmpeg.exe'),'-hide_banner','-loglevel','error','-y']
            if media['kind']!='image':command+=['-ss',str(media.get('in_seconds',0))]
            command+=['-i',str(src),'-vf',f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}']
            if media['kind']=='image':command+=['-frames:v','1']
            else:command+=['-t',str(frames/self.fps),'-r',str(self.fps),'-an','-c:v','libx264','-crf','16','-pix_fmt','yuv420p']
            subprocess.run(command+[str(out)],check=True)
        # MLT letterboxes a source into the profile before Transform; compensate
        # for that letterbox so the visible picture matches the intended box.
        scale=w/self.w; rh=self.h*scale; ry=y-(rh-h)/2
        motion=f'0={x} {ry:.4f} {w} {rh:.4f} 1'
        self.producer(name,frames,'qimage' if media['kind']=='image' else 'avformat',
                      {'resource':os.path.relpath(out,self.edit).replace('\\','/'),
                       'kdenlive:clip_type':'5' if media['kind']=='image' else '2',
                       'audio_index':'-1','video_index':'0'},0,start,motion)

    def scenes(self):
        start=0;p=self.model['palette'];bone=p['bone'];muted=p['muted']
        for num,s in enumerate(self.model['scenes'],1):
            ident=s['id'];n=s['frames'];a=p[s['accent']]
            common=[self.text(s['header'],70,258,24,a,'mono',700),
                    {'x':70,'y':324,'rect':(250,6),'color':a},
                    self.text(f'{num:02} / {len(self.model["scenes"]):02}',760,258,24,a,'mono',700)]
            if s['layout'] in ('narrative','reaction'):
                media=s['media'];reaction=s.get('reaction')
                self.media(ident+'-media',media,reaction['start_frame'] if reaction else n,start)
                if reaction:self.media(ident+'-reaction',reaction,reaction['frames'],start+reaction['start_frame'])
                x,y,w,h=media['box']
                common.append({'x':x,'y':y,'rect':(w,h),'color':bone,'stroke':2})
                common.append({'x':x,'y':y,'rect':(160,6),'color':a})
                common.append(self.text(s['label'],70,1080 if reaction else 990,24,a,'mono',700))
                y0=1165 if reaction else 1080
                size=58 if reaction else 62
                for i,line in enumerate(s['lines']):
                    color=a if i==s.get('accent_line') else bone
                    self.title(f'{ident}-riga-{i+1}',[self.text(line,70,y0+i*86,size,color)],n,2+i,start,i*self.model['motion']['stagger_frames'])
                common.append({'x':70,'y':1505,'rect':(840,4),'color':'#4A4A50'})
                common.append({'x':70,'y':1505,'rect':(round(840*num/len(self.model['scenes'])),4),'color':a})
            elif s['layout']=='title':
                for i,line in enumerate(s['lines']):
                    item=self.text(line,70,650+i*145,104,a if i==s.get('accent_line') else bone,'display',700)
                    item['scale_x']=0.64
                    self.title(f'{ident}-riga-{i+1}',[item],n,2+i,start,i*2)
                common += [{'x':70,'y':1180,'rect':(290,10),'color':a},self.text(s['label'],70,1300,26,bone,'mono',700)]
            else:
                for i,line in enumerate(s['lines']):
                    self.title(f'{ident}-brand-{i+1}',[self.text(line,70,470+i*155,152,bone,'display',700)],n,2+i,start,i*2)
                details=[self.text(s['label'],70,390,25,a,'mono',700)]
                details += [self.text(line,70,930+i*84,58,bone) for i,line in enumerate(s['detail_lines'])]
                self.title(ident+'-descrizione',details,n,4,start,4)
                cta=[{'x':70,'y':1200,'rect':(275,8),'color':a},self.text(s['cta'],70,1280,76,a,'body',700),
                     self.text(s['cta_detail'],70,1410,34,bone,'mono',700)]
                self.title(ident+'-cta',cta,n,5,start,6)
            self.title(ident+'-cornice',common,n,1,start)
            start+=n

    def save(self):
        total=self.duration;seqid='{'+str(uuid.uuid4())+'}'
        black=ET.SubElement(self.root,'producer',id='black_track',**{'in':'0','out':str(total-1)})
        props(black,**{'mlt_service':'color','resource':self.model['palette']['ink'],
                       'length':total,'eof':'continue','mlt_image_format':'rgba'})
        tracks=[]
        names=['Media','Cornici e metadata','Testo riga 1','Testo riga 2','Testo riga 3 / descrizione','CTA','Extra 1','Extra 2']
        for i,clips in enumerate(self.layers):
            if not clips:continue
            pl=ET.SubElement(self.root,'playlist',id=f'playlist{i}a');pos=0
            for start,n,producer,bin_id in sorted(clips):
                if start<pos:raise ValueError(f'Overlapping clips on layer {i}')
                if start>pos:ET.SubElement(pl,'blank',length=str(start-pos))
                ent=ET.SubElement(pl,'entry',producer=producer,**{'in':'0','out':str(n-1)})
                props(ent,**{'kdenlive:id':bin_id});pos=start+n
            ET.SubElement(self.root,'playlist',id=f'playlist{i}b')
            t=ET.SubElement(self.root,'tractor',id=f'track{i}',**{'in':'0','out':str(total-1)})
            props(t,**{'kdenlive:track_name':names[i],'kdenlive:trackheight':'70','kdenlive:timeline_active':'1',
                       'kdenlive:collapsed':'0','kdenlive:audio_track':'0'})
            ET.SubElement(t,'track',producer=f'playlist{i}a',hide='audio')
            ET.SubElement(t,'track',producer=f'playlist{i}b',hide='audio');tracks.append(f'track{i}')
        seq=ET.SubElement(self.root,'tractor',id=seqid,**{'in':'0','out':str(total-1)})
        props(seq,**{'kdenlive:uuid':seqid,'kdenlive:clipname':self.model['name'],'kdenlive:id':'1',
                     'kdenlive:producer_type':'17','kdenlive:folderid':'-1','kdenlive:maxduration':total,
                     'kdenlive:sequenceproperties.documentuuid':seqid,'kdenlive:sequenceproperties.hasVideo':'1',
                     'kdenlive:sequenceproperties.hasAudio':'0','kdenlive:sequenceproperties.tracksCount':len(tracks),
                     'kdenlive:sequenceproperties.tracks':len(tracks),'kdenlive:sequenceproperties.activeTrack':'2',
                     'kdenlive:sequenceproperties.videoTarget':'2','kdenlive:sequenceproperties.zonein':'0',
                     'kdenlive:sequenceproperties.zoneout':total,'kdenlive:sequenceproperties.position':'45',
                     'kdenlive:sequenceproperties.zoom':'8','kdenlive:sequenceproperties.groups':'[]',
                     'kdenlive:sequenceproperties.guides':json.dumps([{'pos':sum(x['frames'] for x in self.model['scenes'][:i]),'comment':s['id'],'type':0} for i,s in enumerate(self.model['scenes'])])})
        ET.SubElement(seq,'track',producer='black_track')
        for i,track in enumerate(tracks,1):
            ET.SubElement(seq,'track',producer=track)
            trans=ET.SubElement(seq,'transition')
            props(trans,**{'a_track':'0','b_track':i,'mlt_service':'qtblend','always_active':'1',
                          'internal_added':'237','compositing':'0','distort':'0'})
        binpl=ET.SubElement(self.root,'playlist',id='main_bin')
        props(binpl,**{'kdenlive:docproperties.version':'1.1','kdenlive:docproperties.kdenliveversion':'26.08.0',
                       'kdenlive:docproperties.documentid':'20260911001','kdenlive:docproperties.uuid':seqid,
                       'kdenlive:docproperties.activetimeline':seqid,'kdenlive:docproperties.opensequences':seqid,
                       'kdenlive:docproperties.audioChannels':'2','kdenlive:docproperties.compositing':'1',
                       'kdenlive:docproperties.enableproxy':'0','kdenlive:docproperties.profile':'vertical_hd_30',
                       'kdenlive:documentnotes':'Prova editabile. Salvare le modifiche manuali in una copia.',
                       'xml_retain':'1'})
        for producer,n in self.bin_entries:ET.SubElement(binpl,'entry',producer=producer,**{'in':'0','out':str(n-1)})
        ET.SubElement(binpl,'entry',producer=seqid,**{'in':'0','out':str(total-1)})
        project=ET.SubElement(self.root,'tractor',id='project',**{'in':'0','out':str(total-1)})
        props(project,**{'kdenlive:projectTractor':'1'})
        ET.SubElement(project,'track',producer=seqid,**{'in':'0','out':str(total-1)})
        render=copy.deepcopy(self.root);render.set('producer','project')
        write_xml(self.edit/f'{self.tag}.mlt',render)
        # Kdenlive serializes timeline effects inside playlist entries. MLT's
        # standalone consumer instead needs them on producer instances.
        native=copy.deepcopy(self.root)
        by_id={p.get('id'):p for p in native.findall('producer')}
        for playlist in native.findall('playlist'):
            if playlist.get('id')=='main_bin':continue
            for entry in playlist.findall('entry'):
                producer=by_id[entry.get('producer')]
                for effect in list(producer.findall('filter')):
                    entry.append(copy.deepcopy(effect));producer.remove(effect)
        path=self.edit/f'{self.tag}.kdenlive';write_xml(path,native)
        (self.edit/f'{self.tag}.json').write_text(json.dumps(self.model,ensure_ascii=False,indent=2),encoding='utf-8')
        (self.edit/f'{self.tag}-layers.json').write_text(json.dumps(self.manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        def tc(frame):
            ms=round(frame*1000/self.fps);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
        cues=[];start=0
        for i,s in enumerate(self.model['scenes'],1):
            lines=s['lines']+s.get('detail_lines',[])+([s['cta'],s['cta_detail']] if 'cta' in s else [])
            cues.append(f'{i}\n{tc(start)} --> {tc(start+s["frames"])}\n'+ '\n'.join(lines));start+=s['frames']
        (self.edit/f'{self.tag}.srt').write_text('\n\n'.join(cues)+'\n',encoding='utf-8')
        return path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,default=BASE/'project.json')
    args=parser.parse_args();model=json.loads(args.project.read_text(encoding='utf-8'))
    if (model['width'],model['height'],model['fps'])!=(1080,1920,30):raise ValueError('Prototipo: formato 1080x1920/30')
    for s in model['scenes']:
        if not isinstance(s['frames'],int) or s['frames']<12:raise ValueError('Durata scena non valida')
        if s.get('reaction') and s['reaction']['start_frame']+s['reaction']['frames']!=s['frames']:raise ValueError('Reaction fuori scena')
    revisions=[int(p.stem.split('-v')[1]) for p in (BASE/'edit').glob('prova-v*.kdenlive') if p.stem.split('-v')[1].isdigit()]
    b=Builder(model,max(revisions,default=0)+1);b.scenes();path=b.save()
    print(path);print(f'{b.duration} frames / {b.duration/b.fps:g}s / {b.count} elementi')


if __name__=='__main__':main()
