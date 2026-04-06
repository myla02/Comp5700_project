from src.extractor import (
    load_and_validate_documents,
    construct_zero_shot_prompt,
    construct_few_shot_prompt,
    construct_chain_of_thought_prompt,
    run_llm_and_extract_kdes,
    save_llm_outputs_to_text
)

# Test 1: load documents
def test_load_documents():
    docs = load_and_validate_documents("inputs/cis-r1.pdf", "inputs/cis-r2.pdf")
    assert isinstance(docs, dict)
    assert len(docs) == 2

# Test 2: zero-shot prompt
def test_zero_shot_prompt():
    prompt = construct_zero_shot_prompt("test.pdf", "sample text")
    assert isinstance(prompt, str)
    assert "key data elements" in prompt

# Test 3: few-shot prompt
def test_few_shot_prompt():
    prompt = construct_few_shot_prompt("test.pdf", "sample text")
    assert isinstance(prompt, str)
    assert "Example" in prompt

# Test 4: chain-of-thought prompt
def test_chain_of_thought_prompt():
    prompt = construct_chain_of_thought_prompt("test.pdf", "sample text")
    assert isinstance(prompt, str)
    assert "analyze" in prompt.lower()

# Test 5: LLM output function (structure check only)
def test_llm_function_structure():
    assert callable(run_llm_and_extract_kdes)

# Test 6: save outputs
def test_save_llm_outputs():
    sample_output = [{
        "llm_name": "test",
        "document_name": "test.pdf",
        "prompt_type": "zero-shot",
        "prompt_used": "prompt",
        "llm_output": "output"
    }]
    save_llm_outputs_to_text(sample_output, "outputs/text/test.txt")
