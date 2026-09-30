# Crediti — immagini di Katlenburg

Tutte scaricate da Wikimedia Commons (file originali o thumbnail alla massima
risoluzione consentita dall'API in caso di limitazione di banda). Nessuna
proviene da Google Maps, anteprime di motori di ricerca o articoli
giornalistici.

| File locale | Titolo originale | Autore | Pagina Commons | Licenza |
|---|---|---|---|---|
| `katlenburg-burgberg-nordest.jpg` (+ derivato `-916`, crop verticale sul lato con la torre) | KatlenburgNordost.jpg | Kassandro | [Commons](https://commons.wikimedia.org/wiki/File:KatlenburgNordost.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `katlenburg-merian-1654.jpg` | Katlenburg 1654 nach Merian.jpg | Matthäus Merian | [Commons](https://commons.wikimedia.org/wiki/File:Katlenburg_1654_nach_Merian.jpg) | Pubblico dominio |
| `katlenburg-st-johannes.jpg` (+ derivato `-916`, crop verticale sul lato con la torre) | Katlenburg, Burgberg, Klosterkirche St. Johannes.jpg | Migebert | [Commons](https://commons.wikimedia.org/wiki/File:Katlenburg,_Burgberg,_Klosterkirche_St._Johannes.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `katlenburg-cripta-romanica.jpg` | StJohannes Katlenburg Krypta.jpg | Jan Stubenitzky/Dehio | [Commons](https://commons.wikimedia.org/wiki/File:StJohannes_Katlenburg_Krypta.jpg) | [CC BY-SA 3.0 DE](https://creativecommons.org/licenses/by-sa/3.0/de/) |
| `katlenburg-ex-refettorio.jpg` | Katlenburg, Burgberg 10, Ehem. Magazin.jpg | Migebert | [Commons](https://commons.wikimedia.org/wiki/File:Katlenburg,_Burgberg_10,_Ehem._Magazin.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `katlenburg-granaio-in-pietra.jpg` | Katlenburg, Burgberg 1, Scheune 01.jpg | Migebert | [Commons](https://commons.wikimedia.org/wiki/File:Katlenburg,_Burgberg_1,_Scheune_01.jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `katlenburg-granaio-interno-libri.jpg` | Non-profit book store at Castle Katlenburg, Germany (114232793).jpg | Bernhard Hanakam | [Commons](https://commons.wikimedia.org/wiki/File:Non-profit_book_store_at_Castle_Katlenburg,_Germany_(114232793).jpg) | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |

Note tecniche:

- `katlenburg-ex-refettorio.jpg`, `katlenburg-granaio-in-pietra.jpg` e
  `katlenburg-granaio-interno-libri.jpg` sono thumbnail a 1280px (non il file
  originale): i download del file originale sono stati bloccati da un rate
  limit dell'API Wikimedia ("Too many requests"); il thumbnail a 1280px è la
  dimensione più alta accettata senza autenticazione. Risoluzione comunque
  ampiamente sufficiente per un master 1080×1920.
- `katlenburg-burgberg-nordest.jpg` e `katlenburg-st-johannes.jpg` hanno un
  derivato `-916`: crop verticale manuale (non centrato) per includere la
  torre della chiesa, che il crop automatico centrato del builder avrebbe
  tagliato fuori. Nessuna deformazione, solo ritaglio. Usati nel reel questi
  derivati, non gli originali.
- `katlenburg-granaio-in-pietra.jpg`, `katlenburg-ex-refettorio.jpg` e
  `katlenburg-granaio-interno-libri.jpg` sono usati senza crop manuale: il
  soggetto principale è già centrato a sufficienza per il crop automatico.
- `katlenburg-cripta-romanica.jpg` e `katlenburg-merian-1654.jpg` erano
  rimaste fuori dal montaggio della v4 (vedi
  `guida-carrellata-katlenburg-storyboard.md`, sezione "Asset facoltativi").
  **In `timeline_v5.json` sono entrambe in uso**, nel beat «I libri riempiono
  prima un refettorio del Milleduecento». Il timore sul ritaglio verticale si
  e' rivelato infondato per queste due inquadrature: il cover-crop centrato
  conserva il 38% della larghezza e in quel 38% restano il complesso sul
  promontorio (Merian) e il pilastro con la volta (cripta). Verificato prima
  dell'inserimento.

## Stringa crediti compatta (per caption Instagram / titoli di coda)

Per un montaggio che usa tutte e sette le immagini (v5):

> Foto di Katlenburg: Kassandro, Migebert, Bernhard Hanakam, Jan Stubenitzky —
> CC BY-SA 3.0, via Wikimedia Commons. Veduta del 1654 di Matthaus Merian,
> pubblico dominio.

Per un montaggio senza cripta e senza veduta storica (v4):

> Foto di Katlenburg: Kassandro, Migebert, Bernhard Hanakam — CC BY-SA 3.0,
> via Wikimedia Commons.
