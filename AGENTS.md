---
user_level: intermediate
compliance: required
---

# Atomy AI Design Checker

AI 기반 애터미 패키지 디자인 합격/불합격 심사 시스템.
내부 및 해외법인 디자인 담당자가 작업한 패키지 디자인을 업로드하면,
애터미 가이드라인 기준으로 점수와 개선 사항을 제공합니다.

## 대화 스타일

- 전문 용어를 쓰되, 처음 나올 때 괄호로 쉬운 설명을 병기하세요
- 결정이 필요할 때는 선택지 + 장단점을 제시하세요
- 역제안을 먼저 하되, 기술적 이유를 간단히 덧붙이세요

## 기본 정보
- **언어:** Python 3.13 (backend), TypeScript (frontend)
- **패키지 관리:** pip (backend), npm (frontend)
- **테스트:** pytest (backend), vitest (frontend)
- **린트:** ruff (backend), eslint (frontend)

## 기술 스택
- Frontend: Next.js (파일 업로드, 결과 시각화)
- Backend: FastAPI + Python (AI 분석 처리)
- AI: Claude Vision API (Anthropic) — 디자인 이미지 분석
- DB: PostgreSQL (분석 결과, 사용자 정보)
- 배포: Railway (backend) + Vercel (frontend)

## 핵심 명령어
- 백엔드 실행: `cd backend && uvicorn src.main:app --reload`
- 프론트엔드 실행: `cd frontend && npm run dev`
- 백엔드 테스트: `cd backend && pytest`
- 프론트엔드 테스트: `cd frontend && npm test`
- 백엔드 린트: `cd backend && ruff check .`
- 프론트엔드 린트: `cd frontend && npm run lint`

## 모노레포 구조
```
atomy-ai-design-checker/
  frontend/         ← Next.js (업로드·결과 화면)
  backend/          ← FastAPI Python (AI 분석 처리)
  docs/             ← 계획서, 맥락, 체크리스트
  scripts/          ← 유틸리티 스크립트
```

## DDD 도메인 (backend)
- `src/analysis/` — 디자인 분석 도메인 (AI 호출, 점수 계산)
- `src/guideline/` — 애터미 가이드라인 관리 도메인
- `src/report/` — 심사 결과 리포트 도메인
- `src/auth/` — 사용자 인증 도메인 (내부/해외법인)

## API 키 목록 (.env)
- `ANTHROPIC_API_KEY`: Claude Vision API 호출
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `COMPLIANCE_API_KEY`: 컴플라이언스 감사 API

## 코드 원칙
1. 항상 한글로 주석 작성
2. 에러 처리는 try-except/try-catch 필수
3. 데이터 없으면 "데이터 없음" — 절대 추측 금지
4. API 키는 .env 전용, 하드코딩 금지
5. 함수명은 동사+명사 형태 (예: analyze_design, calculate_score)
6. 하나의 세션 = 하나의 도메인

## 작업 전 필수
1. `docs/plan.md` → `docs/checklist.md` → `docs/context.md` 순서로 읽기
2. `/rpi [작업내용]` 으로 시작

## 컴플라이언스

이 프로젝트는 **조직 업무 프로젝트** 입니다 (`compliance: required`).
- **규칙 소스**: Compliance Service API (`COMPLIANCE_API_URL` 환경변수)
- `/handoff` 시 `compliance-reviewer` 에이전트가 API 모드로 자동 감사를 수행합니다.
- **Fallback**: API 미연결 시 `~/.claude/compliance/policy.md` 사용
- **감사 로그**: `.claude/memory/compliance-audit/SESSION-{N}.md`

## 메모리 시스템 (ASMR v3.0 — 3-Tier)
- **Hot** (`docs/context.md`): 최근 3세션 압축 요약, 매 세션 자동 로드
- **Warm** (`.claude/memory/`): 활성 메모리 50개 이하
- **Cold** (`.claude/memory/archive/`): 종료된 Phase, 10세션 미참조 메모리
- `/handoff` 시 자동 Update/Extend/Derive + 강등/승격/배치 병합 수행
- 메모리 카테고리: decisions / architecture / bugs / learnings
