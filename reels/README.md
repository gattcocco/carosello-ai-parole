# Reel

Da agosto 2026 ogni nuovo reel vive in una cartella autonoma `reels/<slug>/`.
Il materiale storico in root resta dov'è finché il relativo renderer non viene
migrato e verificato: spostarlo tutto insieme romperebbe i path esistenti e
renderebbe più difficile integrare le branch precedenti.

## Struttura standard

```text
reels/<slug>/
├── README.md
├── content/
│   ├── review-source.docx
│   ├── storyboard.md
│   ├── on-screen-copy.md  # quando il reel non usa voice-over
│   ├── text-track.srt     # timing editoriale/accessibilità
│   ├── voiceover.md       # solo quando è prevista una traccia parlata
│   └── caption.md         # prima della pubblicazione
├── assets/
│   ├── SOURCES.md
│   ├── screenshots/
│   ├── generated/
│   └── raw/               # press kit, meme e footage non versionati
└── render.py              # quando il montaggio viene implementato
```

## Convenzioni

- Nomi di file e cartelle in lowercase kebab-case.
- Storyboard approvato prima del codice di montaggio.
- Path relativi alla root del repository; niente path assoluti di una macchina.
- `assets/SOURCES.md` registra provenienza, URL, credito e stato dei diritti.
- Press kit, GIF meme e footage di terzi vanno in `assets/raw/` e non in Git,
  salvo licenza esplicita che ne consenta la redistribuzione.
- Render finali in `dist/`; frame e cache in `.cache/`. Entrambi sono ignorati.
- Un solo accento cromatico per frame, in accordo con `brand-manual-v2.md`.
- Copy e storyboard seguono [Tono di voce e scrittura a schermo](../brand-manual-v2.md#tono-di-voce-e-scrittura-a-schermo);
  timing e limiti specifici restano nel singolo storyboard.

## Migrazione del materiale storico

La migrazione dei reel precedenti sarà incrementale: un reel per volta, con
aggiornamento dei path e prova del render nello stesso cambiamento. Fino ad
allora `pipeline/`, `testi/`, `Nuove card stile evangelion/`, `GOATS/`,
`Screenshots/` e gli asset sparsi in root sono considerati legacy.

## Episodi disponibili

- [Extra Coin](extra-coin/README.md): bozza v0.5, sorgente di riferimento per narrazione e ritmo.
- [Buco Nero](buco-nero/README.md): migrato sotto `reels/`, conserva i nomi originali dei media.
- [Kokushobi](kokushobi/README.md): indice del materiale storico recuperato.

Il [template Kdenlive condiviso](../templates/reel-v1/README.md) vive separato
dagli episodi. Il prototipo di 22 secondi combina esempi Extra Coin e Buco Nero.
