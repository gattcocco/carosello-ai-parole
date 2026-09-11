"""Render an episode revision through the shared Kdenlive renderer."""
import sys
from pathlib import Path
PROJECT=Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT.parents[1]/'templates/reel-v1'))
from render import main
if __name__=='__main__':
    if '--output' not in sys.argv and len(sys.argv)>1:
        sys.argv.extend(['--output',str(PROJECT/'dist'/(Path(sys.argv[1]).stem+'.mp4'))])
    if '--cache-dir' not in sys.argv:
        sys.argv.extend(['--cache-dir',str(PROJECT/'.cache')])
    main()
