import pytest
import json
from pathlib import Path
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()
FIXTURES_DIR = Path(__file__).parent / 'fixtures'

def load_fixture(filename):
    filepath = FIXTURES_DIR / f'{filename}.json'
    if not filepath.exists():
        return {'valid': [], 'invalid': []}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture(scope='session', autouse=True)
def create_test_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            cursor.execute("DROP TABLE IF EXISTS users_userrolehistory")
            cursor.execute("DROP TABLE IF EXISTS users_role")
            cursor.execute("DROP TABLE IF EXISTS users_user")
            
            cursor.execute("""
                CREATE TABLE users_user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password VARCHAR(128) NOT NULL,
                    last_login DATETIME NULL,
                    is_superuser BOOLEAN NOT NULL,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    email VARCHAR(254) NOT NULL UNIQUE,
                    is_staff BOOLEAN NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    date_joined DATETIME NOT NULL,
                    avatar_image VARCHAR(200) NULL,
                    role VARCHAR(50) NOT NULL,
                    bio VARCHAR(200) NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE users_role (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(50) NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE users_userrolehistory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME NULL,
                    reason VARCHAR(250) NULL,
                    FOREIGN KEY(user_id) REFERENCES users_user(id),
                    FOREIGN KEY(role_id) REFERENCES users_role(id)
                )
            """)
            
            cursor.execute("""
                CREATE UNIQUE INDEX unique_current_role_per_user 
                ON users_userrolehistory (user_id) 
                WHERE end_date IS NULL
            """)
            
            cursor.execute("PRAGMA foreign_keys = ON")

@pytest.fixture(autouse=True)
def create_test_roles_data(db):
    from apps.users.roles import Role
    roles_data = [
        {'code': 'user', 'name': 'Пользователь'},
        {'code': 'partner', 'name': 'Партнер'},
        {'code': 'moderator', 'name': 'Модератор'},
        {'code': 'admin', 'name': 'Администратор'},
    ]
    for role_data in roles_data:
        Role.objects.get_or_create(
            code=role_data['code'],
            defaults={'name': role_data['name']}
        )

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
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password',
        first_name='Test',
        last_name='User'
    )

@pytest.fixture
def group(db, user):
    from apps.group_channels.models import Group
    group = Group.objects.create(
        name='Test Group',
        description='Test Description',
        owner=user,
        is_editorial=False,
        order=0
    )
    return group

@pytest.fixture
def telegram_channel(db):
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
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        username='password_restore_user',
        password='old_password123',
        email='restore@example.com'
    )
    data = restore_password_fixtures['valid'][0]
    return user, data