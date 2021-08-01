import random
import time

from locust import HttpUser, task, between
from locust.clients import HttpSession

import settings
from load_tests import services, auth_roles, notify


def generate_login():
    suffix = random.randint(1, 9999999)
    return settings.BASE_LOGIN.format(suffix=str(suffix))


class QuickstartUser(HttpUser):
    wait_time = between(1, 3)
    client_auth_admin: HttpSession = None
    login = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        session = HttpSession(
            base_url=self.host,
            request_event=self.environment.events.request,
            user=self,
        )
        session.trust_env = False
        self.client_auth_admin = session

    @task(10)
    def search_movies(self):
        """Поиск фильмов."""
        query = random.choice(settings.QUERIES)
        movies = services.async_movies_search(self.client, query)
        if len(movies) == 0:
            return
        movie = random.choice(movies)
        time.sleep(3)
        services.async_movies_detail(self.client, movie['id'])

    @task(2)
    def profile(self):
        """Просмотр профиля."""
        services.auth_profile(self.client)

    @task(1)
    def order(self):
        """Покупка подписки."""

        # смотрим список тарифов
        prods = services.billing_products(self.client)
        results = prods['results']
        product = random.choice(results)
        tariffs = product['tariffs']
        tariff = random.choice(tariffs)
        time.sleep(3)

        # выбираем и просматриваем тариф
        services.billing_tariff(self.client, tariff['id'])
        time.sleep(1)

        # покупаем
        services.billing_order(self.client, tariff['id'], 'stripe')

    @task(1)
    def subscriptions(self):
        """Просмотр подписок."""

        # смотрим подписки пользователя
        prods = services.billing_subscriptions(self.client)
        results = prods['results']
        if not results:
            return
        subscription = random.choice(results)
        time.sleep(3)

        # смотрим детальнее
        services.billing_subscription(self.client, subscription['id'])

    @task(1)
    def add_role(self):
        """Добавить роль пользователю."""
        profile = services.auth_profile(self.client)
        role = random.choice(['extra', 'standard'])
        auth_roles.add_auth_user_role(self.client_auth_admin, profile['user_id'], [role])
        self.client = services.auth_refresh(self.client)

    @task(1)
    def delete_role(self):
        """Удалить роль пользователю."""
        profile = services.auth_profile(self.client)
        roles = set(profile['user_roles']) - {'free'}
        if not roles:
            return
        role = random.choice(profile['user_roles'])
        auth_roles.delete_auth_user_role(self.client_auth_admin, profile['user_id'], [role])
        self.client = services.auth_refresh(self.client)

    @task(2)
    def send_notify(self):
        """Отправить уведомление пользователю."""
        profile = services.auth_profile(self.client)
        notify.send_payment_notify(self.client, profile['user_id'], 1000.0, 'Списание')

    def user_login(self):
        self.client = services.auth_login(
            self.client,
            self.login,
            settings.BASE_PASSWORD
        )

    def user_logout(self):
        services.auth_logout(self.client)

    def on_start(self):
        self.login = generate_login()
        print(self.login)
        self.client = services.auth_signup(
            self.client,
            self.login,
            settings.BASE_PASSWORD
        )
        self.user_login()
