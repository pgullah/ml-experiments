from functools import lru_cache
from pathlib import Path
import yaml
import os


def load_prompts():
    prompts = []

    for file in _prompt_dir().glob("*.md"):
        text = file.read_text()

        data = {"id": file.stem}
        prompt = text
        if text.startswith("---"):
            _, metadata, prompt = text.split("---", 2)
            data.update(yaml.safe_load(metadata) or {})

        data["prompt"] = prompt.strip()
        data["file"] = str(file)

        prompts.append(data)

    return prompts

def load_raw_prompt(prompt_file: str = "system-prompt.md"):
    return _prompt_dir().joinpath(prompt_file).read_text(encoding="utf-8").strip()


@lru_cache()
def _prompt_dir() -> Path:
    configured_dir = os.environ.get("PROMPT_DIR")
    return Path(configured_dir) if configured_dir else Path(__file__).resolve().parent.parent.parent / "prompts"
