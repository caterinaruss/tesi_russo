# -*- coding: utf-8 -*-
import os
import json
import subprocess
import re
import sys  # Importa il modulo sys
from pathlib import Path


# LLM 
MODEL_TO_USE = "gemma3:27b"  #"gemma3:27b"  #"deepseek-v2:16b"  #"gemma3:12b"

API_PROVIDER = "ollama"

# path istruzioni
BENCHMARK_XLSX_PATH = Path("tasks_tesi.xlsx")

# path dataset.
DATASET_DIR = Path("dataset_90")

# path main.py di SheetAgent.
SHEETAGENT_MAIN_PY = Path("main.py")

# path output risultati.
BASE_OUTPUT_DIR = Path("results1")

# --- SCRIPT DI ESECUZIONE ---

def run_benchmark():
    # Imposta a True per vedere l'output in tempo reale, False per output solo a fine esecuzione
    show_live_output = True
    """
    Esegue SheetAgent su un sottoinsieme del benchmark, una volta con e una volta senza
    il pre-processing di rilevamento tabelle, utilizzando il modello LLM specificato.
    """
    print("Caricamento del file di benchmark...")
    try:
        import pandas as pd
        df = pd.read_excel(BENCHMARK_XLSX_PATH)
        benchmark_data = df.to_dict('records')
    except Exception as e:
        print(f"ERRORE: Impossibile caricare o parsare il file Excel '{BENCHMARK_XLSX_PATH}'. Dettagli: {e}")
        return

    print(f"Trovati {len(benchmark_data)} task nel file di benchmark.")

    # Crea un dizionario per un accesso rapido ai dati del benchmark usando il nome del file
    benchmark_map = {}
    for item in benchmark_data:
        # Usa il nome del file come chiave
        file_name = item["Spreadsheet File"]
        benchmark_map[file_name] = item


    # 1. Identifica i file da processare scansionando la cartella DATASET
    files_to_process = {f for f in os.listdir(DATASET_DIR) if f.endswith('.xlsx')}
    print(f"Trovati {len(files_to_process)} file .xlsx nella cartella {DATASET_DIR}")

    # Clear the contents of CON_preprocessing and SENZA_preprocessing directories before each run
    CON_PREPROCESSING_DIR = BASE_OUTPUT_DIR / "CON_preprocessing"
    SENZA_PREPROCESSING_DIR = BASE_OUTPUT_DIR / "SENZA_preprocessing"

    for dir_path in [CON_PREPROCESSING_DIR, SENZA_PREPROCESSING_DIR]:
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_dir():
                    for sub_item in item.iterdir():
                        if sub_item.is_file():
                            sub_item.unlink()  # Remove file
                        elif sub_item.is_dir():
                            for nested in sub_item.iterdir():
                                nested.unlink()  # Remove nested files
                            sub_item.rmdir()  # Remove nested directory
                    item.rmdir()  # Remove subdirectory
                elif item.is_file():
                    item.unlink()  # Remove file

    # 2. Esegui i test
    for i, filename in enumerate(sorted(list(files_to_process))):
        # Cerca l'item corrispondente nel benchmark usando il nome del file
        item = benchmark_map.get(filename)
        
        if not item:
            print(f"ATTENZIONE: Nessuna istruzione trovata per il file '{filename}'. Salto.")
            continue

        # Usa il nome del file come ID per la cartella di output
        base_id = Path(filename).stem
        instruction = item['Instruction']
        context = item['Context']  # Potremmo usarlo per arricchire l'istruzione se necessario
        workbook_path = DATASET_DIR / filename

        print("-" * 60)
        print(f"Processing file {i+1}/{len(files_to_process)}: {filename} (ID: {base_id})")
        print(f"Istruzione: {instruction}")
        print("-" * 60)

        # Esegui per entrambe le modalità
        for use_preprocessing in [False, True]:
            mode_str = "CON_preprocessing" if use_preprocessing else "SENZA_preprocessing"
            print(f"\n--- Esecuzione in modalità: {mode_str} ---")

            # Definisci una cartella di output unica per questo run
            output_dir = BASE_OUTPUT_DIR / mode_str / base_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # 3. Costruisci ed esegui il comando
            command = [
                sys.executable,  # Usa l'interprete Python corrente
                str(SHEETAGENT_MAIN_PY),
                "--workbook_path", str(workbook_path),
                "--instruction", instruction,
                "--output_dir", str(output_dir),
                "--model_type", MODEL_TO_USE,
                "--api_provider", API_PROVIDER,
                "--verbose"
            ]

            if use_preprocessing:
                command.append("--use_table_detection")
            
            print(f"Comando: {' '.join(command)}")
            try:
                if show_live_output:
                    # Output in tempo reale
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            print(output.strip())
                    _, stderr = process.communicate()
                    if process.returncode != 0:
                        print(f"ERRORE durante l'esecuzione per {filename} in modalità {mode_str}.")
                        print(f"Errore: {stderr}")
                    else:
                        print(f"Esecuzione completata con successo. Output in: {output_dir}")
                else:
                    # Output solo a fine esecuzione
                    process = subprocess.run(command, check=True, text=True)
                    print(f"Esecuzione completata con successo. Output in: {output_dir}")
            except subprocess.CalledProcessError as e:
                print(f"ERRORE durante l'esecuzione per {filename} in modalità {mode_str}.")
            except FileNotFoundError:
                print("ERRORE: 'python' non trovato. Assicurati che Python sia nel tuo PATH.")
                return
                
    
    print("\n\nBenchmark completato!")

if __name__ == "__main__":
    run_benchmark()
