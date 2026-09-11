# Template Reel Critical Inventory — consulenza e specifica proposta

> Analisi precedente all’implementazione e al riordino. Per lo stato corrente
> vedi [la mappa della migrazione](riordino-2026-09-11.md) e il
> [template Kdenlive](../templates/reel-v1/README.md).

11 settembre 2026. Analisi del branch `reel/extra-coin`, della working copy di
Buco Nero e della storia locale di `reel/kokushobi`. Requisito confermato:
**testi e animazioni devono essere modificabili anche nell'editor video**.

La raccomandazione è costruire un sistema condiviso con **Python + Kdenlive**:
Python prepara contenuti, asset e progetto; Kdenlive conserva titoli, clip e
keyframe modificabili. Glaxnimate è un'estensione possibile per la grafica
animata più complessa. Il generatore di progetti editabili è da sviluppare e
collaudare: oggi il repository produce video con grafica incorporata nei frame.

## Cosa conservare dei lavori esistenti

| Base | Elementi da portare nel template | Limite attuale |
|---|---|---|
| Extra Coin, draft 06 | Griglia con margine destro prudente; narrazione sans; serif per domanda e verdetto; animazione del solo testo; controllo SRT/copy; preview e motion test | Renderer di 1.144 righe legato a 15 cue e a questo episodio; testi e regia ancora duplicati nel codice |
| Buco Nero, draft 02 locale | Hook e pause; finestra tecnica 4:3; reaction brevi; chiusura Critical Inventory | Renderer di 522 righe specifico dell'episodio; griglia e movimento non sempre coerenti con il brand |
| Kokushobi | Contenuto, fonti, kanji card e materiali da preservare | Sul branch esaminato lo script usa path di sessione remota e font Linux; non è la base tecnica da generalizzare |

Il [brand manual](../brand-manual-v2.md), nonostante il nome `v2`, si dichiara
già **versione 3.0**. È una buona base. Serve tradurre le sue regole in parametri
condivisi e componenti, mantenendo due varianti editoriali: **recensione** e
**racconto/scoperta**. Un template stabile non impone lo stesso numero di scene,
lo stesso rapporto del footage o la stessa durata a tutti i contenuti.

## Riscontri concreti da risolvere

1. **Copy divergente in Extra Coin.** La cue 02 dello storyboard dice
   «Ma poi ho capito che l'obiettivo era quello»; SRT e `DISPLAY_TEXT` nel
   [renderer corrente](../reels/extra-coin/render_v05.py) dicono
   «Forse voleva proprio farlo». Il controllo SRT/render passa, mentre
   `validate_paper_edit()` controlla intestazioni e alcune stringhe, non
   l'equivalenza del testo dello storyboard. Il template deve eliminare questa
   duplicazione.
2. **Timing molto diverso.** Extra Coin contiene 172 parole dopo la scheda
   identità e dura 52 secondi. Cinque cue narrative arrivano a 4 parole/s.
   La prima scheda aggiunge 20 parole in 3,5 secondi, contando i token separati
   da spazi; parte sono metadati, ma costituiscono comunque carico visivo.
   Buco Nero ha un ritmo più disteso. Il limite a 4 parole/s del template
   locale di Extra Coin non dovrebbe diventare il default dell'intera serie.
   Proposta: profilo standard attorno a 2–2,5 parole/s; profilo compatto
   esplicito, con prova di lettura su telefono. Durata e quantità di copy
   vanno bilanciate per episodio.
3. **Safe area diversa.** Extra Coin usa `x 70–910`; Buco Nero `x 70–1010`.
   Adottare il margine destro del brand come base comune e mantenere il rapporto
   4:3 per le demo tecniche. Le coordinate sono una regola compositiva del
   progetto, da verificare nell'interfaccia reale di Instagram.
4. **Reaction che muove il testo.** In Buco Nero il testo della scena 09 passa
   da `y=1190` a `y=450` all'arrivo del gatto. Il layout deve riservare spazio
   alla reaction fin dall'inizio e lasciare la frase nella stessa posizione.
5. **Accenti non centralizzati.** In Buco Nero header/progress verdi convivono
   con il rosso della scena 07; la finale usa testo verde e barra arancione.
   Anche la scheda identità di Extra Coin contiene verde e arancione. Un unico
   parametro `accent` per scena deve governare tutti gli elementi grafici.
   I colori propri del footage restano distinti dalla palette della grafica.
6. **Glitch sul testo.** Buco Nero applica `apply_glitch()` alla composizione
   completa prima di ogni confine di scena. Il modello di Extra Coin separa
   meglio layer testuale e trattamento dei media: è la direzione da conservare.
7. **Footage dimostrativo da qualificare.** Per lo shrink, `media_time()` di
   Buco Nero percorre la demo a ritroso; per la context window riusa la demo
   con una barra aggiunta. Questi montaggi non verificano da soli le due
   modalità reali. Nel template ogni selezione deve distinguere una
   dimostrazione registrata da una visualizzazione illustrativa.
8. **Chiusura e QA.** La locandina corrente è un PNG completo: il suo testo
   interno non diventa editabile importandola nell'editor. Può restare così in
   questo episodio; una futura endcard modificabile richiede elementi separati.
   Inoltre `preview()` di Buco Nero prepara 13 miniature su una griglia da 12:
   la tredicesima resta fuori dal contact sheet. La chiusura va inclusa nel QA.
9. **Portabilità e output.** I renderer recenti puntano a font di Windows;
   i quattro file richiesti esistono su questa macchina, ma non sono una
   dipendenza riproducibile altrove. Buco Nero e Extra Coin usano posizioni
   diverse per `dist/`. Il Python predefinito non trova Pillow senza ambiente
   dedicato: l'avvio deve diventare documentato e unico.

## Software open source e grado di modifica

| Software | Ruolo adatto al progetto | Valutazione |
|---|---|---|
| **Kdenlive** | Montaggio, audio, titoli nativi, trasformazioni animate e template | Prima scelta per lavorare quotidianamente sul reel |
| **Glaxnimate** | Animazioni vettoriali con sorgente e keyframe separati | Aggiunta se il prototipo evidenzia limiti nelle animazioni del testo |
| **Blender** | Grafica e animazione con forte integrazione Python, oltre al montaggio | Alternativa se prevalgono animazioni procedurali complesse; richiede un flusso di lavoro più articolato |
| **Shotcut** | Montaggio e progetti MLT XML | Alternativa per il montaggio; per questo template partirei dall'editor titoli e dall'integrazione grafica di Kdenlive |

Kdenlive è [open source](https://github.com/KDE/kdenlive) e dispone di una
[versione Windows, anche standalone](https://kdenlive.org/download/).
Offre titoli 2D, timeline multitraccia e audio:
[funzioni ufficiali](https://kdenlive.org/features/).

I [titoli template `.kdenlivetitle`](https://docs.kdenlive.org/en/titles_and_graphics/titles/title_template_titles.html)
consentono di riutilizzare una composizione sostituendo il testo; l'effetto
[Transform](https://docs.kdenlive.org/en/effects_and_filters/video_effects/transform_distort_perspective/transform.html)
supporta keyframe. Questo copre la base di posizionamento e movimento.
Stagger per riga e cambio colore della sola keyword richiedono elementi
separati o una costruzione specifica: non sono una conversione automatica delle
funzioni Pillow. La fedeltà di curve, font e impaginazione va verificata.

Per animazioni più articolate, Kdenlive apre e aggiorna sorgenti `.rawr` tramite
[Glaxnimate](https://docs.kdenlive.org/en/titles_and_graphics/graphics_and_animations/glaxnimate.html),
che si installa separatamente. L'editing avviene in Glaxnimate; la durata
cambiata nella timeline non viene automaticamente riportata al documento
animato. Anche questo comportamento va considerato nel flusso di lavoro.

Blender dispone di [video editing](https://www.blender.org/features/video-editing/)
e di un'API Python integrata, descritta nella pagina sulla
[licenza](https://www.blender.org/about/license/).
Shotcut documenta il salvataggio dei progetti MLT XML nelle sue
[FAQ](https://www.shotcut.org/FAQ/).

**Il deliverable corretto è un progetto editabile, oltre al master MP4.**
Un video con trasparenza conserva la trasparenza, ma non rende modificabili
le parole già rasterizzate. Un SRT conserva testo e tempi, ma non tutta la
regia tipografica. Un XML MLT generico non va assunto equivalente a un progetto
Kdenlive completo e correttamente riapribile.

## Specifica della base proposta

- **Formato:** 1080×1920, 30 fps; tempi interni espressi in frame.
- **Brand:** palette, font, griglia, bordi e motion preset in un solo punto.
- **Layout:** identità/hook; narrazione con media; demo tecnica; domanda o
  verdetto; reaction; chiusura. La finestra media ammette 16:9 e 4:3.
- **Testo:** massimo tre righe narrative; dimensione minima controllata.
  Un testo che non entra richiede revisione, divisione o più tempo, senza
  rimpicciolimenti indiscriminati.
- **Movimento:** entrata breve per riga, pausa stabile, uscita facoltativa;
  immagine e testo su layer indipendenti. Reaction dopo la lettura.
- **Finale:** modulo configurabile. Per Buco Nero resta la locandina ferma
  di 7 secondi; questa scelta non impone 7 secondi a ogni futuro reel.
- **Font:** selezione condivisa con file/versione e licenza identificati;
  eventuale cambiamento dai fallback attuali richiede confronto dei frame.

Il modello di ogni scena dovrà contenere ID stabile, funzione editoriale,
testo e a capo, durata, layout, accento, highlight, asset, punto di entrata e
uscita del media, crop, momento della reaction e preset di animazione.
SRT e tabella dello storyboard saranno derivati da questo modello. Note,
ragionamento editoriale e fonti continueranno a vivere nei documenti Markdown.

Per Kdenlive conviene partire da un piccolo progetto creato e salvato dalla
versione scelta dell'applicazione, con titoli ed effetti nativi. Un adattatore
Python potrà istanziarne le strutture per episodio. Occorre verificare il
formato reale e la riapertura: non è una promessa di API Python ufficiale
di Kdenlive né di compatibilità universale del suo XML.

**Gestione delle modifiche manuali:** il generatore crea una nuova revisione;
l'editor salva una copia di lavoro distinta. Non si rigenera sopra il progetto
ritoccato. Nel primo rilascio il passaggio è monodirezionale: le revisioni
editoriali da riutilizzare devono essere riportate nel modello sorgente.
La sincronizzazione automatica editor → JSON è un eventuale lavoro successivo,
non una capacità già disponibile.

## Struttura proposta dopo la consulenza

```text
brand/
  reel-brand.md
  tokens.json
  fonts/
  loghi/
templates/reel-v1/
  titles/
  motion/
  starter.kdenlive
pipeline/
  validate_project.py
  build_kdenlive.py
  export_editorial.py
reels/
  extra-coin/
  buco-nero/
  kokushobi/
    project.json
    content/
    assets/SOURCES.md
    assets/raw/
    edit/
legacy/
dist/<slug>/<revision>/
.cache/<slug>/
```

Lo schema interno mostrato sotto Kokushobi si applica a ciascun episodio.
I nomi dei nuovi script e file sono proposti, non implementati. `edit/` contiene
le revisioni native dell'episodio e i relativi titoli; cache ed export restano
rigenerabili. Le migrazioni dei path vanno fatte un episodio alla volta.

## Prova necessaria prima di chiamarlo definitivo

Costruire un prototipo con una scena narrativa di Extra Coin, una reaction di
Buco Nero, una title card e una chiusura. La prova deve dimostrare che:

1. il progetto si apre, salva e riapre nell'editor senza asset mancanti;
2. si può cambiare una frase, spostare un keyframe e sostituire un media;
3. il testo resta un titolo editabile dopo il salvataggio;
4. le animazioni conservano entrata, pausa e uscita e le reaction non spostano
   la frase;
5. i frame rispettano griglia e accento e la lettura funziona a 360×640;
6. l'export rispetta durata e formato;
7. generare una nuova revisione non sovrascrive il lavoro manuale.

Superata questa prova, portare entrambi i reel nel sistema. Il template v1 è
pronto quando un terzo episodio si costruisce cambiando contenuti e asset,
senza copiare un renderer o aggiungere condizioni legate al numero di scena.

## Riorganizzazione e branch, alla fine

GitHub restituisce `main`, `reel/extra-coin` e `reel/kokushobi`.
Nella copia locale esaminata:

- `reel/extra-coin` è a `4b02105` e comprende anche Buco Nero;
- il riferimento locale `origin/main` è a `623e786`; Extra Coin ha due commit
  successivi;
- `main` locale è a `b8023f2`, tre commit indietro rispetto a `origin/main`;
- Kokushobi è a `584dfb6` e ha **tre commit assenti da Extra Coin**:
  `6ccae9f`, `1074978`, `584dfb6`;
- `README.md`, `render.py` e `storyboard.md` di Buco Nero hanno modifiche
  locali; `Loghi DAVE/` contiene asset non ancora tracciati.

Il normale accesso Git HTTPS ha fallito per un problema di credenziali
Schannel. La lista branch e il README remoto sono stati letti tramite il
connettore GitHub. Le relazioni fra commit sopra derivano dai riferimenti
locali: prima di qualsiasi pulizia si devono aggiornare e riconfermare gli SHA.

Ordine proposto: salvare la revisione locale e inventariare gli asset;
creare riferimenti di archivio agli SHA dei branch; integrare la base recente;
recuperare o archiviare esplicitamente il contenuto esclusivo di Kokushobi;
migrare e verificare i renderer; portare la base stabile in `main`; infine
eliminare i branch di lavoro superati, locali e remoti, verificando che i
commit restino raggiungibili. La cancellazione di un branch e la rimozione
dei file legacy sono operazioni distinte.

In futuro gli episodi vivranno in cartelle; i branch serviranno a modifiche
temporanee, chiuse dopo l'integrazione.

## Verifiche eseguite e limiti

Letti renderer, manuale Reel, documenti editoriali, diff locali e storia Git;
esaminati i contact sheet disponibili e l'immagine di verifica della chiusura.
Il contact sheet storico di Buco Nero rappresenta una revisione precedente:
non è una prova completa della versione corrente a 13 scene.

FFmpeg conferma che i master locali `extra-coin-draft-06.mp4` e
`buco-nero-draft-02.mp4` durano rispettivamente 52 e 55 secondi, sono H.264
1080×1920 a 30 fps e non presentano stream audio. Eseguite isolatamente le
funzioni di controllo di Extra Coin: 15 cue valide e verifica delle
intestazioni superata. Questo non certifica l'allineamento di ogni documento.

Non è stato eseguito un nuovo render completo o un collaudo in Kdenlive.
Non sono stati modificati i renderer, spostati asset o cancellati branch.
Questo documento è la consulenza e la specifica proposta; il template
editabile definitivo resta il risultato della fase di implementazione e prova.
