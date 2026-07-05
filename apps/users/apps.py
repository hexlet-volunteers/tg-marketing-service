from allauth.socialaccount.signals import social_account_added
from django.apps import AppConfig
from django.dispatch import receiver


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        @receiver(social_account_added)
        def handle_yandex_login(sender, request, sociallogin, **kwargs):
            if sociallogin.account.provider == 'yandex':
                user = sociallogin.user
                extra_data = sociallogin.account.extra_data
                
                # Обновляем данные пользователя
                user.email = extra_data.get('default_email', '')
                user.first_name = extra_data.get('first_name', '')
                user.last_name = extra_data.get('last_name', '')