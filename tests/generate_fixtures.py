from typing import Dict, List, Tuple, Any
import logging
import random
import string

from tests.data_generator import DataGenerator, NUM_OF_FIXTURES

# Avoid importing Django app modules (which may require settings/db) just to get constants.
# Use project defaults, falling back safely if not importable.
from apps.users.models import ROLE_MAXLENGTH, BIO_MAXLENGTH

logger = logging.getLogger(__name__)


class ModelAndFormFixtureGenerator:
    '''
    class to actually generate fixtures for forms and models
    '''
    def __init__(self, num: int = NUM_OF_FIXTURES) -> None:
        self.gen = DataGenerator(num)
        self.size = self.gen.data_size

    def _create_test_user(self, username: str, password: str) -> None:
        """Создает тестового пользователя в БД"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Проверяем, есть ли уже такой пользователь
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                password=password,
                email=f"{username}@test.com"
            )

    def _compose(self, field_values: Dict[str, Tuple[Any, ...]]) -> Tuple[Dict[str, Any], ...]:
        '''
        Compose list of dicts from generated data
        '''
        size = self.size
        keys = list(field_values.keys())
        records: List[Dict[str, Any]] = []
        for i in range(size):
            rec = {}
            for k in keys:
                vals = field_values[k]
                rec[k] = vals[i] if i < len(vals) else None
            records.append(rec)
        return tuple(records)

    def _invalid_strings(self) -> Tuple[str, ...]:
        return self.gen.generate_invalid_data()

    def _repeat(self, value: Any) -> Tuple[Any, ...]:
        return tuple(value for _ in range(self.size))

    def _generate_valid_username(self) -> str:
        """Генерирует валидный username (буквы, цифры, @/./+/-/_)"""
        chars = string.ascii_letters + string.digits + '@.+-_'
        return ''.join(random.choice(chars) for _ in range(random.randint(5, 20)))

    def _generate_valid_email(self) -> str:
        """Генерирует валидный email (не длиннее 254 символов)"""
        local = ''.join(random.choice(string.ascii_letters + string.digits + '._-') for _ in range(10))
        domain = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
        return f"{local}@{domain}.com"

    def _generate_valid_password(self) -> str:
        """Генерирует валидный пароль"""
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(random.choice(chars) for _ in range(12))

    def _generate_valid_url(self) -> str:
        """Генерирует валидный URL"""
        return f"https://example.com/{''.join(random.choice(string.ascii_lowercase) for _ in range(10))}.jpg"

    # Models
    def model_users_user(self) -> None:
        '''
        fixtures for users.User model
        '''
        usernames = tuple(self._generate_valid_username() for _ in range(self.size))
        emails = tuple(self._generate_valid_email() for _ in range(self.size))
        roles = self.gen.generate_text(max_len=ROLE_MAXLENGTH)
        bios = self.gen.generate_text(max_len=BIO_MAXLENGTH)
        avatars = tuple(self._generate_valid_url() for _ in range(self.size))
        first_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(8)) for _ in range(self.size))
        last_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(10)) for _ in range(self.size))
        passwords = tuple(self._generate_valid_password() for _ in range(self.size))

        valid = self._compose({
            'username': usernames,
            'email': emails,
            'role': roles,
            'bio': bios,
            'avatar_image': avatars,
            'first_name': first_names,
            'last_name': last_names,
            'password': passwords,
        })

        invalid = []
        too_long_role = ('a' * (ROLE_MAXLENGTH + 5))
        too_long_bio = ('b' * (BIO_MAXLENGTH + 5))
        invalid_email = self._invalid_strings()
        invalid_avatar = self._invalid_strings()
        for i in range(self.size):
            invalid.append({
                'username': '' if i % 2 == 0 else ' ',
                'email': invalid_email[i] if i < len(invalid_email) else 'not-an-email',
                'role': too_long_role,
                'bio': too_long_bio,
                'avatar_image': invalid_avatar[i] if i < len(invalid_avatar) else 'not-a-url',
                'first_name': '',
                'last_name': '',
                'password': '',
            })

        self.gen.save_fixture('model_users_user', valid, tuple(invalid))

    def model_parser_telegram_channel(self) -> None:
        '''
        fixtures for parser.TelegramChannel model
        '''
        channel_ids = self.gen.generate_int(max_len=12, ensure_unique=True)
        titles = self.gen.generate_text(max_len=255)
        usernames = self.gen.generate_text(max_len=255)
        descriptions = self.gen.generate_text(max_len=300)
        participants = self.gen.generate_int(max_len=6)
        parsed_at = self.gen.generate_datetime(rule=None)
        pinned = self.gen.generate_json_object()
        creation_date = self.gen.generate_datetime(rule=None)
        last_messages = self.gen.generate_json_object()
        avg_views = self.gen.generate_int(max_len=6)

        valid = self._compose({
            'channel_id': channel_ids,
            'title': titles,
            'username': usernames,
            'description': descriptions,
            'participants_count': participants,
            'parsed_at': parsed_at,
            'pinned_messages': pinned,
            'creation_date': creation_date,
            'last_messages': last_messages,
            'average_views': avg_views,
        })

        invalid_strs = self._invalid_strings()
        invalid_dt = self._invalid_strings()
        invalid = []
        for i in range(self.size):
            invalid.append({
                'channel_id': invalid_strs[i] if i < len(invalid_strs) else 'abc',
                'title': '',
                'username': None,
                'description': None,
                'participants_count': invalid_strs[i] if i < len(invalid_strs) else 'n/a',
                'parsed_at': invalid_dt[i] if i < len(invalid_dt) else '2020-13-40 99:99',
                'pinned_messages': 'not-json',
                'creation_date': '31-31-2020',
                'last_messages': 'not-json',
                'average_views': 'views',
            })
        self.gen.save_fixture('model_parser_telegram_channel', valid, tuple(invalid))

    def form_user_login(self) -> None:
        usernames = tuple(self._generate_valid_username() for _ in range(self.size))
        passwords = tuple(self._generate_valid_password() for _ in range(self.size))

        for username, password in zip(usernames, passwords):
            self._create_test_user(username, password)

        valid = self._compose({
            'username': usernames,
            'password': passwords,
        })

        invalid = []
        for _ in range(self.size):
            invalid.append({
                'username': '',
                'password': '',
            })
        self.gen.save_fixture('form_user_login', valid, tuple(invalid))

    def form_user_reg(self) -> None:
        """Форма регистрации - генерируем ВАЛИДНЫЕ данные"""
        first_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(8)) for _ in range(self.size))
        last_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(10)) for _ in range(self.size))
        usernames = tuple(self._generate_valid_username() for _ in range(self.size))
        pw = tuple(self._generate_valid_password() for _ in range(self.size))
        emails = tuple(self._generate_valid_email() for _ in range(self.size))
        bios = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(50)) for _ in range(self.size))
        avatars = tuple(self._generate_valid_url() for _ in range(self.size))
        terms_true = self._repeat(True)

        valid = self._compose({
            'first_name': first_names,
            'last_name': last_names,
            'username': usernames,
            'password1': pw,
            'password2': pw,
            'email': emails,
            'bio': bios,
            'terms': terms_true,
            'avatar_image': avatars,
        })

        invalid_email = self._invalid_strings()
        invalid_avatar = self._invalid_strings()
        invalid = []
        for i in range(self.size):
            invalid.append({
                'first_name': '',
                'last_name': '',
                'username': '',
                'password1': 'short',
                'password2': 'different',
                'email': invalid_email[i] if i < len(invalid_email) else 'not-an-email',
                'bio': 'x' * (BIO_MAXLENGTH + 20),
                'terms': False,
                'avatar_image': invalid_avatar[i] if i < len(invalid_avatar) else 'not-a-url',
            })
        self.gen.save_fixture('form_user_reg', valid, tuple(invalid))

    def form_user_update(self) -> None:
        first_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(8)) for _ in range(self.size))
        last_names = tuple(''.join(random.choice(string.ascii_letters) for _ in range(10)) for _ in range(self.size))
        usernames = tuple(self._generate_valid_username() for _ in range(self.size))
        pw = tuple(self._generate_valid_password() for _ in range(self.size))
        emails = tuple(self._generate_valid_email() for _ in range(self.size))
        bios = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(50)) for _ in range(self.size))
        avatars = tuple(self._generate_valid_url() for _ in range(self.size))

        valid = self._compose({
            'first_name': first_names,
            'last_name': last_names,
            'username': usernames,
            'password1': pw,
            'password2': pw,
            'email': emails,
            'bio': bios,
            'avatar_image': avatars,
        })

        invalid_email = self._invalid_strings()
        invalid = []
        for i in range(self.size):
            invalid.append({
                'first_name': '',
                'last_name': '',
                'username': '',
                'password1': 'short',
                'password2': 'short-but-diff',
                'email': invalid_email[i] if i < len(invalid_email) else 'invalid',
                'bio': 'y' * (BIO_MAXLENGTH + 1),
                'avatar_image': 'no-url',
            })
        self.gen.save_fixture('form_user_update', valid, tuple(invalid))

    def form_user_avatar_change(self) -> None:
        avatars = tuple(self._generate_valid_url() for _ in range(self.size))
        valid = self._compose({'avatar_image': avatars})
        invalid = self._compose({'avatar_image': self._invalid_strings()})
        self.gen.save_fixture('form_user_avatar_change', valid, invalid)

    def form_restore_password_request(self) -> None:
        emails = tuple(self._generate_valid_email() for _ in range(self.size))
        valid = self._compose({'email': emails})
        invalid = self._compose({'email': self._invalid_strings()})
        self.gen.save_fixture('form_restore_password_request', valid, invalid)

    def form_restore_password(self) -> None:
        pw = tuple(self._generate_valid_password() for _ in range(self.size))
        valid = self._compose({
            'new_password1': pw,
            'new_password2': pw,
        })
        invalid = self._compose({
            'new_password1': self.gen.generate_text(max_len=10),
            'new_password2': self.gen.generate_text(max_len=12),
        })
        self.gen.save_fixture('form_restore_password', valid, invalid)

    def form_group_create(self) -> None:
        names = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(20)) for _ in range(self.size))
        descriptions = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(50)) for _ in range(self.size))
        images = tuple(self._generate_valid_url() for _ in range(self.size))

        valid = self._compose({
            'name': names,
            'description': descriptions,
            'image_url': images,
        })

        invalid = []
        invalid_img = self._invalid_strings()
        for i in range(self.size):
            invalid.append({
                'name': '',
                'description': 'z' * 1000,
                'image_url': invalid_img[i] if i < len(invalid_img) else 'invalid',
            })
        self.gen.save_fixture('form_group_create', valid, tuple(invalid))

    def form_group_update(self) -> None:
        names = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(20)) for _ in range(self.size))
        descriptions = tuple(''.join(random.choice(string.ascii_letters + ' ') for _ in range(50)) for _ in range(self.size))
        images = tuple(self._generate_valid_url() for _ in range(self.size))

        valid = self._compose({
            'name': names,
            'description': descriptions,
            'image_url': images,
        })

        invalid = []
        for _ in range(self.size):
            invalid.append({
                'name': '',
                'description': '',
                'image_url': 'not-a-url',
            })
        self.gen.save_fixture('form_group_update', valid, tuple(invalid))

    def form_parser_channel_parse(self) -> None:
        """Форма парсинга канала с обязательными полями"""
        identifiers = tuple('@' + ''.join(random.choice(string.ascii_lowercase) for _ in range(15)) for _ in range(self.size))
        raw_ints = self.gen.generate_int(max_len=3)
        limits = tuple(1 + (abs(n) % 20) for n in raw_ints)

        categories = ['Новости и СМИ', 'Юмор и развлечения', 'Технологии', 'Бизнес и стартапы']
        countries = ['Россия', 'США', 'Германия', 'Франция']
        languages = ['Русский', 'Английский', 'Немецкий', 'Французский']

        valid = self._compose({
            'channel_identifier': identifiers,
            'limit': limits,
            'category': tuple(random.choice(categories) for _ in range(self.size)),
            'country': tuple(random.choice(countries) for _ in range(self.size)),
            'language': tuple(random.choice(languages) for _ in range(self.size)),
        })

        invalid_limits = []
        for i in range(self.size):
            invalid_limits.append(0 if i % 2 == 0 else 99)

        invalid = self._compose({
            'channel_identifier': self._repeat(''),
            'limit': tuple(invalid_limits),
            'category': self._repeat(''),
            'country': self._repeat(''),
            'language': self._repeat(''),
        })
        self.gen.save_fixture('form_parser_channel_parse', valid, invalid)

    def generate_all(self) -> None:
        self.model_users_user()
        self.model_parser_telegram_channel()

        self.form_user_login()
        self.form_user_reg()
        self.form_user_update()
        self.form_user_avatar_change()
        self.form_restore_password_request()
        self.form_restore_password()

        self.form_group_create()
        self.form_group_update()

        self.form_parser_channel_parse()
