from urllib.parse import urljoin
from helpers.settings import BASE_URL


def make_url(page: str = '#') -> str:
    return urljoin(BASE_URL, page)
