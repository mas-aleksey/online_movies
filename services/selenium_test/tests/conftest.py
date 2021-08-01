from uuid import uuid4
from selenium import webdriver
import pytest
import allure
import requests
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from helpers.help_utils import make_url
from helpers.settings import IMPLICITLY_WAIT


@pytest.fixture(scope='session')
def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-first-run")
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")

    with webdriver.Chrome(options=options) as driver:
        driver.implicitly_wait(IMPLICITLY_WAIT)
        yield driver


@pytest.fixture
def user_driver(web_driver: RemoteWebDriver):

    user_pass = str(hash(uuid4()))
    user_email = f'allure_{user_pass}@allure.ru'

    signup_url = make_url('auth2/api/v1/auth/signup')
    headers = {'content-type': 'application/json', 'user-agent': 'allure_test'}
    payload = {
        "email": user_email,
        "password": user_pass
    }
    resp = requests.post(
        url=signup_url,
        json=payload,
        headers=headers,
    )
    if resp.status_code != 200:
        raise Exception(f"Sign up error {resp.status_code} {resp.content}")

    login_url = make_url('billing/demo/login/')

    web_driver.get(login_url)
    allure.attach(web_driver.get_screenshot_as_png(), login_url, allure.attachment_type.PNG)

    input_login = web_driver.find_element_by_id('id_login')
    input_pass = web_driver.find_element_by_id('id_password')
    input_login.send_keys(user_email)
    input_pass.send_keys(user_pass)
    allure.attach(web_driver.get_screenshot_as_png(), login_url, allure.attachment_type.PNG)
    login_btn = web_driver.find_element_by_tag_name('button')
    login_btn.click()
    yield web_driver


def pytest_sessionfinish(session, exitstatus):
    import helpers.send_test_result as sender