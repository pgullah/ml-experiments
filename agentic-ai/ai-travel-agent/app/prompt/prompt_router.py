import json
from pathlib import Path

from openai import OpenAI

from pathlib import Path
import yaml

PROMPT_DIR = Path("prompts")


def load_prompts():
    prompts = []

    for file in PROMPT_DIR.glob("*.md"):
        text = file.read_text()

        # Split YAML front matter from prompt body
        _, metadata, prompt = text.split("---", 2)

        data = yaml.safe_load(metadata)

        data["prompt"] = prompt.strip()
        data["file"] = str(file)

        prompts.append(data)

    return prompts


client = OpenAI()

BASE_DIR = Path(__file__).parent
PROMPT_DIR = BASE_DIR / "prompts"


def load_registry():
    with open(BASE_DIR / "prompt_registry.json") as f:
        return json.load(f)


def load_prompt(prompt_id):
    path = PROMPT_DIR / f"{prompt_id}.txt"

    with open(path) as f:
        return f.read()


def route(user_request):

    registry = load_registry()

    router_prompt = """
You are a travel-planning prompt router.

Analyse the user's request and select the prompts that
should be used to answer it.

Choose:
- exactly one primary prompt
- zero or more secondary prompts

Only select prompts from the supplied registry.

Do not answer the travel question.

Return JSON only:

{
    "primary_prompt": "prompt_id",
    "secondary_prompts": ["prompt_id"],
    "reason": "brief explanation"
}

Available prompts:

""" + json.dumps(registry, indent=2)

    response = client.chat.completions.create(
        model="gpt-5.6",
        messages=[
            {
                "role": "system",
                "content": router_prompt
            },
            {
                "role": "user",
                "content": user_request
            }
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)