import json
import logging
import os
from datetime import datetime
from re import sub
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, cast

import django.core.validators
from django.core.exceptions import ValidationError
from rstr import xeger

logger = logging.getLogger(__name__)

FIXTURES_DIR_PATH = "tests/fixtures"
DEFAULT_TEXT_LEN = 50
DEFAULT_INT_LEN = 10
NUM_OF_FIXTURES = 10
INVALID_DATA_LEN = 20


class DataValidator:
    @staticmethod
    def validate_json_object(json_obj: Any) -> bool:
        try:
            if isinstance(json_obj, (str, bytes, bytearray)):
                json.loads(json_obj)
            else:
                json.dumps(json_obj)
        except (TypeError, ValueError) as e:
            raise ValidationError(str(e))
        else:
            return True

    @staticmethod
    def validate_url(url: str) -> bool:
        django.core.validators.URLValidator()(url)
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        django.core.validators.EmailValidator()(email)
        return True

    @staticmethod
    def validate_datetime(value: Any) -> bool:
        if isinstance(value, datetime):
            return True
        if not isinstance(value, str):
            raise ValidationError("Invalid datetime type")

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
        raise ValidationError("Invalid datetime format")


class DataGenerator:
    def __init__(self, num_of_fixtures: int = NUM_OF_FIXTURES) -> None:
        self.data_size = num_of_fixtures

        self.rule_url: str = (
            r"(https?:\/\/)(?:www\.)?[A-Za-z0-9-]{2,63}\.[A-Za-z]{2,6}\/"
            r"[A-Za-z0-9._~-]{3,50}\.(?:apng|avif|gif|jpg|jpeg|jfif|pjp|pjpeg|png|svg|webp|bmp|ico|tiff)"
        )
        self.rule_email: str = (
            r"([-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]+)*)@"
            r"([A-Za-z0-9]([A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)*[A-Za-z]{2,}"
        )
        self.rule_datetime: str = (
            r"^(19\d\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
            r"[ T]([0-1][0-9]|2[0-3]):[0-5][0-9]((:[0-5][0-9])?(\.\d{1,6})?)?$"
        )
        self.rule_text: str = r"[\t\n\r -~]"
        self.rule_int: str = r"\d"
        self.rule_invalid: str = r"[\t\n\r -~]"

        self.fixtures_generators: Dict[str, Dict[str, Any]] = {
            "url": {
                "generator": self.generate_urls,
                "rule": self.rule_url,
                "data_type": str,
                "validator": DataValidator.validate_url,
            },
            "email": {
                "generator": self.generate_emails,
                "rule": self.rule_email,
                "data_type": str,
                "validator": DataValidator.validate_email,
            },
            "text": {
                "generator": self.generate_text,
                "rule": self.rule_text,
                "data_type": str,
                "validator": None,
            },
            "int": {
                "generator": self.generate_int,
                "rule": self.rule_int,
                "data_type": int,
                "validator": None,
            },
            "datetime": {
                "generator": self.generate_datetime,
                "rule": self.rule_datetime,
                "data_type": str,
                "validator": DataValidator.validate_datetime,
            },
            "json": {
                "generator": self.generate_json_object,
                "rule": None,
                "data_type": Any,
                "validator": DataValidator.validate_json_object,
            },
            "invalid": {
                "generator": self.generate_invalid_data,
                "rule": self.rule_invalid,
                "data_type": None,
                "validator": None,
            },
        }

    def _generate_data(
        self,
        rgx: str,
        max_len: int = 0,
        data_type: Any = str,
        validator: Optional[Callable[[Any], bool]] = None,
        remove_whitespace: bool = True,
        ensure_unique: bool = False,
        max_attempts_multiplier: int = 20,
    ) -> Tuple[Any, ...]:
        data: List[Any] = []
        if not isinstance(rgx, str):
            return tuple(data)
        if max_len:
            rgx = f"(?:{rgx}){{1,{max_len}}}"

        attempts = 0
        max_attempts = self.data_size * max_attempts_multiplier
        seen: Optional[Set[Any]] = set() if ensure_unique else None

        while len(data) < self.data_size and attempts < max_attempts:
            attempts += 1
            elem = xeger(rgx)
            if remove_whitespace:
                elem = elem.strip()
            try:
                elem = data_type(elem)
            except Exception as e:
                logger.warning(f"Casting to {data_type} failed: {e}")

            if ensure_unique and seen is not None:
                if elem in seen:
                    continue
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

    def generate_urls(
        self,
        rule: Optional[str] = None,
        data_type: Any = str,
        validator: Optional[Callable] = None,
        **kwargs,
    ) -> Tuple[Any, ...]:
        rule_val = (
            self.fixtures_generators["url"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            cast(str, rule_val),
            data_type=data_type,
            validator=validator,
            **kwargs,
        )

    def generate_emails(
        self,
        rule: Optional[str] = None,
        data_type: Any = str,
        validator: Optional[Callable] = None,
        **kwargs,
    ) -> Tuple[Any, ...]:
        rule_val = (
            self.fixtures_generators["email"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            cast(str, rule_val),
            data_type=data_type,
            validator=validator,
            ensure_unique=True,
            **kwargs,
        )

    def generate_text(
        self,
        rule: Optional[str] = None,
        data_type: Any = str,
        validator: Optional[Callable] = None,
        max_len: int = DEFAULT_TEXT_LEN,
        **kwargs,
    ) -> Tuple[Any, ...]:
        rule_val = (
            self.fixtures_generators["text"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            cast(str, rule_val),
            max_len=max_len,
            data_type=data_type,
            validator=validator,
            remove_whitespace=False,
            **kwargs,
        )

    def generate_datetime(
        self,
        rule: Optional[str] = None,
        data_type: Any = str,
        validator: Optional[Callable] = None,
        **kwargs,
    ) -> Tuple[Any, ...]:
        rule_val = (
            self.fixtures_generators["datetime"]["rule"]
            if rule is None
            else rule
        )
        return self._generate_data(
            cast(str, rule_val),
            data_type=data_type,
            validator=validator,
            remove_whitespace=False,
            **kwargs,
        )

    def generate_int(
        self,
        rule: Optional[str] = None,
        data_type: Any = int,
        validator: Optional[Callable] = None,
        max_len: int = DEFAULT_INT_LEN,
        **kwargs,
    ) -> Tuple[Any, ...]:
        rule_val = (
            self.fixtures_generators["int"]["rule"] if rule is None else rule
        )
        return self._generate_data(
            cast(str, rule_val),
            max_len=max_len,
            data_type=data_type,
            validator=validator,
            **kwargs,
        )

    def generate_json_object(
        self,
        rule: Optional[str] = None,
        data_type: Any = Any,
        validator: Optional[Callable] = None,
        **kwargs,
    ) -> Tuple[Any, ...]:
        def rand_str(max_line_len: int = DEFAULT_TEXT_LEN) -> str:
            s = xeger(self.rule_text + "{1," + str(max_line_len) + "}")
            return sub(r"^\s+|\s+$", "", s) or "x"

        items: List[List[Dict[str, str]]] = []
        for _ in range(self.data_size):
            list_len = 2
            items.append([{rand_str(): rand_str()} for __ in range(list_len)])

        json_obj_list = items
        if validator:
            filtered = []
            for obj in json_obj_list:
                try:
                    if validator(obj):
                        filtered.append(obj)
                except ValidationError:
                    continue
            json_obj_list = (
                filtered if filtered else [[{"x": "y"}]] * self.data_size
            )

        return tuple(json_obj_list)

    def generate_invalid_data(
        self, rule: Optional[str] = None, max_len: int = INVALID_DATA_LEN
    ) -> Tuple[str, ...]:
        rule_val = (
            self.fixtures_generators["invalid"]["rule"]
            if rule is None
            else rule
        )
        rgx = f"(?:{cast(str, rule_val)}){{1,{max_len}}}"
        return tuple(xeger(rgx) for _ in range(self.data_size))

    def generate_fixtures(self) -> None:
        for name, cfg in self.fixtures_generators.items():
            if name == "invalid":
                continue

            gen_func = cast(Callable[..., Tuple[Any, ...]], cfg["generator"])
            rule_val = cfg.get("rule")
            dt_type = cfg.get("data_type", str)
            val_func = cfg.get("validator")

            valid = gen_func(
                rule=rule_val,
                data_type=dt_type,
                validator=val_func,
            )
            self.save_fixture(
                name, valid, self.generate_invalid_data(rule=self.rule_invalid)
            )

    def save_fixture(
        self,
        fixture_name: str,
        valid_data: Any,
        invalid_data: Any,
        fixture_path: str = FIXTURES_DIR_PATH,
    ) -> None:
        data = {"valid": valid_data, "invalid": invalid_data}
        os.makedirs(fixture_path, exist_ok=True)
        full_path = f"{fixture_path}/{fixture_name}.json"
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    from tests.generate_fixtures import ModelAndFormFixtureGenerator

    print("Начинаю генерацию фикстур...")
    generator = ModelAndFormFixtureGenerator()
    generator.generate_all()
    print("Готово! Проверь папку tests/fixtures")
