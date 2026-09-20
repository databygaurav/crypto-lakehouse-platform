import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _build_session():
    retry_policy = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False
    )

    adapter = HTTPAdapter(max_retries=retry_policy)
    session = requests.Session()
    session.mount("https://", adapter)

    return session


class HTTPClient:

    _session = _build_session()

    @classmethod
    def get(
        cls,
        url,
        params=None,
        headers=None,
        timeout=(5, 30)
    ):
        """Perform a resilient GET request and return JSON."""

        response = cls._session.get(
            url=url,
            params=params,
            headers=headers,
            timeout=timeout
        )

        if not response.ok:
            raise requests.HTTPError(
                f"HTTP {response.status_code} from remote API",
                response=response
            )

        try:
            return response.json()
        except ValueError as error:
            raise RuntimeError(
                "Remote API returned invalid JSON"
            ) from error

    @classmethod
    def post(
        cls,
        url,
        data=None,
        headers=None,
        timeout=(5, 30)
    ):
        """Perform a POST request and return JSON."""

        response = cls._session.post(
            url=url,
            data=data,
            headers=headers,
            timeout=timeout
        )

        if not response.ok:
            raise requests.HTTPError(
                f"HTTP {response.status_code} from remote API",
                response=response
            )

        try:
            return response.json()
        except ValueError as error:
            raise RuntimeError(
                "Remote API returned invalid JSON"
            ) from error
