from typing import Any, cast

from django.contrib import auth, messages
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.http import (
    HttpRequest,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import View
from inertia import InertiaResponse
from inertia import render as inertia_render

from apps.users.forms import (
    AvatarChange,
    RestorePasswordForm,
    RestorePasswordRequestForm,
    UserLoginForm,
    UserRegForm,
    UserUpdateForm,
)
from apps.users.middleware import RoleRequest
from apps.users.models import User
from config.mixins import UserAuthenticationCheckMixin

# константа с дефолтной=аватаркой для представления UserRegister
DEFAULT_AVATAR_URL = static("users/default-avatar.svg")


class LogoutView(UserAuthenticationCheckMixin, View):
    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseRedirect:
        return redirect(reverse("main_index"))

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        messages.add_message(request, messages.INFO, "Вы разлогинены")
        auth.logout(request)
        return redirect(reverse("main_index"))


@method_decorator(
    sensitive_post_parameters("password"),
    name="post",
)
class LoginView(View):
    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse:
        # возвращаем форму
        return inertia_render(
            request,
            "Auth",
            props={
                "form": {"data": {"email": "", "password": ""}, "errors": {}}
            },
        )

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse:
        form = UserLoginForm(request, request.POST)

        # валидируем данные
        if form.is_valid():
            # сохраняем полученные данные в объект
            user = form.get_user()

            # записываем пользователя в сессию
            login(request, user)

            # возвращаем компонент и props
            return inertia_render(
                request,
                "Home",
                props={
                    "flash": {"success": "Вы залогинены"},
                    "user": {"username": request.POST.get("username")},
                },
            )

        else:
            # Ошибки валидации
            return inertia_render(
                request,
                "Auth",
                props={
                    "form": {
                        "data": {
                            "email": request.POST.get("email", ""),
                            "password": "",
                        },
                        "errors": form.errors,
                    }
                },
            )


class UserCabinetView(UserAuthenticationCheckMixin, View):
    """
    Account page view.

    component: UserProfilePage
    props: user, subscription, notifications, usage_stats, user_role
    url: /auth/profile/
    """

    def _build_base_props(
        self,
        request: HttpRequest,
        user: User,
    ) -> dict[str, Any]:
        registration_date = user.date_joined
        last_visit = user.last_login if user.last_login else timezone.now()
        total_hours = (last_visit - registration_date).total_seconds() / 3600
        usage_stats = {
            "registration_date": user.date_joined.strftime("%d.%m.%Y"),
            "last_visit": (
                user.last_login.strftime("%d.%m.%Y")
                if user.last_login
                else "Никогда"
            ),
            "total_time": f"{total_hours:.0f} часов",
        }

        return {
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "email": user.email,
                "avatar": user.avatar_image,
                "role": user.role,
                "bio": user.bio,
            },
            "subscription": {
                "plan": "Pro",
                "price": "$29",
                "period": "в месяц",
                "channels_used": 47,
                "channels_limit": 100,
                "ai_requests_used": 234,
                "ai_requests_limit": 1000,
            },
            "notifications": {
                "weekly_reports": True,
                "trend_notifications": True,
                "limit_exceeded": False,
                "new_features": True,
            },
            "usage_stats": usage_stats,
            "user_role": cast(RoleRequest, request).role,
        }

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse:
        user = cast(User, request.user)
        props = self._build_base_props(request, user)
        return inertia_render(request, "UserProfilePage", props=props)

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        user = cast(User, request.user)
        action = request.POST.get("action")

        if action == "notifications":
            # Уведомления сейчас заглушки
            messages.add_message(
                request, messages.SUCCESS, "Настройки уведомлений сохранены"
            )
        else:
            form = UserUpdateForm(data=request.POST, instance=user)
            if form.is_valid():
                try:
                    form.save()
                    messages.add_message(
                        request, messages.SUCCESS, "Профиль успешно изменен"
                    )
                except Exception as e:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Ошибка при сохранении: {str(e)}",
                    )
                    return redirect(reverse("users:user_cabinet"))
            else:
                props = self._build_base_props(request, user)
                props["errors"] = form.errors.get_json_data()
                props["values"] = {
                    "first_name": request.POST.get("first_name", ""),
                    "last_name": request.POST.get("last_name", ""),
                    "email": request.POST.get("email", ""),
                    "bio": request.POST.get("bio", ""),
                    "avatar_image": request.POST.get("avatar_image", ""),
                }
                return inertia_render(request, "UserProfilePage", props=props)

        return redirect(reverse("users:user_cabinet"))


@method_decorator(
    sensitive_post_parameters("password1", "password2"),
    name="post",
)
class UserRegister(View):
    form_fields = (
        "first_name",
        "last_name",
        "password1",
        "password2",
        "email",
        "bio",
        "avatar_image",
    )

    def _empty_form_data(self) -> dict[str, str]:
        return {field: "" for field in self.form_fields}

    def _bound_form_data(self, request: HttpRequest) -> dict[str, str]:
        data = self._empty_form_data()
        data.update(
            {field: request.POST.get(field, "") for field in self.form_fields}
        )
        data["password1"] = ""
        data["password2"] = ""
        return data

    def _form_props(
        self,
        data: dict[str, str] | None = None,
        errors: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "form": {
                "data": data or self._empty_form_data(),
                "errors": errors or {},
            }
        }

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse:
        return inertia_render(
            request,
            "FormRegistration",
            props=self._form_props(),
        )

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        form = UserRegForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "user"
            if not user.avatar_image:
                user.avatar_image = DEFAULT_AVATAR_URL
            user.save()

            request.session["flash"] = {
                "success": "Пользователь успешно зарегистрирован"
            }
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect(reverse("homepage:dashboard"))

        return inertia_render(
            request,
            "FormRegistration",
            props=self._form_props(
                data=self._bound_form_data(request),
                errors=form.errors.get_json_data(),
            ),
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

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        user = cast(User, request.user)
        if user.username == kwargs.get("username"):
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
                request, "UpdateUserProfile", props={"form": data, "errors": {}}
            )

        request.session["flash"] = {
            "error": "У вас нет прав для изменения другого пользователя."
        }
        return redirect(reverse("users:user_cabinet"))

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        username = kwargs.get("username")
        user = User.objects.get(username=username)
        form = UserUpdateForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            request.session["flash"] = {"success": "Профиль успешно изменен."}
            return redirect(reverse("users:user_cabinet"))

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
            "UpdateUserProfile",
            props={"form": data, "errors": form.errors},
        )


class AvatarChangeView(View):
    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseRedirect:
        username = kwargs.get("username")
        user = User.objects.get(username=username)
        avatar_form = AvatarChange(data=request.POST, instance=user)
        if avatar_form.is_valid():
            avatar_form.save()
            request.session["flash"] = {"success": "Аватар успешно изменен"}
            return redirect(reverse("users:user_cabinet"))
        avatar_error = avatar_form.errors.get("avatar_url")
        if avatar_error is not None:
            avatar_url = avatar_error.as_text()
            request.session["flash"] = {"error": f"{avatar_url[1:]}"}
        return redirect(reverse("users:user_cabinet"))


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

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        return inertia_render(
            request, "RestorePasswordRequest", props={"email": ""}
        )

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        form = RestorePasswordRequestForm(data=request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="emails/restore-password-email.html",
            )
            request.session["flash"] = {
                "success": (
                    "Ссылка на восстановление пароля "
                    "отправлена на указанный вами Email"
                )
            }
            return redirect("users:login")
        return inertia_render(
            request,
            "RestorePasswordRequest",
            props={
                "email": request.POST.get("email", ""),
                "errors": form.errors,
            },
        )


@method_decorator(
    sensitive_post_parameters(
        "new_password1",
        "new_password2",
    ),
    name="post",
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

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        try:
            uid = kwargs["uidb64"]
        except KeyError:
            uid = None
        try:
            token = kwargs["token"]
        except KeyError:
            token = None

        if uid is None or token is None:
            request.session["flash"] = {
                "error": "Некорректная ссылка для восстановления пароля"
            }
            return redirect("users:login")

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            request.session["flash"] = {"error": "Некорректный id пользователя"}
            return redirect("users:login")
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            request.session["flash"] = {"error": "Пользователь не найден"}
            return redirect("users:login")

        if not default_token_generator.check_token(user, token):
            request.session["flash"] = {
                "error": "Некорректная ссылка для восстановления пароля"
            }
            return redirect("users:login")

        return inertia_render(
            request,
            "RestorePassword",
            props={
                "new_password1": "",
                "new_password2": "",
                "uid": uid,
                "token": token,
            },
        )

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse | HttpResponseRedirect:
        try:
            uid = kwargs["uidb64"]
        except KeyError:
            uid = None
        try:
            token = kwargs["token"]
        except KeyError:
            token = None

        if uid is None or token is None:
            request.session["flash"] = {
                "error": "Некорректная ссылка для восстановления пароля"
            }
            return redirect("users:login")

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
        except TypeError:
            request.session["flash"] = {"error": "Некорректный id пользователя"}
            return redirect("users:login")
        try:
            user = User.objects.get(pk=uid_decoded)
        except User.DoesNotExist:
            request.session["flash"] = {"error": "Пользователь не найден"}
            return redirect("users:login")

        if not default_token_generator.check_token(user, token):
            request.session["flash"] = {
                "error": "Некорректная ссылка для восстановления пароля"
            }
            return redirect("users:login")

        form = RestorePasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            request.session["flash"] = {"success": "Пароль успешно изменен"}
            return redirect("users:login")

        return inertia_render(
            request,
            "RestorePassword",
            props={
                "new_password1": request.POST.get("new_password1", ""),
                "new_password2": request.POST.get("new_password2", ""),
                "uid": uid,
                "token": token,
                "errors": form.errors,
            },
        )
