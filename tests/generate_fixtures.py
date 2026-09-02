import logging
import re
from typing import Any, Dict, List, Tuple

# Avoid importing Django app modules
# (which may which require settings/db) just to get constants.
# Use project defaults, falling back safely if not importable.
from apps.users.constants import BIO_MAXLENGTH, ROLE_MAXLENGTH
from tests.data_generator import NUM_OF_FIXTURES, DataGenerator

logger = logging.getLogger(__name__)


class ModelAndFormFixtureGenerator:
    """
    class to actually generate fixtures for forms and models
    """

    def __init__(self, num: int = NUM_OF_FIXTURES) -> None:
        self.gen = DataGenerator(num)
        self.size = self.gen.data_size

    def _compose(
        self,
        field_values: Dict[str, Tuple[Any, ...]],
    ) -> Tuple[Dict[str, Any], ...]:
        """
        Compose list of dicts from generated data
        """
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

    # make invalid data (it's only strings, so _invalid_strings)
    def _invalid_strings(self) -> Tuple[str, ...]:
        return self.gen.generate_invalid_data()

    # generate again
    def _repeat(self, value: Any) -> Tuple[Any, ...]:
        return tuple(value for _ in range(self.size))

    # Models
    def model_users_user(self) -> None:
        """
        fixtures for users.User model
        """
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        emails = self.gen.generate_emails(rule=None)
        roles = self.gen.generate_text(max_len=ROLE_MAXLENGTH)
        bios = self.gen.generate_text(max_len=BIO_MAXLENGTH)
        avatars = self.gen.generate_urls(rule=None)
        first_names = self.gen.generate_text(max_len=50)
        last_names = self.gen.generate_text(max_len=50)
        passwords = self.gen.generate_text(max_len=50)

        valid = self._compose(
            {
                "username": usernames,
                "email": emails,
                "role": roles,
                "bio": bios,
                "avatar_image": avatars,
                "first_name": first_names,
                "last_name": last_names,
                "password": passwords,
            }
        )

        invalid: List[Dict[str, Any]] = []
        too_long_role = "a" * (ROLE_MAXLENGTH + 5)
        too_long_bio = "b" * (BIO_MAXLENGTH + 5)
        invalid_email = self._invalid_strings()
        invalid_avatar = self._invalid_strings()
        for i in range(self.size):
            invalid.append(
                {
                    "username": "" if i % 2 == 0 else " ",
                    "email": invalid_email[i]
                    if i < len(invalid_email)
                    else "not-an-email",
                    "role": too_long_role,
                    "bio": too_long_bio,
                    "avatar_image": invalid_avatar[i]
                    if i < len(invalid_avatar)
                    else "not-a-url",
                    "first_name": "",
                    "last_name": "",
                    "password": "",
                }
            )

        self.gen.save_fixture("model_users_user", valid, tuple(invalid))

    def model_parser_telegram_channel(self) -> None:
        """
        fixtures for parser.TelegramChannel model
        """
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

        valid = self._compose(
            {
                "channel_id": channel_ids,
                "title": titles,
                "username": usernames,
                "description": descriptions,
                "participants_count": participants,
                "parsed_at": parsed_at,
                "pinned_messages": pinned,
                "creation_date": creation_date,
                "last_messages": last_messages,
                "average_views": avg_views,
            }
        )

        invalid_strs = self._invalid_strings()
        invalid_dt = self._invalid_strings()
        invalid: List[Dict[str, Any]] = []
        for i in range(self.size):
            invalid.append(
                {
                    "channel_id": invalid_strs[i]
                    if i < len(invalid_strs)
                    else "abc",
                    "title": "",
                    "username": None,
                    "description": None,
                    "participants_count": invalid_strs[i]
                    if i < len(invalid_strs)
                    else "n/a",
                    "parsed_at": invalid_dt[i]
                    if i < len(invalid_dt)
                    else "2020-13-40 99:99",
                    "pinned_messages": "not-json",
                    "creation_date": "31-31-2020",
                    "last_messages": "not-json",
                    "average_views": "views",
                }
            )
        self.gen.save_fixture(
            "model_parser_telegram_channel",
            valid,
            tuple(invalid),
        )

    def model_parser_post(self) -> None:
        """
        fixtures for parser.Post model
        """

        msg_ids = self.gen.generate_int(max_len=10, ensure_unique=True)
        views = self.gen.generate_int(max_len=7)
        forwards = self.gen.generate_int(max_len=5)
        comments = self.gen.generate_int(max_len=5)
        fwd_froms = self.gen.generate_int(max_len=10)
        dates = self.gen.generate_datetime(rule=None)
        permalinks = self.gen.generate_urls(rule=None)

        # Генерируем кортежи данных заранее
        all_raw_names_1 = self.gen.generate_text(max_len=10, ensure_unique=True)
        all_raw_names_2 = self.gen.generate_text(max_len=10, ensure_unique=True)

        all_mentions = []
        all_texts = []

        for i in range(self.size):
            # Берем i-й элемент из кортежей, чтобы получить строку
            raw_m1 = all_raw_names_1[i]
            raw_m2 = all_raw_names_2[i]

            # На случай если генератор вернул не строку, а что-то еще
            if not isinstance(raw_m1, str):
                raw_m1 = str(raw_m1)
            if not isinstance(raw_m2, str):
                raw_m2 = str(raw_m2)

            # Очищаем, чтобы регулярка @([\w\.]+) сработала
            m1_clean_text = re.sub(r"[^\w.]", "", raw_m1)
            m2_clean_text = re.sub(r"[^\w.]", "", raw_m2)

            if not m1_clean_text:
                m1_clean_text = "user1"
            if not m2_clean_text:
                m2_clean_text = "user2"

            # Для текста с @
            m1_with_at = f"@{m1_clean_text}"
            m2_with_at = f"@{m2_clean_text}"

            # Для базы без @
            current_mentions = [m1_clean_text, m2_clean_text]

            all_mentions.append(current_mentions)
            all_texts.append(
                f"Important news from {m1_with_at} and {m2_with_at}!"
            )

        valid = self._compose(
            {
                "telegram_message_id": msg_ids,
                "text": tuple(all_texts),
                "published_at": dates,
                "views": views,
                "permalink": permalinks,
                "forwards": forwards,
                "comments_count": comments,
                "fwd_from": fwd_froms,
                "mentions": tuple(all_mentions),
            }
        )

        invalid: List[Dict[str, Any]] = []
        for _ in range(self.size):
            invalid.append(
                {
                    "telegram_message_id": "not-an-id",
                    "text": "",
                    "published_at": "not-a-date",
                    "views": -100,
                    "forwards": -1,
                    "comments_count": -5,
                    "fwd_from": None,
                    "mentions": "not-json",
                }
            )
        self.gen.save_fixture("model_parser_post", valid, tuple(invalid))

    def model_parser_post_reaction(self) -> None:
        """
        fixtures for parser.PostReaction model
        """
        # Исправлено: генерируем плоский список строк, а не список кортежей,
        # чтобы соответствовать ожидаемому типу Dict[str, Any] в моделях
        emojis_raw = ["🔥", "❤️", "👍", "😂"] * (self.size // 4 + 1)
        emojis: Tuple[str, ...] = tuple(emojis_raw[: self.size])

        counts = self.gen.generate_int(max_len=5)

        valid = self._compose(
            {
                "emoji": emojis,
                "count": counts,
            }
        )

        invalid: List[Dict[str, Any]] = []
        for _ in range(self.size):
            invalid.append(
                {
                    "emoji": "",
                    "count": -1,
                }
            )
        self.gen.save_fixture(
            "model_parser_post_reaction", valid, tuple(invalid)
        )

    # Forms
    def form_user_login(self) -> None:
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        passwords = self.gen.generate_text(max_len=50)
        valid = self._compose(
            {
                "username": usernames,
                "password": passwords,
            }
        )
        invalid: List[Dict[str, Any]] = []
        for _ in range(self.size):
            invalid.append(
                {
                    "username": "",
                    "password": "",
                }
            )
        self.gen.save_fixture("form_user_login", valid, tuple(invalid))

    def form_user_reg(self) -> None:
        first_names = self.gen.generate_text(max_len=50)
        last_names = self.gen.generate_text(max_len=50)
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        pw = self.gen.generate_text(max_len=50)
        emails = self.gen.generate_emails(rule=None)
        bios = self.gen.generate_text(max_len=BIO_MAXLENGTH)
        avatars = self.gen.generate_urls(rule=None)
        terms_true = self._repeat(True)

        valid = self._compose(
            {
                "first_name": first_names,
                "last_name": last_names,
                "username": usernames,
                "password1": pw,
                "password2": pw,
                "email": emails,
                "bio": bios,
                "terms": terms_true,
                "avatar_image": avatars,
            }
        )

        invalid_email = self._invalid_strings()
        invalid_avatar = self._invalid_strings()
        invalid: List[Dict[str, Any]] = []
        for i in range(self.size):
            invalid.append(
                {
                    "first_name": "",
                    "last_name": "",
                    "username": "",
                    "password1": "password123",
                    "password2": "different",
                    "email": invalid_email[i]
                    if i < len(invalid_email)
                    else "not-an-email",
                    "bio": "x" * (BIO_MAXLENGTH + 20),
                    "terms": False,
                    "avatar_image": invalid_avatar[i]
                    if i < len(invalid_avatar)
                    else "not-a-url",
                }
            )
        self.gen.save_fixture("form_user_reg", valid, tuple(invalid))

    def form_user_update(self) -> None:
        first_names = self.gen.generate_text(max_len=50)
        last_names = self.gen.generate_text(max_len=50)
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        pw = self.gen.generate_text(max_len=50)
        emails = self.gen.generate_emails(rule=None)
        bios = self.gen.generate_text(max_len=BIO_MAXLENGTH)
        avatars = self.gen.generate_urls(rule=None)

        valid = self._compose(
            {
                "first_name": first_names,
                "last_name": last_names,
                "username": usernames,
                "password1": pw,
                "password2": pw,
                "email": emails,
                "bio": bios,
                "avatar_image": avatars,
            }
        )

        invalid_email = self._invalid_strings()
        invalid: List[Dict[str, Any]] = []
        for i in range(self.size):
            invalid.append(
                {
                    "first_name": "",
                    "last_name": "",
                    "username": "",
                    "password1": "short",
                    "password2": "short-but-diff",
                    "email": invalid_email[i]
                    if i < len(invalid_email)
                    else "invalid",
                    "bio": "y" * (BIO_MAXLENGTH + 1),
                    "avatar_image": "no-url",
                }
            )
        self.gen.save_fixture("form_user_update", valid, tuple(invalid))

    def form_user_avatar_change(self) -> None:
        avatars = self.gen.generate_urls(rule=None)
        valid = self._compose({"avatar_image": avatars})
        invalid = self._compose({"avatar_image": self._invalid_strings()})
        self.gen.save_fixture("form_user_avatar_change", valid, invalid)

    def form_restore_password_request(self) -> None:
        emails = self.gen.generate_emails(rule=None)
        valid = self._compose({"email": emails})
        invalid = self._compose({"email": self._invalid_strings()})
        self.gen.save_fixture("form_restore_password_request", valid, invalid)

    def form_restore_password(self) -> None:
        pw = self.gen.generate_text(max_len=50)
        valid = self._compose(
            {
                "new_password1": pw,
                "new_password2": pw,
            }
        )
        invalid = self._compose(
            {
                "new_password1": self.gen.generate_text(max_len=10),
                "new_password2": self.gen.generate_text(max_len=12),
            }
        )
        self.gen.save_fixture("form_restore_password", valid, invalid)

    def form_group_create(self) -> None:
        names = self.gen.generate_text(max_len=150, ensure_unique=True)
        descriptions = self.gen.generate_text(max_len=200)
        images = self.gen.generate_urls(rule=None)

        valid = self._compose(
            {
                "name": names,
                "description": descriptions,
                "image_url": images,
            }
        )

        invalid: List[Dict[str, Any]] = []
        invalid_img = self._invalid_strings()
        for i in range(self.size):
            invalid.append(
                {
                    "name": "",
                    "description": "z" * 1000,
                    "image_url": invalid_img[i]
                    if i < len(invalid_img)
                    else "invalid",
                }
            )
        self.gen.save_fixture("form_group_create", valid, tuple(invalid))

    def form_group_update(self) -> None:
        names = self.gen.generate_text(max_len=150, ensure_unique=True)
        descriptions = self.gen.generate_text(max_len=200)
        images = self.gen.generate_urls(rule=None)

        valid = self._compose(
            {
                "name": names,
                "description": descriptions,
                "image_url": images,
            }
        )

        invalid: List[Dict[str, Any]] = []
        for _ in range(self.size):
            invalid.append(
                {
                    "name": "",
                    "description": "",
                    "image_url": "not-a-url",
                }
            )
        self.gen.save_fixture("form_group_update", valid, tuple(invalid))

    def form_parser_channel_parse(self) -> None:
        identifiers = self.gen.generate_text(max_len=255)
        raw_ints = self.gen.generate_int(max_len=3)
        limits = tuple(1 + (abs(n) % 20) for n in raw_ints)

        valid = self._compose(
            {
                "channel_identifier": identifiers,
                "limit": limits,
            }
        )

        invalid_limits: List[int] = []
        for i in range(self.size):
            invalid_limits.append(0 if i % 2 == 0 else 99)

        invalid = self._compose(
            {
                "channel_identifier": self._repeat(""),
                "limit": tuple(invalid_limits),
            }
        )
        self.gen.save_fixture("form_parser_channel_parse", valid, invalid)

    def generate_all(self) -> None:
        self.model_users_user()
        self.model_parser_telegram_channel()
        self.model_parser_post()
        self.model_parser_post_reaction()

        self.form_user_login()
        self.form_user_reg()
        self.form_user_update()
        self.form_user_avatar_change()
        self.form_restore_password_request()
        self.form_restore_password()

        self.form_group_create()
        self.form_group_update()

        self.form_parser_channel_parse()
