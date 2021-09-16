from time import sleep
import allure
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from helpers.help_utils import make_url


@allure.step
def go_to_page(user_driver: RemoteWebDriver, page_url: str, element_class: str):
    user_driver.get(make_url(page_url))
    assert user_driver.find_element_by_class_name(element_class)
    allure.attach(user_driver.get_screenshot_as_png(), f'Load page: {page_url}', allure.attachment_type.PNG)


@allure.step
def wait_subscription_status(user_driver: RemoteWebDriver, status: str):
    i = 0
    while True:
        i += 1
        sleep(2)
        status_element = user_driver.find_element_by_xpath('/html/body/main/div/p[6]')
        if i > 10:
            error_msg = f'Error: status is not {status}'
            allure.attach(user_driver.get_screenshot_as_png(), error_msg, allure.attachment_type.PNG)
            raise Exception(error_msg)
        if status_element.text == status:
            msg = f'Success: status is {status}'
            allure.attach(user_driver.get_screenshot_as_png(), msg, allure.attachment_type.PNG)
            break


@allure.epic("Подписки")
class TestCatalog:

    @allure.title('YooMoney - создание, отмена подписки')
    def test_create_yoomoney_subscription(self, user_driver: RemoteWebDriver):
        go_to_page(user_driver, '/billing/demo/profile/', 'flex-shrink-0')
        go_to_page(user_driver, '/billing/demo/tariff/05787e6d-8d92-4882-ad36-1f0121ee296e', 'flex-shrink-0')

        # press pay button (YooMoney as default)
        buy_button = user_driver.find_element_by_class_name('btn-primary')
        assert buy_button
        buy_button.click()
        sleep(3)

        # fill payment form
        card_field = user_driver.find_element_by_name('skr_card-number')
        month_field = user_driver.find_element_by_name('skr_month')
        year_field = user_driver.find_element_by_name('skr_year')
        cvc_field = user_driver.find_element_by_name('skr_cardCvc')

        card_field.send_keys('5555555555554444')
        month_field.send_keys('11')
        year_field.send_keys('22')
        cvc_field.send_keys('123')

        allure.attach(user_driver.get_screenshot_as_png(), 'Fill YooMoney card form', allure.attachment_type.PNG)

        # press confirm pay button
        pay_button = user_driver.find_element_by_class_name('button__text')
        pay_button.click()
        sleep(5)

        # check page with success payment info
        assert user_driver.find_element_by_class_name('title_last_yes')
        allure.attach(user_driver.get_screenshot_as_png(), 'Success payment page', allure.attachment_type.PNG)

        # back to subscription page
        back_link = user_driver.find_element_by_class_name('link__control')
        back_link.click()
        sleep(3)

        # wait active subscription status
        wait_subscription_status(user_driver, "Статус: Активная")

        # click cancel subscription
        cancel_btn = user_driver.find_element_by_class_name('btn-danger')
        cancel_btn.click()
        wait_subscription_status(user_driver, "Статус: Подписка отменена")

    @allure.title('Stripe - создание, отмена подписки')
    def test_stripe_subscription(self, user_driver: RemoteWebDriver):

        allure.attach(user_driver.get_screenshot_as_png(), 'Stripe video', allure.attachment_type.MP4)
        go_to_page(user_driver, '/billing/demo/profile/', 'flex-shrink-0')
        go_to_page(user_driver, '/billing/demo/tariff/fb167b09-7d56-4330-814a-0ba799e985de', 'flex-shrink-0')

        # select stripe payment system
        payment_selector = Select(user_driver.find_element_by_name("payment_system"))
        payment_selector.select_by_value('stripe')
        allure.attach(user_driver.get_screenshot_as_png(), 'Set stripe payment system', allure.attachment_type.PNG)

        # press pay button (YooMoney as default)
        buy_button = user_driver.find_element_by_class_name('btn-primary')
        assert buy_button
        buy_button.click()
        sleep(3)

        # fill payment form
        email_field = user_driver.find_element_by_id('email')
        card_field = user_driver.find_element_by_id('cardNumber')
        month_year_field = user_driver.find_element_by_id('cardExpiry')
        cvc_field = user_driver.find_element_by_id('cardCvc')
        bill_name = user_driver.find_element_by_id('billingName')

        email_field.send_keys('kongrun@yandex.ru')
        card_field.send_keys('4242424242424242')
        month_year_field.send_keys('1122')
        cvc_field.send_keys('123')
        bill_name.send_keys('stripe bill')

        allure.attach(user_driver.get_screenshot_as_png(), 'Fill Stripe card form', allure.attachment_type.PNG)

        # press confirm pay button
        html = user_driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        html.send_keys(Keys.END)
        pay_button = user_driver.find_element_by_class_name('SubmitButton')

        allure.attach(user_driver.get_screenshot_as_png(), 'Scroll to pay button', allure.attachment_type.PNG)
        pay_button.click()
        sleep(5)

        # wait active subscription status
        wait_subscription_status(user_driver, "Статус: Активная")

        # click cancel subscription
        cancel_btn = user_driver.find_element_by_class_name('btn-danger')
        cancel_btn.click()
        wait_subscription_status(user_driver, "Статус: Подписка отменена")
