# Atomy AI Design Checker — 프로젝트 계획서

## 목표
애터미 내부 및 해외법인 디자인 담당자가 패키지 디자인 이미지를 업로드하면,
Claude Vision API가 애터미 가이드라인 기준으로 자동 심사하여 합격/불합격 판정,
점수, 그리고 구체적인 개선 사항을 제공하는 웹 서비스.

## 아키텍처
```
디자인 파일 업로드 (Frontend)
  → FastAPI 수신 (Backend)
  → Claude Vision API 호출 (AI 분석)
  → 가이드라인 규칙셋 비교
  → 점수 계산 + 개선 사항 생성
  → 결과 저장 (PostgreSQL)
  → 결과 화면 표시 (Frontend)
```

## 기술 스택
- Frontend: Next.js 14+ (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI, Python 3.13, SQLAlchemy
- AI: Anthropic Claude Vision API (claude-opus-4-8 또는 claude-sonnet-4-6)
- DB: PostgreSQL
- 배포: Railway (backend) + Vercel (frontend)

## DDD 도메인 매핑
| 모듈 | 도메인 | 역할 |
|------|--------|------|
| `backend/src/analysis/` | 분석 | AI 호출, 채점 로직 |
| `backend/src/guideline/` | 가이드라인 | 애터미 규칙 관리 |
| `backend/src/report/` | 리포트 | 결과 저장, 조회 |
| `backend/src/auth/` | 인증 | 사용자 로그인, 권한 |
| `frontend/app/upload/` | 업로드 | 파일 업로드 화면 |
| `frontend/app/result/` | 결과 | 점수·피드백 표시 |

## Phase별 구현 계획

### Phase 1: 기반 구축 (MVP)
- [ ] FastAPI 프로젝트 초기 설정 (라우터, DB 연결)
- [ ] Next.js 프로젝트 초기 설정 (레이아웃, 라우팅)
- [ ] 이미지 업로드 API 엔드포인트 구현
- [ ] Claude Vision API 연동 (단순 분석 테스트)
- [ ] 기본 결과 표시 화면 구현

### Phase 2: 핵심 기능 — 가이드라인 심사
- [ ] 애터미 디자인 가이드라인 규칙셋 정의 (텍스트 프롬프트)
- [ ] 점수 계산 로직 구현 (카테고리별 가중치)
- [ ] 합격/불합격 판정 기준 구현
- [ ] 개선 사항 생성 로직 구현
- [ ] 결과 저장 및 이력 조회 구현

### Phase 3: 사용자 관리 & 배포
- [ ] 사용자 인증 구현 (내부/해외법인 구분)
- [ ] Railway 배포 설정 (backend)
- [ ] Vercel 배포 설정 (frontend)
- [ ] 성능 최적화 및 에러 처리 강화

## 메모리 정책 (ASMR)
- 주요 도메인: analysis / guideline / report / auth
- 예상 주요 메모리:
  - decisions: Claude Vision 프롬프트 설계, 점수 가중치 결정
  - architecture: DB 스키마, API 엔드포인트 설계
  - learnings: Claude Vision API 제한사항, 이미지 포맷 처리
