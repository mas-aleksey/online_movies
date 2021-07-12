import requests
from marshmallow import ValidationError

from app import app


class ReCaptchaError(ValidationError):
    default_code = 'recaptcha_check'


def get_ip_from_request(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def recaptcha_check(request, token, threshold=0.5) -> dict:
    secret_key = app.config.get('RECAPTCHA_SECRET_KEY')
    if not secret_key:
        return {'score': 1.0}

    user_ip = get_ip_from_request(request)
    response = requests.post(
        'https://www.google.com/recaptcha/api/siteverify',
        {'secret': secret_key, 'response': token, 'remoteip': user_ip},
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        raise ReCaptchaError('Ошибка запроса к ReCaptcha.') from e

    data = response.json()

    # ReCaptcha вернула ошибку. Коды ошибок указаны тут
    # https://developers.google.com/recaptcha/docs/verify#error-code-reference
    if not data.get('success', False):
        raise ReCaptchaError('Ошибка запроса к ReCaptcha.')

    if data['score'] < threshold:
        raise ReCaptchaError('Оценка ниже порога.')

    return data
