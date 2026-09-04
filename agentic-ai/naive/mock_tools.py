from app.models import SearchResult, Source

def search_web(query: str) -> list[SearchResult]:
    print(f"SEARCH TOOL CALLED: {query}")

    return [
        SearchResult(
            title="FastAPI Deployment",
            url="https://fastapi.tiangolo.com/deployment/",
            snippet="Official FastAPI deployment documentation."
        ),
        SearchResult(
            title="Docker Documentation",
            url="https://docs.docker.com/",
            snippet="Official Docker documentation."
        ),
    ]
    
def read_page(url: str) -> Source:
    print(f"READ TOOL CALLED: {url}")

    mock_pages = {
        "https://fastapi.tiangolo.com/deployment/": Source(
            title="FastAPI Deployment",
            url="https://fastapi.tiangolo.com/deployment/",
            content=(
                "FastAPI applications can be deployed using "
                "containers and ASGI servers."
            ),
        ),
        "https://docs.docker.com/": Source(
            title="Docker Documentation",
            url="https://docs.docker.com/",
            content=(
                "Docker packages applications and their dependencies "
                "into containers."
            ),
        ),
    }

    return mock_pages.get(
        url,
        Source(
            title="Unknown Source",
            url=url,
            content="No content found."
        )
    )