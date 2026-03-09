import pytest
import json
from pathlib import Path
from django.contrib.auth import get_user_model

User = get_user_model()

FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def load_fixture(filename):
    """Загружает данные из JSON файла"""
    filepath = FIXTURES_DIR / f'{filename}.json'
    if not filepath.exists():
        return {'valid': [], 'invalid': []}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def user_fixtures():
    return load_fixture('model_users_user')


@pytest.fixture
def telegram_channel_fixtures():
    return load_fixture('model_parser_telegram_channel')


@pytest.fixture
def user_reg_fixtures():
    return load_fixture('form_user_reg')


@pytest.fixture
def user_login_fixtures():
    return load_fixture('form_user_login')


@pytest.fixture
def user_update_fixtures():
    return load_fixture('form_user_update')


@pytest.fixture
def user_avatar_fixtures():
    return load_fixture('form_user_avatar_change')


@pytest.fixture
def restore_request_fixtures():
    return load_fixture('form_restore_password_request')


@pytest.fixture
def restore_password_fixtures():
    return load_fixture('form_restore_password')


@pytest.fixture
def group_fixtures():
    return load_fixture('form_group_create')


@pytest.fixture
def group_create_fixtures():
    return load_fixture('form_group_create')


@pytest.fixture
def group_update_fixtures():
    return load_fixture('form_group_update')


@pytest.fixture
def channel_parse_fixtures():
    return load_fixture('form_parser_channel_parse')


@pytest.fixture
def user(db):
    """Создает тестового пользователя"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def group(db, user):
    """Создает тестовую группу с owner"""
    from apps.group_channels.models import Group
    group = Group.objects.create(
        name='Test Group',
        description='Test Description',
        owner=user,  # Обязательно указываем owner!
        is_editorial=False,
        order=0
    )
    # У группы нет members, только owner
    return group


@pytest.fixture
def telegram_channel(db):
    """Создает тестовый Telegram канал"""
    from apps.parser.models import TelegramChannel
    return TelegramChannel.objects.create(
        channel_id=123456789,
        title='Test Channel',
        username='test_channel',
        participants_count=1000,
        description='Test Description'
    )


@pytest.fixture
def client():
    from django.test import Client
    return Client()

@pytest.fixture
def test_user_from_login_fixture(user_login_fixtures, db):
    """Создает тестового пользователя из фикстур для формы логина"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    data = user_login_fixtures['valid'][0]
    user = User.objects.create_user(
        username=data['username'],
        password=data['password'],
        email=f"{data['username']}@test.com"
    )
    return user, data

@pytest.fixture
def test_user_for_password_restore(restore_password_fixtures, db):
    """Создает тестового пользователя для формы восстановления пароля"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Создаем пользователя
    user = User.objects.create_user(
        username='password_restore_user',
        password='old_password123',
        email='restore@example.com'
    )
    
    data = restore_password_fixtures['valid'][0]
    return user, data