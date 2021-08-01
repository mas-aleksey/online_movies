import pytest
from time import sleep
import allure
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from helpers.help_utils import make_url


@allure.epic("Подписки")
class TestCatalog:
    def test_create_subscription(self, user_driver: RemoteWebDriver):
        user_driver.get(make_url('/billing/demo/profile/'))
        assert user_driver.find_element_by_class_name('flex-shrink-0')
        allure.attach(user_driver.get_screenshot_as_png(), 'profile', allure.attachment_type.PNG)

        user_driver.get(make_url('/billing/demo/tariff/05787e6d-8d92-4882-ad36-1f0121ee296e'))
        assert user_driver.find_element_by_class_name('flex-shrink-0')
        allure.attach(user_driver.get_screenshot_as_png(), 'tariff', allure.attachment_type.PNG)
        buy_button = user_driver.find_element_by_class_name('btn-primary')
        assert buy_button
        buy_button.click()
        sleep(3)

        card_field = user_driver.find_element_by_name('skr_card-number')
        month_field = user_driver.find_element_by_name('skr_month')
        year_field = user_driver.find_element_by_name('skr_year')
        cvc_field = user_driver.find_element_by_name('skr_cardCvc')

        card_field.send_keys('5555555555554444')
        month_field.send_keys('11')
        year_field.send_keys('22')
        cvc_field.send_keys('123')

        allure.attach(user_driver.get_screenshot_as_png(), 'yoomoney', allure.attachment_type.PNG)
        pay_button = user_driver.find_element_by_class_name('button__text')
        pay_button.click()
        sleep(5)

        assert user_driver.find_element_by_class_name('title_last_yes')
        back_link = user_driver.find_element_by_class_name('link__control')
        allure.attach(user_driver.get_screenshot_as_png(), 'payment', allure.attachment_type.PNG)
        back_link.click()
        sleep(3)

        i = 0
        while i < 10:
            i += 1
            sleep(2)
            status = user_driver.find_element_by_xpath('/html/body/main/div/p[6]')
            allure.attach(user_driver.get_screenshot_as_png(), f'{i}_{status.text}', allure.attachment_type.PNG)
            if status.text == "Статус: Активная":
                break
