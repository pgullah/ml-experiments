class ServiceError(Exception):
    """A safe, expected failure while calling an application service."""


class ClientError(Exception):
    """Invalid input supplied by an application client."""


class SearchProviderError(ServiceError):
    """A search provider failed or returned an invalid response."""
