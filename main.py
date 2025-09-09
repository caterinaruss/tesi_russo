from argparse import ArgumentParser
from pathlib import Path

from core.sandbox import Sandbox
from core.session import Session
from dataset.dataloader import load_problem
from utils.enumeration import MODEL_TYPE
from utils.table_detector import analyze_workbook


def main(args):
    sandbox = Sandbox()
    problem = load_problem(Path(args.workbook_path), Path(args.db_path), args.instruction)
    
    table_detection_results = None
    if args.use_table_detection:
        print("Running multi-table detection...")
        table_detection_results = analyze_workbook(args.workbook_path, verbose=args.verbose)
        if args.verbose and table_detection_results:
            import json
            print("Table detection results:")
            print(json.dumps(table_detection_results, indent=2))

    session = Session(
        problem,
        output_dir=Path(args.output_dir),
        model_type=args.model_type,
        table_rep=args.table_rep,
        sandbox=sandbox,
        few_shot_planner=args.few_shot_planner,
        with_informer=args.with_informer,
        few_shot_informer=args.few_shot_informer,
        with_retriever=args.with_retriever,
        verbose=args.verbose,
        api_config=args.api_config,
        milvus_config=args.milvus_config,
        table_detection_results=table_detection_results,
    )
    session.run()


if __name__ == "__main__":
    parser = ArgumentParser()
    # parser.add_argument(
    #     "--instruction", type=str, default="Count the number of each Product and put the results in a new sheet."
    # )
    parser.add_argument(
        "--instruction",
        type=str,
        default='Fill the "Bookname" column. Plot a column chart showing the prices of different books in Sheet "Numbering Reference" and put it in a new sheet named "Chart".',
    )
    # parser.add_argument("--workbook_path", type=str, default="example_sheets/BoomerangSales.xlsx")
    parser.add_argument("--workbook_path", type=str, default="example_sheets/BookSales.xlsx")
    parser.add_argument("--db_path", type=str, default="./db_path")
    parser.add_argument("--output_dir", type=str, default="./output")
    parser.add_argument("--few_shot_planner", action="store_true")
    parser.add_argument("--with_informer", action="store_true")
    parser.add_argument("--few_shot_informer", action="store_true")
    parser.add_argument("--with_retriever", action="store_true")
    parser.add_argument("--add_row_number", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--use_table_detection", action="store_true", help="Enable multi-table detection.")
    parser.add_argument("--table_rep", type=str, choices=["json", "markdown", "dfloader", "html"], default="json")
    parser.add_argument(
        "--model_type",
        type=MODEL_TYPE,
        choices=list(MODEL_TYPE),
        default=None,
    )
    parser.add_argument("--api_provider", type=str, choices=["openai", "google", "ollama"], default="openai")
    parser.add_argument("--api_config", type=str, default=None)
    parser.add_argument("--milvus_config", type=str, default="./config/milvus.yaml")
    args = parser.parse_args()

    if args.api_provider == "google":
        if args.api_config is None:
            args.api_config = "./config/google.yaml"
        if args.model_type is None:
            args.model_type = MODEL_TYPE.GEMMA_3_12B
    elif args.api_provider == "ollama":
        if args.api_config is None:
            args.api_config = "./config/ollama.yaml"
        if args.model_type is None:
            # modello default Ollama
            args.model_type = MODEL_TYPE.OLLAMA_DEEPSEEK_V2_16B
    else:  # openai
        if args.api_config is None:
            args.api_config = "./config/openai.yaml"
        if args.model_type is None:
            args.model_type = MODEL_TYPE.GPT_4_1106
    
    main(args)
