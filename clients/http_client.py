import requests

class HTTPClient:
    """Reusable HTTP client for making API requests."""

    @staticmethod
    def get(url: str, params: dict | None = None):
        response = requests.get(
            url=url,
            params=params,
            timeout=10
        )

        response.raise_for_status()
        return response.json()