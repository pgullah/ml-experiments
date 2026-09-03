import json
import os

from openai import OpenAI

from app.prompt.prompt_loader import load_prompts


def route(user_request):

    registry = [
        {key: value for key, value in prompt.items() if key not in {"prompt", "file"}}
        for prompt in load_prompts()
    ]

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

    response = OpenAI().chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-5.6"),
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
