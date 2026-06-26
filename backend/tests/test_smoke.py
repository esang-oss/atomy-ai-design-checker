"""스모크 테스트 — 프로젝트 기본 임포트와 상수 검증."""


def test_constants_exist():
    """중앙 상수 파일이 정상 임포트되는지 확인한다."""
    from src.config.constants import MAX_ANALYSIS_RETRIES, SCORE_PASS_THRESHOLD
    assert MAX_ANALYSIS_RETRIES > 0
    assert SCORE_PASS_THRESHOLD == 70


def test_validate_env_function_exists():
    """환경변수 검증 함수가 존재하는지 확인한다."""
    from src.config.validate_env import validate_env
    assert callable(validate_env)
