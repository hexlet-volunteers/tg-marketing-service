from django.urls import path

from apps.users.views import (
    AccountDeletionView,
    AvatarChangeView,
    ConsentHistoryView,
    ConsentWithdrawalView,
    DataSubjectRequestHistoryView,
    LoginView,
    LogoutView,
    PersonalDataAccessView,
    PersonalDataExportView,
    RestorePasswordRequestView,
    RestorePasswordView,
    UserCabinetView,
    UserRegister,
    UserUpdate,
)

app_name = "users"

urlpatterns = [
    path(
        "me/personal-data/access/",
        PersonalDataAccessView.as_view(),
        name="personal_data_access",
    ),
    path(
        "me/consents/withdraw/",
        ConsentWithdrawalView.as_view(),
        name="consent_withdrawal",
    ),
    path(
        "me/personal-data/delete/",
        AccountDeletionView.as_view(),
        name="account_deletion",
    ),
    path(
        "me/personal-data/requests/",
        DataSubjectRequestHistoryView.as_view(),
        name="subject_request_history",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "me/personal-data/export/",
        PersonalDataExportView.as_view(),
        name="personal_data_export",
    ),
    path(
        "me/consents/",
        ConsentHistoryView.as_view(),
        name="consent_history",
    ),
    path("profile/", UserCabinetView.as_view(), name="user_cabinet"),
    path("create/", UserRegister.as_view(), name="user_create"),
    path(
        "restore-password/",
        RestorePasswordRequestView.as_view(),
        name="restore_password_request",
    ),
    path(
        "restore-password/<uidb64>/<token>/",
        RestorePasswordView.as_view(),
        name="restore_password",
    ),
    path(
        "<slug:username>/avatar-change/",
        AvatarChangeView.as_view(),
        name="avatar_update",
    ),
    path("<slug:username>/update/", UserUpdate.as_view(), name="user_update"),
]
