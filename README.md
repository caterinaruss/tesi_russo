# Istruzioni per AWS

## Setup (da eseguire in ordine)

1. **Crea e attiva ambiente Python**

Se non hai Python >= 3.10, puoi installarlo/aggiornarlo su macOS con Homebrew:
```bash
brew install python@3.10
```
Dopo l'installazione, usa:
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Se hai già Python >= 3.10, puoi usare direttamente:
```bash
python -m venv venv
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
