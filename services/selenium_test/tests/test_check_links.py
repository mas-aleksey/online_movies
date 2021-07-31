import pytest
import allure
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from helpers.help_utils import make_url

pages_url = [
    pytest.param('#', 'movies', id='Main'),
    pytest.param('/movies/admin/login/', 'site-name', id='Movies Admin'),
    pytest.param('/async/openapi', 'swagger-ui', id='Swagger Async API'),
    pytest.param('/auth2/apidocs/', 'swagger-ui', id='Swagger Auth API'),
    pytest.param('/notify/admin/login', 'site-name', id='Notify Admin'),
    pytest.param('notify/api/openapi', 'swagger-ui', id='Notify API'),
    pytest.param('/billing/admin/login', 'site-name', id='Billing Admin'),
    pytest.param('/billing/demo/login/', 'id_login', id='DEMO'),
]


@allure.epic("Загрузка страниц")
class TestCatalog:

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("page, element_id", pages_url)
    def test_load_page(self, web_driver: RemoteWebDriver, page, element_id):
        web_driver.get(make_url(page))
        assert web_driver.find_element_by_id(element_id)
        allure.attach(web_driver.get_screenshot_as_png(), page, allure.attachment_type.PNG)
