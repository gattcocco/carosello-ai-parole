import re
import subprocess
import sys
from pathlib import Path
PROJECT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT.parents[1]/'templates/reel-v1'))
from build import native_bin
projects=[p for p in (PROJECT/'edit').glob('showreel-v*.kdenlive') if re.fullmatch(r'showreel-v[0-9]+',p.stem)]
if not projects:raise SystemExit('Genera prima la prova con build.py')
latest=max(projects,key=lambda p:int(p.stem.split('-v')[1]))
print(latest)
if '--check' not in sys.argv:subprocess.Popen([str(native_bin()/'kdenlive.exe'),'--no-welcome',str(latest)],cwd=PROJECT)
