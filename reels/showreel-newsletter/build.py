"""Build this episode using the shared native Kdenlive serializer."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT=Path(__file__).resolve().parent
REPO=PROJECT.parents[1]
sys.path.insert(0,str(REPO/'templates/reel-v1'))
from build import Builder, write_xml


class Showreel(Builder):
    def rect(self,x,y,w,h,color,stroke=0):
        return dict(x=x,y=y,rect=(w,h),color=color,stroke=stroke)

    def illustration(self,s,n,start,a,bone):
        """Native schematic illustrations, not screenshots of real datasets."""
        ink=self.model['palette']['ink']
        items=[]
        if s['layout']=='intro':
            for i,(text,y) in enumerate([('UNA STORIA',420),('UNA DOMANDA',590),('UNO STRUMENTO',760)]):
                self.title(s['id']+'-indice-'+str(i),[
                    self.rect(70,y,840,130,bone,2),
                    self.text(text,108,y+33,46,a if i==1 else bone,'mono',700)],n,0 if i==0 else 6+i-1,start,10+i*6)
        elif s['layout']=='network':
            # A visual metaphor for exploration, with no invented data values.
            for x,y,w,h in [(274,482,380,4),(274,742,380,4),(273,482,4,264),(650,482,4,264)]:
                items.append(self.rect(x,y,w,h,a))
            for i,(x,y,label) in enumerate([(110,432,'PERSONE'),(560,432,'LUOGHI'),(110,692,'FONTI'),(560,692,'LEGAMI')]):
                items.extend([self.rect(x,y,300,110,ink),self.rect(x,y,300,110,bone,2),self.text(label,x+30,y+32,31,bone,'mono',700)])
        elif s['layout']=='web':
            for i,(x,y,label) in enumerate([(70,420,'IDEE'),(155,580,'GIOCHI'),(240,740,'ESPERIMENTI')]):
                items.extend([self.rect(x,y,660,130,ink),self.rect(x,y,660,130,bone,2),self.rect(x,y,660,28,a),self.text(label,x+30,y+56,37,bone,'mono',700)])
        elif s['layout']=='books':
            for i,(x,y,w,h) in enumerate([(85,430,145,390),(250,410,160,410),(435,470,145,350),(605,450,145,370),(775,510,120,310)]):
                items.extend([self.rect(x,y,w,h,bone,2),self.rect(x+20,y+30,w-40,6,a),self.rect(x+20,y+h-52,w-40,4,bone)])
        if items:self.title(s['id']+'-illustrazione',items,n,0,start,8)

    def scenes(self):
        start=0
        bone=self.model['palette']['bone'];ink=self.model['palette']['ink']
        total=len(self.model['scenes'])
        for number,s in enumerate(self.model['scenes'],1):
            ident=s['id'];n=s['frames'];a=self.model['palette'][s['accent']]
            common=[self.text(s['header'],70,258,23,a,'mono',700),self.text(f'{number:02}/{total:02}',818,258,23,a,'mono',700),self.rect(70,324,250,6,a)]
            if s['layout']=='title':
                self.model['motion']['enter_frames']=3
                for i,line in enumerate(s['lines']):
                    item=self.text(line,70,610+i*157,132,a if i==s.get('accent_line') else bone,'display',700)
                    item['scale_x']=s.get('display_scale_x',0.68)
                    self.title(f'{ident}-riga-{i+1}',[item],n,2+i,start,i*2)
                if s['label']:common.append(self.text(s['label'],70,1230,24,a,'mono',700))
            elif s['layout']=='closing':
                self.model['motion']['enter_frames']=8
                for i,line in enumerate(s['lines']):
                    self.title(f'{ident}-brand-{i+1}',[self.text(line,70,470+i*163,152,bone,'display',700)],n,2+i,start,i*2)
                self.title(ident+'-promessa',[self.text(s['label'],70,900,27,a,'mono',700),self.text(s['detail_lines'][0],70,992,52,bone)],n,4,start,4)
                self.title(ident+'-cta',[self.rect(70,1200,280,8,a),self.text(s['cta'],70,1280,80,a,'body',700),self.text(s['cta_detail'],70,1410,34,bone,'mono',700)],n,5,start,6)
            else:
                self.model['motion']['enter_frames']=8
                if s.get('images'):
                    end=n-33 if s.get('gif') else n
                    begin=12
                    segment=(end-begin)//len(s['images'])
                    for i,name in enumerate(s['images']):
                        length=segment if i<len(s['images'])-1 else end-begin-i*segment
                        self.media(ident+'-media-'+str(i+1),{'source':'assets/raw/'+name,'kind':'image','box':[70,390,840,473]},length,start+begin+i*segment)
                    common.extend([self.rect(70,390,840,473,bone,2),self.rect(70,390,155,6,a)])
                    if s.get('gif'):
                        slot=next(g for g in self.model['gif_slots'] if g['id']==s['gif'])
                        source=PROJECT/slot['source']
                        if source.exists():
                            self.media('GIF-'+slot['id'],{'source':slot['source'],'kind':'video','box':[70,390,840,473]},slot['frames'],slot['start_frame'])
                        else:
                            self.title('GIF-'+slot['id']+'-INSERISCI-QUI',[
                                self.rect(72,392,836,469,ink),self.text('GIF '+slot['id'],115,492,86,a,'display',700),
                                self.text(slot['subject'],115,644,32,bone,'mono',700)],slot['frames'],0,slot['start_frame'])
                else:self.illustration(s,n,start,a,bone)
                common.append(self.text(s['label'],70,935,23,a,'mono',700))
                for i,line in enumerate(s['lines']):
                    # 60 px leaves the longest 30-character lines within the safe area.
                    self.title(f'{ident}-riga-{i+1}',[self.text(line,70,1070+i*88,60,a if i==s.get('accent_line') else bone)],n,2+i,start,i*2)
                common.extend([self.rect(70,1505,840,4,'#4A4A50'),self.rect(70,1505,round(840*number/total),4,a)])
            self.title(ident+'-cornice',common,n,1,start)
            start+=n


def main():
    model=json.loads((PROJECT/'project.json').read_text(encoding='utf-8'))
    assert sum(s['frames'] for s in model['scenes'])==1590
    revisions=[int(m.group(1)) for p in (PROJECT/'edit').glob('showreel-v*.kdenlive') if (m:=re.fullmatch(r'showreel-v(\d+)',p.stem))]
    builder=Showreel(model,max(revisions,default=0)+1,base=PROJECT,prefix='showreel')
    builder.scenes();path=builder.save()
    for suffix in ('.kdenlive','.mlt'):
        target=path.with_suffix(suffix);root=ET.parse(target).getroot()
        for prop in root.findall('.//property[@name="kdenlive:sequenceproperties.guides"]'):
            guides=json.loads(prop.text)
            guides.extend({'pos':g['start_frame'],'comment':'GIF '+g['id']+' / '+g['subject'],'type':0} for g in model['gif_slots'])
            prop.text=json.dumps(sorted(guides,key=lambda g:g['pos']),ensure_ascii=False)
        write_xml(target,root)
    print(path)
    print(f'{builder.duration} frame / {builder.duration/30:g} s / {builder.count} elementi nativi')

if __name__=='__main__':main()
