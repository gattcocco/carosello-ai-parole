# Showreel di Critical Inventory — prova

**53 secondi, 11 scene, 1080×1920, 30 fps, senza audio.** Rassegna dei temi dei due numeri indicati: cinema e videogiochi, lavoro culturale, giornalismo e codice, dati, web indipendente, libri e storie quotidiane.

- Video locale: `dist/showreel-v002.mp4`.
- Progetto modificabile: `edit/showreel-v002.kdenlive`.
- Avvio: `APRI-SHOWREEL.cmd` apre la revisione generata più recente.
- [Storyboard](content/storyboard.md) · [Testi](content/on-screen-copy.md) · [Caption](content/caption.md).
- **[Dove inserire le due GIF](content/gif-inserimento.md)**: 15,9–17,0 s e 40,9–42,0 s.
- [Guida Kdenlive da zero](../../templates/reel-v1/GUIDA-PRIMO-UTILIZZO-KDENLIVE.md): applica i passaggi alla copia di questo showreel.

La prova contiene due segnaposto GIF visibili, non meme già selezionati. Le immagini provengono dagli articoli: tra queste la tua infografica e la tua lavagna. Titoli, illustrazioni schematiche e animazioni sono nativi Kdenlive.

## Rigenerare

Con Python 3.10+ e la [configurazione Kdenlive del template](../../templates/reel-v1/README.md#setup-su-un-altro-pc), dalla root del repo:

```powershell
python reels/showreel-newsletter/fetch_assets.py
python reels/showreel-newsletter/build.py
python reels/showreel-newsletter/render.py reels/showreel-newsletter/edit/showreel-v002.kdenlive
```

Usa il numero stampato dal generatore: non sovrascrive revisioni o video esistenti. Gli originali devono essere presenti in `assets/raw/`; i loro URL sono in [sources.json](assets/sources.json). I file locali già scaricati sono pronti su questo PC.

Salva le modifiche manuali in una copia e conservala con i media: `edit/`, `dist/`, `previews/`, `assets/raw/` e `assets/normalized/` sono fuori Git. Le modifiche manuali non ritornano automaticamente in `project.json`.

Il serializer Kdenlive è condiviso con `templates/reel-v1`; il montaggio e gli esempi editoriali dello showreel vivono qui. Non è stato pubblicato alcun reel sui social.

## Verifiche della prova v002

Render completato con Kdenlive 26.08.0: 1590 frame, 53 secondi, 1080×1920 a 30 fps,
master muto. Verificati i media referenziati, gli effetti nativi e la posizione
dei due slot da 33 frame. Controllate visivamente le scene esportate, inclusi
i segnaposto e la chiusura; il copy principale resta entro 2 parole al secondo
e il corpo entro gli 840 px disponibili.

Anteprima locale: `previews/v002/contact-sheet.jpg`; report: `dist/qa.json`.
SRT sincronizzato: [content/text-track.srt](content/text-track.srt).
Il collaudo di modifica e salvataggio dalla GUI resta da fare: il controllo
qui svolto usa il vero loader e render nativo di Kdenlive.
