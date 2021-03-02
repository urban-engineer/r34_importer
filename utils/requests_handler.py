import requests


def get_url(request_url: str, params: dict = None) -> requests.Response:
    if params is None:
        params = {}

    request = requests.get(request_url, params=params)
    if request.status_code != 200:
        raise RuntimeError("GET for [{}] returned code [{}]".format(request_url, request.status_code))
    return request


def send_post(request_url: str, params: dict = None) -> requests.Response:
    if params is None:
        params = {}

    request = requests.post(request_url, params=params)
    if request.status_code != 200:
        raise RuntimeError("POST for [{}] returned code [{}]".format(request_url, request.status_code))
    return request


def send_post_with_file(request_url: str, params: dict, file: bytes, errors_okay=False) -> requests.Response:
    if params is None:
        params = {}
    files = {
        "file": file
    }

    request = requests.post(request_url, params=params, files=files)
    if request.status_code != 200 and not errors_okay:
        raise RuntimeError("POST for [{}] with file returned code [{}]".format(request_url, request.status_code))
    return request
