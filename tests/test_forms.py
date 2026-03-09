# import pytest
# from django import forms

# from apps.users.forms import (
#     UserLoginForm, UserRegForm, UserUpdateForm,
#     AvatarChange, RestorePasswordRequestForm, RestorePasswordForm
# )
# from apps.group_channels.forms import CreateGroupForm, UpdateGroupForm
# from apps.parser.forms import ChannelParseForm


# @pytest.mark.django_db
# class TestUserRegistrationForm:
#     """Тесты для формы регистрации пользователя"""
    
#     def test_valid_form(self, user_reg_fixtures):
#         """Тест валидной формы"""
#         valid_data = user_reg_fixtures['valid'][0]
#         form = UserRegForm(data=valid_data)
        
#         assert form.is_valid()
    
#     def test_password_mismatch(self, user_reg_fixtures):
#         """Тест несовпадения паролей"""
#         valid_data = user_reg_fixtures['valid'][0]
#         form = UserRegForm(data={
#             **valid_data,
#             'password2': 'different_password'
#         })
        
#         assert not form.is_valid()
#         assert 'password2' in form.errors
    
#     def test_invalid_email(self, user_reg_fixtures):
#         """Тест невалидного email"""
#         invalid_data = user_reg_fixtures['invalid'][0]
#         form = UserRegForm(data=invalid_data)
        
#         assert not form.is_valid()
#         assert 'email' in form.errors


# @pytest.mark.django_db
# class TestUserLoginForm:
#     """Тесты для формы входа"""
    
#     def test_valid_form(self, test_user_from_login_fixture):
#         """Тест валидной формы"""
#         user, valid_data = test_user_from_login_fixture
        
#         form = UserLoginForm(data=valid_data)
        
#         if not form.is_valid():
#             print(f"Ошибки формы: {form.errors}")
        
#         assert form.is_valid()


# @pytest.mark.django_db
# class TestUserUpdateForm:
#     """Тесты для формы обновления пользователя"""
    
#     def test_valid_form(self, user_update_fixtures):
#         """Тест валидной формы"""
#         valid_data = user_update_fixtures['valid'][0]
#         form = UserUpdateForm(data=valid_data)
        
#         assert form.is_valid()
    
#     def test_password_mismatch(self, user_update_fixtures):
#         """Тест несовпадения паролей"""
#         valid_data = user_update_fixtures['valid'][0]

#         modified_data = {
#             **valid_data,
#             'password2': 'different'
#         }

#         form = UserUpdateForm(data=modified_data)

#         assert not form.is_valid()
#         assert 'Пароли не совпадают' in str(form.errors)


# @pytest.mark.django_db
# class TestUserAvatarChangeForm:
#     """Тесты для формы изменения аватара"""
    
#     def test_valid_form(self, user_avatar_fixtures):
#         """Тест валидной формы"""
#         valid_data = user_avatar_fixtures['valid'][0]
#         form = AvatarChange(data=valid_data)
        
#         assert form.is_valid()


# @pytest.mark.django_db
# class TestRestorePasswordForms:
#     """Тесты для форм восстановления пароля"""
    
#     def test_restore_password_request_valid(self, restore_request_fixtures):
#         """Тест валидной формы запроса восстановления"""
#         valid_data = restore_request_fixtures['valid'][0]
#         form = RestorePasswordRequestForm(data=valid_data)
        
#         assert form.is_valid()
    
#     def test_restore_password_valid(self, test_user_for_password_restore):
#         """Тест валидной формы восстановления пароля"""
#         user, valid_data = test_user_for_password_restore
#         form = RestorePasswordForm(user=user, data=valid_data)

#         if not form.is_valid():
#             print(f"Ошибки формы: {form.errors}")

#         assert form.is_valid()

#     def test_restore_password_invalid(self, restore_password_fixtures, db):
#         """Тест невалидной формы восстановления пароля"""
#         from django.contrib.auth import get_user_model
#         User = get_user_model()

#         user = User.objects.create_user(
#             username='testuser',
#             password='oldpassword',
#             email='test@example.com'
#         )

#         invalid_data = restore_password_fixtures['invalid'][0]
#         form = RestorePasswordForm(user=user, data=invalid_data)

#         assert not form.is_valid()


# @pytest.mark.django_db
# class TestGroupForms:
#     """Тесты для форм групп из group_channels"""
    
#     def test_group_create_valid(self, group_create_fixtures):
#         """Тест валидной формы создания группы"""
#         valid_data = group_create_fixtures['valid'][0]
#         form = CreateGroupForm(data=valid_data)
        
#         assert form.is_valid()
    
#     def test_group_create_name_required(self, group_create_fixtures):
#         """Тест обязательности названия группы"""
#         invalid_data = group_create_fixtures['invalid'][0]
#         form = CreateGroupForm(data=invalid_data)
        
#         assert not form.is_valid()
#         assert 'name' in form.errors
    
#     def test_group_update_valid(self, group_update_fixtures):
#         """Тест валидной формы обновления группы"""
#         valid_data = group_update_fixtures['valid'][0]
#         form = UpdateGroupForm(data=valid_data)
        
#         assert form.is_valid()


# @pytest.mark.django_db
# class TestChannelParseForm:
#     """Тесты для формы парсинга канала"""
    
#     def test_channel_parse_valid(self, channel_parse_fixtures):
#         """Тест валидной формы парсинга"""
#         valid_data = channel_parse_fixtures['valid'][0]
#         form = ChannelParseForm(data=valid_data)
        
#         assert form.is_valid()
