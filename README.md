## Clona la repository

```bash
git clone https://github.com/caterinaruss/tesi_russo.git
cd tesi_russo
```

1. **Crea e attiva ambiente Python**
```bash
python3.10 -m venv venv
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
