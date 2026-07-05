from rstr import xeger
from re import sub
import json
import django.core.validators
from django.core.exceptions import ValidationError
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# generated data is stored as json files in FIXTURES_DIR directory
FIXTURES_DIR_PATH = "tests/fixtures"
DEFAULT_TEXT_LEN = 50
DEFAULT_INT_LEN = 10
NUM_OF_FIXTURES = 10
INVALID_DATA_LEN = 20


class DataValidator:
    @staticmethod
    def validate_json_object(json_obj) -> bool:
        try:
            if isinstance(json_obj, (str, bytes, bytearray)):
                json.loads(json_obj)
            else:
                json.dumps(json_obj)
        except (TypeError, ValueError) as e:
            raise ValidationError(e)
        else:
            return True

    @staticmethod
    def validate_url(url: str) -> bool:
        django.core.validators.URLValidator()(url)
        return True  # URLValidator raises exception, so simply return True

    @staticmethod
    def validate_email(email: str) -> bool:
        django.core.validators.EmailValidator()(email)
        return True  # EmailValidator raises exception, so simply return True

    @staticmethod
    def validate_datetime(value) -> bool:
        # accept datetime objects
        if isinstance(value, datetime):
            return True
        # if not str, then what is it
        if not isinstance(value, str):
            raise ValidationError("Invalid datetime type")
        # all possible formats
        formats = (
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        # if here, then not datetime format - raise validation error
        raise ValidationError("Invalid datetime format")


class DataGenerator:
    """
    class to generate random data (only valid except generate_invalid_data)
    dummy json is cool tho requires internet, faker is too complex

    def f(regex or func to validate):
        regex: check if randomly generated data matches regex
        func: check that randomly generated data is validateable

    output: lists with data_size num of elements
    """

    def __init__(self, num_of_fixtures=NUM_OF_FIXTURES) -> None:
        # how many fixtures to make
        self.data_size = num_of_fixtures
        self.rules = {
            "limited": {
                # for eaxmple https://example.com/image.jpg
                "url": r"(https?:\/\/)(?:www\.)?[A-Za-z0-9-]{2,63}\.[A-Za-z]{2,6}\/[A-Za-z0-9._~-]{3,50}\.(?:apng|avif|gif|jpg|jpeg|jfif|pjp|pjpeg|png|svg|webp|bmp|ico|tiff)",
                "email": r"([-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+)*)@([A-Za-z0-9]([A-Za-z0-9\-]{0,61}[0-9A-Za-z])?\.)*[A-Za-z]{2,}",
                "datetime": r"^(19\d\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])[ T]([0-1][0-9]|2[0-3]):[0-5][0-9]((:[0-5][0-9])?(\.\d{1,6})?)?$",
            },
            "unlimited": {
                "text": r"[\t\n\r -~]",
                "int": r"\d",
            },
            "invalid": r"[\t\n\r -~]",
        }
        """
        rule - how the fixture is generated
        (for example regex)
        validator - how the fixture is validated
        (for example func that receives fixture)
        """
        self.fixtures_generators = {
            "url": {
                "generator": self.generate_urls,
                "rule": self.rules["limited"]["url"],
                "data_type": str,
                "validator": DataValidator.validate_url,
            },
            "email": {
                "generator": self.generate_emails,
                "rule": self.rules["limited"]["email"],
                "data_type": str,
                "validator": DataValidator.validate_email,
            },
            "text": {
                "generator": self.generate_text,
                "rule": self.rules["unlimited"]["text"],
                "data_type": str,
                "validator": None,
            },
            "int": {
                "generator": self.generate_int,
                "rule": self.rules["unlimited"]["int"],
                "data_type": int,
                "validator": None,
            },
            "datetime": {
                "generator": self.generate_datetime,
                "rule": self.rules["limited"]["datetime"],
                "data_type": str,
                "validator": DataValidator.validate_datetime,
            },
            "json": {
                "generator": self.generate_json_object,
                "rule": None,
                "data_type": object,
                "validator": DataValidator.validate_json_object,
            },
            "invalid": {
                "generator": self.generate_invalid_data,
                "rule": self.rules["invalid"],
                "data_type": None,
                "validator": None,  # in future use it for injextions, xss attacks etc
            },
        }

    # max len is for fixtures which len is controlled by changeable code in forms etc.
    # for exmaple email regex has len
    def _generate_data(
        self,
        rgx: str,
        max_len: int = 0,
        data_type=str,
        validator: object = None,
        remove_whitespace: bool = True,
        ensure_unique: bool = False,  # for fields on models that are unique
        max_attempts_multiplier: int = 20,  # just some OK number
    ) -> tuple:
        data = []
        if not isinstance(rgx, str):
            return tuple(data)
        if max_len:
            rgx = f"(?:{rgx}){{1,{max_len}}}"

        attempts = 0
        # avoid not enough generations when validation is strict - simply make more generations
        max_attempts = self.data_size * max_attempts_multiplier
        # some models require unique values, so we make set() for fields with such data
        seen = set() if ensure_unique else None

        while len(data) < self.data_size and attempts < max_attempts:
            attempts += 1
            elem = xeger(rgx)
            if remove_whitespace:
                # only remve edges
                elem = elem.strip()
            try:
                elem = data_type(elem)
            except Exception as e:
                logger.warning(f"Casting to {data_type} failed: {e}")

            if ensure_unique and elem not in seen:
                seen.add(elem)

            valid = True
            if callable(validator):
                try:
                    validator(elem)
                except ValidationError as e:
                    logger.warning(f"Validation by {validator} failed: {e}")
                    valid = False
            if valid:
                data.append(elem)
        return tuple(data)

    # kwargs because there is too many args and just accept all of them
    def generate_urls(
        self, rule: str = None, data_type=str, validator=None, **kwargs
    ) -> tuple:
        # sadly, cannot do generate_urls(self, rule: str=self.fixture_generators),
        # because self is not imported yet
        rule = self.fixtures_generators["url"]["rule"] if rule is None else rule
        return self._generate_data(
            rule, data_type=data_type, validator=validator, **kwargs
        )

    def generate_emails(
        self, rule: str = None, data_type=str, validator=None, **kwargs
    ) -> tuple:
        # ensure uniqueness for models like users.User.email (unique=True)
        rule = (
            self.fixtures_generators["email"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            rule,
            data_type=data_type,
            validator=validator,
            ensure_unique=True,
            **kwargs,
        )

    def generate_text(
        self,
        rule: str = None,
        data_type=str,
        validator=None,
        max_len=DEFAULT_TEXT_LEN,
        **kwargs,
    ) -> tuple:
        # keep whitespace in text
        rule = (
            self.fixtures_generators["text"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            rule,
            max_len=max_len,
            data_type=data_type,
            validator=validator,
            remove_whitespace=False,
            **kwargs,
        )

    def generate_datetime(
        self, rule: str = None, data_type=str, validator=None, **kwargs
    ) -> tuple:
        # by default keep whitespace as-is for datetime strings
        rule = (
            self.fixtures_generators["datetime"]["rule"]
            if rule is None
            else rule
        )
        return self._generate_data(
            rule,
            data_type=data_type,
            validator=validator,
            remove_whitespace=False,
            **kwargs,
        )

    def generate_int(
        self,
        rule: str = None,
        data_type=int,
        validator=None,
        max_len=DEFAULT_INT_LEN,
        **kwargs,
    ) -> tuple:
        rule = self.fixtures_generators["int"]["rule"] if rule is None else rule
        return self._generate_data(
            rule,
            max_len=max_len,
            data_type=data_type,
            validator=validator,
            **kwargs,
        )

    def generate_json_object(
        self, rule: str = None, data_type=object, validator=None, **kwargs
    ) -> tuple:
        # a list of dicts
        if rule is not None:
            ...  # honestly i have no energy for this. regex for json is too big for now

        def rand_str(max_line_len: int = DEFAULT_TEXT_LEN) -> str:
            # random printable string without leading/trailing whitespace
            s = xeger(
                self.rules["unlimited"]["text"]
                + "{1,"
                + str(max_line_len)
                + "}"
            )
            return sub(r"^\s+|\s+$", "", s) or "x"

        # produce a list (not nested) of small dicts per entry
        items = []
        for _ in range(self.data_size):
            list_len = 2
            items.append([{rand_str(): rand_str()} for __ in range(list_len)])
        json_obj = tuple(items)
        if validator:
            # keep only those that pass validator;
            # allow validator to raise ValidationError
            filtered = []
            for obj in json_obj:
                try:
                    if validator(obj):
                        filtered.append(obj)
                except ValidationError:
                    continue
            # if anything passed validator and got to filtered
            if filtered:
                json_obj = tuple(filtered)  # just use it
            # otherwise fill with something
            else:
                json_obj = tuple([[{"x": "y"}]] for _ in range(self.data_size))
        return json_obj

    def generate_invalid_data(self, rule: str = None, max_len=INVALID_DATA_LEN):
        # random data with choices (random)
        # only restriction is data_size
        rule = self.fixtures_generators["invalid"]["rule"] if not rule else rule
        rgx = f"(?:{rule}){{1,{max_len}}}"
        return tuple(xeger(rgx) for _ in range(self.data_size))

    def generate_fixtures(self) -> None:
        """
        save_fixture(FIXTURE_DIR_PATH/fixturename, generate_data, generate_invalid_data)
        -> json file with 2 keys ('valid', 'invalid') each with data_size num of elems
        """
        for name, cfg in self.fixtures_generators.items():
            if name == "invalid":
                # 'invalid' is generated per-file below; no "valid" set for it
                continue
            valid = cfg["generator"](
                rule=cfg.get("rule"),
                data_type=cfg.get("data_type", str),
                validator=cfg.get("validator"),
            )
            self.save_fixture(
                name,
                valid,
                self.generate_invalid_data(rule=self.rules["invalid"]),
            )

    # fixture saved as json file
    def save_fixture(
        self,
        fixture_name: str,
        valid_data,
        invalid_data,
        fixture_path=FIXTURES_DIR_PATH,
    ) -> None:
        data = {
            "valid": valid_data,
            "invalid": invalid_data,
        }
        os.makedirs(fixture_path, exist_ok=True)
        fixture_path = f"{FIXTURES_DIR_PATH}/{fixture_name}.json"
        with open(fixture_path, "w", encoding="utf-8") as f:
            # default=str handles datetime objects
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return None
