"""앱 시작 시 필수 환경변수 검증 — 누락 시 즉시 실패(fail-fast)."""
import os
import sys

REQUIRED_VARS: list[tuple[str, str]] = [
    ("ANTHROPIC_API_KEY", "Claude Vision API 키"),
]

OPTIONAL_VARS_WITH_DEFAULT: list[tuple[str, str, str]] = [
    ("LOG_LEVEL", "INFO", "로그 레벨"),
    ("RATE_LIMIT_PER_MIN", "60", "분당 요청 제한"),
]


def validate_env() -> None:
    """필수 환경변수가 모두 설정되어 있는지 검증한다."""
    missing = [
        f"  - {name}: {desc}"
        for name, desc in REQUIRED_VARS
        if not os.getenv(name)
    ]
    if missing:
        print("❌ 필수 환경변수가 누락되었습니다:", file=sys.stderr)
        print("\n".join(missing), file=sys.stderr)
        print("\n.env.example을 참고하여 .env 파일을 설정하세요.", file=sys.stderr)
        sys.exit(1)

    for name, default, _desc in OPTIONAL_VARS_WITH_DEFAULT:
        if not os.getenv(name):
            os.environ[name] = default
