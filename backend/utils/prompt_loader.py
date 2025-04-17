import os
import re

def load_prompt_template(prompt_type: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "..", "static", "prompts.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"\[{prompt_type.lower()}\](.*?)(?=\n\[|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if not match:
        raise ValueError(f"Prompt '{prompt_type}' not found in prompts.txt")

    return match.group(1).strip()
