from functools import lru_cache
from pathlib import Path
import yaml

from app.common.config import AppSettings


def load_prompts(settings: AppSettings | None = None):
    prompts = []

    for file in _prompt_dir(settings.prompt_dir if settings else None).glob("*.md"):
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

def load_raw_prompt(
    prompt_file: str = "system-prompt.md",
    settings: AppSettings | None = None,
):
    prompt_dir = settings.prompt_dir if settings else None
    return _prompt_dir(prompt_dir).joinpath(prompt_file).read_text(encoding="utf-8").strip()


@lru_cache()
def _prompt_dir(configured_dir: Path | None = None) -> Path:
    return configured_dir or Path(__file__).resolve().parent.parent.parent / "prompts"
