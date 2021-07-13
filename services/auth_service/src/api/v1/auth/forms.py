from flask_wtf import RecaptchaField, FlaskForm


class RecaptchaForm(FlaskForm):
    recaptcha = RecaptchaField()
