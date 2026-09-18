# Fonti — La discarica dei libri

## A. Library Organization

- Titolo: *Library Organization*
- Produzione: Coronet Instructional Films, 1951
- Fonte: Internet Archive / Prelinger Archives — https://archive.org/details/0044LibraryOrganization20110400
- File scaricato: `raw/library-organization.mp4` (MP4 diretto, 64 MB, durata 10:20)
- Uso: contrappunto simbolico (biblioteca ideale). Non attribuito alla DDR nel testo o nelle didascalie.
- Diritti: Prelinger Archives distribuisce la maggior parte del proprio catalogo come materiale sponsorizzato/educativo di pubblico dominio o a licenza permissiva; verificare la scheda specifica su archive.org prima della pubblicazione pubblica.

Clip estratte:

| Clip | Timecode sorgente | Contenuto |
|---|---|---|
| L1 | 00:00:07–00:00:12 | Sala di lettura, scaffali sullo sfondo |
| L2 | 00:03:10–00:03:15 | Schedario a cassetti |
| L3 | 00:07:12–00:07:17 | Dorso di "New Practical Physics" |
| L4 | 00:08:35–00:08:40 | Scaffale, etichetta di classificazione "920" |

## B. Bücherdeponie Plottendorf

- Titolo: *Bücherdeponie Plottendorf*
- Data delle riprese: 22 luglio 1991
- Autore/archivio: KANAL X — Archiv Bürgerbewegung Leipzig e.V.
- Fonte: https://vimeo.com/935726773 (pagina archivio: https://kanalx.org/rohmaterial/)
- File scaricato: `raw/plottendorf.mp4` (via embed player.vimeo.com, 720x540, ~100 MB, durata 7:58)
- Uso: prova documentaria della distruzione/abbandono dei libri della DDR.
- Diritti: materiale d'archivio associato a un movimento civico (Archiv Bürgerbewegung Leipzig e.V.); non risulta una licenza esplicita sulla pagina. Uso qui a scopo di montaggio critico/divulgativo con attribuzione diretta — verificare condizioni con l'archivio prima di una pubblicazione pubblica, come già segnalato nel documento di montaggio.

Clip estratte:

| Clip | Timecode sorgente | Contenuto |
|---|---|---|
| P1 | 00:00:05–00:00:10 | Inquadratura introduttiva della massa di libri |
| P2 | 00:01:30–00:01:35 | Dettaglio di fascicoli/copertine (es. copertina blu "Der..." visibile) |
| P3 | 00:03:30–00:03:35 | Campo largo della discarica indoor |
| P4 | 00:05:12–00:05:17 | **Spostato da 00:06:40** (marker originale: esterno senza libri, passaggio debole). Pacco di libri sottovuoto, copertina di libro per bambini leggibile ("… Adebar und Kunigunde"), inquadratura statica — usato anche come fermo immagine nel segmento 10 della timeline |

## C. Fonti testuali (fact-check per la v4 "tg divulgativo")

- **"Frane nella terra dei lettori" + "I cingoli del mercato"** — il manifesto, 30 aprile 1991, pag. 10 (cultura e comunicazione), firmati Guido Ambrosino ed Elisabetta D'Erme. File: `../../../../nuovi materiali per reel libri lipsia/articolo manifesto.pdf`.
  Dati usati nel copy: fiera di Lipsia 24–29 aprile 1991, nata nel 1470, "forse l'ultima" edizione; produzione DDR di 6 milioni di libri/anno con tiratura media 23.000 copie; espositori 340 dall'ovest / 89 dall'est (D'Erme — nello stesso articolo compare anche un dato "503 espositori, 343 dall'ovest" di Ambrosino, incoerente con l'altro conteggio, probabilmente per ambiti di conteggio diversi o refusi OCR: **usato solo il dato 340/89, più coerente e verificabile nel testo**); Aufbau Verlag da 180 a 55 dipendenti (Volk & Welt da 130 a 35, non usato nel copy per non sovraccaricare la battuta); "terra dei lettori" come autodefinizione DDR; censura e sovvenzioni statali a editori/autori/prezzi.
- **"Ritratto — Il pastore del libro"** — Süddeutsche Zeitung (sueddeutsche.de), di Cord Aschenbrenner, 27/28 gennaio 2017. File: `../../../../nuovi materiali per reel libri lipsia/Ritratto - Il pastore del libro - Società - SZ.de.pdf`.
  Dati usati nel copy: Martin Weskott, pastore di San Giovanni a Katlenburg dal 1979 (1.800 parrocchiani — **non usato come "popolazione del paese"**, la fonte non lo specifica, solo i parrocchiani); vide la foto della discarica di Plottendorf sulla SZ nel maggio 1991; autori citati nella discarica: Brigitte Reimann, Stefan Heym, Christoph Hein, Walter Janka, Heinrich Mann, Dostoevskij, Jaroslav Seifert (Nobel); anche libri di fisica, cucina, musica, biologia e "Come riparare la tua Trabant"; 150 viaggi in camion; libri prima nel refettorio duecentesco (XII sec.) poi nella Zehntscheune gotica; oggi un milione di libri; distribuzione la domenica contro donazione a "Brot für die Welt" (oltre 130.000 € raccolti nel tempo).
  Dettagli **non usati** nel copy per motivi di ritmo/pertinenza (restano disponibili per una v5 più lunga): il paragone con il pastore Oberlin, l'aneddoto del ricercatore Max-Planck/sonda Cassini, la rassegna "Müll-Literaten lesen" dal 1992, il Bundesverdienstkreuz 1993, le sculture di Wilfried Völlger, il pensionamento di Weskott nel 2017.

## D. Immagini fisse dell'episodio

Stanno in `assets/images/` ma **non sono versionate** (il `.gitignore`
dell'episodio esclude i binari): chi clona il repo deve recuperarle a mano,
e `build_fullscreen.py` fallisce con un errore che ne stampa il percorso.

| Id | File locale | Provenienza | Diritti |
|---|---|---|---|
| `trabant` | `images/trabant-manuale-copertina.webp` | Copertina originale del manuale *Ich fahre einen Trabant* | Editore DDR, successori non verificati. Non ridistribuire |
| `pastore` | `images/martin-weskott.avif` | Ritratto di Martin Weskott fra le pile di libri | Foto giornalistica associata al ritratto SZ. Non ridistribuire |
| `kat_*` | `images/katlenburg/` | Wikimedia Commons | CC BY-SA 3.0 e pubblico dominio — vedi `images/katlenburg/CREDITS.md` |
| `marco_*` | `images/ddr-marchi/card/` | Banconote DDR, Internet Archive `1948ddr1markbanknotes` | Nessuna licenza dichiarata dall'uploader. Stato dissolto, valuta demonetizzata nel 1990, documenti ufficiali esenti in diritto tedesco: rischio basso, non nullo |
| `cta_newsletter` | `brand/loghi/` | Grafica propria | Nostra |

Le card `marco_*` sono generate da `scripts/compose_banknotes.py` a partire
dalle scansioni in `images/ddr-marchi/`: rigenerabili, non vanno versionate.

### Video

| Id | File | Provenienza | Diritti |
|---|---|---|---|
| `trabant_ad` | `clips/trabant_ad.mp4` | *East German Trabant 601 Car Advertising Film*, 1969 — https://archive.org/details/trabant601 | L'uploader dichiara il pubblico dominio perche' «l'azienda statale non esiste piu'». **Il ragionamento non e' valido**: l'estinzione di un'impresa non estingue il diritto d'autore. Rischio contenuto ma non verificato |

### Materiali fuori dal progetto

Gli scan delle fonti testuali — `articolo manifesto.pdf`, il ritratto SZ, la
traccia vocale usata dalle versioni v2/v3 — stanno in una cartella `nuovi
materiali per reel libri lipsia` esterna a `PROGETTO`. Non servono alla
pipeline a testo animato, che non usa audio: servono solo per rileggere le
fonti.

## Crediti da mostrare nel video/caption di pubblicazione

> *Library Organization*, Coronet Instructional Films, 1951 — via Internet Archive / Prelinger Archives
> *Bücherdeponie Plottendorf*, KANAL X / Archiv Bürgerbewegung Leipzig e.V., 22 luglio 1991

La brevità dell'estratto e la finalità critica o divulgativa non rendono automaticamente
qualsiasi riuso libero: mantenere l'attribuzione sopra, il rapporto diretto tra immagini
e commento, e verificare le condizioni delle fonti prima della pubblicazione pubblica.
