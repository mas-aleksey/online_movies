from urllib.parse import urljoin
import allure
from helpers.settings import BASE_URL


def make_url(page: str = '#') -> str:
    return urljoin(BASE_URL, page)

