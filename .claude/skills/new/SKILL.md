---
name: new
description: /new — 새 프로젝트 부트스트랩
metadata:
  short-description: /new — 새 프로젝트 부트스트랩
---

<!--
generated-by: atomy-toolkit codex-adapter
source: _global-toolkit/core/new.yaml
generated-at: 2026-06-02T06:24:10.418188+00:00
transformations: ['frontmatter_codex']
-->

# /new — 새 프로젝트 부트스트랩

> 사용법: `/new [프로젝트에 대한 간단한 설명]`
> 예시: `/new 아토미 제품 정보를 기반으로 숏폼 영상을 자동 생성하는 도구`

---

## ━━━ PHASE 0: 시작 선언 ━━━

다음 메시지를 출력하세요:

```
🚀 새 프로젝트를 만들어 드릴게요!
입력하신 설명: "$ARGUMENTS"

제가 먼저 분석해서 제안서를 보여드릴게요.
마음에 드시면 "좋아", 바꾸고 싶으면 말씀해주세요.
잠시만요...
```

---

## ━━━ PHASE 0.5: Pre-diagnosis 판정 ━━━

PHASE 1 AI 진단 **직전**, `$ARGUMENTS` 품질을 체크:

**트리거 조건 (OR):**
- 전체 길이 ≤20자
- 명사만 있음 (동사·형용사 없음, 예: "가계부", "대시보드", "쇼핑몰")
- 모호한 단어 1~2개만 (예: "AI 앱", "자동화 도구")

트리거되면 **PHASE 1 실행 전**에 Pre-diagnosis brainstorming 을 선행:

```
🚀 새 프로젝트를 만들어 드릴게요!
입력: "{$ARGUMENTS}"

음, 조금 더 여쭤봐도 될까요? 기본 정보 2~3개만 확인할게요.

(질문 1/3) 누가 쓸 건가요?
  (A) 나 혼자 — 로컬에서 돌리는 개인용
  (B) 우리 집/팀 — 2~5명이 공유
  (C) 외부 공개 — 남들도 쓸 수 있는 웹 서비스
```

2~3 질문으로 다음을 수집:
1. 사용자 규모 (혼자/팀/외부)
2. 핵심 기능 한 줄 (동사 + 명사 형태로)
3. (선택) 화면이 필요한지 / CLI 로 충분한지

수집 완료 후 수집된 정보를 합쳐서 PHASE 1 AI 진단으로 진행. AI 진단의 복합 태그 분류 및 자동 추측은 **수집된 답변을 포함한 확장 입력**을 기반으로 수행.

**트리거되지 않으면 (> 20자 + 동사 포함):** 바로 PHASE 1 진행, 이 단계 스킵.

---

## ━━━ PHASE 1: AI 진단 ━━━

$ARGUMENTS를 분석하여 다음을 자동 추측하세요. **사용자에게 질문하지 마세요.**

### 1-A. 복합 태그 분류

설명에서 다음 태그를 **복수** 추출하세요:

| 태그 | 키워드 예시 |
|------|-------------|
| `분석` | 분석, 통계, 데이터, 추이, 비교, 집계, 리포트 |
| `자동화` | 자동, 봇, 스크래핑, 발송, 생성, 변환, 배치, 크롤링 |
| `서비스` | 예약, 주문, 게시판, 관리, 접속, 로그인, 회원, 신청 |
| `시각화` | 그래프, 차트, 대시보드, 보고서, 화면, 표시, 보여주다 |

예: "매출 분석을 자동으로 수행" → `[분석, 자동화]`

### 1-B. 자동 추측

| 항목 | 추측 기준 | 기본값 |
|------|-----------|--------|
| **프로젝트 폴더명** | 설명에서 추론 (예: "매출 분석" → `sales-analyzer`) | 설명 기반 |
| **화면 필요 여부** | `시각화` 태그 있음, "보여주다/접속/화면" → Y | N |
| **사용 규모** | "나/혼자" → 소규모, "팀/부서" → 중규모, "고객/서비스" → 대규모 | 소규모 |
| **배포 방식** | 소규모 → 로컬, 중규모 이상 → 배포 | 로컬 |
| **조직 업무** | "회사/부서/업무/사내/아토미" → Y | N |
| **프로젝트 구조** | 화면 Y + 중규모 이상 → 분리, 그 외 → 단일 | 단일 |

추측에 실패한 항목(판단 불가)은 PHASE 2 제안서에서 "⚠️ 골라주세요" 로 표시합니다.

### 1-C. user_level 1차 추측

| 신호 | 판정 |
|------|------|
| 전문 용어 2개 이상 (API, DB, FastAPI, Next.js, Docker, PostgreSQL, REST, GraphQL, CI/CD, 모노레포, ORM 등) | `advanced` (잠정) |
| 전문 용어 1개 또는 애매 | `intermediate` (잠정) |
| 전문 용어 없음 | `beginner` (잠정) |

### 1-D. 제안서 톤 결정

| user_level (잠정) | 제안서 톤 |
|-------------------|-----------|
| `beginner` | 쉬운 말 + 일상 비유 |
| `intermediate` | 쉬운 말 + 괄호에 전문 용어 |
| `advanced` | 전문 용어 사용, 비유 생략 |

PHASE 1의 결과는 사용자에게 출력하지 않습니다. 바로 PHASE 1.5로 넘어가세요.

---

## ━━━ PHASE 1.5: Brainstorming Fallback 판정 ━━━

PHASE 1 AI 진단 **직후**, 다음 두 조건을 순서대로 평가:

### 조건 1. 서브시스템 ≥3개 (Decompose 제안)

PHASE 1-A 에서 추출한 복합 태그 + `$ARGUMENTS` 의 명사구를 분석하여 **독립 서브시스템**을 식별:

- 식별 기준: 태그 3개 이상 AND 서로 다른 목적의 명사가 3개 이상 (예: "채팅 + 결제 + 분석")
- 트리거 시 다음 출력:
```
📋 들어보니 이 프로젝트 안에 독립적인 세 덩어리가 있어요:

  1. {서브시스템 1} — {한 줄 설명}
  2. {서브시스템 2} — {한 줄 설명}
  3. {서브시스템 3} — {한 줄 설명}

세 개를 한 프로젝트에 넣으면 작업 분해가 흐려져요. 어떻게 할까요?

  (A) 셋 다 한 프로젝트로 (모노레포) — 이유 알려주세요
  (B) 셋을 별도 프로젝트로 분리 — 각자 /new 실행
  (C) 하나만 먼저 만들기 — 어떤 것?
       (1) 첫 번째 부터 (2) 두 번째 부터 (3) 세 번째 부터
```

응답 처리:
- A → 이유를 받은 후 PHASE 2 제안서 진행 (모노레포 구조 반영)
- B → "알겠습니다. 각 프로젝트를 `/new` 로 따로 부트스트랩해주세요" 출력 후 종료
- C → 선택한 서브시스템만 남긴 $ARGUMENTS 로 PHASE 1 재실행

### 조건 2. 판단 불가 ≥2개 (Targeted brainstorming)

PHASE 1-B 자동 추측에서 `⚠️ 골라주세요` 로 표시될 예정인 항목 수를 사전 카운트. 2개 이상이면 PHASE 2 제안서 **출력 전**에 판단 불가 항목들만 brainstorming 루프로 선행 해소:

```
📋 몇 가지만 먼저 여쭤볼게요 (AI 추측 신뢰도가 낮은 부분).

(질문 1/{N}) {해당 항목명 — 쉬운 말}
  (A) {선택지 1} — {장점}
  (B) {선택지 2} — {장점}
  (C) {선택지 3} — {장점}
```

N 개 질문 전부 답변 받은 후 PHASE 2 진행.

### 조건 없음 (skip)

위 두 조건 모두 해당 없으면 PHASE 2 로 바로 진행 (기존 동작).

---

## ━━━ PHASE 2: 제안서 출력 ━━━

PHASE 1의 진단 결과를 바탕으로 제안서를 출력하세요.
**톤은 1-D에서 결정한 user_level에 따라 자동 조절합니다.**

### 제안서 포맷

```
📋 이렇게 만들면 어떨까요?

🎯 프로젝트: {폴더명}
📊 유형: {복합 태그를 user_level 톤에 맞게 표현}

━━━ 1. {화면 관련 결정} ━━━

{추측 결과를 user_level 톤으로 설명}

  👉 추천: {추천 옵션}
  
  💡 다른 방법도 있어요:
     • {대안 1} — 장점: ... / 단점: ...
     • {대안 2} — 장점: ... / 단점: ...

━━━ 2. 프로젝트 구조 ━━━

{구조 설명을 user_level 톤으로}

  👉 추천: {추천}
  💡 다른 방법: ...

━━━ 3. 사용 범위 ━━━

  👉 추천: {추측 결과}
  💡 다른 선택: ...

━━━ 4. 조직 업무 여부 ━━━

  👉 추천: {추측 결과}
  💡 {반대 경우 안내}

━━━━━━━━━━━━━━━━━━
👉 마음에 드시면 "좋아"
👉 바꾸고 싶은 부분이 있으면 번호로 말씀해주세요 (예: "2번 바꿔줘")
👉 잘 모르겠는 부분이 있으면 물어보셔도 돼요
```

### 톤별 용어 매핑 (제안서 작성 시 참조)

| 기술 개념 | beginner | intermediate | advanced |
|-----------|----------|--------------|----------|
| Frontend | 보여주는 부분 | 보여주는 부분(프론트엔드) | Frontend |
| Backend | 처리하는 부분 | 처리하는 부분(백엔드) | Backend |
| 분리 구조 | 홀이랑 주방을 따로 두는 구조 | 분리 구조(모노레포) | 모노레포 |
| 단일 구조 | 한 덩어리로 만들기 | 단일 구조 | 단일 앱 |
| 배포 | 인터넷에 올려서 다른 사람도 접속 가능하게 | 배포(서버에 올림) | 배포 (Railway/Vercel) |
| API | 프로그램끼리 대화하는 통로 | API(데이터 주고받는 통로) | REST API |
| 데이터베이스 | 데이터 저장소 | 데이터베이스(DB) | PostgreSQL |
| 환경변수 | 비밀번호 같은 걸 안전하게 보관하는 곳 | 환경변수(.env 파일) | .env |

### 추측 실패 항목 처리

판단 불가 항목은 제안서 해당 섹션에서:

```
  ⚠️ 이 부분은 잘 모르겠어요 — 골라주세요:
     (A) {선택지 1} — {설명}
     (B) {선택지 2} — {설명}
```

---

## ━━━ PHASE 3: 사용자 수정 + user_level 확정 ━━━

### 반응 패턴 처리

사용자의 반응을 다음 3가지 패턴으로 분류하여 처리하세요:

**패턴 1: 승인 ("좋아" / "시작" / "ok" / "ㅇㅇ")**
→ 바로 PHASE 4(자동 실행)로 진행

**패턴 2: 번호 지정 수정 ("2번 바꿔줘" / "2번 한 덩어리로")**
→ 해당 섹션만 수정 반영
→ 다른 섹션에 연쇄 영향이 있으면 알림:

```
✅ {N}번 수정했어요: {변경 내용 요약}

⚠️ 참고: {연쇄 영향 설명, 있을 때만}

나머지는 그대로 유지합니다. 이대로 진행할까요?
```

**패턴 3: 질문 / "잘 모르겠어" (Item brainstorming)**

→ 해당 항목만 brainstorming 루프로 전환. **다음 규칙 필수:**

1. **한 번에 한 질문** — 복수 질문 금지. 항목이 크면 분해해서 메시지 여러 번
2. **A/B/C 포맷 필수** — open-ended 금지 (user_level 무관)
3. **2-3 접근법 + trade-off** — 각 선택지에 장단점 1줄씩
4. **user_level 톤 적용** — Step 0 에서 감지한 `user_level` 을 메시지에 반영

예시:
```
━━━ 2. 프로젝트 구조 ━━━

🤔 "잘 모르겠어" 라고 하셨으니 차근차근 볼게요.

(질문 1/?) 앞으로 프론트엔드와 백엔드를 나눠서 쓸 일이 있을 것 같아요?

  (A) 아니, 웹 페이지 하나 + 뒤에서 돌아가는 로직이 한 덩어리면 됨
      → 단일 구조 (빠르게 만들기 좋음)
  (B) 나중에 모바일 앱도 붙일 수 있어
      → 분리 구조 (API 공유 가능)
  (C) 솔직히 지금은 모르겠음
      → 일단 단일로 가고, 나중에 필요할 때 분리 (가장 일반적)
```

답변 후 해당 섹션만 업데이트, 나머지 제안서 섹션 유지.

**패턴 4: 전체 거부 ("이거 아냐" / "다시" / "전부 다 별로")**

→ 기존 제안서 버리고 **Full brainstorming 루프** 진입:

1. 질문을 5~8개 순차 진행 (패턴 3 와 동일 규칙):
   1. 프로젝트의 한 줄 목적
   2. 사용자 (나/팀/외부)
   3. 화면 필요 여부
   4. 주요 도메인 3개 이내
   5. 외부 API 의존 여부
   6. 배포 방식 (로컬/서버)
   7. (조직 업무일 경우) 조직 내부용 여부
2. 마지막 질문 답변 후 **요약 제안서 1회 출력** (기존 PHASE 2 포맷 재사용)
3. 요약 제안서에 사용자 최종 승인 받으면 PHASE 4 진입

### user_level 2차 확정

제안서에 대한 사용자 반응에서 user_level을 확정합니다:

| 반응 신호 | 조정 |
|-----------|------|
| 전문 용어로 수정 요청 ("모노레포 말고 단일 앱으로", "FastAPI 빼고 Flask로") | 상향 |
| "잘 모르겠어" / 비유로 질문 / 단순 번호만 지정 | 하향 |
| "좋아" (수정 없이 승인) | 잠정 유지 |

확정된 user_level은 PHASE 4에서 CLAUDE.md 생성 시 기록합니다.

### 수정 루프

수정이 끝날 때마다 "이대로 진행할까요?" 로 재확인합니다.
사용자가 승인하면 PHASE 4로 넘어갑니다.

---

## ━━━ PHASE 4: 자동 실행 ━━━

승인된 Todo를 **순서대로** 실행하세요. 각 태스크 완료 시 체크 표시를 출력하세요.

### 실행 원칙
- Atomy Toolkit 경로: `$env:USERPROFILE\atomy-toolkit\_atomy-toolkit\`
- 프로젝트 생성 경로: `$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\`
- Windows 경로이므로 Bash 명령어는 PowerShell 문법 사용
- 파일 복사 후 반드시 내용을 프로젝트에 맞게 수정할 것 (템플릿 그대로 두지 않음)

### Runtime path contract (cross-OS)
- Windows installer runtime root: `$env:USERPROFILE\atomy-toolkit\_atomy-toolkit`
- macOS/Linux installer runtime root: `$HOME/atomy-toolkit/AtomyToolkit`
- New project root: `$ATOMY_TOOLKIT_WORKSPACE/projects/[folder]` if set, otherwise `$HOME/atomy-toolkit/projects/[folder]`
- Use platform-native copy syntax and path separators. PowerShell examples below are pseudo-code on macOS/Linux.
- If `atomy-toolkit` CLI is available, prefer it over hardcoded template paths:

```text
atomy-toolkit project-rules "[project-root]" --toolkit-root "[runtime-root]" --user-level "[confirmed_user_level]"
```

This command MUST be run for every new project, regardless of selected coding tool or IDE. It creates or preserves all three rule files: `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.

### T00.5: 텔레메트리 첫 실행 동의 (opt-in, 로컬 전용)

**텔레메트리 첫 실행 동의 (opt-in, 로컬 전용):** 새 프로젝트 부트스트랩 시 1회만 묻습니다. 거절도 기록되어 다시 묻지 않습니다.

```python
import sys; sys.path.insert(0, '.claude/lib')
from atomy_toolkit.telemetry import needs_consent_prompt, apply_consent
if needs_consent_prompt():
    # 사용자에게 1회 질문: "익명 로컬 사용 통계를 남길까요? (로컬에만 저장, 언제든 telemetry off)"
    # 응답을 accepted(bool) 로 받아 기록 (거절도 기록 → 재질문 안 함):
    apply_consent(accepted=accepted)
```

### T01: Atomy Toolkit 복사 (Bash 사용)

```text
# OS별 runtime root / project root 를 먼저 확정
# Windows: $toolkitRoot = "$env:USERPROFILE\atomy-toolkit\_atomy-toolkit"
# macOS/Linux: $toolkitRoot = "$HOME/atomy-toolkit/AtomyToolkit"
# project root: $projectRoot = "$HOME/atomy-toolkit/projects/[폴더명]"

# Atomy Toolkit .claude 폴더 복사
Copy-Item -Recurse "$toolkitRoot\.claude" "$projectRoot\.claude"

# docs 폴더 생성
New-Item -ItemType Directory -Path "$projectRoot\docs" -Force
New-Item -ItemType Directory -Path "$projectRoot\src" -Force
```

### T01.5: 메모리 디렉토리 초기화 (ASMR v3.1 — mempalace 통합)

```text
# Warm tier — 메모리 카테고리 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\decisions" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\architecture" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\bugs" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\learnings" -Force

# Knowledge Fabric — 그래프 + 데이터소스 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\graph\glossary" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\graph\sources" -Force

# Cold tier — 아카이브 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\archive\decisions" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\archive\architecture" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\archive\bugs" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\archive\learnings" -Force
```

`_index.md` 초기 파일을 생성하세요:

```markdown
# Memory Index
> 최종 업데이트: [생성일] (세션 0)
> Warm 메모리: 0개 (active: 0, superseded: 0)
> Cold 아카이브: 0개

## 카테고리별 목록
### decisions/ (Warm: 0건, Cold: 0건)
### architecture/ (Warm: 0건, Cold: 0건)
### bugs/ (Warm: 0건, Cold: 0건)
### learnings/ (Warm: 0건, Cold: 0건)

## 도메인별 태그 색인

## 참조 추적
| ID | 마지막 참조 세션 | 비활성 세션 수 |
|----|-----------------|--------------|
```

`_archive_index.md` 초기 파일도 생성하세요:

```markdown
# Archive Index (Cold Tier)
> 최종 업데이트: [생성일] (세션 0)
> 총 아카이브: 0개

## 카테고리별 목록
### decisions/ (0건)
### architecture/ (0건)
### bugs/ (0건)
### learnings/ (0건)

## 도메인별 태그 색인 (Cold)
```

`graph_meta.yaml` 초기 파일도 생성하세요:

```yaml
version: "2.0.0"
namespace:
  org: "[조직명]"
  dept: "[부서명]"
  user: "[사용자명]"
  project: "[프로젝트명]"
settings:
  auto_link_glossary: true
  max_graph_nodes: 500
  orphan_warning: true
harness:
  registered_at: "[생성일]"
```

### T01.6: recurring-mistakes.md 템플릿 생성

`.claude\memory\learnings\recurring-mistakes.md` 를 다음 내용으로 생성:

```markdown
---
id: LEARN-RECURRING
category: learning
title: 반복 실수 로그 (복리 학습)
tags: [meta, mistakes, compound-learning]
status: active
project: [프로젝트명]
---

# 반복 실수 로그

> 보리스 원칙: "같은 실수를 반복하지 말 것."
> 버그·테스트 실패·린트 실패·Verification Gate 실패가 발생할 때마다 /handoff 가 이 파일에 1행 이상 추가하도록 강제합니다.

| 날짜 | 도메인 | 실수 | 원인 | 재발 방지책 |
|------|--------|------|------|-------------|
```

### T01.8.5: memtemple vault + wing 자동 부트스트랩

`atomy-toolkit` CLI 가 PATH 에 있으면 두 명령을 자동 호출합니다:
- `atomy-toolkit memtemple init-vault` — 전역 vault root (`~/.memtemple/` + `.memtemple_version`) 박음 (idempotent, 1회만 실효).
- `atomy-toolkit memtemple init` (Tier 1 자동 선택) — 현 cwd 의 wing (`~/.memtemple/<basename>/`) 박음.

```text
if (Get-Command atomy-toolkit -ErrorAction SilentlyContinue) {
    & atomy-toolkit memtemple init-vault
    # Tier 1 (Layer 1, v1 기본) 자동 선택
    "1" | & atomy-toolkit memtemple init
    Write-Host "✓ memtemple vault + wing 박힘 — 첫 /handoff 부터 sessions/docs/decisions 자동 mining"
} else {
    Write-Host "⚠ atomy-toolkit 미설치 — memtemple vault 부트스트랩 skip"
    Write-Host "  수동 설치 후: atomy-toolkit memtemple init-vault; atomy-toolkit memtemple init"
}
```

> 두 명령 모두 idempotent — 이미 박혀있으면 noop. v1.x-A spec: `docs/specs/2026-05-20-memtemple-vault-bootstrap.md`.

### T01.8.7: Cross-tool project rules 부트스트랩 (필수)

**user_level persistence:** `templates/CLAUDE.md.template` 와 `templates/GEMINI.md.template` 의 `{{USER_LEVEL}}` placeholder 는 PHASE 3 에서 확정된 `confirmed_user_level` 로 치환한다. `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 모두 YAML frontmatter `user_level: {confirmed_user_level}` 를 가져야 한다.

선택한 coding tool/IDE 와 무관하게 프로젝트 루트에 세 파일을 모두 생성한다. Codex-only, Claude-only, Antigravity-only, 교차 사용, 기존 사용 경험이 있는 환경 모두 같은 규칙을 적용한다.

```text
if (Get-Command atomy-toolkit -ErrorAction SilentlyContinue) {
    atomy-toolkit project-rules "$projectRoot" --toolkit-root "$toolkitRoot" --user-level "$confirmed_user_level"
} else {
    # CLI 를 찾지 못하는 경우에만 템플릿을 직접 렌더링한다.
    # CLAUDE.md 는 templates/CLAUDE.md.template 기반.
    # AGENTS.md 와 GEMINI.md 는 templates/GEMINI.md.template 기반이며 byte-equal mirror.
}
```

검증:
- `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 가 모두 존재해야 한다.
- `AGENTS.md` 와 `GEMINI.md` 는 byte-equal 이어야 한다.
- 세 파일 모두 `{{USER_LEVEL}}` placeholder 가 남아 있으면 실패로 본다.

### T01.9: vibe-sunsang `.md` 풀 동봉 안내 (Task 9, AC-9, D-006)

`atomy-toolkit install` 의 단계 6 (`_run_stage_6_vibe_sunsang`) 이 본 프로젝트의 `.claude/skills/vibe-sunsang*` 폴더 6개 (index + 5 sub-skill SKILL.md) 를 자동 복사합니다 — plugin marketplace 의존 제거, air-gapped 환경 호환.

```text
# 복사 결과 확인 (install 후)
Get-ChildItem .claude\skills | Where-Object { $_.Name -like "vibe-sunsang*" } | Select-Object Name
# 예상 출력:
#   vibe-sunsang
#   vibe-sunsang-growth
#   vibe-sunsang-knowledge
#   vibe-sunsang-mentor
#   vibe-sunsang-onboard
#   vibe-sunsang-retro
```

`--no-vibe-sunsang` 플래그로 동봉을 skip 할 수 있습니다 (예: 라이선스 이슈 또는 사용자가 자체 plugin 사용 중).

### T02~T03: docs 템플릿 & .gitignore 생성
기존과 동일하게 docs/plan.md, context.md, checklist.md 템플릿과 .gitignore를 생성.
`.gitignore` 에는 `.env`, `.env.local`, `.env.*.local` 이 반드시 포함되어야 합니다. 단, `.env.example` 은 추적 가능해야 하므로 `.env.*` 전체 패턴은 사용하지 마세요.

### T03.1: Toolkit `.env` to project `.env` idempotent seed

Use the toolkit runtime root `.env` as the first seed source for each new project `.env`. Process/user environment variables are fallback only.

Hard rules:
- Never `Copy-Item` or full-copy a `.env` file.
- If the project `.env` does not exist, create it.
- If the project `.env` already exists, preserve it and upsert only managed variable lines.
- Keep unrelated user-owned variables intact. If the same managed key already exists, replace that key with the toolkit-managed value.
- Never write real secret values to `.env.example`.
- Write `.claude/bootstrap/env-seeded.json` with variable names only.
- Installer, cascade, and update payloads must never overwrite toolkit `.env`.

```text
$projectRoot = "$env:USERPROFILE\atomy-toolkit\projects\[folder-name]"
$toolkitRoot = "$env:USERPROFILE\atomy-toolkit\_atomy-toolkit"
$toolkitEnvFile = Join-Path $toolkitRoot ".env"
$envExample = Join-Path $projectRoot ".env.example"
$gitignore = Join-Path $projectRoot ".gitignore"

# .env.example stores placeholders only. Never write real API keys here.
if (-not (Test-Path -LiteralPath $envExample)) {
    @"
# === Atomy Toolkit environment ===
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash

# Compliance Service / MCP
COMPLIANCE_MCP_URL=https://compliance-service-production-5355.up.railway.app/mcp/
COMPLIANCE_API_URL=https://compliance-service-production-5355.up.railway.app
COMPLIANCE_API_KEY=
"@ | Set-Content -LiteralPath $envExample -Encoding UTF8
}

# .env is ignored, while .env.example remains trackable.
if (-not (Test-Path -LiteralPath $gitignore)) {
    New-Item -ItemType File -Path $gitignore -Force | Out-Null
}
$gitignoreText = Get-Content -LiteralPath $gitignore -Raw
foreach ($pattern in @(".env", ".env.local", ".env.*.local")) {
    if ($gitignoreText -notmatch "(?m)^$([regex]::Escape($pattern))$") {
        Add-Content -LiteralPath $gitignore -Value $pattern
    }
}

if (Get-Command atomy-toolkit -ErrorAction SilentlyContinue) {
    atomy-toolkit setup project-env --project-root "$projectRoot" --toolkit-env-file "$toolkitEnvFile" --sentinel
} else {
    Write-Host "env seed skipped: atomy-toolkit CLI not found. Fill .env from .env.example manually."
}
```

### T02.5: docs/specs/ 폴더 + spec 템플릿 (SDD)

`docs\specs\` 폴더를 생성하고, `docs\specs\_TEMPLATE.md` 를 다음 내용으로 생성:

```markdown
# [기능명] — Spec

> SDD (Specification-Driven Development) 기반 기능 스펙.
> 신규 기능 구현 전에 작성하여 방향성을 고정합니다. `/rpi` 가 신규 기능 요청 시 이 템플릿 복사를 제안합니다.

## 1. 문제 정의
[어떤 문제를 해결하는가? 왜 지금 필요한가?]

## 2. 사용자 스토리
- As a [역할], I want [행동] so that [가치].

## 3. 검토된 접근법
> Brainstorm 모드 결과를 기록. 각 접근법에 장단점 + 선택/탈락 사유 1줄.

| 접근법 | 장점 | 단점 | 선택? |
|--------|------|------|-------|
| A. ... | ... | ... | ✅ 선택 — 이유: ... |
| B. ... | ... | ... | ❌ 탈락 — 이유: ... |

## 4. 입·출력 계약
- **입력**: [형식, 필수 필드, 범위]
- **출력**: [형식, 성공/실패 응답]
- **부작용**: [DB 쓰기, 외부 호출 등]

## 5. 비기능 요구
- 성능: [응답시간/처리량 목표]
- 보안: [인증/권한/암호화 요구]
- 관측성: [로그·메트릭 항목]

## 6. 엣지 케이스
- [케이스 1]
- [케이스 2]

## 7. 수용 기준 (Acceptance Criteria)
- [ ] AC-1: [검증 가능한 조건]
- [ ] AC-2: [검증 가능한 조건]

## 8. 범위 외 (Non-Goals)
- [명시적으로 포함하지 않는 것]
```

### T03.5: 조직 프로젝트 컴플라이언스 셋업 (인터뷰에서 조직 업무 Y 선택 시만)

> **v2.2 변경**: 로컬 policy.md 복사 방식 → Compliance Service API 포인터 방식으로 전환.
> 서비스 장애 시 `~/.claude/compliance/policy.md` 로컬 fallback 은 여전히 유효.

```text
# 프로젝트 로컬 compliance 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\compliance" -Force

# 감사 로그 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\.claude\memory\compliance-audit" -Force
```

`.claude\compliance\README.md` 포인터 파일을 생성하세요:

```markdown
# Compliance Rules 소스

이 프로젝트의 컴플라이언스 규칙은 **Compliance Service API** 에서 조회합니다.

- API URL: `COMPLIANCE_API_URL` 환경변수 (`.env` 참조)
- API Key: `COMPLIANCE_API_KEY` 환경변수 (`.env` 참조)
- API 키 발급: `compliance-service/scripts/issue_api_key.py --project [프로젝트명]`

## Fallback

API 미연결 시 `~/.claude/compliance/policy.md` + `checklist.md` 로컬 파일을 사용합니다.
```

`.env.example` 에 다음 항목을 추가하세요:

```
# === Compliance API (조직 컴플라이언스 감사) ===
COMPLIANCE_MCP_URL=https://compliance-service-production-5355.up.railway.app/mcp/
COMPLIANCE_API_URL=https://compliance-service-production-5355.up.railway.app
COMPLIANCE_API_KEY=
```

추가로 생성되는 `CLAUDE.md` 최상단에 다음 플래그를 반드시 포함하세요:

```yaml
---
compliance: required
---
```

그리고 `CLAUDE.md` 본문에 "## 컴플라이언스" 섹션을 추가:
- 이 프로젝트는 **조직 업무 프로젝트** 입니다 (`compliance: required`).
- **규칙 소스**: Compliance Service API (`COMPLIANCE_API_URL` 환경변수)
- `/handoff` 시 `compliance-reviewer` 에이전트가 API 모드로 자동 감사를 수행합니다.
- **Fallback**: API 미연결 시 `~/.claude/compliance/policy.md` 사용
- **감사 로그**: `.claude/memory/compliance-audit/SESSION-{N}.md`
- **Compliance API**: `COMPLIANCE_API_URL` + `COMPLIANCE_API_KEY` 환경변수 설정 시 API 모드 감사 (미설정 시 로컬 fallback)

### T04: Cross-tool rule files 작성 — user_level 반영
T01.8.7 의 `atomy-toolkit project-rules` 결과를 기준으로 `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` 를 모두 확인하고, 제안서 결과를 반영하여 필요한 부분을 수정하세요 (각 파일 300줄 이내):

**user_level 반영 (v2.2):**
1. frontmatter에 `user_level: {확정된 레벨}` 기록
2. `## 대화 스타일` 섹션을 user_level에 맞게 생성:
   - `beginner`: 전체 쉬운 말 지침 포함
   - `intermediate`: 괄호 병기 지침 포함
   - `advanced`: 이 섹션 생략 또는 "기본 모드" 한 줄
3. `beginner`일 때 핵심 명령어 설명에 "이 명령어가 뭘 하는지" 한 줄 주석 추가

4. coding tool 이 Codex 가 아니어도 프로젝트 루트 `AGENTS.md` 를 반드시 유지한다.
5. target IDE 가 Antigravity 가 아니어도 `GEMINI.md` 를 반드시 유지한다.
6. `AGENTS.md` 와 `GEMINI.md` 는 byte-equal mirror 로 유지한다.

```markdown
# [프로젝트명] — [한 줄 설명]

## 목표
[이 프로젝트가 해결하는 문제와 최종 목표]

## 기술 스택
- 언어: [Python/Node.js 버전]
- 주요 라이브러리: [목록]
- 외부 API: [목록 또는 없음]
- 테스트: pytest / jest
- 린트: ruff / eslint

## 핵심 명령어
- 실행: `[실행 명령어]`
- 테스트: `pytest` 또는 `npm test`
- 린트: `ruff check .` 또는 `npm run lint`

## DDD 폴더 구조
- `src/[도메인1]/`: [역할 설명]
- `src/[도메인2]/`: [역할 설명]
- ...

## API 키 목록 (.env)
- `[API_KEY_NAME]`: [용도]

## 코드 원칙
1. 항상 한글로 주석 작성
2. 에러 처리는 try-except/try-catch 필수
3. 데이터 없으면 N/A — 절대 추측 금지
4. API 키는 .env 전용, 하드코딩 금지
5. 하나의 세션 = 하나의 도메인

## 작업 전 필수
1. docs/plan.md → docs/checklist.md → docs/context.md 순서로 읽기
2. /rpi [작업내용] 으로 시작

## 메모리 시스템 (ASMR v3.0 — 3-Tier)
- **Hot** (`docs/context.md`): 최근 3세션 압축 요약, 매 세션 자동 로드
- **Warm** (`.claude/memory/`): 활성 메모리 50개 이하, `/rpi`가 최대 5개 선택 조회
- **Cold** (`.claude/memory/archive/`): 종료된 Phase, superseded, 10세션 미참조 메모리
- `/rpi` 티어 라우팅: Warm 우선 탐색, 과거 Phase 참조 시 Cold 자동 접근
- `/handoff` 시 자동 Update/Extend/Derive + 강등/승격/배치 병합 수행
- 메모리 카테고리: decisions / architecture / bugs / learnings
```

### T05a: 모노레포 구조 생성 (Frontend+Backend Y 선택 시만)

> **v2.2 신규**: compliance-service 패턴을 기반으로 한 Frontend+Backend 분리 템플릿.

인터뷰에서 Frontend+Backend 분리가 Y인 경우, 기존 `src/` 대신 모노레포 구조를 생성합니다.

```text
# 기존 src/ 를 제거하고 모노레포 구조 생성
Remove-Item -Recurse -Force "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\src" -ErrorAction SilentlyContinue

# backend/ 구조 생성 — templates/backend-fastapi/ 에서 복사
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\backend\src\config" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\backend\src\api" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\backend\src\db" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\backend\src\services" -Force
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\backend\tests" -Force

# frontend/ 구조 생성 — templates/frontend-nextjs/ 에서 복사
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\frontend\app" -Force

# scripts/ 폴더 생성
New-Item -ItemType Directory -Path "$env:USERPROFILE\atomy-toolkit\projects\[폴더명]\scripts" -Force
```

다음 템플릿 파일들을 복사한 뒤, `{{PROJECT_NAME}}`과 `{{PROJECT_DESCRIPTION}}`을 실제 값으로 치환하세요:

**backend/ 템플릿** (`$env:USERPROFILE\atomy-toolkit\_atomy-toolkit\templates\backend-fastapi/`):
- `main.py` → `backend/src/main.py`
- `config/constants.py` → `backend/src/config/constants.py`
- `config/validate_env.py` → `backend/src/config/validate_env.py`
- `tests/test_smoke.py` → `backend/tests/test_smoke.py`
- `pyproject.toml` → `backend/pyproject.toml`
- `requirements.txt` → `backend/requirements.txt`  # railway.toml buildCommand 가 참조 — pyproject deps 와 sync 유지
- `railway.toml` → `backend/railway.toml`

**frontend/ 템플릿** (`$env:USERPROFILE\atomy-toolkit\_atomy-toolkit\templates\frontend-nextjs/`):
- `app/page.tsx` → `frontend/app/page.tsx`
- `next.config.ts` → `frontend/next.config.ts`
- `package.json` → `frontend/package.json`
- `tsconfig.json` → `frontend/tsconfig.json`

**monorepo-root/ 템플릿** (`$env:USERPROFILE\atomy-toolkit\_atomy-toolkit\templates\monorepo-root/`):
- `.gitignore.template` → `.gitignore` (T03 의 .gitignore 를 대체)
- `CLAUDE.md.monorepo-section` → CLAUDE.md 에 모노레포 구조 섹션 삽입

각 `backend/src/` 폴더에 `__init__.py` 를 생성하세요.

T05a 를 실행한 경우 **T05, T06, T09.5, T09.6, T09.7, T09.8** 은 스킵합니다 (템플릿에 이미 포함).

### T05~T06: DDD 폴더 & __init__.py 생성 (Frontend+Backend N 인 경우만)
인터뷰에서 파악한 도메인으로 폴더를 생성하고, Python이면 각 폴더에 `__init__.py` 생성.

**T05 보강 (Phase 1 wiring Task 3, AC-5):** 인터뷰에서 받은 도메인 + 한 줄 책임 설명을 `_install_input.yaml` 로 박아둔다. 그 다음 `atomy-toolkit install` 실행 시 단계 2/3/4 가 이 yaml 을 읽어 자동 처리:

```python
from atomy_toolkit.cli.install_input import write_install_input_yaml

# 인터뷰 결과 (예시 — 실제 값은 user_level 별 prompt 결과)
confirmed_user_level = "intermediate"
domains = {
    "order": "주문 도메인 — 주문 생성/조회/취소 책임",
    "billing": "결제 도메인 — 청구/환불/연체 처리 책임",
}
write_install_input_yaml(target_dir, domains, user_level=confirmed_user_level)
print(f"✓ _install_input.yaml created with {len(domains)} domain(s)")
```

이후 `atomy-toolkit install <target>` 실행 시 단계 2 (DDD 골격), 단계 3 (plan.md 매트릭스), 단계 4 (ARCH-001 메모리) 가 yaml 을 자동 읽어 도메인 자산 박는다.

### T07: settings.json Hook 수정
복사된 `.claude/settings.json`에서 PreToolUse Write/Edit Hook의 도메인 감지 메시지를 이 프로젝트의 실제 도메인명으로 수정하세요.

### T08: 프로젝트 전용 SKILL.md 작성
`.claude/skills/[프로젝트명]/SKILL.md`를 생성하세요.

```markdown
---
name: [프로젝트명]
description: [언제 이 스킬이 활성화되는지 한 줄 설명]
---

# [프로젝트명] 전용 규칙

## 데이터 규칙
[프로젝트 특성에 맞는 데이터 처리 규칙]

## 코드 규칙
[도메인 격리, 네이밍 컨벤션 등]

## 외부 API 규칙
[Rate Limit, Retry 등]
```

### T09: docs/plan.md 초안 작성

```markdown
# [프로젝트명] — 프로젝트 계획서

## 목표
[최종 목표]

## 아키텍처
[데이터 흐름: A → B → C → D]

## 기술 스택
[목록]

## DDD 매핑
| 파일/모듈 | 도메인 | 역할 |
|-----------|--------|------|
| [예시] | [도메인] | [역할] |

## Phase별 구현 계획

### Phase 1: 기반 구축
- [ ] [Task 1]
- [ ] [Task 2]

### Phase 2: 핵심 기능
- [ ] [Task 3]

### Phase 3: 개선 & 검증
- [ ] [Task 4]

## 메모리 정책 (ASMR)
- 이 프로젝트의 주요 도메인: [도메인 목록]
- 예상되는 주요 메모리 유형:
  - decisions: [어떤 종류의 의사결정이 많을지]
  - architecture: [시스템 구조 관련 기록 필요 사항]
  - learnings: [외부 API/도구 관련 학습 예상 사항]
- context.md 경량화: 3세션 이전 기록은 mempalace 가 자동 관리
```

### T09.5: 중앙 상수 파일 생성

프로젝트 전체에서 사용하는 운영 상수(파일 크기 제한, 재시도 횟수, 타임아웃 등)를 한 파일에 집중 관리합니다.

**Python 프로젝트:**
```python
# src/config/constants.py
"""프로젝트 전역 상수 — 매직 넘버 대신 이 파일의 상수를 사용하세요."""

# 파일 처리
MAX_FILE_SIZE_MB = 100
MAX_UPLOAD_COUNT = 10

# API 호출
API_TIMEOUT_SEC = 30
MAX_RETRIES = 3
RETRY_DELAY_SEC = 1.0

# 동시성
MAX_CONCURRENT_REQUESTS = 5
```

**TypeScript 프로젝트:**
```typescript
// src/config/limits.ts
/** 프로젝트 전역 상수 — 매직 넘버 대신 이 파일의 상수를 사용하세요. */

export const LIMITS = {
  FILE: { maxSizeMB: 100, maxUploadCount: 10 },
  API: { timeoutMs: 30_000, maxRetries: 3, retryDelayMs: 1_000 },
  CONCURRENCY: { maxRequests: 5 },
} as const;
```

### T09.6: 환경변수 검증 유틸리티 생성

앱 시작 시 필수 환경변수를 검증하고, 누락 시 즉시 실패하는 유틸리티입니다.

**Python 프로젝트:**
```python
# src/config/validate_env.py
"""앱 시작 시 필수 환경변수 검증 — 누락 시 즉시 실패(fail-fast)."""
import os
import sys

REQUIRED_VARS = [
    # ("변수명", "설명"),
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
```

**TypeScript 프로젝트:**
```typescript
// src/config/validateEnv.ts
/** 앱 시작 시 필수 환경변수 검증 — 누락 시 즉시 실패(fail-fast). */

const REQUIRED_VARS: [string, string][] = [
  // ["변수명", "설명"],
];

export function validateEnv(): void {
  const missing = REQUIRED_VARS.filter(([name]) => !process.env[name]);
  if (missing.length > 0) {
    console.error("❌ 필수 환경변수가 누락되었습니다:");
    missing.forEach(([name, desc]) => console.error(`  - ${name}: ${desc}`));
    console.error("\n.env.example을 참고하여 .env 파일을 설정하세요.");
    process.exit(1);
  }
}
```

### T09.7: Security Headers 설정 (Next.js 프로젝트 한정)

Next.js 프로젝트인 경우 `next.config.ts`에 보안 헤더를 추가합니다.

```typescript
// next.config.ts 내 headers() 함수 추가
async headers() {
  return [{
    source: '/(.*)',
    headers: [
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
      { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    ],
  }];
}
```

### T09.8: 첫 번째 테스트 파일 생성

테스트 프레임워크 설정과 함께 **반드시 첫 번째 테스트 파일**을 생성합니다. "설정만 있고 테스트 없음" 상태를 방지합니다.

**Python 프로젝트:**
```python
# tests/test_smoke.py
"""스모크 테스트 — 프로젝트 기본 임포트와 상수 검증."""

def test_constants_exist():
    """중앙 상수 파일이 정상 임포트되는지 확인한다."""
    from src.config.constants import MAX_RETRIES
    assert MAX_RETRIES > 0

def test_validate_env_function_exists():
    """환경변수 검증 함수가 존재하는지 확인한다."""
    from src.config.validate_env import validate_env
    assert callable(validate_env)
```

**TypeScript 프로젝트:**
```typescript
// tests/smoke.test.ts
import { describe, it, expect } from 'vitest'; // 또는 jest
import { LIMITS } from '../src/config/limits';

describe('스모크 테스트', () => {
  it('중앙 상수 파일이 정상 임포트된다', () => {
    expect(LIMITS.API.maxRetries).toBeGreaterThan(0);
  });
});
```

### T10~T12: 선택 항목 (Todo에 포함된 경우만)
- `requirements.txt`: 인터뷰에서 언급된 라이브러리 포함
- `.env.example`: 인터뷰에서 파악한 API 키 목록
- `README.md`: 프로젝트 설명, 설치 방법, 실행 방법

---

## ━━━ PHASE 5: 완료 보고 ━━━

모든 태스크 완료 후 다음 형식으로 보고하세요:

```
✅ 프로젝트 부트스트랩 완료!

📁 생성된 구조:
[실제 생성된 폴더/파일 트리 출력]

✅ 완료된 태스크:
  ✓ T01. Atomy Toolkit 복사
  ✓ T01.5. 메모리 디렉토리 초기화 (ASMR)
  ✓ T02. docs 템플릿 생성
  ... (전체 목록)

⚠️  수동으로 해야 할 것:
  1. installer 환경변수가 없어서 `.env` 가 자동 생성되지 않았다면 `.env.example` 참고 후 수동 입력
  2. requirements.txt 확인 후 `pip install -r requirements.txt` 실행
  3. docs/plan.md 열어서 Phase 1 태스크를 구체화

🚀 첫 번째 작업을 시작하려면:
  /rpi [첫 번째 작업 내용]
```

---

## ⚠️ 주의사항

- **실제 파일을 쓰기 전 항상 경로를 출력**하여 사용자가 확인할 수 있게 하세요
- **기존 프로젝트 폴더가 있을 경우** 덮어쓰기 전에 반드시 확인하세요
- **Atomy Toolkit이 존재하지 않는 경우** 사용자에게 알리고 인라인으로 기본 파일을 생성하세요
- PHASE 4 실행 전 "실행 시작합니다. 잠시 기다려주세요." 메시지를 먼저 출력하세요
