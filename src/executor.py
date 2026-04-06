import os
import json
import zipfile
import subprocess
import pandas as pd


def load_text_inputs(
    names_diff_path="outputs/text/element_name_differences.txt",
    req_diff_path="outputs/text/element_requirement_differences.txt"
):
    if not os.path.exists(names_diff_path):
        raise FileNotFoundError(f"File not found: {names_diff_path}")

    if not os.path.exists(req_diff_path):
        raise FileNotFoundError(f"File not found: {req_diff_path}")

    with open(names_diff_path, "r") as f:
        names_text = f.read().strip()

    with open(req_diff_path, "r") as f:
        req_text = f.read().strip()

    return names_text, req_text


def determine_kubescape_controls(
    names_text,
    req_text,
    output_path="outputs/text/mapped_controls.txt"
):
    combined = f"{names_text}\n{req_text}".lower()

    keyword_to_control = {
        "root": "C-0013",
        "non-root": "C-0013",
        "privilege": "C-0016",
        "escalation": "C-0016",
        "secret": "C-0012",
        "credential": "C-0012",
        "service account": "C-0034",
        "network": "C-0030",
        "ingress": "C-0030",
        "egress": "C-0030",
        "hostpath": "C-0048",
        "hostnetwork": "C-0041",
        "capabilities": "C-0046",
        "resources": "C-0009",
        "limits": "C-0009",
        "memory": "C-0004",
        "cpu": "C-0050",
        "registry": "C-0001",
        "registries": "C-0001"
    }

    no_name_diff = names_text == "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES"
    no_req_diff = req_text == "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS"

    controls = set()

    if not (no_name_diff and no_req_diff):
        for keyword, control in keyword_to_control.items():
            if keyword in combined:
                controls.add(control)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        if no_name_diff and no_req_diff:
            f.write("NO DIFFERENCES FOUND\n")
        elif controls:
            for control in sorted(controls):
                f.write(control + "\n")
        else:
            f.write("NO DIFFERENCES FOUND\n")

    return sorted(controls)


def execute_kubescape_scan(
    controls_file_path="outputs/text/mapped_controls.txt",
    zip_path="project-yamls.zip",
    extract_dir="project-yamls",
    json_output_path="outputs/text/kubescape_results.json"
):
    if not os.path.exists(controls_file_path):
        raise FileNotFoundError(f"File not found: {controls_file_path}")

    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"File not found: {zip_path}")

    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(os.path.dirname(json_output_path), exist_ok=True)

    if not os.listdir(extract_dir):
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

    scan_target = os.path.join(extract_dir, "YAMLfiles")
    if not os.path.exists(scan_target):
        scan_target = extract_dir

    with open(controls_file_path, "r") as f:
        control_text = f.read().strip()

    if control_text == "NO DIFFERENCES FOUND":
        cmd = [
            "kubescape", "scan", scan_target,
            "--format", "json",
            "--format-version", "v2",
            "--output", json_output_path
        ]
    else:
        controls = [line.strip() for line in control_text.splitlines() if line.strip()]

        if len(controls) == 1:
            cmd = [
                "kubescape", "scan", "control", controls[0], scan_target,
                "--format", "json",
                "--format-version", "v2",
                "--output", json_output_path
            ]
        else:
            cmd = [
                "kubescape", "scan", scan_target,
                "--format", "json",
                "--format-version", "v2",
                "--output", json_output_path
            ]

    subprocess.run(cmd, check=True)

    with open(json_output_path, "r") as f:
        results = json.load(f)

    rows = []

    if isinstance(results, dict):
        controls_data = results.get("summaryDetails", {}).get("controls", {})

        if isinstance(controls_data, dict):
            for control_id, control_info in controls_data.items():
                status_info = control_info.get("statusInfo", {})
                severity = status_info.get("status", "N/A")
                control_name = control_info.get("name", control_id)
                failed_resources = control_info.get("failedResources", "N/A")
                all_resources = control_info.get("allResources", "N/A")
                compliance_score = control_info.get("complianceScore", "N/A")

                if isinstance(failed_resources, list):
                    failed_resources = len(failed_resources)
                if isinstance(all_resources, list):
                    all_resources = len(all_resources)

                rows.append({
                    "FilePath": scan_target,
                    "Severity": severity,
                    "Control name": control_name,
                    "Failed resources": failed_resources,
                    "All Resources": all_resources,
                    "Compliance score": compliance_score
                })

    df = pd.DataFrame(rows, columns=[
        "FilePath",
        "Severity",
        "Control name",
        "Failed resources",
        "All Resources",
        "Compliance score"
    ])

    return df


def generate_csv_report(
    df,
    output_csv_path="outputs/text/kubescape_results.csv"
):
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    return output_csv_path


if __name__ == "__main__":
    names_text, req_text = load_text_inputs()
    determine_kubescape_controls(names_text, req_text)
    df = execute_kubescape_scan()
    generate_csv_report(df)
    print("Task 3 complete.")
