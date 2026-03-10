from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)

from apps.users.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['usernme', 'password']
        
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={"autofocus": True,
                                      'class': 'form-control',
                                      'placeholder': 'Имя пользователя'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          'class': 'form-control',
                                          'placeholder': 'Пароль'})
    )
    
    
class UserRegForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            'last_name',
            'username',
            'password1',
            'password2',
            'email',
            'bio',
            'avatar_image',
        )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Имя'})
    ) 
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Фамилия'})
    ) 
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={"autofocus": True,
                                      'class': 'form-control',
                                      'placeholder': 'Имя пользователя'})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                      'placeholder': 'Пароль'})
    ) 
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                      'class': 'form-control',
                                      'placeholder': 'Подтверждение пароля'})
    )
    email = forms.CharField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                      'placeholder': 'Email'}))
    bio = forms.CharField(
        required=False,
        label='Email',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                      'placeholder': 'О себе',
                                      'rows': 3}))
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input',
            }
        )
    )
    avatar_image = forms.CharField(
        required=False,
        label='URL аватара',
        widget=forms.TextInput(attrs={'name': 'avatar_image',
                                      'class': 'form-control'})
    )
    

class UserUpdateForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            'last_name',
            'username',
            'password1',
            'password2',
            'email',
            'bio',
            'avatar_image',
        )
    
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Имя'})
    ) 
    
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Фамилия'})
    ) 
    
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={"autofocus": True,
                                      'class': 'form-control',
                                      'placeholder': 'Имя пользователя'})
    )
    
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                      'placeholder': 'Пароль'})
    ) 
    
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                      'class': 'form-control',
                                      'placeholder': 'Подтверждение пароля'})
    )
    
    email = forms.CharField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                      'placeholder': 'Email'}))
    
    bio = forms.CharField(
        required=False,
        label='Email',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                      'placeholder': 'О себе',
                                      'rows': 3}))
    
    avatar_image = forms.CharField(
        required=False,
        label='URL аватара',
        widget=forms.TextInput(attrs={'name': 'avatar_image',
                                      'class': 'form-control'})
    )
    
    def clean(self):
        """Проверяет совпадение паролей"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Пароли не совпадают')
        
        return cleaned_data
    
    
class AvatarChange(UserChangeForm):
    class Meta:
        model = User
        fields = ('avatar_image',)
    avatar_image = forms.CharField(
        required=False,
        label='URL аватара',
        widget=forms.TextInput(attrs={'id': 'avatarUrl',
                                      'name': 'avatar_image',
                                      'class': 'form-control',
                                      'placeholder': 'https://example.com/avatar.jpg'})
    )


class RestorePasswordRequestForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                       'placeholder': 'Пожалуйста, введите ваш email'})
    )


class RestorePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Подтверждение пароля'})
    )