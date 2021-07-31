import os

ALLURE_URL = os.getenv('ALLURE_URL', 'http://allure:5050')
BASE_URL = 'https://yandexmovies.online'
SEND_ALLURE_REPORT = 1

IMPLICITLY_WAIT = 20
EXPLICITY_WAIT = 20
PROJECT_ID = os.getenv('PROJECT_ID', 'default')
