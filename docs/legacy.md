# Archivio dei progetti precedenti

Questi materiali sono conservati nei percorsi originali. I renderer storici
dipendono da quei nomi e, in alcuni casi, da font e directory Linux: il riordino
non costituisce un collaudo dei vecchi render.

| Progetto o materiale | Sorgenti |
|---|---|
| Carosello risograph | [monta_card.py](../pipeline/monta_card.py), [card finali](../card%20finali/) |
| Reel parole AI v1 | [reel.py](../pipeline/reel.py) |
| Reel parole AI v2 / Evangelion | [reel2.py](../pipeline/reel2.py), [asset](../Nuove%20card%20stile%20evangelion/), [prompt](../pipeline-immagini-v2.md) |
| Styleframe del brand | [styleframes.py](../pipeline/styleframes.py) |
| Mountain Goats / Titanium Court | [storyboard](../testi/storyboard-reel-mountain-goats.md), [GOATS](../GOATS/), [Screenshots](../Screenshots/) |
| Kokushobi | [Indice dell'episodio](../reels/kokushobi/README.md) |
| Testi e bibliografie | [testi](../testi/) |

Il B-roll di *Titanium Court* non è versionato: proviene dal press kit di
Fellow Traveller e va ripristinato in `B-Roll/` con i nomi dello storyboard
(`Game Intro.mov`, `Dragon Fight.mov`, ecc.). Gli MP4 si rigenerano e sono ignorati.

Per migrare un altro episodio: individua i riferimenti ai media, sposta sorgenti
e asset nella sua cartella `reels/<slug>`, correggi i percorsi e verifica il render
nello stesso intervento. Le cartelle condivise si spostano dopo aver migrato
tutti i renderer che le usano.
