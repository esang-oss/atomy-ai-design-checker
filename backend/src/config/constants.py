"""프로젝트 전역 상수 — 매직 넘버 대신 이 파일의 상수를 사용하세요."""

# API 응답 캐시
DEFAULT_CACHE_MAX_AGE_SEC = 600  # 10분

# Rate limiting
DEFAULT_RATE_LIMIT_PER_MIN = 60

# 요청 본문 크기 제한
MAX_PAYLOAD_BYTES = 256 * 1024  # 256 KB
MAX_FIELD_STRING_LENGTH = 8000

# 응답 envelope
ENVELOPE_VERSION = 1

# 디자인 파일 업로드
MAX_UPLOAD_SIZE_MB = 20
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "ai", "psd"}

# AI 분석
ANALYSIS_TIMEOUT_SEC = 60  # Claude Vision 호출 타임아웃
MAX_ANALYSIS_RETRIES = 5

# 심사 점수
SCORE_PASS_THRESHOLD = 70  # 70점 이상 합격
SCORE_MAX = 100
