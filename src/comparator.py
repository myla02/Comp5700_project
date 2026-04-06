import os
import yaml


def load_yaml_files(yaml1_path, yaml2_path):
    """
    Load two YAML files and return their contents as dictionaries.
    Also removes markdown code fences if they exist.
    """
    if not os.path.exists(yaml1_path):
        raise FileNotFoundError(f"File not found: {yaml1_path}")

    if not os.path.exists(yaml2_path):
        raise FileNotFoundError(f"File not found: {yaml2_path}")

    def read_and_clean_yaml(file_path):
        with open(file_path, "r") as f:
            content = f.read()

        # Remove markdown code fences if Gemma added them
        content = content.replace("```yaml", "")
        content = content.replace("```", "")
        content = content.strip()

        data = yaml.safe_load(content)

        if data is None:
            data = {}

        if not isinstance(data, dict):
            raise ValueError(f"YAML content in {file_path} is not a dictionary")

        return data

    data1 = read_and_clean_yaml(yaml1_path)
    data2 = read_and_clean_yaml(yaml2_path)

    return data1, data2


def compare_element_names(data1, data2, output_path="outputs/text/element_name_differences.txt"):
    """
    Compare KDE names between two YAML dictionaries.
    Write differences to a text file.
    """
    names1 = set()
    names2 = set()

    for element in data1.values():
        if isinstance(element, dict) and "name" in element:
            names1.add(str(element["name"]).strip())

    for element in data2.values():
        if isinstance(element, dict) and "name" in element:
            names2.add(str(element["name"]).strip())

    differences = sorted((names1 - names2) | (names2 - names1))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        if differences:
            for name in differences:
                f.write(name + "\n")
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES\n")

    return differences


def compare_element_requirements(
    data1,
    data2,
    output_path="outputs/text/element_requirement_differences.txt"
):
    """
    Compare KDE requirements between two YAML dictionaries.
    Write differences as NAME,REQU tuples in a text file.
    """
    items1 = set()
    items2 = set()

    for element in data1.values():
        if isinstance(element, dict) and "name" in element and "requirements" in element:
            name = str(element["name"]).strip()
            requirements = element["requirements"]

            if isinstance(requirements, list):
                for req in requirements:
                    items1.add((name, str(req).strip()))

    for element in data2.values():
        if isinstance(element, dict) and "name" in element and "requirements" in element:
            name = str(element["name"]).strip()
            requirements = element["requirements"]

            if isinstance(requirements, list):
                for req in requirements:
                    items2.add((name, str(req).strip()))

    differences = sorted((items1 - items2) | (items2 - items1))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        if differences:
            for name, req in differences:
                f.write(f"{name},{req}\n")
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS\n")

    return differences


if __name__ == "__main__":
    yaml1 = "outputs/yaml/cis-r1-kdes.yaml"
    yaml2 = "outputs/yaml/cis-r2-kdes.yaml"

    data1, data2 = load_yaml_files(yaml1, yaml2)
    compare_element_names(data1, data2)
    compare_element_requirements(data1, data2)

    print("Task 2 complete.")
