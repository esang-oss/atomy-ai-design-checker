"""Atomy AI Design Checker FastAPI 앱 엔트리."""
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.score import router as score_router
from src.config.constants import ENVELOPE_VERSION
from src.config.validate_env import validate_env

# backend/ 또는 루트의 .env를 자동 로드
_env_path = Path(__file__).parents[2] / ".env"
load_dotenv(_env_path)

validate_env()

app = FastAPI(
    title="Atomy AI Design Checker",
    description="애터미 패키지 디자인 AI 심사 시스템 — 가이드라인 기반 합격/불합격 판정 및 개선 사항 제공",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(score_router)


@app.get("/health")
def health() -> dict:
    """Railway 헬스체크 엔드포인트."""
    return {
        "data": {"status": "ok", "version": app.version},
        "meta": {"envelope_version": ENVELOPE_VERSION},
    }
