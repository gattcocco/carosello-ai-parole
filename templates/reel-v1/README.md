# Prova editabile — Critical Inventory

**Base verificata prima del riordino: v004.**
[Anteprima delle quattro scene](docs/contact-sheet.png). Quattro scene, 22 secondi,
1080×1920, 30 fps, senza audio.

**Prima volta con Kdenlive?** Parti dalla
[guida da zero: apertura, testi, animazioni ed export](GUIDA-PRIMO-UTILIZZO-KDENLIVE.md).

Apri **`APRI-PROVA.cmd`**: genera una base se manca e apre la revisione generata
con il numero più alto. Le copie `-manuale` non vengono selezionate dal launcher.
Su questo PC la copia standalone di Kdenlive 26.08.0 è stata conservata nella
`.cache`; su un nuovo clone va installata separatamente.

## Setup su un altro PC

1. Clona tutto il repository: il template usa anche i media dei due episodi.
2. Installa Python 3.10+ e [Kdenlive per Windows](https://kdenlive.org/download/).
   La versione verificata è **26.08.0**. Con la versione standalone, estrai il
   pacchetto: la cartella `bin` deve contenere `kdenlive.exe`, `melt.exe`,
   `ffmpeg.exe` e `ffprobe.exe`.
3. Il generatore cerca `KDENLIVE_BIN`, poi `.cache/kdenlive/*/bin`, il PATH e
   `C:/Program Files/kdenlive/bin`. Per un percorso diverso, dal terminale:

   ```powershell
   $env:KDENLIVE_BIN = 'C:\percorso\kdenlive\bin'
   python templates/reel-v1/build.py
   python templates/reel-v1/open.py
   ```

   Sostituisci il percorso di esempio. La variabile vale per quel terminale;
   per usarla anche con il doppio clic, impostala nelle variabili utente Windows
   oppure estrai Kdenlive nella `.cache/kdenlive/` del template.
4. Verifica i font **Segoe UI, Consolas, Bodoni MT**. Non sono inclusi nel repo;
   Bodoni MT può mancare su un'altra installazione Windows. Se lo sostituisci
   in `project.json`, ricontrolla lunghezza delle righe e resa tipografica.

Gli script usano la libreria standard Python. Il primo avvio converte i media
in `assets/` e genera `edit/prova-v001.kdenlive`. La demo MP4 non è versionata:
quando manca, il generatore usa `reels/buco-nero/ghostty-blackhole.gif`.
Le revisioni successive diventano v002, v003, ecc.; gli esempi con v004 nella
guida si riferiscono al numero della tua revisione.

`edit/`, `assets/`, `dist/` e `.cache/` sono locali e ignorate da Git.
Questo include le copie manuali: conservale con i media in un backup o
archivio Kdenlive. Un push salva modello e script, non il montaggio manuale.

## Cosa contiene

| Tempo | Scena | Elementi modificabili |
|---|---|---|
| 0–5 s | Extra Coin, narrazione | Due righe di testo, entrata sfalsata, immagine, cornice e metadata |
| 5–10 s | Buco Nero, reaction | Demo, gatto negli ultimi 1,1 s, testo che rimane fermo |
| 10–15 s | Buco Nero, battuta finale | Tre titoli separati con entrata animata |
| 15–22 s | Critical Inventory | Nome, descrizione, CTA e linea grafica, tutti elementi nativi |

I 18 elementi sono distribuiti su sei tracce, nominate per funzione. Non sono
immagini del testo: sono **titoli Kdenlive** con effetti **Transform** e keyframe.
La chiusura è una variante tipografica creata per provare l'editabilità; non
sostituisce la locandina del reel Buco Nero originale.

La prova usa Bodoni MT Bold per il display, con compressione orizzontale della
title card, Segoe UI Semibold per il corpo e Consolas Bold per i metadata.
Il Bodoni della vecchia pipeline usa un taglio diverso: questa scelta va
considerata nella successiva rifinitura del template.

## Prova nell'editor

1. Apri il progetto e fai **Salva con nome** → `prova-v004-manuale.kdenlive`.
2. Nel contenitore del progetto apri `01-narrazione-riga-1`: cambia la frase e
   conferma l'aggiornamento del titolo.
3. Seleziona la stessa riga nella timeline: nello stack degli effetti apri
   **Transform** e sposta il keyframe di arrivo dal frame 8 al frame 18.
4. Sostituisci il media della prima scena con un'immagine dello stesso rapporto
   16:9, mantenendo o copiando il suo effetto Transform. Una sorgente con un
   rapporto diverso richiede di rivedere ritaglio e posizionamento.
5. Salva, chiudi e riapri la copia; controlla testo, durata e keyframe.

Le righe separate permettono lo stagger. Per spostare una frase composta da
più righe, seleziona tutti i relativi clip; il progetto non usa un unico blocco
testuale con animazione interna. Il testo del prototipo ha entrata breve e
rimane visibile fino al taglio, senza animazione di uscita.

## Riprodurre la generazione

Python 3.10 o successivo; gli script di generazione e render usano solo la
libreria standard. FFmpeg e MLT sono inclusi nella copia Kdenlive locale.

Dalla root del repository:

```powershell
python templates/reel-v1/build.py
# Il comando stampa il percorso della nuova revisione, per esempio v006.
python templates/reel-v1/render.py templates/reel-v1/edit/prova-v006.kdenlive
```

`project.json` è il modello sorgente. Contiene testi, durate in frame, asset e
parametri d'animazione. Ogni generazione crea una nuova revisione in `edit/`,
insieme ai titoli `.kdenlivetitle`, alla copia JSON e alla traccia SRT.
Le immagini e i video normalizzati sono conservati in `assets/`; il nome
include un'impronta del file sorgente e dei parametri di ritaglio.

Il `.mlt` è un file tecnico per il consumer MLT. Per modificare il lavoro apri
il **`.kdenlive`**: la collocazione degli effetti nel documento è diversa e
rispetta la serializzazione dell'applicazione.

Il render usa Kdenlive in modalità headless, poi rimuove la traccia AAC
silenziosa aggiunta dal preset dell'applicazione, senza ricodificare il video.
Non sovrascrive un MP4 già esistente; `--output` permette di scegliere un
percorso nuovo.

**Le modifiche nell'editor non ritornano automaticamente in `project.json`.**
Conserva la copia manuale. Le modifiche da riutilizzare negli episodi successivi
vanno riportate nel modello sorgente prima di generare una nuova revisione.
Se sposti il progetto in un'altra posizione, rigenera i file per riallineare
la root del documento e conserva la struttura `edit/` + `assets/`.

## Verifiche eseguite

- Caricamento del documento nativo con Kdenlive 26.08.0 ed export: riusciti.
- Master: 660 frame, 1080×1920, 30 fps, 22 secondi, nessuno stream audio.
- Controllo visivo delle quattro scene e dei frame di entrata.
- Reaction: confronto dei pixel nella zona testo prima/dopo l'arrivo del
  gatto; differenza media 0,015 su 255, compatibile con la compressione video.
- Copia `verifica-edit.kdenlive`: cambiati testo e immagine della prima scena
  e spostato il keyframe da 8 a 18; ricaricamento ed export riusciti.
- Nuova generazione v005: la revisione v004 rimane identica, verificata con
  SHA-256. V005 è una duplicazione prodotta per questo controllo.

La variante di verifica cambia temporaneamente «annoiato» in «sorpreso»:
serve a verificare la modifica, non è una revisione editoriale proposta.
Vedi [confronto dei fotogrammi](docs/verifica-modifiche.png) e
`dist/qa-edit.json` locale della verifica iniziale.

**Limite del collaudo:** Computer Use non si è collegato al desktop Windows
(`native pipe unavailable`, anche dopo il ripristino). Le modifiche sono state
eseguite sul documento XML nativo e caricate dal vero loader di Kdenlive.
Non è stato verificato il gesto di modifica tramite mouse/tastiera né il
salvataggio dalla GUI. I cinque passaggi sopra completano quella verifica.

Le iterazioni preliminari sono archiviate in `.cache/iterations/`.
La storia del successivo riordino è in
[docs/riordino-2026-09-11.md](../../docs/riordino-2026-09-11.md).

## Provenienza tecnica

- [Kdenlive standalone Windows](https://kdenlive.org/download/), versione 26.08.0.
- Struttura confrontata con i [fixture ufficiali Kdenlive](https://github.com/KDE/kdenlive/tree/master/tests/dataset).
- [Titoli template](https://docs.kdenlive.org/en/titles_and_graphics/titles/title_template_titles.html)
  e [Transform](https://docs.kdenlive.org/en/effects_and_filters/video_effects/transform_distort_perspective/transform.html).
- Media: asset già presenti nei progetti Extra Coin e Buco Nero. Nessun nuovo
  materiale editoriale esterno scaricato. I file multimediali della prova sono
  locali e ignorati da Git.

## Dopo il riordino

Verificata anche la generazione e l'esportazione in una cartella pulita, senza
MP4 o cache dei media precedenti: 660 frame, 22 secondi, 1080×1920/30, senza audio.
Su questo PC la base rigenerata è `edit/prova-v006.kdenlive`; il launcher apre
la revisione generata più recente.

Per ripetere la prova di modifica senza alterare la base:

```powershell
python templates/reel-v1/qa_edit.py templates/reel-v1/edit/prova-v006.kdenlive
python templates/reel-v1/render.py templates/reel-v1/edit/prova-v006-verifica.kdenlive
```

Sostituisci v006 con la tua revisione. Il comando crea una variante nuova e
rifiuta di sovrascriverla se esiste già. Anche questa verifica modifica l'XML
nativo e usa il loader Kdenlive; il collaudo manuale della GUI rimane separato.
