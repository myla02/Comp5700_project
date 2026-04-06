from src.comparator import (
    load_yaml_files,
    compare_element_names,
    compare_element_requirements
)


def test_load_yaml_files():
    data1, data2 = load_yaml_files(
        "outputs/yaml/cis-r1-kdes.yaml",
        "outputs/yaml/cis-r2-kdes.yaml"
    )
    assert isinstance(data1, dict)
    assert isinstance(data2, dict)


def test_compare_element_names():
    data1 = {
        "element1": {
            "name": "username",
            "requirements": ["must exist"]
        }
    }

    data2 = {
        "element1": {
            "name": "password",
            "requirements": ["must exist"]
        }
    }

    differences = compare_element_names(
        data1,
        data2,
        "outputs/text/test_element_name_differences.txt"
    )

    assert isinstance(differences, list)
    assert len(differences) > 0


def test_compare_element_requirements():
    data1 = {
        "element1": {
            "name": "username",
            "requirements": ["must exist"]
        }
    }

    data2 = {
        "element1": {
            "name": "username",
            "requirements": ["must be encrypted"]
        }
    }

    differences = compare_element_requirements(
        data1,
        data2,
        "outputs/text/test_element_requirement_differences.txt"
    )

    assert isinstance(differences, list)
    assert len(differences) > 0
