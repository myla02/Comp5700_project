import os
import pandas as pd
from src.executor import (
    load_text_inputs,
    determine_kubescape_controls,
    execute_kubescape_scan,
    generate_csv_report
)

def test_load_text_inputs():
    names, reqs = load_text_inputs(
        "outputs/text/element_name_differences.txt",
        "outputs/text/element_requirement_differences.txt"
    )
    assert isinstance(names, str)
    assert isinstance(reqs, str)

def test_determine_kubescape_controls():
    names = "root\nnetwork"
    reqs = "privilege escalation"
    controls = determine_kubescape_controls(names, reqs, "outputs/text/test_controls.txt")
    assert isinstance(controls, list)

def test_execute_kubescape_scan():
    assert callable(execute_kubescape_scan)

def test_generate_csv_report():
    df = pd.DataFrame([
        {
            "FilePath": "test.yaml",
            "Severity": "failed",
            "Control name": "Test Control",
            "Failed resources": "N/A",
            "All Resources": "N/A",
            "Compliance score": 50
        }
    ])
    output = generate_csv_report(df, "outputs/text/test_kubescape.csv")
    assert os.path.exists(output)
