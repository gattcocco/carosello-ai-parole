"""Open the newest generated base; build one on a fresh clone."""
import argparse
import re
import subprocess
import sys
from build import BASE, native_bin

def latest_project():
    projects = [p for p in (BASE/'edit').glob('prova-v*.kdenlive')
                if re.fullmatch(r'prova-v[0-9]+', p.stem)]
    return max(projects, key=lambda p: int(p.stem.split('-v')[1]), default=None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Verifica i percorsi senza aprire finestre')
    args = parser.parse_args()
    binary = native_bin()/'kdenlive.exe'
    project = latest_project()
    if project is None:
        if args.check:
            raise RuntimeError('Nessuna revisione: esegui build.py oppure APRI-PROVA.cmd')
        subprocess.run([sys.executable, str(BASE/'build.py')], check=True)
        project = latest_project()
    print(f'Kdenlive: {binary}\nProgetto base: {project}')
    if not args.check:
        subprocess.Popen([str(binary), '--no-welcome', str(project)], cwd=BASE)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f'Errore: {error}', file=sys.stderr)
        sys.exit(1)
