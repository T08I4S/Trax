# PROMPT — NotebookLM Source Converter (Windows Desktop App)

---

## 🎯 Obiettivo

Crea un'applicazione desktop **Windows** con un **singolo eseguibile** (.exe), sviluppata in **Python** e impacchettata con **PyInstaller**. L'app si chiama **"Trax"** e permette di convertire file di vari formati in output compatibili con [NotebookLM di Google](https://notebooklm.google.com/), che accetta: PDF, file audio (MP3/WAV), e file di testo.

---

## 🖥️ Interfaccia Grafica

Usa **CustomTkinter** per un'interfaccia moderna e accattivante (dark mode di default).

### Layout generale
- **Barra dei menu in alto** con le seguenti voci:
  - `📁 File` — apri file, apri cartella, esci
  - `🖼️ Foto` — modalità conversione immagini
  - `🎬 Video/Audio` — modalità estrazione audio
  - `📄 Documenti` — modalità conversione Word/PDF
  - `⭐ NotebookLM` — **la sezione speciale** (vedi sotto)
  - `⚙️ Impostazioni` — qualità audio, DPI PDF, lingua
  - `❓ Aiuto`

- **Area centrale** — zona di drag & drop con animazione al passaggio del mouse, messaggio "Trascina i file qui oppure clicca per selezionarli"

- **Lista file caricati** — tabella con: nome file, tipo, dimensione, stato conversione (icona colorata: in attesa 🟡 / completato 🟢 / errore 🔴)

- **Barra di progresso** — visibile durante le elaborazioni, con percentuale e nome file in corso

- **Pannello output in basso** — mostra i file pronti per il download con opzioni:
  - `⬇️ Scarica singolo file` (click su ogni file)
  - `📦 Scarica tutto come .zip`

---

## ⭐ Sezione Speciale: "NotebookLM"

Questa è la funzione principale e distintiva dell'app.

L'utente trascina o seleziona file di qualsiasi tipo supportato. L'app analizza automaticamente il tipo e applica la conversione corretta per renderlo **compatibile con NotebookLM**.

### Regole di conversione per tipo di file:

#### 📊 PowerPoint (.pptx)
- Estrai le slide come **PDF** (un unico file, una pagina per slide)
- Estrai **tutte le registrazioni audio** embedded nelle slide, uniscile in ordine (slide 1, 2, 3...) in un **unico file MP3**, silenzi brevi (500ms) tra una slide e l'altra
- Output: `nome_file_slides.pdf` + `nome_file_audio.mp3`

#### 📝 Word (.docx)
- Converti in **PDF** mantenendo la formattazione
- Output: `nome_file.pdf`

#### 🖼️ Immagini (.jpg, .png, .bmp, .tiff, .webp)
- Se viene caricata una singola immagine → converti in PDF singola pagina
- Se vengono caricate più immagini → chiedi all'utente se vuole **un PDF per immagine** oppure **un unico PDF multi-pagina** (con dialog popup)
- Output: `nome_file.pdf` oppure `raccolta_immagini.pdf`

#### 🎬 Video (.mp4, .avi, .mov, .mkv)
- Estrai la **traccia audio** e salvala come **MP3** (bitrate 128kbps)
- Output: `nome_file_audio.mp3`

#### 🔊 Audio (.mp3, .wav, .m4a, .aac, .ogg)
- Converti nel formato **MP3** se non già MP3
- Output: `nome_file.mp3`

#### 📄 PDF già esistenti
- Verifica che sia leggibile (non corrotto)
- Se è un PDF scansionato (solo immagini), applica **OCR** con pytesseract per renderlo testuale
- Output: `nome_file_ocr.pdf`

---

## 📦 Librerie Python da usare

```
customtkinter       # GUI moderna
python-pptx         # lettura PowerPoint
pydub               # manipolazione audio
moviepy             # estrazione audio da video
Pillow              # manipolazione immagini
img2pdf             # immagini → PDF
reportlab           # creazione PDF
pypdf               # lettura/manipolazione PDF
pytesseract         # OCR per PDF scansionati
python-docx         # lettura Word
docx2pdf            # Word → PDF
zipfile (stdlib)    # creazione archivi ZIP
tkinter (stdlib)    # base GUI (per dialog nativi)
```

---

## ⬇️ Sistema di Download Output

Nella parte bassa dell'interfaccia appare un **pannello "Output pronti"** che si espande man mano che i file vengono elaborati.

- Ogni file ha: icona tipo, nome, dimensione, pulsante `⬇️ Scarica`
- In fondo al pannello: pulsante grande `📦 Scarica tutto (.zip)` che comprime tutti gli output in un archivio con nome `Trax_export_YYYYMMDD_HHMM.zip`
- I file restano nell'output panel fino a quando l'utente clicca `🗑️ Pulisci lista`

---

## 🎨 Design e UX

- **Tema**: dark mode con accenti in **blu elettrico** (#0096FF) e sfondo `#1a1a2e`
- **Font**: Segoe UI o equivalente moderno
- **Angoli arrotondati** su tutti i componenti (CustomTkinter li supporta nativamente)
- **Animazione drag & drop**: l'area centrale cambia colore al passaggio dei file
- **Notifiche toast** in basso a destra al completamento di ogni conversione (scompaiono dopo 3 secondi)
- **Icone**: usa emoji Unicode come icone leggere (no dipendenze esterne)

---

## ⚙️ Build finale

Usa **PyInstaller** per creare un singolo `.exe`:

```bash
pyinstaller --onefile --windowed --icon=trax.ico --name=Trax main.py
```

Includi nella build:
- Tutti gli asset (icone, font se custom)
- `tesseract` binaries per OCR (o istruzioni per installarlo separatamente con avviso in-app se non trovato)
- `ffmpeg` binaries per pydub/moviepy (bundled con `--add-binary`)

---

## 🔁 Flusso utente tipico

1. L'utente apre Trax
2. Clicca su **"NotebookLM"** nel menu in alto
3. Trascina una presentazione `.pptx` nell'area centrale
4. L'app mostra: "Trovate 3 slide con audio registrato — Elaborazione..."
5. Barra di progresso avanza
6. Nel pannello output appaiono: `lezione_slides.pdf` e `lezione_audio.mp3`
7. L'utente clicca `📦 Scarica tutto (.zip)` e salva i file
8. Carica i file su NotebookLM ✅

---

## 📌 Note implementative

- Gestisci sempre le **eccezioni** con messaggi chiari in italiano all'utente
- Se una slide PowerPoint **non ha audio**, includi comunque il PDF ma avvisa che l'MP3 non è stato generato
- Per `docx2pdf` su Windows è richiesto Microsoft Word installato — in alternativa usa `LibreOffice` in headless mode come fallback (verifica disponibilità all'avvio)
- Usa **thread separati** (threading o concurrent.futures) per le conversioni, così la GUI non si blocca mai
- Salva i file temporanei in `%TEMP%\Trax\` e pulisci all'uscita
