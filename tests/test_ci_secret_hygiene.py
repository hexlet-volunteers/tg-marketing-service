"""Guards for GitHub Actions secret hygiene (issue #421).

The CI workflows must never reference Telegram credentials and must not
print or publish ``django.log`` / ``errors.log``. The build job must also
keep logging quiet. These regression tests fail loudly if those
protections are removed.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

FORBIDDEN_TELEGRAM_SECRETS = (
    "TELEGRAM_SESSION_STRING",
    "TELEGRAM_API_ID",
    "TELEGRAM_API_HASH",
)
FORBIDDEN_LOG_ARTIFACTS = ("django.log", "errors.log", "upload-artifact")

LOG_LEVEL_PATTERN = re.compile(
    r"^\s*LOG_LEVEL:\s*[\"']?WARNING[\"']?\s*$", re.MULTILINE
)


def _workflow_sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(WORKFLOWS_DIR.glob("*.y*ml"))
    }


def test_workflows_do_not_reference_telegram_secrets() -> None:
    for name, source in _workflow_sources().items():
        for secret in FORBIDDEN_TELEGRAM_SECRETS:
            assert secret not in source, f"{name} must not expose {secret}"


def test_workflows_do_not_print_or_publish_logs() -> None:
    for name, source in _workflow_sources().items():
        for marker in FORBIDDEN_LOG_ARTIFACTS:
            assert marker not in source, (
                f"{name} must not publish or print {marker}"
            )


def test_ci_lowers_log_level_to_warning() -> None:
    source = _workflow_sources()["tests.yml"]
    assert LOG_LEVEL_PATTERN.search(source), (
        "CI must run the build job with LOG_LEVEL=WARNING"
    )
