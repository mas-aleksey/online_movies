import abc
import dataclasses
from typing import List


class OAuthError(Exception):
    pass


@dataclasses.dataclass
class OauthUserDataclass:
    social_name: str
    social_id: str
    email: str


class BaseOAuthProvider:
    name: str

    @abc.abstractmethod
    def get_login_url(self) -> str:
        pass

    @abc.abstractmethod
    def callback(self, request) -> OauthUserDataclass:
        pass


class BaseOAuthService:
    providers_class: List[BaseOAuthProvider]

    def __init__(self, backend: str) -> None:
        self.provider = self.get_backend(backend)

    def get_backend(self, backend: str) -> BaseOAuthProvider:
        for provider in self.providers_class:
            if provider.name == backend:
                return provider()
        raise OAuthError(f'Backend {backend} nod found.')

    def get_login_url(self) -> str:
        return self.provider.get_login_url()

    def callback(self, request) -> OauthUserDataclass:
        return self.provider.callback(request)
