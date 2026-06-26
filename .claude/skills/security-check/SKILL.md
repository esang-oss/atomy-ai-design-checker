---
name: security-check
description: 결제, 인증, 데이터베이스, 외부 API 연동 코드 작성 시 보안 취약점 점검. payment, auth, login, database, transaction, api_key, webhook, token 키워드가 관련될 때 활성화.
---

# 보안 점검 체크리스트

## API 키 & 인증 정보
- [ ] API 키가 코드에 하드코딩 되어 있지 않은가?
- [ ] .env 파일이 .gitignore에 포함되어 있는가?
- [ ] 인증 토큰의 만료 처리가 되어 있는가?
- [ ] 로그에 API 키나 토큰이 출력되지 않는가?

## 데이터베이스
- [ ] SQL 쿼리에 파라미터 바인딩을 사용하는가? (f-string SQL 금지)
- [ ] DB 트랜잭션이 All or Nothing으로 묶여 있는가?
- [ ] DB 연결이 finally 블록 또는 context manager로 해제되는가?
- [ ] 대량 INSERT 시 배치 처리를 하는가?

## 외부 API 연동
- [ ] API 호출에 타임아웃(timeout)이 설정되어 있는가?
- [ ] Rate Limit 초과 시 대응 로직(sleep/retry)이 있는가?
- [ ] API 응답의 HTTP 상태 코드를 검증하는가?
- [ ] 네트워크 실패 시 재시도(Retry) 로직이 있는가?

## 입력/출력 검증
- [ ] 외부 입력 데이터의 타입과 범위를 검증하는가?
- [ ] 에러 메시지가 내부 시스템 경로나 구조를 노출하지 않는가?
- [ ] 파일 경로 입력 시 Path Traversal 방어가 되어 있는가?

## 에러 응답 보안 (에러 마스킹)
- [ ] 프로덕션 에러 응답에 스택트레이스가 포함되지 않는가?
- [ ] DEBUG 모드에서만 상세 에러를 반환하고, 프로덕션에서는 제너릭 메시지("내부 서버 오류")를 반환하는가?
- [ ] 에러 마스킹 유틸리티(`mask_error()` 등)를 사용하여 환경별 분기하는가?

## SSRF (Server-Side Request Forgery) 방지
- [ ] 서버에서 외부 URL을 fetch할 때 **도메인 화이트리스트**를 적용하는가?
- [ ] 사용자 입력 URL을 서버에서 직접 요청하지 않는가? (프록시 사용 또는 화이트리스트 검증)
- [ ] 내부 네트워크 주소(127.0.0.1, 10.x.x.x, 172.16-31.x.x, 192.168.x.x)를 차단하는가?

## 프론트엔드 XSS 방지
- [ ] `dangerouslySetInnerHTML` 사용 시 반드시 DOMPurify로 새니타이징하는가?
- [ ] SafeHTML 래퍼 컴포넌트를 통해서만 HTML을 렌더링하는가?

## 파일 업로드 보안
- [ ] 업로드 파일명에 **UUID 프리픽스**를 부여하여 경로 순회 공격을 방지하는가?
- [ ] 파일 MIME 타입을 Content-Type 헤더가 아닌 **매직 넘버(파일 시그니처)** 로 검증하는가?
- [ ] 업로드 파일 크기 제한이 설정되어 있는가?

## 의존성 보안
- [ ] 인증/보안 핵심 라이브러리(auth, JWT, OAuth)는 **stable 버전**만 사용하는가? (beta/rc 금지)
- [ ] lockfile(package-lock.json, yarn.lock)이 커밋되어 빌드 재현성을 보장하는가?
- [ ] 보안 취약점이 알려진 의존성이 없는가? (`npm audit`, `pip audit`)
