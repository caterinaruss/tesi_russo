# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path
import pandas as pd

MODEL_TO_USE = "gemma3:27b"       #"gemma3:12b"  # Modello LLM da utilizzare
API_PROVIDER = "ollama"

BENCHMARK_XLSX_PATH = Path("tasks_tesi.xlsx")     # Path del file benchmark istruzioni
DATASET_DIR = Path("dataset_90")                  # Cartella dataset di input
SHEETAGENT_MAIN_PY = Path("main.py")              # Main script SheetAgent
BASE_OUTPUT_DIR = Path("results1")                # Cartella risultati

PREPROCESSING_MODES = [
    ("SENZA_preprocessing", False),
    ("CON_preprocessing", True)
]

def clear_output_folder(folder_path: Path):
    """ Svuota completamente una cartella di output """
    if not folder_path.exists():
        return
    for item in folder_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            clear_output_folder(item)
            item.rmdir()

def clear_all_outputs():
    """ Svuota tutte le cartelle delle due modalità prima dei test """
    for mode, _ in PREPROCESSING_MODES:
        clear_output_folder(BASE_OUTPUT_DIR / mode)

def load_benchmark_instructions(path: Path):
    """ Carica istruzioni e mapping dal file xlsx """
    try:
        df = pd.read_excel(path)
        data = df.to_dict('records')
        print(f"Trovati {len(data)} task nel file di benchmark.")
        return {item["Spreadsheet File"]: item for item in data}
    except Exception as e:
        print(f"ERRORE: Impossibile caricare/parsing file Excel '{path}'. Dettagli: {e}")
        return {}

def get_files_to_process(dataset_dir: Path):
    """ Ritorna l'elenco dei file .xlsx da processare """
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith('.xlsx')])
    print(f"Trovati {len(files)} file .xlsx nella cartella {dataset_dir}")
    return files

def build_command(workbook_path: Path, instruction: str, output_dir: Path, use_preprocessing: bool):
    """ Crea la command line per subprocess """
    cmd = [
        sys.executable,
        str(SHEETAGENT_MAIN_PY),
        "--workbook_path", str(workbook_path),
        "--instruction", instruction,
        "--output_dir", str(output_dir),
        "--model_type", MODEL_TO_USE,
        "--api_provider", API_PROVIDER,
        "--verbose"
    ]
    if use_preprocessing:
        cmd.append("--use_table_detection")
    return cmd

def run_task(filename: str, instruction: str, mode: str, use_preprocessing: bool, show_live_output: bool):
    """ Esegue SheetAgent su una combinazione file/modalità """
    base_id = Path(filename).stem
    output_dir = BASE_OUTPUT_DIR / mode / base_id
    output_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = DATASET_DIR / filename

    print("-" * 60)
    print(f"Processing: {filename} (id: {base_id}) [{mode}]")
    print(f"Istruzione: {instruction}")
    print("-" * 60)

    command = build_command(workbook_path, instruction, output_dir, use_preprocessing)
    print(f"Comando: {' '.join(command)}")
    try:
        if show_live_output:
            # Output in tempo reale
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            _, stderr = process.communicate()
            if process.returncode != 0:
                print(f"ERRORE durante l'esecuzione per {filename} in modalità {mode}.")
                print(f"Errore: {stderr}")
            else:
                print(f"Esecuzione completata con successo. Output in: {output_dir}")
        else:
            process = subprocess.run(command, check=True, text=True)
            print(f"Esecuzione completata con successo. Output in: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"ERRORE durante l'esecuzione per {filename} in modalità {mode}.")
    except FileNotFoundError:
        print("ERRORE: 'python' non trovato. Assicurati che Python sia nel PATH.")

def run_benchmark(show_live_output=True):
    """ Funzione principale di orchestrazione """
    print("Caricamento del file di benchmark...")
    benchmark_map = load_benchmark_instructions(BENCHMARK_XLSX_PATH)
    if not benchmark_map:
        print("Errore nel caricamento delle istruzioni. Interrotto.")
        return

    files_to_process = get_files_to_process(DATASET_DIR)
    clear_all_outputs()

    for i, filename in enumerate(files_to_process):
        item = benchmark_map.get(filename)
        if not item:
            print(f"ATTENZIONE: Nessuna istruzione trovata per il file '{filename}'. Salto.")
            continue

        for mode_name, use_preprocessing in PREPROCESSING_MODES:
            run_task(
                filename=filename,
                instruction=item['Instruction'],
                mode=mode_name,
                use_preprocessing=use_preprocessing,
                show_live_output=show_live_output
            )

    print("\nBenchmark completato!")

if __name__ == "__main__":
    run_benchmark()
