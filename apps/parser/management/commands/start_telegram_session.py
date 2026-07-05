"""
Custom action for "parser" application.
This action creates and stores in .env a TelegramClient StringSession.
StringSession is a serialized TelegramClient session, essentially a session.

Prerequisites:
- Telegram account with registered app
- Connection to the internet

How to:
    uv run python manage.py set_telegram_session

Variables:
    ENV_SESSION_KEY = TelegramClient Session key name in .env
    ENV_API_ID_KEY = Telegram app api_id key name in .env
    ENV_API_HASH_KEY = Telegram app api_hash key name in .env
    ENV_PHONE_KEY = Telegram account phone key name in .env
    ENV_PASSWORD_KEY = Telegram account password key name in .env

P.S.:
    This class can be used at any time and does not require starting up anything
"""

import asyncio
from typing import Optional, Callable, Any
from pathlib import Path
from operator import itemgetter
from os import getenv
from dotenv import load_dotenv, find_dotenv, set_key
from django.core.management.base import BaseCommand, CommandError, CommandParser
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import rpcerrorlist

ENV_STRING_SESSION_KEY = "TELEGRAM_SESSION_STRING"
ENV_API_ID_KEY = "TELEGRAM_API_ID"
ENV_API_HASH_KEY = "TELEGRAM_API_HASH"
ENV_PASSWORD_KEY = "TELEGRAM_PASSWORD"
ENV_PHONE_KEY = "PHONE"
ENV_PATH = "/"


class Command(BaseCommand):
    """Django management (manage.py) command to generate and
    save to .env a TelegramClient StringSession.

    Prerequisites:
    - .env and provided data that in total is enough for starting TelegramClient
    - User (or workaround) who will paste code,
    which will be sent to a Telegram account, which waas registered with the  passed phone

    Features:
    - Provided data can be automatically be loaded from .env,
    if not passed via cli (cli is prioritised)
    - Raises CommandError
    - Safely disconnects from the client after successfull set of TelegramClient StringSession

    How to and when:
    1. uv run python manage.py set_telegram_session
    when: when everything is present in .env or user will provide data via cli in same terminal
    2. uv run python manage.py set_telegram_session --force
    when: StringSession is in .env, but want to regenerate it with data in .env
    3. uv run python manage.py set_telegram_session --string-session <value>
    when: set new StringSession
    4. uv run python manage.py set_telegram_session --api-id 123 --api-hash 123abc
    when: use passed data and what data is not passed should be loaded from .env
    4. uv run python manage.py set_telegram_session --api-id 123 --api-hash 123abc --phone +71235456789
    when: use passed data and what data is not passed should be loaded from .env
    5. uv run python manage.py set_telegram_session chilling
    when: u r tired and want to receive argparse.ArgumentError
    """

    def __init__(self, *args, **kwargs):
        """Initialize command state:
        1. init super (required for backward compatibility with BaseCommand)
        2. create fields
        """

        super().__init__(*args, **kwargs)
        # I didnt know about this so added it
        self.string_session: Optional[str] = None
        self.api_id: Optional[int] = None
        self.api_hash: Optional[str] = None
        self.phone: Optional[str] = None
        self.password: Optional[str] = None
        self.env_path: Optional[str] = None

    # argparse arguments
    def add_arguments(self, parser: CommandParser) -> None:
        """Define CLI options

        Options:
        - --force: to regenerate StringSession even if it is already in .env
        - --string-session: provide StringSession and set it in .env for future use (override)
        - --api-id: override TELEGRAM_API_ID in .env
        - --api-hash: override TELEGRAM_API_HAS in .env
        - --phone: override PHONE in .env
        - --env-path: override path to .env
        """
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate Telegram StringSession",
        )
        parser.add_argument(
            "--string-session",
            dest="string_session",
            type=str,
            help="Set this string as a Telegram StringSession",
        )
        parser.add_argument(
            "--api-id",
            dest="api_id",
            type=int,  # ensure int at parse time
            help=f"Override {ENV_API_ID_KEY}",
        )
        parser.add_argument(
            "--api-hash",
            dest="api_hash",
            type=str,
            help=f"Override {ENV_API_HASH_KEY}",
        )
        parser.add_argument(
            "--password",
            dest="password",
            type=str,
            help=f"Override {ENV_PASSWORD_KEY}",
        )
        parser.add_argument(
            "--phone", dest="phone", type=str, help=f"Override {ENV_PHONE_KEY}"
        )
        parser.add_argument(
            "--env-path",
            dest="env_path",
            type=str,
            help="Set this string as a path to .env",
        )
        # is it needed?
        # return super().add_arguments(parser)

        # **options instead of **kwargs because of legacy

    def handle(self, *args, **options: dict[str, str]) -> None:
        """Entrypoint: resolve input, authenticate in Telegram, save it.

        Structure:
        - Resolve .env path
        - If --string-session is provided, set it in TELEGRAM_STRING_SESSION
        - If --string-session is not provided, generate it on provided and
        existing in .env data
        - If type of provided data already exists in .env,
        then ask for overwrite permission (default is yes)
        - Run Telethon authentication in cli and generate StringSession
        - Set StringSession in .env

        Check of arguments:
        - if argument was provided in command
        - then validate it
        -- if validation is passed, set it in .env
        - else use what is present in .env

        Raises:
            PermissionError: permission denied to .env file error
            OSError: error while writing to .env
            CommandError: other errors
            Exception: this is bad, phone me if it happens: +79856455594
        """
        # Get all key (option) arguments. cool, huh?
        force, string_session, api_id, api_hash, password, phone, env_path = (
            itemgetter(
                "force",
                "string_session",
                "api_id",
                "api_hash",
                "password",
                "phone",
                "env_path",
            )(options)
        )

        # Set env path
        if env_path:
            p = Path(env_path)
            env_file = p if p.suffix == ".env" else (p / ".env")
            if not env_file.is_file():
                raise CommandError(f".env was not found at: {env_file}")
            self.env_path = str(env_file)
        else:
            try:
                self.env_path = find_dotenv(
                    raise_error_if_not_found=True, usecwd=True
                )
            except Exception as e:
                raise CommandError(f".env was not found: {e}") from e

        load_dotenv(self.env_path)

        # Set inputs
        self.replace_env_data(
            "string_session", ENV_STRING_SESSION_KEY, string_session, str, force
        )
        self.replace_env_data("api_id", ENV_API_ID_KEY, api_id, int, force)
        self.replace_env_data(
            "api_hash", ENV_API_HASH_KEY, api_hash, str, force
        )
        self.replace_env_data(
            "password", ENV_PASSWORD_KEY, password, str, force
        )
        self.replace_env_data("phone", ENV_PHONE_KEY, phone, str, force)

        # If user provided a new StringSession via CLI, use it and start TelegramClient
        if string_session:
            self.ensure_required(["api_id", "api_hash"])
            self.set_string_session(ENV_STRING_SESSION_KEY)
            asyncio.run(self.start_telegram_session())
            return

        # If session exists in env and not forcing regeneration, start with it
        if self.string_session and not force:
            self.ensure_required(["api_id", "api_hash"])
            asyncio.run(self.start_telegram_session())
            return

        # No StringSession present and is --force if happen here, so get StringSession and start TelegramClient
        self.ensure_required(["api_id", "api_hash", "phone"])
        asyncio.run(self.get_string_session())
        self.set_string_session(ENV_STRING_SESSION_KEY)
        asyncio.run(self.start_telegram_session())

    def replace_env_data(
        self,
        att_name: str,
        env_key: str,
        value: Any,
        to_type: Callable[[Any], Any] = str,
        force: bool = False,
        remove_whitespace: bool = True,
    ) -> None:
        # Normalize incoming value (CLI value)
        if isinstance(value, str) and remove_whitespace:
            value = value.replace(" ", "")

        # If no CLI value, use env and stop
        if value is None or (isinstance(value, str) and value == ""):
            setattr(self, att_name, getenv(env_key))
            return None

        # Convert provided value
        try:
            converted = value if isinstance(value, to_type) else to_type(value)
        except (ValueError, TypeError) as e:
            raise CommandError(
                f"Error while converting {value} of {type(value)} to {to_type}: {e}"
            ) from e

        # If env already has value, ask if replace (unless --force)
        if getenv(env_key) and not force:
            answer = (
                input(
                    f"{env_key} is present. Do you want to replace it? [y/N] "
                )
                .strip()
                .lower()
            )
            if answer != "y":
                setattr(self, att_name, getenv(env_key))
                return None

        # --force is if here, so set provided data
        setattr(self, att_name, converted)

    def ensure_required(self, required: list[str]) -> None:
        """Ensure required attributes are present after resolution."""
        missing = [name for name in required if not getattr(self, name)]
        if missing:
            raise CommandError(
                f"Missing required data: {', '.join(missing)}. Please add it in .env or via -- (e.g. --{missing[0]}) in command"
            )

    async def get_string_session(self) -> None:
        """Authentucate in TelegramClient and save StringSession in self.string_session.

        Raises:
            OSError: if disconnect error occurs
            CommandError: other errors
        """
        # Build TelegramClient
        try:
            client = TelegramClient(StringSession(), self.api_id, self.api_hash)
        except ValueError as e:
            raise CommandError(
                f"api_id, api_hash and phone are required to generate StringSession: {e}"
            ) from e
        try:
            # Use the resolved password (CLI or .env), not getenv('PASSWORD')
            await client.start(phone=self.phone, password=self.password)
        except Exception as e:
            raise CommandError(f"Failed to generate StringSession: {e}") from e

        # save StringSession
        try:
            self.string_session = client.session.save()
        except Exception as e:
            raise CommandError(f"Failed to save StringSession: {e}") from e
        finally:
            try:
                await client.disconnect()
            except Exception as e:
                raise OSError(
                    f"Error while disconnecting TelegramClient: {e}"
                ) from e

    def set_string_session(self, string_session_key: str) -> None:
        """Set the generated StringSession in .env.

        Args:
            string_session_key: StringSession key name in .env

        Raises:

        """
        # Sei StringSession
        try:
            set_key(self.env_path, string_session_key, self.string_session)
        except ValueError as e:
            raise CommandError(
                f" Not enough data provided for generating StringSession: {e}"
            ) from e
        except PermissionError as e:
            raise
        except OSError as e:
            raise

    async def start_telegram_session(self) -> None:
        """Start TelegramClient session using resolved StringSession and API creds."""
        # Use resolved values
        client = TelegramClient(
            StringSession(self.string_session), self.api_id, self.api_hash
        )
        try:
            await client.connect()
            if not await client.is_user_authorized():
                # Try to login if we have phone/password (fallback to env for convenience)
                phone = self.phone or getenv(ENV_PHONE_KEY)
                password = self.password or getenv(ENV_PASSWORD_KEY)
                try:
                    await client.start(phone=phone, password=password)
                except ValueError as e:
                    if not phone:
                        raise CommandError(
                            f"Phone not passed to client: {e}\nPass it via --phone."
                        ) from e
                    elif not password:
                        raise CommandError(
                            f"Password not passed to client: {e}\nPass it via --password."
                        ) from e
                    raise CommandError(
                        f"Phone and password not passed to client: {e}\nPass them via --password and --phone."
                    ) from e
                except rpcerrorlist.PasswordHashInvalidError as e:
                    raise CommandError(
                        f"Wrong password. Please check for typos. Quotation marks ' or \" are not needed."
                    )
                # Set StrinGseeion
                self.string_session = client.session.save()
                set_key(
                    self.env_path, ENV_STRING_SESSION_KEY, self.string_session
                )
                self.stdout.write(
                    "Telegram session authorized and updated in .env."
                )
            user_ = await client.get_me()
            self.stdout.write(
                f"Telegram session is active. Logged in as: {getattr(user_, 'username', None) or user_.id}"
            )
        except Exception as e:
            raise CommandError(f"This is bad: {e}") from e

        try:
            await client.disconnect()
        except OSError as e:
            raise CommandError(
                f"Error while disconnecting from Telegram client: {e}"
            ) from e
