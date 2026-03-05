from django.contrib import auth, messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.middleware.csrf import get_token
from django.utils import timezone
from inertia import render as inertia_render
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import View

from apps.group_channels.forms import CreateGroupForm, UpdateGroupForm

from config.mixins import UserAuthenticationCheckMixin

from apps.users.forms import (
    AvatarChange,
    RestorePasswordForm,
    RestorePasswordRequestForm,
    UserLoginForm,
    UserRegForm,
    UserUpdateForm,
)
from apps.users.models import User


class LogoutView(UserAuthenticationCheckMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('main_index'))

    def post(self, request, *args, **kwargs):
        messages.add_message(request, messages.INFO, 'Вы разлогинены')
        auth.logout(request)
        return redirect(reverse('main_index'))


class LoginView(View):
    def get(self, request, *args, **kwargs):
        # возвращаем форму
        return inertia_render(
            request,
            "Auth",
            props={'form': {
                "data": {
                        "email": "",
                        "password": ""
                }, 
                "errors": {}
                }
            }
        )

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request, request.POST)
        
        # валидируем данные
        if form.is_valid():
            # сохраняем полученные данные в объект
            user = form.get_user()
            
            # записываем пользователя в сессию
            login(request, user)
            
            # возвращаем компонент и props
            return inertia_render(request, 'Home', props={
                "flash": {
                    "success": "Вы залогинены"
                },
                "user": {
                    "username": request.POST.get('username')
                }
            })
        
        else:
            # Ошибки валидации
            return inertia_render(request, "Auth", props={
                "form": {
                    "data": {
                        "email": request.POST.get("email", ""),
                        "password": ""
                        },
                    "errors": form.errors
                }
            })


class UserProfileView(UserAuthenticationCheckMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        groups = user.owned_groups.all()
        
        user_data = {
            "id": request.user.id,
            "username": request.user.username,
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
            "avatar": request.user.avatar_image,
            "role": request.user.role,
            "bio": request.user.bio,
            "is_active": request.user.is_active
        }
        
        groups_data = [group.get_data() for group in groups]
        
        create_form_data = {
            "name": "",
            "description": "",
            "image_url": ""
        }
        
        update_form_data = {
            "name": "",
            "description": "",
            "image_url": ""
        }
        
        return inertia_render(
            request,
            "UserProfilePage",
            props={
                    "user": user_data,
                    "groups": groups_data,
                    "form": {
                        "create_form": create_form_data,
                        "update_form": update_form_data,
                        "avatar_form": {"avatar": ""}
                    },
                    "errors": {}
            }
        )


class UserCabinetView(UserAuthenticationCheckMixin, View):
    def _build_base_props(self, request, user: User) -> dict:
        registration_date = user.date_joined
        last_visit = user.last_login if user.last_login else timezone.now()
        total_hours = (last_visit - registration_date).total_seconds() / 3600
        usage_stats = {
            'registration_date': user.date_joined.strftime('%d.%m.%Y'),
            'last_visit': user.last_login.strftime('%d.%m.%Y') if user.last_login else 'Никогда',
            'total_time': f'{total_hours:.0f} часов',
        }

        return {
            'user': {
                'first_name': user.first_name,
                'email': user.email,
            },
            'csrfToken': get_token(request),
            'subscription': {
                'plan': 'Pro',
                'price': '$29',
                'period': 'в месяц',
                'channels_used': 47,
                'channels_limit': 100,
                'ai_requests_used': 234,
                'ai_requests_limit': 1000,
            },
            'notifications': {
                'weekly_reports': True,
                'trend_notifications': True,
                'limit_exceeded': False,
                'new_features': True,
            },
            'usage_stats': usage_stats,
            'user_role': request.role,  # Используем атрибут из middleware
        }
        
    def get(self, request, *args, **kwargs):
        user = request.user
        props = self._build_base_props(request, user)
        return inertia_render(request, 'UserProfilePage', props=props)

    def post(self, request, *args, **kwargs):
        user = request.user
        action = request.POST.get('action')

        if action == 'notifications':
            # Уведомления сейчас заглушки
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Настройки уведомлений сохранены')
        else:
            form = UserUpdateForm(data=request.POST, instance=user)
            if form.is_valid():
                try:
                    form.save()
                    messages.add_message(request,
                                         messages.SUCCESS,
                                         'Профиль успешно изменен')
                except Exception as e:
                    messages.add_message(request,
                                         messages.ERROR,
                                         f'Ошибка при сохранении: {str(e)}')
                    return redirect(reverse('users:user_cabinet'))
            else:
                props = self._build_base_props(request, user)
                props['errors'] = form.errors.get_json_data()
                props['values'] = {
                    'first_name': request.POST.get('first_name', ''),
                    'email': request.POST.get('email', ''),
                }
                return inertia_render(request, 'UserProfilePage', props=props)

        return redirect(reverse('users:user_cabinet'))


class UserRegister(View):
    
    """
    Страница регистрации и аутентификации пользователя
    При первом посещении рендерится страница регистрации GET запрос.
    Props возвращает пустые поля формы email и password:
        {
            "email": "",
            "password": ""
        }
    После заполнения формы на сервер направляется POST запрос с данными формы,
    метод post перенаправляет на главную страницу с сообщением об
    успешной регистрации, либо возвращает форму регистрации с props
    email, password-пустое поле, сообщение об ошибке если есть.
    {
        "form": {
            "email": request.POST.get("email", ""),
            "password": ""
        },
        "errors": form.errors
    }
    """
    
    def get(self, request):
        return inertia_render(
            request,
            "FormRegistration",
            props={
                "form": {
                    "email": "",
                    "password": "",
                },
                "errors": {}
            }
        )
        
    def post(self, request, *args, **kwargs):
        form = UserRegForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Устанавливаем роль пользователя
            user.role = 'user'
            
            if not user.avatar_image:
                user.avatar_image = 'data:image/png;base64,iVBORw0KGg\
                    oAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAMFBMVEX\
                    Q3uP////1+PnX4+ft8vT7/P3U4eXM2+Hk7O/d5+vu8/XW4ub\
                        c5ur4+vvl7e/p7/KylbazAAAIGUlEQVR4nO2d2bqrIAyF2U\
                        6IQ33/tz11arVFBbISldN1tS92W/4PSBiSoP5ilzq7Ae\
                            z6Ed5fUoR50pVNWqinirQxjyoR+mERwjwzhdJqJa1VXVa5wK+\
                            zE7aPWn/QLTDTjh2SlzDvii26F2WasTaBlTBpjvBGRl\
                                W2jK3gI6xqJ74RsuEzPFyEiQffyMjVjzyEufHjGxhLl\
                                    qbwEHbeeKNYbA4DYes5QBfdmDL4DjxhFso3M\
                                        Hbw9sAJA2bgCrFBNwhMmBckvl4FeKRi\
                                            CVsyXy+sb4QSJrQROktDbSqSEAQ\
                                                ItjdAQhggthdxhJg5OCNWsH\
                                                    bBCHMk4BMRZm5ghFjAp\
                                                        1BOA0XYwAkLUMtA\
                                                            hA+clXnJY\
                                                                JqGIQS\
a0bdAUxFDyMDXC9M2xJeUTISQcYogZBmjvSBeEUFYMwEqyDgFfAdpy3sgwNkNgJCPTyH8P\
    p2Qy8yMohsbOiHjGH1Kk49RyYS8XQjoRDIhMyC9E6mEHe8gVXRzSiWkn60dSZ9LyLa\
        cWRASTzSIhIYdUKn0VEIBQKVpXp9GWPEP0qdoZ4s0QolBSh2mNEIRQKI1JREKW\
            NKBkHScQSJ8iAASnT6JMBUiJN0pkgiFAGlbfcqHW5lpSPSIFEIZb6iIpoZ\
                CGBpU4i/K0pRCKOPvez1OIpQypbSNPoWQf284i+IuKIRigKqOnpByl\
                    3gPQlIrwz8Kvrn/Ef4If4RBn/0R/ggvTyi3ajtrTSO38j5rXSq\
                        3ezprb8F9OfoW5bCNQpiJEZ61xxc6ED7xnCaP/qwt/vNSM\
                            XdBunwiEUoZ0/PuLYSOhGk3+SRCIVNDC6m5ww0psY2\
                                kT8us22gJezRCztDSt2gBNTRCkYlIjGwjxtNIe\
                                    ERiagmRUOImnxi6RyQUuAamJpZcPzaR2kJ\
                                        yfCk74NnxpezDlJz9RI6C5ram5CQ9M\
iG30ycnPdOzEXgBicGlEML4M0pYV26ALEtA3hPnBoMY4w0iZHQYiARERIYfPo97FuVGZtY\
    vh9RJXJ2I6EIMIdNMxKSrYzLCecwpwJD+oQhZwjLoyZWDQFUjOJL0QBXqUJU/GHbCo\
        JahvgfuMWA1eGD1adALcIyZ+UNWUQKPU1jVNhwhdJxesU4UtgoPqPpOL2S9Nty\
            RDaqCUi9ozT0YIbJ04iWrCuIm4R+6MiTk4E1TMmS+Ba7uWdIRNdDK9EJXa\
                KUjwlz9pKvVoIUDMtQRpm34Idv6lRhqQVMQ8YAs9bzDByoDIE/F8kB\
                    zg68D3Yun6nzQlh/tJiYxvRyQBAAyvXPB9TZC7l16/l5vI/Tym\
                        oxMI7QXhrAylt1A4rHrt6y1W4NZgCPunsr+ISDbhsexG60\
                            d2A7PswBOven3+POEszWmTY8ZdWr75GSqdEF+TIhGm\
                                Jj3O072XV118FiQLqwfW9hi6mNCBMJxdC6aYp8\
                                    31U4/6nTjM+sv1oYwWoMJLQ3fKoffloXlU\
                                        Su9/QrS90b6OVpDGxpG+Nl9czs2rxr\
                                            yqjR10WP1UkVtymrTAdoNlDZhH\
                                                jOEcHvcQR6K2fn2EP/hT9h\
Zu+8lqn3fXe/pgBApT8L28C6U+GzT0Zpdq4fnMPEidHpITRfhK8zcwX8q5TchPQidH1IL7\
    kbXTZfXM23OhMfv/C0VYhISj1/wYHQkPDAv3y2ofS2OywJv9QvWxV4ooS+fVwtGPre\
        nEkN+wYEwC+DzY3R8CjLsFw4Jq0C+oQUuay2HlzxJjAeEvg81fjfBZHv+K888p\
            9/3Dxw9DblLmFB/fmiCLsossWDmSbn9zKzPD9gOGNwIqVcQi0b0z/82pnx\
                0gx6laWqFoJu+fs8BbxPK1QxEaHvCbxGSJ6CwdLFlcjYIATed0tKNf\
                    TpaCX3OAa8k64GOjfCGHTjKugH/Jmxv2oGjvmfjF6FYYVkefTu\
                        OT8LbjtBZX5eQH4SBS+BLKd0jlKttxal6m5Av+UVWzRYhb\
                            h16slZxYwvCm1vRpZa5KAvCs5uFVGEj5H/XSFCLsAc\
                                VZReqRbbG66+IZmGv92XmizAWTzEr/SQUqy4np\
                                    Vde2Ex4rzMLF5UfhIxviZ6lNWF0g/Tt9VW\
                                        sg/Q1TCfCODYVaxVLwggH6cuaqhjd/\
                                            aRuQShX81hS6YLw7LbwaKxtMxC\
                                                KFQSW1bg2HQilXoiTlnkRR\
                                                    rigGTUTRukreg3+QkX\
rK3p1E6Fc9XhpNRPhra9i9jUSSr4XI6zeI6povWGv3iMqqWLA56gbCOM1NMMeUcW67B5lB\
    sLYzhGXav6TPox/HsbvLSLd/w6Kfl1qJkKx16el9do9RWtN33v8WNfesZ+XThcX06l\
        +hONUr+8t4ru4eCWIv265I0N8Z8C/YxaiOlJcpPgvIoZiiEuctIwyXca13T62d\
            NYqb34Vm1id3TSMilW09zq+1C1L9dr6jIP+jIK++4X+d2bJVyR7fusoU0t\
                ZB0u+xd0Sgt6yZrFZc2YyQs7jedrIRNzIe7of42am5WZ2nnP2/SW0U\
                    xZkJ8MyNP9YXFqVO1mku1my+YOQ5iyloxpER7ncVYNLZmXQdhU\
                        fZ8KnsqtCauVS8MyppkKeNZcbrlo1bsU3nCt/VOZCkG695\
0n4VFLWF6Ds8/t9Sm541hjKK2vdLjk8tV+jgU44qHqkJ/Tls+9MFlC+KLReW9IZSMkHRzi\
    VllVgGTFSVcEkK1Ng8Qc7XNEEw9EJB+VJN3CCQfsvbOwlQ6QJR+XP/jRpQScdi4SU3\
        XZJPk+ha9DmSdWVpinGtrrSTv+amjKDkc3iq7Kbt0mV9YVaTJOmdfEdPFcUdZo\
            2xpRdViVJi3zTYik+wqvoR3h/xU/4DwzAeQMogZYGAAAAAElFTkSuQmCC'
            user.save()
            request.session["flash_success"] = \
                "Пользователь успешно зарегистрирован"
            return redirect("/home")
        return inertia_render(
            request,
            'FormRegistration',
            props={
                "form": {
                    "email": request.POST.get("email", ""),
                    "password": ""
                },
                "errors": form.errors
            }
        )


class UserUpdate(UserAuthenticationCheckMixin, View):
    
    """
    Метод get рендерит страницу UpdateUserProfile и передает данные в props
    
    {
        'username': .....,
        'first_name': ........,
        'last_name': .......,
        'avatar_image': .......,
        'email': ........,
        'bio': ......,
    }
    """
    """
    Метод post при успешном изменении данных перенаправляет 
    на страницу профиля пользователя и выводит флеш сообжение 
    об успешности изменений сохраняя данные в БД иначе
    
    рендерит страницу изменений профиля, передает props с данными:
    {
        'username': .....,
        'first_name': ........,
        'last_name': .......,
        'avatar_image': .......,
        'email': ........,
        'bio': ......,
    }
    нформацию об ошибке:
    "errors": form.errors
    """
    
    def get(self, request, *args, **kwargs):
        if request.user.username == kwargs.get('username'):
            
            data = {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'avatar_image': request.user.avatar_image,
                'email': request.user.email,
                'bio': request.user.bio,
            }
            return inertia_render(
                request,
                'UpdateUserProfile',
                props={
                    'form': data,
                    'errors': {} 
                }
            )
        
        request.session["flash_error"] = \
            "У вас нет прав для изменения другого пользователя."
        return redirect(reverse('users:user_cabinet'))

    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        form = UserUpdateForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            request.session["flash_success"] = \
                "Профиль успешно изменен."
            return redirect(reverse('users:user_cabinet'))
        
        data = {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'avatar_image': user.avatar_image,
                'email': user.email,
                'bio': user.bio,
            }
        return inertia_render(
            request,
            'UpdateUserProfile',
            props={
                'form': data,
                'errors': form.errors
            }
        )


class AvatarChangeView(View):
    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        avatar_form = AvatarChange(data=request.POST, instance=user)
        if avatar_form.is_valid():
            avatar_form.save()
            request.session["flash_success"] = \
                'Аватар успешно изменен'
            return redirect(reverse('users:user_cabinet'))
        if avatar_form.errors.get('avatar_url'):
            avatar_url = avatar_form.errors.get('avatar_url').as_text()
            request.session["flash_error"] = f"{avatar_url[1:]}"
        return redirect(reverse('users:user_cabinet'))


class RestorePasswordRequestView(View):
    def get(self, request, *args, **kwargs):
        form = RestorePasswordRequestForm()
        return render(
            request,
            'users/restore-password-request.html',
            {'form': form}
        )

    def post(self, request, *args, **kwargs):
        form = RestorePasswordRequestForm(data=request.POST)
        if form.is_valid():
            form.save(request=request,
                      use_https=request.is_secure(),
                      email_template_name='emails/restore-password-email.html',
            )
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Ссылка на восстановление пароля \
                                    отправлена на указанный вами Email'
            )
            return redirect('users:login')  # redirect already uses reverse
        
        messages.add_message(request,
                             messages.ERROR,
                             'Пожалуйста, введите корректный Email'
        )
        return render(request,
                      'users/restore-password-request.html',
                      {'form': form}
        )


class RestorePasswordView(View):
    def get(self, request, *args, **kwargs):
        try:
            uid = kwargs['uidb64']
        except KeyError:
            uid = None
        try:
            token = kwargs['token']
        except KeyError:
            token = None

        if uid is None or token is None:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректная ссылка для восстановления пароля')
            return redirect('users:login')

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректный id пользователя')
            return redirect('users:login')
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Пользователь не найден')
            return redirect('users:login')

        if not default_token_generator.check_token(user, token):
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректная ссылка для восстановления пароля')
            return redirect('users:login')

        form = RestorePasswordForm(user=user)
        return render(
            request,
            'users/restore-password.html',
            {'form': form,
             'uid': uid,
             'token': token,
            }
        )

    def post(self, request, *args, **kwargs):
        try:
            uid = kwargs['uidb64']
        except KeyError:
            uid = None
        try:
            token = kwargs['token']
        except KeyError:
            token = None

        if uid is None or token is None:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректная ссылка для восстановления пароля')
            return redirect('users:login')

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректный id пользователя')
            return redirect('users:login')
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Пользователь не найден')
            return redirect('users:login')

        if not default_token_generator.check_token(user, token):
            messages.add_message(request,
                                 messages.ERROR,
                                 'Некорректная ссылка для восстановления пароля')
            return redirect('users:login')

        form = RestorePasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Пароль успешно изменен')
            return redirect('users:login')

        return render(
            request,
            'users/restore-password.html',
            {'form': form,
             'uid': uid,
             'token': token,
            }
        )
