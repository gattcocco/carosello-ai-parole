# Critical Inventory — caroselli e reel

Repository di testi, identità visiva, asset e codice per i contenuti di Critical
Inventory. I progetti più avanzati sono **Extra Coin** e **Buco Nero**.
Il template Kdenlive è una prova funzionante di montaggio con testi e animazioni
editabili; la sua rifinitura nell'editor precede l'adozione come template definitivo.

## Da dove partire

| Voglio… | Apri |
|---|---|
| Provare il montaggio modificabile | [Template Kdenlive](templates/reel-v1/README.md) |
| Imparare Kdenlive da zero | [Guida al primo utilizzo](templates/reel-v1/GUIDA-PRIMO-UTILIZZO-KDENLIVE.md) |
| Lavorare su Extra Coin | [Progetto e render v0.5](reels/extra-coin/README.md) |
| Lavorare su Buco Nero | [Progetto](reels/buco-nero/README.md) · [Storyboard](reels/buco-nero/storyboard.md) |
| Riprendere Kokushobi | [Materiale recuperato e stato](reels/kokushobi/README.md) |
| Consultare identità e regole dei reel | [Brand asset](brand/README.md) · [Manuale reel](brand-manual-v2.md) |
| Capire le decisioni sul template | [Consulenza](docs/consulenza-template-reel.md) |

## Struttura

```text
brand/                  loghi, poster e manuale generale
reels/                  episodi: extra-coin, buco-nero, indice kokushobi
templates/reel-v1/      modello JSON, generatore e guida Kdenlive
docs/                   consulenza, migrazione e indice storico
pipeline/               renderer storici
testi/                  archivio editoriale delle serie precedenti
.cache/                 dipendenze, frame e backup locali (fuori Git)
dist/                   esportazioni rigenerabili (fuori Git)
```

[Convenzioni degli episodi](reels/README.md) ·
[Archivio dei lavori precedenti](docs/legacy.md) ·
[Riordino e tag di archivio](docs/riordino-2026-09-11.md).

## Prova Kdenlive su Windows

1. Clona l'intero repository e installa Python 3.10+ e Kdenlive (versione
   verificata: 26.08.0). I binari non sono inclusi in Git.
2. Segui il [setup del template](templates/reel-v1/README.md#setup-su-un-altro-pc)
   per indicare la cartella `bin` di Kdenlive e verificare i font.
3. Apri `templates/reel-v1/APRI-PROVA.cmd`: genera la base se manca e apre
   l'ultima revisione generata. Salva le modifiche manuali in una copia.

Il codice produce titoli e keyframe nativi. Il lavoro manuale nell'editor non
torna automaticamente nel JSON; le copie di lavoro e i video locali non sono
salvati su GitHub. Nel template trovi le istruzioni per conservarli.

## Lavorare sul repository

`main` raccoglie il lavoro corrente. Per un intervento usa un branch temporaneo
(`reel/<slug>` o `chore/<nome>`), integralo dopo i controlli e rimuovilo quando
non serve più. Le revisioni di un episodio vivono nei suoi file e nella storia
Git. I vecchi branch Extra Coin e Kokushobi sono conservati anche tramite tag.

I sorgenti video derivati, le cache, i programmi e i render non vengono
versionati. Alcune GIF e immagini storiche erano già presenti nella storia:
il riordino le conserva. Per nuovi materiali registra fonte e condizioni d'uso
in `assets/SOURCES.md`, secondo le convenzioni degli episodi.
