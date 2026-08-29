from functools import lru_cache
from pathlib import Path
import yaml
import os


def load_prompts():
    prompts = []

    for file in _prompt_dir().glob("*.md"):
        text = file.read_text()

        # Split YAML front matter from prompt body
        _, metadata, prompt = text.split("---", 2)

        data = yaml.safe_load(metadata)

        data["prompt"] = prompt.strip()
        data["file"] = str(file)

        prompts.append(data)

    return prompts

def load_raw_prompt(prompt_file: str = "system-prompt.md"):
    return _prompt_dir().joinpath(prompt_file).read_text(encoding="utf-8")


@lru_cache()
def _prompt_dir() -> Path:
    return os.environ.get("PROMPT_DIR", Path(__file__).resolve().parent.parent.parent.joinpath("prompts"))
     