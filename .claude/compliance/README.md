# Compliance Rules 소스

이 프로젝트의 컴플라이언스 규칙은 **Compliance Service API** 에서 조회합니다.

- API URL: `COMPLIANCE_API_URL` 환경변수 (`.env` 참조)
- API Key: `COMPLIANCE_API_KEY` 환경변수 (`.env` 참조)
- API 키 발급: `compliance-service/scripts/issue_api_key.py --project atomy-ai-design-checker`

## Fallback

API 미연결 시 `~/.claude/compliance/policy.md` + `checklist.md` 로컬 파일을 사용합니다.
