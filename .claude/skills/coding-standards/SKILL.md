---
name: coding-standards
description: 코드 작성 시 참조할 기본 코딩 규칙. 파일 생성, 함수 작성, 에러 처리, 데이터 검증 등 모든 코딩 작업에 적용.
---

# 공통 코딩 표준 규칙

## 에러 처리
- 모든 외부 API 호출은 try-except로 감싼다
- except 블록에서는 반드시 에러를 로그에 기록한다 (logger.error)
- 빈 except (bare except)는 절대 사용하지 않는다
- 사용자에게 보여주는 에러 메시지는 한글로 작성한다

## 데이터 검증
- 외부에서 받은 데이터는 반드시 타입과 범위를 검증한다
- None/Null 체크를 함수 시작 부분에서 먼저 수행한다
- 데이터가 없으면 추측하지 말고 "데이터 없음(N/A)"으로 표기한다
- 숫자 데이터는 float/int 변환 시 예외 처리를 포함한다

## 보안
- API 키는 절대 코드에 하드코딩하지 않는다 (.env + python-dotenv 사용)
- 사용자 입력은 반드시 sanitize한다
- SQL 쿼리는 반드시 파라미터 바인딩을 사용한다 (f-string 금지)
- 로그에 API 키나 비밀값을 출력하지 않는다

## 파일/함수 규칙
- 하나의 파일은 하나의 책임(도메인)만 갖는다
- 함수는 50줄을 넘지 않도록 노력한다. **200줄을 초과하면 반드시 분리한다**
- 함수명은 동사+명사 형태로 짓는다 (예: fetch_stock_data, calculate_score)
- 주석은 한글로 작성한다
- 매직 넘버는 상수로 정의한다
- 도메인 상수(언어 코드, 파일 크기 제한, 재시도 횟수 등)는 **Single Source of Truth 파일**에 집중 관리한다 (예: `config/limits.ts`, `config/constants.py`)

## TypeScript 전용 규칙
- `any` 타입 사용을 금지한다. `unknown` + 타입 가드로 대체한다
- `parseInt()`는 반드시 기수(radix)를 명시한다 (예: `parseInt(value, 10)`)

## 에러 처리 (심화)
- 빈 catch 블록(`catch {}`, `catch { return null }`)은 절대 금지한다. 최소한 `logger.error()`를 호출한다
- 프로덕션 에러 응답은 **에러 마스킹**을 적용한다 — DEBUG 모드에서만 상세 메시지, 프로덕션에서는 제너릭 메시지 반환

## 환경변수
- 환경변수에 `|| 'http://localhost:...'` 같은 폴백을 사용하지 않는다
- 필수 환경변수는 앱 시작 시 검증하고, 누락 시 **즉시 실패(fail-fast)** 한다
- `validateEnv()` 유틸리티로 시작 시점에 일괄 검증한다

## 비동기/동시성
- 반복문(for/forEach) 안에서 개별 API/DB 호출을 하지 않는다. **배치(bulk) API를 사용한다**
- `Promise.all()` 사용 시 반드시 **동시성 제한(concurrency limit)** 을 설정한다 (예: p-limit, Promise.allSettled + chunk)

## 데이터 직렬화
- DB JSON 컬럼은 **저장 시 1회만 직렬화, 조회 시 1회만 파싱**한다. 이중 인코딩(`JSON.stringify(JSON.stringify(...))`)을 절대 하지 않는다

## 로깅
- print() 대신 logging 모듈을 사용한다
- 로그 레벨을 적절히 구분한다 (DEBUG, INFO, WARNING, ERROR)
- 중요한 작업의 시작/완료/실패를 로그에 남긴다
- 프론트/백엔드 각각 **단일 로거 유틸리티**를 사용한다 (console.log, log_to_file 등 혼재 금지)
