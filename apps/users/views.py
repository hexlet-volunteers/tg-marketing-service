from django.contrib import auth, messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.middleware.csrf import get_token
from django.utils import timezone
from inertia import render as inertia_render
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import View
from django.conf import settings

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


# константа с дефолтной=аватаркой для представления UserRegister
DEFAULT_AVATAR_URL = f"{settings.STATIC_URL}default_avatar.jpeg"


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
            "first_name": "",
            "last_name": "",
            "username": "",
            "password1": "",
            "password2": "",
            "email": "",
            "bio": "",
            "avatar_image": ""
        }
        
    POST /register/ 
    Назначение: обрабатывает отправку данных формы регистрации.
    Входные данные (request.POST):
    
    {
        "data": {
            "first_name": "",
            "last_name": "",
            "username": "",
            "password1": "",
            "password2": "",
            "email": "",
            "bio": "",
            "avatar_image": ""
        },
        "errors": form.errors
    }
    """
    
    def get(self, request):
        return inertia_render(
            request,
            "FormRegistration",
            props={
                "first_name": "",
                "last_name": "",
                "username": "",
                "password1": "",
                "password2": "",
                "email": "",
                "bio": "",
                "avatar_image": ""
            }
        )
        
    def post(self, request, *args, **kwargs):
        form = UserRegForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Устанавливаем роль пользователя
            user.role = 'user'
            
            if not user.avatar_image:
                user.avatar_image = DEFAULT_AVATAR_URL
            user.save()
            request.session["flash_success"] = \
                "Пользователь успешно зарегистрирован"
            return redirect("/home")
        return inertia_render(
            request,
            'FormRegistration',
            props={
                "data": { 
                    "first_name": request.POST.get("first_name", ""),
                    "last_name": request.POST.get("last_name", ""),
                    "username": request.POST.get("username", ""),
                    "password1": request.POST.get("password1", ""),
                    "password2": request.POST.get("password2", ""),
                    "email": request.POST.get("email", ""),
                    "bio": request.POST.get("bio", ""),
                    "avatar_image": request.POST.get("avatar_image", "")
                },
                "errors": form.errors,
            }
        )


class UserUpdate(UserAuthenticationCheckMixin, View):
    
    """
    Метод get рендерит страницу UpdateUserProfile и передает данные в props
    
    {
        'first_name': ........,
        'last_name': .......,
        'username': .....,
        'password1': "",
        'password2': "",
        'email': ........,
        'bio': ......,
        'avatar_image': .......,
    }
    
    Метод post при успешном изменении данных перенаправляет 
    на страницу профиля пользователя и выводит флеш сообжение 
    об успешности изменений сохраняя данные в БД иначе
    
    рендерит страницу изменений профиля, передает props с данными:
    {
        'first_name': ........,
        'last_name': .......,
        'username': .....,
        'password1': "",
        'password2': "",
        'email': ........,
        'bio': ......,
        'avatar_image': .......,
    }
    нформацию об ошибке:
    "errors": form.errors
    
    """
    
    def get(self, request, *args, **kwargs):
        if request.user.username == kwargs.get('username'):
            
            data = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "username": request.user.username,
                "password1": "",
                "password2": "",
                "email": request.user.email,
                "bio": request.user.bio,
                "avatar_image": request.user.avatar_image,
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
        return redirect(reverse('users:profile'))

    def post(self, request, *args, **kwargs):
        username = kwargs.get('username')
        user = User.objects.get(username=username)
        form = UserUpdateForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            request.session["flash_success"] = \
                "Профиль успешно изменен."
            return redirect(reverse('users:profile'))
        
        data = {
                
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "password1": "",
                "password2": "",
                "email": user.email,
                "bio": user.bio,
                "avatar_image": user.avatar_image,
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
            return redirect(reverse('users:profile'))
        if avatar_form.errors.get('avatar_url'):
            avatar_url = avatar_form.errors.get('avatar_url').as_text()
            request.session["flash_error"] = f"{avatar_url[1:]}"
        return redirect(reverse('users:profile'))


class RestorePasswordRequestView(View):
    """
    Метод get возвращает props 
    {
        "email": ""
    }
    
    Метод post либо сообщает о направлении информаци на email
    и релирект на страницу login,
    либо сообщение об ошибке в введенном eamil и возвращает props 
    {
        "email": ..........,
    }
    """
    
    def get(self, request, *args, **kwargs):       
       
        return inertia_render(
            request,
            'RestorePasswordRequest',
            props={"email": ""}
        )

    def post(self, request, *args, **kwargs):
        form = RestorePasswordRequestForm(data=request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='emails/restore-password-email.html',
            )
            request.session["flash_success"] = \
                "Ссылка на восстановление пароля \
                отправлена на указанный вами Email"
            return redirect('users:login')
        return inertia_render(
            request,
            "RestorePasswordRequest",
            props={
                "email": request.POST.get("email", ""),
                'errors': form.errors
                }
        )


class RestorePasswordView(View):
    """
    Метод get возвращает props 
    {
        "new_password1": "",
        "new_password2": "",
        "id": uid,
        "token": token,
    }
    
    Метод post либо сообщает о направлении информаци на email
    и релирект на страницу login,
    либо сообщение об ошибке в введенном eamil и возвращает props 
    {
        "new_password1": .......,
        "new_password2": .......,
        "id": uid,
        "token": token,
    }
    """
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
            request.session["flash_error"] = \
                "Некорректная ссылка для восстановления пароля"
            return redirect('users:login')

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            request.session["flash_error"] = \
                'Некорректный id пользователя'
            return redirect('users:login')
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            request.session["flash_error"] = \
                'Пользователь не найден'
            return redirect('users:login')

        if not default_token_generator.check_token(user, token):
            request.session["flash_error"] = \
                'Некорректная ссылка для восстановления пароля'
            return redirect('users:login')
        
        return inertia_render(
            request,
            "RestorePassword",
            props={
                "new_password1": "",
                "new_password2": "",
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
            request.session["flash_error"] = \
                'Некорректная ссылка для восстановления пароля'
            return redirect('users:login')

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            request.session["flash_error"] = \
                'Некорректный id пользователя'
            return redirect('users:login')
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            request.session["flash_error"] = \
                'Пользователь не найден'
            return redirect('users:login')

        if not default_token_generator.check_token(user, token):
            request.session["flash_error"] = \
                'Некорректная ссылка для восстановления пароля'
            return redirect('users:login')

        form = RestorePasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            request.session["flash_success"] = \
                'Пароль успешно изменен'
            return redirect('users:login')

        return inertia_render(
            request,
            "RestorePassword",
            props={
                "new_password1": request.POST.get("new_password1", ""),
                "new_password2": request.POST.get("new_password2", ""),
                'uid': uid,
                'token': token,
                "errors": form.errors
            }
        )
