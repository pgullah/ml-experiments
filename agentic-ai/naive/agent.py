
from app.models import (
    AgentAction,
    AgentStep,
    ResearchResponse,
    SearchResult,
    Source,
)

import app.mock_tools as tools

# Architecture
#  research query
#       │
#       ▼
# ResearchAgent
#       │
#       ▼
# ┌─────────────────┐
# │ Agent Loop      │
# │                 │
# │ SEARCH → READ   │
# │    ↑        ↓   │
# │    └────────────│
# │          ↓      │
# │        FINISH   │
# └─────────────────┘
#       │
#       ▼
# Research Report

class ResearchAgent:
    
    def __init__(self, max_steps = 10):
        self.max_steps = max_steps
    
    def research(self, question: str) -> ResearchResponse:
        steps: list[AgentStep] = []
        sources: list[Source] = []
        
        action = AgentAction(
            action="search",
            query=question,
            reason="Start by searching for relevant information.",
        )
        
        max_allowed_actions = range(0, self.max_steps + 1)
        for step_number in max_allowed_actions:
            print(f"\n--- STEP {step_number} ---")
            print(f"ACTION: {action.action}")
            print(f"REASON: {action.reason}")
            
            steps.append(
                AgentStep(
                    step=step_number,
                    action=action.action,
                    reason=action.reason
                )
            )
            
            if action.action == 'search':
                results = tools.search_web(action.query or question)
                action = self._decide_after_search(results)
            elif action.action == 'read':
                source = tools.read_page(action.url or "")
                sources.append(source)
                action = self._decide_after_read(sources)
            elif action.action == 'finish':
                break
                
        answer = self._generate_answer(question, sources)

        return ResearchResponse(
            question=question,
            answer=answer,
            sources=sources,
            steps=steps,
        )
    
    def _generate_answer(self, question, sources: list[Source]):
        if not sources:
            return "I could not find enough information."

        source_text = "\n".join(
            f"- {source.title}: {source.content}"
            for source in sources
        )

        return (
            f"Research question: {question}\n\n"
            f"Based on the collected sources:\n"
            f"{source_text}"
        )
    
    def _decide_after_research() -> AgentAction:
        pass
    
    def _decide_after_search(self, results: list[SearchResult]) -> AgentAction:
        if not results:
            return AgentAction(
                action="finish",
                reason="No search results were found.",
            )

        return AgentAction(
            action="read",
            url=results[0].url,
            reason="Read the most relevant search result.",
        )
    
    
    def _decide_after_read(self, sources: list[Source]) -> AgentAction:
        if len(sources) >= 2:
            return AgentAction(
                action="finish",
                reason="Enough sources have been collected.",
            )

        return AgentAction(
            action="read",
            url="https://docs.docker.com/",
            reason="Read another source for additional information.",
        )

    
    