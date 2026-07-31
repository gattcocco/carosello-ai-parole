# Carosello Instagram — «Le parole nuove dell'AI»

9 card, formato 4:5 (1080×1350). Ogni card: una parola, una definizione, un'illustrazione.

## Come funziona la pipeline (leggi prima)

**Regola 1 — Il testo non va nell'immagine.** I generatori sbagliano ancora troppo spesso il rendering del testo, e in italiano peggio. Genera solo le illustrazioni, poi monta titolo e definizione in Canva (o simili) sopra l'immagine. Così hai anche font coerenti con la tua identità e puoi correggere un refuso senza rigenerare.

**Regola 2 — Una sola chat, stile bloccato.** Apri una nuova chat ChatGPT, incolla il Prompt 0 (lo style lock), poi genera le card una alla volta *nella stessa conversazione*. Ogni prompt di card ripete comunque il blocco stile in coda: la coerenza tra immagini generate separatamente è il punto debole di questi strumenti, meglio dirlo due volte che una.

**Regola 3 — Rigenera, non correggere.** Se una card esce male, non chiedere modifiche puntuali ("togli il terzo braccio"): rigenera con il prompt intero, eventualmente aggiungendo un vincolo. Le modifiche puntuali degradano lo stile.

**Regola 4 — Lascia aria in basso.** Ogni prompt chiede già composizione centrata con il terzo inferiore semplice/scuro: è lo spazio dove monterai il testo.

---

## Prompt 0 — Style lock (incollalo per primo)

> Sto per chiederti una serie di 9 illustrazioni per un carosello Instagram. Devono essere PERFETTAMENTE coerenti tra loro, come uscite dalla stessa mano. Lo stile, identico per tutte, è questo: illustrazione flat editoriale in stile rivista (tipo The New Yorker / Il Post), texture leggera tipo risograph, palette limitata a 4 colori: blu notte (#1B2A4A), crema (#F5EFE0), arancio caldo (#E8632C), azzurro polvere (#8FB8D8). Niente gradienti, niente 3D, niente fotorealismo, NIENTE TESTO né lettere nell'immagine. Composizione centrata, un solo soggetto per immagine, sfondo crema, terzo inferiore dell'immagine visivamente semplice (servirà per il testo). Formato verticale 4:5. Conferma che hai capito e aspetta i prompt uno alla volta.

---

## Le card

### Card 1 — Copertina
**Testo da montare:** LE PAROLE NUOVE DELL'AI / 7 termini per dire cose che vivevi già (+ 2 coniati da me)
**Prompt:**
> Prima illustrazione della serie: un dizionario aperto da cui si sollevano in volo piccole forme luminose astratte (chip, fumetti, scintille), come parole che escono dalle pagine. Atmosfera curiosa e leggera. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 2 — Vibe coding
**Testo da montare:** VIBE CODING — programmare dicendo all'AI cosa vuoi, dimenticando che il codice esista. Coniata da Andrej Karpathy a febbraio 2025, parola dell'anno Collins.
**Prompt:**
> Una persona rilassata su una sdraio con le mani dietro la testa, gli occhi chiusi, mentre accanto a lei blocchi astratti si impilano da soli formando una piccola torre ordinata (un'app che si costruisce da sé). Le mani NON toccano nulla. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 3 — Pappagalli stocastici
**Testo da montare:** PAPPAGALLI STOCASTICI — un modello ricuce frammenti di ciò che ha letto, secondo le probabilità, senza sapere cosa significano. Dal paper di Bender, Gebru e colleghe (2021).
**Prompt:**
> Un pappagallo elegante fatto interamente di ritagli di carta strappata (frammenti di pagine, senza lettere leggibili, solo righe astratte che suggeriscono testo), appollaiato su un trespolo. Bello da lontano, patchwork da vicino. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo leggibile, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 4 — Allucinazione
**Testo da montare:** ALLUCINAZIONE — quando il modello inventa, con totale sicurezza. Parola dell'anno Cambridge 2023.
**Prompt:**
> Un piccolo robot dall'aria fiduciosa e soddisfatta che dipinge su una tela un oggetto impossibile (una scala di Escher o una teiera con due beccucci), pennello in mano, petto in fuori, per niente in dubbio. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 5 — Jailbreak
**Testo da montare:** JAILBREAK — convincere l'AI a fare ciò che le è stato vietato. Termine rubato agli iPhone sbloccati.
**Prompt:**
> Una gabbia per uccelli aperta con la porticina spalancata; un piccolo robot ne sta uscendo in punta di piedi con aria complice, tenendo una chiave a forma di fumetto/nuvoletta di dialogo. Tono giocoso, non minaccioso. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 6 — Slop
**Testo da montare:** SLOP — la brodaglia generata che nessuno ha chiesto e nessuno leggerà. Parola dell'anno Merriam-Webster 2025.
**Prompt:**
> Un nastro trasportatore che riversa una colata densa e grigia-azzurra di fogli, fumetti e forme indistinte dentro un imbuto a forma di smartphone che trabocca. Sensazione di eccesso e monotonia, quasi comica. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 7 — AI blues *(coniata da me)*
**Testo da montare:** AI BLUES — quando generi ma non hai la sensazione di creare. Nostalgia di qualcosa che avevi, e che la comodità ti ha tolto.
**Prompt:**
> Una persona di sera al tavolo, malinconica ma serena, che tiene in mano una penna stilografica e la guarda; alle sue spalle, sfocato e freddo, il bagliore azzurro di uno schermo acceso. Dominante blu notte, l'unico punto arancio è la penna. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema scuro/blu per questa card, terzo inferiore semplice, 4:5.]

### Card 8 — Reading debt *(coniata da me)*
**Testo da montare:** READING DEBT — il debito di lettura, cugino del debito tecnico: l'AI produce più testo di quanto ne leggerai mai, e il non-letto matura interessi. Paghi la macchina per scrivere ciò che poi paghi la macchina per non leggere.
**Prompt:**
> Una persona minuscola seduta alla scrivania con una tazzina di caffè, davanti a una montagna incombente ma ordinata di pile di fogli che esce da un piccolo laptop, come scontrini che non finiscono mai. La montagna è alta, la persona è calma e piccolissima. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

### Card 9 — CTA
**Testo da montare:** E TU? Ne conosci altre, o ne hai coniate di tue? Scrivile nei commenti: le migliori finiscono nel pezzo di settembre, con attribuzione. → link in bio
**Prompt:**
> Tante nuvolette di dialogo vuote di forme e dimensioni diverse che convergono giocosamente verso il centro dell'immagine, come una conversazione che si accende. Una sola nuvoletta è arancio, le altre blu e azzurre. [Stesso stile della serie: flat editoriale, texture risograph, palette blu notte/crema/arancio/azzurro, niente testo, sfondo crema, terzo inferiore semplice, 4:5.]

---

## Caption del post (pronta)

L'AI porta con sé parole nuove — e due dizionari hanno appena eletto parole dell'anno nate dall'AI, nello stesso anno. Nel carosello: 7 termini che nominano cose che vivevi già, più 2 che ho coniato io. Swipe fino in fondo e dimmi la tua: le migliori parole dei commenti finiscono nel pezzo lungo di settembre, con attribuzione. 🔗 Post completo su Substack, link in bio.

`#AI #intelligenzaartificiale #vibecoding #linguaggio #parole #comunicazione #digitalculture`

---

## Checklist finale

1. Genera le 9 immagini nella stessa chat, in ordine, una alla volta
2. Scarta e rigenera le incoerenti (di solito 2-3 su 9)
3. Monta i testi in Canva: stesso font per tutti i titoli, corpo più piccolo per le definizioni, sempre nel terzo inferiore
4. Card 7 (AI blues) è volutamente più scura delle altre: è il momento emotivo del carosello, non "correggerla"
5. Esporta a 1080×1350, ordina: la copertina decide il click, la CTA decide i commenti
