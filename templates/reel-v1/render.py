#!/usr/bin/env python3
"""Render a native Kdenlive project headlessly and deliver its silent master."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from build import BASE, native_bin


def main():
    p=argparse.ArgumentParser()
    p.add_argument('project',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--cache-dir',type=Path,default=BASE/'.cache')
    a=p.parse_args();project=a.project.resolve()
    if not project.is_file():raise FileNotFoundError(project)
    output=(a.output or BASE/'dist'/f'{project.stem}.mp4').resolve()
    if output.exists():raise FileExistsError(f'Output già presente: {output}; scegli un nuovo nome.')
    output.parent.mkdir(parents=True,exist_ok=True)
    bd=native_bin();cache=a.cache_dir.resolve();cache.mkdir(parents=True,exist_ok=True)
    index=1
    while (cache/f'{project.stem}-native-{index}.mp4').exists():index+=1
    intermediate=cache/f'{project.stem}-native-{index}.mp4'
    env=os.environ.copy();env['QT_QPA_PLATFORM']='offscreen'
    env['QT_QPA_FONTDIR']=str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts')
    logfile=cache/f'{project.stem}-native-{index}.log'
    with logfile.open('w',encoding='utf-8') as log:
        result=subprocess.run([str(bd/'kdenlive.exe'),'--no-welcome','--config',str(cache/f'{project.stem}-native-{index}.rc'),
                               '--render',str(project),str(intermediate)],env=env,stdout=log,stderr=log)
    if result.returncode or not intermediate.is_file():raise RuntimeError(f'Render fallito (codice {result.returncode}): {logfile}')
    info=json.loads(subprocess.check_output([str(bd/'ffprobe.exe'),'-v','error','-show_streams','-show_format',
                                            '-of','json',str(intermediate)],text=True))
    video=next(s for s in info['streams'] if s['codec_type']=='video')
    if (video['width'],video['height'],video['r_frame_rate'])!=(1080,1920,'30/1'):
        raise RuntimeError('Kdenlive ha esportato un profilo diverso da 1080x1920/30')
    # Kdenlive's stock preset creates a silent AAC track even on video-only
    # timelines. Remux without re-encoding to retain the original silent-master workflow.
    subprocess.run([str(bd/'ffmpeg.exe'),'-hide_banner','-loglevel','error','-n','-i',str(intermediate),
                    '-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(output)],check=True)
    print(output)
    print(f'{video.get("nb_frames")} frame, 1080x1920, 30 fps, master muto')


if __name__=='__main__':main()
