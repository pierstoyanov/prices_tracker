import requests


def get_url_request_with_headers(url: str, headers: dict):
    return requests.get(url, headers=headers)


