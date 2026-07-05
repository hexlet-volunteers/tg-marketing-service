from typing import Dict, List, Tuple, Any
import logging

from tests.data_generator import DataGenerator, NUM_OF_FIXTURES

# Avoid importing Django app modules (which may require settings/db) just to get constants.
# Use project defaults, falling back safely if not importable.
from apps.users.models import ROLE_MAXLENGTH, BIO_MAXLENGTH

logger = logging.getLogger(__name__)


class ModelAndFormFixtureGenerator:
    """
    class to actually generate fixtures for forms and models
    why new class and not a script? so that can configure in future
    not all models and forms present, because some of them require foreign key etc.
    in future, need to connect to present DB or make local SQLite, populate it and test via it
    """

    def __init__(self, num: int = NUM_OF_FIXTURES) -> None:
        self.gen = DataGenerator(num)
        self.size = self.gen.data_size

    def _compose(
        self, field_values: Dict[str, Tuple[Any, ...]]
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

    # make invalid data (its only strings, so _invalid_strings)
    def _invalid_strings(self) -> Tuple[str, ...]:
        return self.gen.generate_invalid_data()

    # generate again
    def _repeat(self, value: Any) -> Tuple[Any, ...]:
        return tuple(value for _ in range(self.size))

    # Models
    def model_users_user(self) -> None:
        """
        fixtures for users.User model
        required: username (text, unique, 1-150), email (email, unique, blank allowed but generate), role (text, 1-150)
        optional: first_name (text), last_name (text), bio (text, 1-200), avatar_image (url)
        """
        # usernames unique
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        # emails unique and valid
        emails = self.gen.generate_emails(rule=None)
        # role and bio lengths
        roles = self.gen.generate_text(max_len=ROLE_MAXLENGTH)
        bios = self.gen.generate_text(max_len=BIO_MAXLENGTH)
        # avatar image (URL)
        avatars = self.gen.generate_urls(rule=None)
        # names - simple text
        first_names = self.gen.generate_text(max_len=50)
        last_names = self.gen.generate_text(max_len=50)
        # password placeholder (not hashed; for fixtures only)
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

        # Invalid: empty username, invalid email, too-long role and bio, non-url avatar image
        invalid = []
        too_long_role = "a" * (ROLE_MAXLENGTH + 5)
        too_long_bio = "b" * (BIO_MAXLENGTH + 5)
        invalid_email = self._invalid_strings()
        invalid_avatar = self._invalid_strings()
        for i in range(self.size):
            invalid.append(
                {
                    "username": ""
                    if i % 2 == 0
                    else " ",  # required -> invalid
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
                    "password": "",  # empty password
                }
            )

        self.gen.save_fixture("model_users_user", valid, tuple(invalid))

    def model_parser_telegram_channel(self) -> None:
        """
        fixtures for parser.TelegramChannel model
        required: channel_id (bigint unique), title (text, 1-255), participants_count (int), parsed_at (datetime auto)
        optional: username (text, 0-255, can be blank), description (text), pinned_messages (json), creation_date (datetime),
                  last_messages (json), average_views (int)
        """
        # unique channel ids, up to 12 digits
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

        # invalid set: non-int channel_id, empty title, invalid datetime/json, non-int counts
        invalid_strs = self._invalid_strings()
        invalid_dt = self._invalid_strings()
        invalid = []
        for i in range(self.size):
            invalid.append(
                {
                    "channel_id": invalid_strs[i]
                    if i < len(invalid_strs)
                    else "abc",  # should be int
                    "title": "",  # required -> invalid
                    "username": None,
                    "description": None,
                    "participants_count": invalid_strs[i]
                    if i < len(invalid_strs)
                    else "n/a",  # should be int
                    "parsed_at": invalid_dt[i]
                    if i < len(invalid_dt)
                    else "2020-13-40 99:99",  # invalid dt
                    "pinned_messages": "not-json",
                    "creation_date": "31-31-2020",
                    "last_messages": "not-json",
                    "average_views": "views",
                }
            )
        self.gen.save_fixture(
            "model_parser_telegram_channel", valid, tuple(invalid)
        )

    # Forms
    def form_user_login(self) -> None:
        # username (text), password (text)
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        passwords = self.gen.generate_text(max_len=50)
        valid = self._compose(
            {
                "username": usernames,
                "password": passwords,
            }
        )
        invalid = []
        for _ in range(self.size):
            invalid.append(
                {
                    "username": "",
                    "password": "",
                }
            )
        self.gen.save_fixture("form_user_login", valid, tuple(invalid))

    def form_user_reg(self) -> None:
        # first_name (text), last_name (text), username(text), password1 (text), password2 (text),
        # email (email), bio (text, can be blank), terms (bool), avatar_image (url)
        first_names = self.gen.generate_text(max_len=50)
        last_names = self.gen.generate_text(max_len=50)
        usernames = self.gen.generate_text(max_len=150, ensure_unique=True)
        # keep passwords equal for validity
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
        invalid = []
        for i in range(self.size):
            invalid.append(
                {
                    "first_name": "",
                    "last_name": "",
                    "username": "",
                    "password1": "password123",
                    "password2": "different",  # mismatch
                    "email": invalid_email[i]
                    if i < len(invalid_email)
                    else "not-an-email",
                    "bio": "x" * (BIO_MAXLENGTH + 20),  # too long
                    "terms": False,  # required True
                    "avatar_image": invalid_avatar[i]
                    if i < len(invalid_avatar)
                    else "not-a-url",
                }
            )
        self.gen.save_fixture("form_user_reg", valid, tuple(invalid))

    def form_user_update(self) -> None:
        # mirrors UserUpdateForm fields as defined in forms.py
        # first_name (text), last_name (text), username(text),
        # password1 (text), password2 (text), email (email), bio (text), avatar_image (url)
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
        invalid = []
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
        # avatar_image (url) required=False but provide valid urls
        avatars = self.gen.generate_urls(rule=None)
        valid = self._compose({"avatar_image": avatars})
        invalid = self._compose({"avatar_image": self._invalid_strings()})
        self.gen.save_fixture("form_user_avatar_change", valid, invalid)

    def form_restore_password_request(self) -> None:
        # email (email)
        emails = self.gen.generate_emails(rule=None)
        valid = self._compose({"email": emails})
        invalid = self._compose({"email": self._invalid_strings()})
        self.gen.save_fixture("form_restore_password_request", valid, invalid)

    def form_restore_password(self) -> None:
        # new_password1 (text), new_password2 (text)
        pw = self.gen.generate_text(max_len=50)
        valid = self._compose(
            {
                "new_password1": pw,
                "new_password2": pw,
            }
        )
        invalid = self._compose(
            {
                "new_password1": self.gen.generate_text(max_len=10),  # len 10
                "new_password2": self.gen.generate_text(
                    max_len=12
                ),  # not same len
            }
        )
        self.gen.save_fixture("form_restore_password", valid, invalid)

    def form_group_create(self) -> None:
        # name (text, 1-150), description (text, optional), image_url (url)
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

        invalid = []
        invalid_img = self._invalid_strings()
        for i in range(self.size):
            invalid.append(
                {
                    "name": "",  # required
                    "description": "z"
                    * 1000,  # overly long, tho not really invalid, but assume like 1000 url is not real
                    "image_url": invalid_img[i]
                    if i < len(invalid_img)
                    else "invalid",
                }
            )
        self.gen.save_fixture("form_group_create", valid, tuple(invalid))

    def form_group_update(self) -> None:
        # same fields as create
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

        invalid = []
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
        # channel_identifier (text, 1-255), limit (int, 1-20)
        identifiers = self.gen.generate_text(max_len=255)
        # produce ints using generator and make no bigger than 20
        raw_ints = self.gen.generate_int(max_len=3)
        limits = tuple(1 + (abs(n) % 20) for n in raw_ints)

        valid = self._compose(
            {
                "channel_identifier": identifiers,
                "limit": limits,
            }
        )

        # invalid: empty identifier, limit out of range
        invalid_limits = []
        for i in range(self.size):
            invalid_limits.append(0 if i % 2 == 0 else 99)
        invalid = self._compose(
            {
                "channel_identifier": self._repeat(""),
                "limit": tuple(invalid_limits),
            }
        )
        self.gen.save_fixture("form_parser_channel_parse", valid, invalid)

    # can simply make obj and call this method to get every fixture file
    def generate_all(self) -> None:
        """
        for now only includes forms and models that not require database relations.
        """
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
