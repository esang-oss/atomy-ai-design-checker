---
name: atomy-ai-design-checker
description: 디자인 분석, 가이드라인 심사, 점수 계산 관련 작업 시 활성화. analysis/guideline/report/auth 도메인 언급 시 사용.
---

# Atomy AI Design Checker 전용 규칙

## 데이터 규칙
- 디자인 이미지는 업로드 직후 임시 저장, 분석 완료 후 결과만 DB 보관
- 점수가 없으면 "데이터 없음" — 0점으로 처리 금지
- 해외법인 사용자의 언어 설정에 따라 피드백 언어를 분기 (한국어/영어)

## 코드 규칙
- 도메인 격리 엄수: `analysis/`는 `report/`를 직접 import 금지 (서비스 레이어 경유)
- Claude Vision API 호출은 반드시 `analysis/` 도메인에서만 수행
- 점수 계산 로직은 `analysis/scorer.py` 한 곳에 집중
- 합격 기준(`SCORE_PASS_THRESHOLD = 70`)은 `constants.py`에서만 참조

## AI 프롬프트 규칙
- 가이드라인 규칙셋은 `guideline/` 도메인에서 로드
- 프롬프트에 반드시 "애터미 디자인 가이드라인 기준으로 평가" 명시
- 응답 포맷: JSON (score, pass, categories, improvements)

## 외부 API 규칙
- Claude Vision API: 타임아웃 60초, 최대 3회 재시도 (`ANALYSIS_TIMEOUT_SEC`, `MAX_ANALYSIS_RETRIES`)
- 이미지 크기 20MB 초과 시 업로드 단계에서 차단 (`MAX_UPLOAD_SIZE_MB`)
- API 키는 반드시 환경변수에서 로드 (`ANTHROPIC_API_KEY`)
