## Clona la repository

```bash
git clone https://github.com/caterinaruss/tesi_russo.git
cd tesi_russo
```

1. **Crea e attiva ambiente Python**
*(Nota: è richiesta la versione 3.10 di Python o una successiva)*

<details>
<summary>Come verificare e aggiornare la versione di Python</summary>

Per verificare la tua versione di Python, esegui:
```bash
python3 --version
```
Se la versione è inferiore alla 3.10, dovrai aggiornarla. La procedura varia a seconda del tuo sistema operativo:

- **macOS (con [Homebrew](https://brew.sh/)):**
  ```bash
  brew install python@3.10
  ```
- **Debian/Ubuntu:**
  ```bash
  sudo apt update
  sudo apt install python3.10
  ```
- **Windows:**
  Scarica l'installer dal [sito ufficiale di Python](https://www.python.org/downloads/).

</details>

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

2. **Installa e avvia Ollama** (mantieni questo terminale aperto)
```bash
curl https://ollama.ai/install.sh | sh
ollama serve
```

3. **Scarica il modello** (in un nuovo terminale)
```bash
ollama pull gemma3:27b
```

4. **Avvia i test**
```bash
python run_benchmark.py
```

Gli output verranno salvati in:
- `results1/CON_preprocessing/`
- `results1/SENZA_preprocessing/`
