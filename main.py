import argparse
from src.extractor import load_and_validate_documents, run_llm_and_extract_kdes, save_llm_outputs_to_text
from src.comparator import load_yaml_files, compare_element_names, compare_element_requirements
from src.executor import load_text_inputs, determine_kubescape_controls, execute_kubescape_scan, generate_csv_report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf1")
    parser.add_argument("pdf2")
    args = parser.parse_args()

    docs = load_and_validate_documents(args.pdf1, args.pdf2)
    outputs = run_llm_and_extract_kdes(docs)
    save_llm_outputs_to_text(outputs)

    yaml1 = f"outputs/yaml/{args.pdf1.split('/')[-1].replace('.pdf','')}-kdes.yaml"
    yaml2 = f"outputs/yaml/{args.pdf2.split('/')[-1].replace('.pdf','')}-kdes.yaml"

    data1, data2 = load_yaml_files(yaml1, yaml2)
    compare_element_names(data1, data2)
    compare_element_requirements(data1, data2)

    names, reqs = load_text_inputs()
    determine_kubescape_controls(names, reqs)

    df = execute_kubescape_scan()
    generate_csv_report(df)

    print("Pipeline complete.")

if __name__ == "__main__":
    main()
