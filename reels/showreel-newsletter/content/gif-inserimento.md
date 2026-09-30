# Dove inserire le GIF

La prova ha due slot già presenti nella timeline, con guide e clip chiamati `GIF-01-INSERISCI-QUI` e `GIF-02-INSERISCI-QUI`. Sono **reaction**: non aggiungere scritte alla GIF e non coprire il testo del reel.

| Slot | Secondi | Timecode Kdenlive a 30 fps | Soggetto da cercare | Perché qui |
|---|---|---|---|---|
| GIF 01 | **15,9–17,0** | **00:00:15:27 → 00:00:17:00** | Qualcuno che sgranocchia cracker o aspetta il pranzo; reaction asciutta, non frenetica | Chiude «E chi porta solo i cracker», dopo la tua infografica sulla writers’ room. |
| GIF 02 | **40,9–42,0** | **00:00:40:27 → 00:00:42:00** | Qualcuno attaccato al telefono, esasperato da una chiamata interminabile; meglio un telefono fisso | Controcampo comico alla cabina, prima della tesi finale. |

Ogni slot dura **33 frame = 1,1 secondi**. La fine indicata è esclusiva: l’ultimo frame visibile è rispettivamente 00:00:16:29 e 00:00:41:29.

## Inserimento a mano in Kdenlive

1. Apri la prova e salva una copia `showreel-v002-manuale.kdenlive` nella stessa cartella `edit/`.
2. Importa la GIF (o la sua conversione MP4 muta) nel contenitore del progetto.
3. Vai alla guida `GIF 01` o `GIF 02`. Il segnaposto si trova sulla traccia **Media**.
4. Rimuovi **solo quel segnaposto**, senza eliminazione con scorrimento/ripple: la durata delle altre clip deve rimanere invariata.
5. Metti la GIF nello spazio liberato, esattamente all’inizio dello slot. Imposta durata `00:00:01:03`, ossia 33 frame, nella finestra Durata della clip.
6. Ritaglia e usa **Transform / Trasforma** per tenerla nella cornice superiore: x=70…910, y=390…863. Per una sorgente 16:9 già normalizzata a 840×473, il progetto compensa il letterbox MLT con X=70, Y≈−120,17, larghezza=840 e altezza≈1493,33. Per proporzioni diverse usa il monitor come riferimento e ritaglia prima; non copiare quei numeri alla cieca.
7. Lascia i titoli sulle loro tracce. La frase deve restare ferma fino al taglio. Riproduci l’intera scena, non solo la GIF.

## Inserimento tramite codice

Salva una clip già selezionata (almeno 1,1 secondi) in:

```text
reels/showreel-newsletter/assets/raw/gif-01-cracker.gif
reels/showreel-newsletter/assets/raw/gif-02-telefono.gif
```

Rilancia `python reels/showreel-newsletter/build.py`: la nuova revisione usa automaticamente la GIF al posto del segnaposto, la converte in MP4 muto e la ritaglia nella finestra. Le revisioni esistenti rimangono intatte. Il file deve partire dal momento che vuoi usare.

Registra URL e credito in `assets/SOURCES.md`. Le GIF non sono state ancora scelte né scaricate: per ora il video contiene due segnaposto visibili. Se non trovi una reaction adatta, prolunga la foto precedente fino alla fine della scena e rimuovi il segnaposto: la narrazione funziona comunque.
