from enum import Enum
from typing import Literal
from functools import wraps
from typing import Callable
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from app.prompt.prompt_loader import load_raw_prompt


class DomainDecision(str, Enum):
    """
    Enum representing the possible decisions for a domain.
    """
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    UNSAFE = "unsafe"
    AMIBIGUOUS = "ambiguous"
    

class DomainClassification(BaseModel):
    """
    Model representing the classification of a domain.
    """
    decision: Literal[
        "in_scope",
        "out_of_scope",
        "unsafe",
        "ambiguous",
    ]
    confidence: float = Field(ge=0, le=1)
    reason: str


TRAVEL_REFUSAL = (
    "I can only help with travel planning and related travel questions."
)

def travel_domain_guard(confidence_threshold: float = 0.8,) -> Callable:
    domain_classifier_prompt = SystemMessage(content=load_raw_prompt(prompt_file="domain-classifier-prompt.md"))
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, query: str, *args, **kwargs):
            if not hasattr(self, "llm"):
                raise AttributeError(
                    "The class must have 'llm' attribute."
                )
            classifier = self.llm.with_structured_output(DomainClassification)
            classification = classifier.invoke([
                domain_classifier_prompt,
                HumanMessage(content=query),
            ])

            if classification.decision != "in_scope" or classification.confidence < confidence_threshold:
                return TRAVEL_REFUSAL

            return method(self, query, *args, **kwargs)

        return wrapper

    return decorator