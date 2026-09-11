# Scaricare il video di Ghostty Black Hole

Il file demo ufficiale del progetto è qui:

https://raw.githubusercontent.com/s0xDk/ghostty-blackhole/main/demo.gif

## Metodo rapido — PowerShell / terminale di VS Code

Apri il terminale nella cartella in cui vuoi salvare il file e lancia:

```powershell
curl.exe -L "https://raw.githubusercontent.com/s0xDk/ghostty-blackhole/main/demo.gif" -o ghostty-blackhole.gif
```

A questo punto avrai:

```text
ghostty-blackhole.gif
```

nella cartella corrente.

---

## Convertirlo in MP4

Se hai `ffmpeg` installato:

```powershell
ffmpeg -i ghostty-blackhole.gif -movflags +faststart -pix_fmt yuv420p ghostty-blackhole.mp4
```

Output:

```text
ghostty-blackhole.mp4
```

Questo formato è generalmente più comodo per Substack, social e montaggio video.

---

## Se non hai ffmpeg

Con `winget`:

```powershell
winget install Gyan.FFmpeg
```

Chiudi e riapri il terminale, poi verifica:

```powershell
ffmpeg -version
```

Quindi esegui:

```powershell
ffmpeg -i ghostty-blackhole.gif -movflags +faststart -pix_fmt yuv420p ghostty-blackhole.mp4
```

---

## Tutto in sequenza

```powershell
curl.exe -L "https://raw.githubusercontent.com/s0xDk/ghostty-blackhole/main/demo.gif" -o ghostty-blackhole.gif

ffmpeg -i ghostty-blackhole.gif -movflags +faststart -pix_fmt yuv420p ghostty-blackhole.mp4
```

## Repository

https://github.com/s0xDk/ghostty-blackhole
