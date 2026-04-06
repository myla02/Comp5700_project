import os
import warnings
import yaml
import torch
from pypdf import PdfReader
from transformers import pipeline


def load_and_validate_documents(pdf1_path, pdf2_path):
    documents = {}

    for pdf_path in [pdf1_path, pdf2_path]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        if not pdf_path.lower().endswith(".pdf"):
            raise ValueError(f"Invalid file type: {pdf_path}")

        text_parts = []

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reader = PdfReader(pdf_path)

            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception:
                    continue

        full_text = "\n".join(text_parts).strip()

        if not full_text:
            raise ValueError(f"No readable text found in: {pdf_path}")

        documents[os.path.basename(pdf_path)] = full_text

    return documents


def construct_zero_shot_prompt(doc_name, doc_text):
    return f"""
You are a helpful document analyzer and security requirements analyst.

Read the following security requirements document and identify the key data elements (KDEs).
A key data element can map to multiple requirements.

Extract at least 3 to 5 key data elements and their corresponding requirements.

Return only valid YAML in this exact format:

element1:
  name: <KDE name>
  requirements:
    - <requirement 1>
    - <requirement 2>

element2:
  name: <KDE name>
  requirements:
    - <requirement 1>

Do not include explanations.
Do not include markdown code fences.

Document name: {doc_name}

Document text:
{doc_text}
""".strip()


def construct_few_shot_prompt(doc_name, doc_text):
    return f"""
You are a helpful document analyzer and security requirements analyst.

Example:

Document text:
Users must provide a username and password. Passwords must be encrypted at rest.

Expected YAML output:
element1:
  name: username
  requirements:
    - Users must provide a username.
element2:
  name: password
  requirements:
    - Users must provide a password.
    - Passwords must be encrypted at rest.

Now read the following security requirements document and identify the key data elements (KDEs).
A key data element can map to multiple requirements.

Extract at least 3 to 5 key data elements and their corresponding requirements.

Return only valid YAML in this exact format:

element1:
  name: <KDE name>
  requirements:
    - <requirement 1>
    - <requirement 2>

element2:
  name: <KDE name>
  requirements:
    - <requirement 1>

Do not include explanations.
Do not include markdown code fences.

Document name: {doc_name}

Document text:
{doc_text}
""".strip()


def construct_chain_of_thought_prompt(doc_name, doc_text):
    return f"""
You are a helpful document analyzer and security requirements analyst.

Carefully analyze the document.
First identify important data-related nouns, entities, fields, and configuration items.
Then determine which of them are key data elements (KDEs).
Then map each KDE to all related requirements found in the document.

Extract at least 3 to 5 key data elements and their corresponding requirements.

Return only the final YAML answer in this exact format:

element1:
  name: <KDE name>
  requirements:
    - <requirement 1>
    - <requirement 2>

element2:
  name: <KDE name>
  requirements:
    - <requirement 1>

Do not include explanations.
Do not include markdown code fences.

Document name: {doc_name}

Document text:
{doc_text}
""".strip()


def run_llm_and_extract_kdes(documents, output_yaml_dir="outputs/yaml"):
    if not isinstance(documents, dict):
        raise ValueError("documents must be a dictionary")

    os.makedirs(output_yaml_dir, exist_ok=True)

    pipe = pipeline(
        "text-generation",
        model="google/gemma-3-1b-it",
        device="cpu",
        dtype=torch.bfloat16
    )

    prompt_builders = {
        "zero-shot": construct_zero_shot_prompt,
        "few-shot": construct_few_shot_prompt,
        "chain-of-thought": construct_chain_of_thought_prompt
    }

    llm_outputs = []

    for doc_name, doc_text in documents.items():
        first_yaml_saved = False

        for prompt_type, builder in prompt_builders.items():
            prompt = builder(doc_name, doc_text[:3000])

            messages = [[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are a helpful document analyzer."}]
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]]

            output = pipe(messages, max_new_tokens=500)
            llm_text = output[0][0]["generated_text"][-1]["content"]

            llm_outputs.append({
                "llm_name": "google/gemma-3-1b-it",
                "document_name": doc_name,
                "prompt_type": prompt_type,
                "prompt_used": prompt,
                "llm_output": llm_text
            })

            if not first_yaml_saved:
                yaml_filename = os.path.splitext(doc_name)[0] + "-kdes.yaml"
                yaml_path = os.path.join(output_yaml_dir, yaml_filename)

                cleaned_text = llm_text.replace("```yaml", "").replace("```", "").strip()

                with open(yaml_path, "w") as f:
                    f.write(cleaned_text)

                first_yaml_saved = True

    return llm_outputs


def save_llm_outputs_to_text(llm_outputs, output_text_path="outputs/text/llm_outputs.txt"):
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

    with open(output_text_path, "w") as f:
        for item in llm_outputs:
            f.write("*LLM Name*\n")
            f.write(f"{item['llm_name']}\n\n")

            f.write("*Prompt Used*\n")
            f.write(f"{item['prompt_used']}\n\n")

            f.write("*Prompt Type*\n")
            f.write(f"{item['prompt_type']}\n\n")

            f.write("*LLM Output*\n")
            f.write(f"{item['llm_output']}\n\n")
            f.write("=" * 60 + "\n\n")


if __name__ == "__main__":
    pdf1 = "inputs/cis-r1.pdf"
    pdf2 = "inputs/cis-r2.pdf"

    documents = load_and_validate_documents(pdf1, pdf2)
    llm_outputs = run_llm_and_extract_kdes(documents)
    save_llm_outputs_to_text(llm_outputs)

    print("Task 1 complete.")
