import requests


class HTTPClient:

    @staticmethod
    def get(
        url,
        params=None,
        headers=None
    ):

        response = requests.get(
            url=url,
            params=params,
            headers=headers
        )

        if not response.ok:

            print("\nHTTP ERROR")
            print(
                "Status:",
                response.status_code
            )

            print(
                "Response:",
                response.text
            )

            print(
                "URL:",
                response.url
            )

        response.raise_for_status()

        return response.json()