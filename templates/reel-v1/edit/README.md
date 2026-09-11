# Progetti generati e copie di lavoro

`python templates/reel-v1/build.py` crea qui una nuova revisione `prova-vNNN.kdenlive`,
i titoli nativi, la timeline MLT, il modello JSON e l'SRT. Su un clone nuovo parte
da v001. Il launcher apre la revisione generata con il numero più alto.

I file generati contengono la root locale del progetto: si rigenerano su ogni PC.
Questa cartella (eccetto questo README) è ignorata da Git, comprese le copie
manuali. Conservale con i relativi media in un backup o archivio Kdenlive; un push
non le salva. Non sostituire il modello `project.json` con un export MP4.
