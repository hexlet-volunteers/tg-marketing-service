import json
from typing import Any, cast

from django.contrib import auth, messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
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

from apps.billing.services.subscription_service import (
    get_subscription,
    serialize_subscription,
)
from apps.users.account_deletion import request_account_deletion
from apps.users.consents import record_consent, serialize_user_consent_history
from apps.users.data_subject_requests import (
    complete_subject_request,
    create_subject_request,
    fail_subject_request,
    serialize_subject_request,
)
from apps.users.forms import (
    AvatarChange,
    RestorePasswordForm,
    RestorePasswordRequestForm,
    UserLoginForm,
    UserRegForm,
    UserUpdateForm,
)
from apps.users.middleware import RoleRequest
from apps.users.models import Consent, DataSubjectRequestLog, User
from apps.users.personal_data_export import build_personal_data_export
from config.mixins import UserAuthenticationCheckMixin

# константа с дефолтной=аватаркой для представления UserRegister
DEFAULT_AVATAR_URL = static("users/default-avatar.svg")


class PersonalDataExportView(UserAuthenticationCheckMixin, View):
    """Download personal data belonging to the authenticated subject."""

    request_type = DataSubjectRequestLog.RequestType.EXPORT

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        return self._export(request)

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        return self._export(request)

    def _export(self, request: HttpRequest) -> HttpResponse:
        user = cast(User, request.user)
        request_log = create_subject_request(
            user, self.request_type, cast(str, request.method)
        )
        exported_at = timezone.now()
        try:
            with transaction.atomic():
                locked = User.objects.select_for_update().get(pk=user.pk)
                if not locked.is_active or locked.anonymized_at is not None:
                    raise ValueError("Account processing has stopped")
                payload = build_personal_data_export(locked, exported_at)
                content = json.dumps(payload, ensure_ascii=False, indent=2)
                complete_subject_request(
                    request_log, {"format_version": payload["format_version"]}
                )
        except Exception:
            fail_subject_request(request_log)
            return JsonResponse(
                {"request_id": request_log.pk, "error": "export_failed"},
                status=503,
            )

        filename = f"personal-data-{user.pk}-{exported_at:%Y-%m-%d}.json"
        response = HttpResponse(
            content,
            content_type="application/json; charset=utf-8",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Cache-Control"] = "no-store"
        response["Pragma"] = "no-cache"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class PersonalDataAccessView(PersonalDataExportView):
    request_type = DataSubjectRequestLog.RequestType.ACCESS


class AccountDeletionView(UserAuthenticationCheckMixin, View):
    withdraw_consent = False

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        try:
            request_log = request_account_deletion(
                cast(User, request.user),
                cast(str, request.method),
                withdraw_consent=self.withdraw_consent,
            )
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=409)
        auth.logout(request)
        response = JsonResponse(
            serialize_subject_request(request_log),
            status=200
            if request_log.status == DataSubjectRequestLog.Status.COMPLETED
            else 503,
        )
        response["Cache-Control"] = "no-store"
        return response


class ConsentWithdrawalView(AccountDeletionView):
    withdraw_consent = True


class DataSubjectRequestHistoryView(UserAuthenticationCheckMixin, View):
    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        logs = DataSubjectRequestLog.objects.filter(
            subject=cast(User, request.user)
        )
        response = JsonResponse(
            {"requests": [serialize_subject_request(log) for log in logs]}
        )
        response["Cache-Control"] = "no-store"
        return response


class ConsentHistoryView(UserAuthenticationCheckMixin, View):
    """Return consent history for the authenticated subject."""

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        user = cast(User, request.user)
        content = json.dumps(
            {"consents": serialize_user_consent_history(user)},
            ensure_ascii=False,
        )
        return HttpResponse(
            content,
            content_type="application/json; charset=utf-8",
        )


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
    ) -> InertiaResponse | HttpResponseRedirect:
        form = UserLoginForm(request, request.POST)

        # валидируем данные
        if form.is_valid():
            # сохраняем полученные данные в объект
            user = form.get_user()

            # записываем пользователя в сессию
            login(request, user)

            request.session["flash"] = {"success": "Вы залогинены"}
            return redirect("homepage:dashboard")

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
            "subscription": serialize_subscription(get_subscription(user)),
            "notifications": None,
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
                    update_session_auth_hash(request, user)
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
        "terms",
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
            with transaction.atomic():
                user = form.save(commit=False)
                user.role = "user"
                if not user.avatar_image:
                    user.avatar_image = DEFAULT_AVATAR_URL
                user.save()
                record_consent(
                    user=user,
                    document_type=Consent.DocumentType.PERSONAL_DATA,
                    source=Consent.Source.EMAIL_REGISTRATION,
                    request=request,
                )

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
        user = cast(User, request.user)
        if user.username != username:
            request.session["flash"] = {
                "error": "У вас нет прав для изменения другого пользователя."
            }
            return redirect(reverse("users:user_cabinet"))

        form = UserUpdateForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)
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


class AvatarChangeView(UserAuthenticationCheckMixin, View):
    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseRedirect:
        username = kwargs.get("username")
        user = request.user
        if user.username != username:
            request.session["flash"] = {
                "error": "У вас нет прав для изменения другого пользователя."
            }
            return redirect(reverse("users:user_cabinet"))
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
        except (TypeError, ValueError, UnicodeDecodeError):
            request.session["flash"] = {"error": "Некорректный id пользователя"}
            return redirect("users:login")
        try:
            user = User.objects.get(pk=uid_decoded)
        except (User.DoesNotExist, ValueError, OverflowError):
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
        except (TypeError, ValueError, UnicodeDecodeError):
            request.session["flash"] = {"error": "Некорректный id пользователя"}
            return redirect("users:login")
        try:
            user = User.objects.get(pk=uid_decoded)
        except (User.DoesNotExist, ValueError, OverflowError):
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
                "new_password1": "",
                "new_password2": "",
                "uid": uid,
                "token": token,
                "errors": form.errors,
            },
        )
