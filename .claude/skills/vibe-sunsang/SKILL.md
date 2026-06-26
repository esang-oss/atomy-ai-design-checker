---
name: vibe-sunsang
description: 바선생 — AI 활용 성장 멘토 에이전트. 5개 sub-skill (growth/knowledge/mentor/onboard/retro) 으로 라우팅합니다. "바선생", "성장", "멘토", "회고", "코칭" 같은 요청에 사용됩니다.
---

# 바선생 (Vibe Sunsang) — AI 활용 성장 멘토

> 본 skill 은 plugin marketplace 의존 없이 동봉된 v2.0.1 사본 (Task 9, AC-9, D-006).
> 원본: `gptaku-plugins/vibe-sunsang` plugin (사용자 환경의 Claude Code).

## 5개 sub-skill 라우팅

| sub-skill | 용도 | 트리거 키워드 |
|---|---|---|
| **vibe-sunsang-onboard** | 초기 설정 (워크스페이스/프로젝트/유형/첫 변환) | "바선생 시작", "온보딩", "초기화", "셋업" |
| **vibe-sunsang-knowledge** | 지식 베이스 (v2 6축×7단계, 안티패턴, 워크스페이스 유형) | "바선생 안티패턴", "레벨 시스템", "6축", "성장 지표" |
| **vibe-sunsang-mentor** | 멘토링 4모드 (요청 품질 / 안티패턴 / 개념 학습 / 종합 코칭) | "멘토링", "코칭", "요청 코칭", "어떻게 요청" |
| **vibe-sunsang-growth** | 성장 리포트 자동 생성 (v2 6축×7단계, 0.5 단위) | "성장 리포트", "성장 분석", "얼마나 성장", "레벨 체크" |
| **vibe-sunsang-retro** | Claude Code 대화 변환 + 회고 (Markdown 변환, 분석 가이드) | "변환", "retro", "대화 변환", "로그 변환", "회고" |

각 sub-skill 의 상세는 `.claude/skills/vibe-sunsang-<name>/SKILL.md` 참조.

## 사용 시점 (라우팅 우선순위)

1. 사용자가 명시적 sub-skill 키워드 사용 → 해당 sub-skill 직접 호출
2. "바선생" 만 언급 → onboard (첫 사용) 또는 mentor (반복 사용) 분기
3. AI 활용 진단·코칭·성장 데이터 관련 요청 → mentor 또는 growth

## air-gapped 호환

본 동봉 사본은 marketplace 다운로드 없이 동작합니다. 단, 각 sub-skill SKILL.md
의 `${CLAUDE_PLUGIN_ROOT}` 참조는 plugin 환경에서만 resolve 되므로 air-gapped
환경에서는 references 경로를 수동 조정해야 할 수 있습니다 (별도 트랙).
