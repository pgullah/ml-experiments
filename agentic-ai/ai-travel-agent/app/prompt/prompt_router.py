import json

from openai import OpenAI
from pydantic import BaseModel, Field

from app.common.config import AppSettings
from app.common.errors import ServiceError
from app.prompt.prompt_loader import load_prompts


class PromptRoute(BaseModel):
    primary_prompt: str
    secondary_prompts: list[str] = Field(default_factory=list)
    reason: str


def route(user_request: str, settings: AppSettings) -> PromptRoute:
    if not user_request.strip():
        raise ValueError("user_request must not be empty")
    if settings.openai_api_key is None:
        raise ValueError("OPENAI_API_KEY is required to use the prompt router")

    prompts = load_prompts(settings)
    registry = [
        {key: value for key, value in prompt.items() if key not in {"prompt", "file"}}
        for prompt in prompts
    ]
    prompt_ids = {prompt["id"] for prompt in prompts}

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

    try:
        response = OpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            timeout=settings.request_timeout_seconds,
        ).chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": user_request},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Prompt router returned no content")
        selection = PromptRoute.model_validate_json(content)
    except Exception as error:
        raise ServiceError("Prompt routing is currently unavailable") from error

    selected_ids = {selection.primary_prompt, *selection.secondary_prompts}
    unknown_ids = selected_ids - prompt_ids
    if unknown_ids:
        raise ServiceError("Prompt router selected an unknown prompt")
    return selection
