"""Gemini Vision API를 이용한 디자인 채점 서비스."""
import asyncio
import io
import json
import os
import time

from google import genai
from google.genai import types
from PIL import Image

from src.config.constants import ANALYSIS_TIMEOUT_SEC, MAX_ANALYSIS_RETRIES


# ─── 1. 제출 정보 컨텍스트 ────────────────────────────────────────────────────

_CONTEXT_TEMPLATE = """[제출 정보 — 이 카테고리 규정으로만 판독]
카테고리: {category} / 라인: {line_type} / 용기타입: {product_type}
"""

# ─── 2. 공통 판독 원칙 (항상 포함) ──────────────────────────────────────────

_COMMON_RULES = """[역할]
애터미 패키지 디자인 QA 전문가. 이미지를 아래 규정에 따라 점수로 평가한다.

[판독 원칙]
1. 물리적 용기 형태(펌프/자/튜브) 추측 금지. 보이는 디자인 요소(로고·텍스트·컬러·라인)만으로 평가.
2. 레이아웃 불일치: 단박스 선택인데 용기 라벨 구조만 보이면 → graphic_and_legal_mark 0점, layout_mismatch=true.
3. 점수 체계 (100점, 90점↑ PASS):
   - identity_and_symbol_check: 30점
   - color_and_printing_rules: 25점
   - font_and_layout_check: 25점
   - graphic_and_legal_mark: 20점
4. atomy美 심볼: 프리미엄(앱솔루트) 제외 전 카테고리 필수. 누락 시 identity 감점.
5. 한글 메인 서체: 애터미 M 또는 L 필수. Bold 사용 시 font 감점.

[정렬 판별 — 제품명·카피만 기준, 나머지는 무시]

판별 대상: 제품명(Product Name)과 카피(Copy) 텍스트만.
무시 대상: 로고(atomy美, ATOMY), 용량(mL, g, OZ 등), 성분, 기능성 표기, 기타 정보성 텍스트.

판별 방법:
  제품명·카피 줄 중 긴 줄과 짧은 줄의 왼쪽 시작점을 비교한다.
  - 짧은 줄의 왼쪽 시작 ≈ 긴 줄의 왼쪽 시작 (±5% 이내 오차 허용) → 좌측 정렬
  - 짧은 줄의 왼쪽 시작이 긴 줄보다 명확히 오른쪽 (5% 초과) → 중앙 정렬

⚠️ 폰트 크기 차이에 의한 광학적 오차 주의:
  큰 서체(메인 제품명)와 작은 서체(카피, 영문)는 같은 좌측 기준선에 맞춰져 있어도
  픽셀 단위로는 수 px 차이가 날 수 있다. 이는 정상 좌측 정렬이다.
  텍스트 블록 전체가 시각적으로 왼쪽 기준선을 공유하고 있으면 좌측 정렬로 판단한다.
  명확하게 중앙 정렬 구조(짧은 줄이 양쪽으로 들여쓰여 가운데 축을 형성)일 때만 중앙 정렬로 판단한다.

예시:
  좌측 정렬: "NATURAL"과 "DEODORANT"의 왼쪽 시작이 같은 위치
  좌측 정렬: 큰 제품명과 작은 카피가 시각적으로 같은 왼쪽 기준선을 공유 (수 px 차이는 무시)
  중앙 정렬: "FOAM CLEANSER"가 "ACNE CLEAR EXPERT SYSTEM"보다 명확히 오른쪽에서 시작하며 가운데 축 형성

- 중앙 정렬 필수: 뷰티 전 라인, 옴므 전 라인
- 좌측 정렬 필수: 건기식, 식품, 리빙, 가전
- ⚠️ 헤어바디 전 라인: 좌측 정렬 필수. 중앙 정렬 확인 시 → font_and_layout_check 0점 + FAIL.
"""

# ─── 3. 카테고리별 세부 규정 (선택한 것만 주입) ──────────────────────────────

_RULES: dict[str, dict[str, str]] = {
    "뷰티": {
        "프리미엄": """[뷰티-프리미엄 규정]
정렬: 중앙 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 짧은 줄일수록 왼쪽이 더 들여쓰여 중심축 기준 좌우 대칭.
BI: [ATOMY ABSOLUTE] 형태 BI 필수. 단박스 전면 Line Box (두께 2.0pt↑, 앱솔루트 금박) 구조 적용. 전면의 33%↑.
단박스 전면 모든 요소(BI·제품명 등): 앱솔루트 금박 필수. 후면 표시사항: 애터미 다크그레이.
용기 직접 인쇄: 금박 절대 금지 → 애터미 다크그레이 적용. 후면 심볼만 애터미 블루.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. 애터미 Bold는 영문 서체에만 허용.
서체 참고: 라인명 애터미 L / 품목명·카피 DINOT-L 또는 애터미 L.
레이아웃 순서: BI → 라인명 → 영문 품목명 → 카피 → 내용량(최하단). 사방간격(상하좌우 여백) 동일.
심볼: 앱솔루트 라인 전면에 심볼 없는 것이 정상 (감점 금지).""",

        "스탠다드": """[뷰티-스탠다드 규정]
정렬: 중앙 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 짧은 줄일수록 왼쪽이 더 들여쓰여 중심축 기준 좌우 대칭.
심볼: atomy美 필수. 애터미 블루, 가로폭 20~25%↑.
BI: Line Box 금지. 애터미 다크그레이 컬러로 직접 배치.
BI 색상: 흰색·밝은 용기→애터미 블루, 컬러 용기→흰색, 그 외→본사 디자인팀 확인 필요.
포인트 라인: 전면 가로 포인트 라인 애터미 다크그레이 / 두께 0.3pt 이하 / 제품명 길이의 30% 또는 문안 끝까지.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.
강조 요소(품목명·국문 제품명·기능성 표기): 컨셉 컬러 필수.
카피 서체: DINOT-L, 4.5pt↑. 사방간격 동일.""",

        "색조": """[뷰티-색조 규정]
정렬: 중앙 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 짧은 줄일수록 왼쪽이 더 들여쓰여 중심축 기준 좌우 대칭.
심볼: atomy美 필수. 색조 특성상 후면 심볼은 애터미 블루 대신 다크그레이(또는 그레이)로 예외 적용.
팩트(Pact) 타입 단박스 전면: 주요 요소(BI·제품명·라인 등)에 은박(Silver) 후가공 필수.
용기·스틱 타입: 전면 BI·식별 요소에 컨셉 컬러 적용. 기능성 표기는 앱솔루트 금박 혼용.
홋수·색상라벨: 상단면 또는 전·후면에 누락 없이 표기. 서체: 애터미 M 또는 DINOT-M.""",
    },

    "헤어바디": {
        "프리미엄": """[헤어바디-프리미엄 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 중앙 정렬 확인 시 font_and_layout_check 0점 + FAIL. 로고 위치: 박스·용기 타입에 따라 다르게 적용, 일반적으로 우측 상단 권장.
BI: ATOMY ABSOLUTE 형태, 애터미 다크그레이. 용기·튜브 가로폭 40%↑, 단박스 50%↑.
단박스 전면: BI 하단 Line Box 필수 (두께 2.4pt, 컨셉 컬러).
펌프 용기 전면: 영문 제품명 애터미 M·컨셉컬러·20pt↑, 국문 제품명 애터미 M·컨셉컬러·10.5pt↑.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.
영문 카피: 첫 글자만 대문자 유지. 사방간격 동일.""",

        "스탠다드": """[헤어바디-스탠다드 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 중앙 정렬 확인 시 font_and_layout_check 0점 + FAIL. 로고 위치: 박스·용기 타입에 따라 다르게 적용, 일반적으로 우측 상단 권장.
심볼: atomy美 필수. 애터미 블루, 가로폭 20~35%.
캡 컬러: 펌프 타입 바디류 상단 캡 반드시 화이트 통일.
제품명: 영문·국문 컨셉 컬러 적용 필수.
포인트 라인 두께: 0.3pt~0.5pt 준수.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.""",

        "헤어에센스": """[헤어바디-헤어에센스 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 중앙 정렬 확인 시 font_and_layout_check 0점 + FAIL. 로고 위치: 박스·용기 타입에 따라 다르게 적용, 일반적으로 우측 상단 권장.
심볼: atomy美 필수. 애터미 블루, 가로폭 30~35%↑.
제품명 전용 컬러: 영문·국문 모두 반드시 Pantone 2116C 적용. 타 색상 사용 시 FAIL.
스페셜 그래픽: 영문 카피와 하단 용량 표기 사이에 Pantone 7444C 웨이브 그래픽 필수. 크기는 두 요소 사이 간격의 정확히 40%.
단박스 상단면 BI: 전면 BI 크기의 70~80% 스케일. 애터미 M 서체 + 좌측 정렬 필수.
사방간격 동일.""",
    },

    "옴므": {
        "스탠다드": """[옴므-스탠다드 규정]
정렬: 중앙 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 짧은 줄일수록 왼쪽이 더 들여쓰여 중심축 기준 좌우 대칭.
심볼: atomy美 필수. 용기 후면 애터미 블루로 표기.
펌프 용기: 전·후면 모든 문안·심볼 화이트·애터미 블루 1도 인쇄만 허용.
전면 사각 Line Box 필수: 용량 제외 전체 문안 감싸는 사각 라인. 가로폭의 70% / 두께 1~2pt.
서체: 품목명 DIN OT-M (6pt↑), 영문카피·내용량 DIN OT-L.
후면 참고: 애터미 로고 가로폭 25%↑, 국문 제품명 애터미 M (5pt↑·두께 0.2pt↑), 표시사항 Noto Sans CJK KR-Regular (4.5pt↑).
단박스 전면 사각 Line Box: 컨셉 컬러 / 가로폭 70% 이하 / 두께 1~2pt.
단박스 전면 모든 요소(BI·영문 제품명·카피·내용량): 컨셉 컬러 적용. 영문 제품명 DINOT-M / 6pt↑.
단박스 후면 심볼: 애터미 블루 / 가로폭 30%↑ 필수.""",

        "색조": """[옴므-색조 규정]
정렬: 중앙 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 짧은 줄일수록 왼쪽이 더 들여쓰여 중심축 기준 좌우 대칭.
심볼: atomy美 필수. 용기 후면 화이트로 표기 (1도 인쇄 규정).
용기: 다크 블루 용기 위에 화이트 1도 인쇄만 허용. 후면 심볼도 화이트.
용기 전면 사각 Line Box: 화이트 / 가로폭 80% 이하 / 두께 1~2pt.
홋수 공식: 전면 홋수(*01·02·03) 표기 필수. DINOT-L / 두께 0.5pt / 영문 제품명 크기의 정확히 2배. 미준수 시 FAIL.
내용량 표기: DINOT-L / 두께 0.2pt 이하 / 5pt↑.
단박스: 메인 그래픽·BI·테두리 박스 전부 Pantone 2728C 필수. Line Box [2728C / 80% 이하 / 1~2pt]. 홋수 동일 공식 (전면·상단면 필수). Pantone 2728C / DINOT-L / 두께 0.5pt.
단박스 후면: 심볼 애터미 블루 20%↑, 국문 제품명·기능성 표기 Pantone 2728C, 표시사항 애터미 다크그레이 / Noto Sans CJK Bold / 4.5pt↑.""",
    },

    "건기식": {
        "": """[건강기능식품 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 로고 위치: 우측 상단, 가운데 정렬 시 FAIL.
심볼: atomy美 필수. 애터미 블루, 전면 가로폭 기준 20%.
인증마크: 건강기능식품 인증마크 + GMP 마크 표기 (해당 시).
컬러박스: 하단 컬러박스 세로 비율 — 세로형 소=1/4(25%), 가로형 중·대=1/3(33%). 컬러박스 색상: 영문 제품명 서브 컬러와 동일.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.
제품명 크기: 국문 25pt↑ (대형 30pt↑), 영문 14pt↑ (대형 20pt↑). stroke 0.3pt.
내용량 표기: 반드시 제품명 크기의 1/2 미만.
레이아웃: 컨셉 이미지 가로폭 30~45%.
카톤박스: 유통기한·제조일자는 측면 인쇄 대신 스티커 별도 부착.""",
    },

    "식품": {
        "": """[식품 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 로고 위치: 우측 상단, 가운데 정렬 시 FAIL.
심볼: atomy美 필수. 애터미 블루, 전면 가로폭 기준 12%.
인증마크: HACCP 등 인증 마크 (해당 시).
컬러박스: 하단 컬러박스 세로 비율 — 소형=1/4(25%), 대형(가로)=1/3(33%).
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.
제품명 크기: 국문 25pt↑, 영문 14pt↑. stroke 0.25~0.4pt.
전면 주표시면: 세트박스·파우치·단박스 전면에 메인 카피 없이 제품 BI만 배치.
레이아웃: 컨셉 이미지 가로폭 30~35%.
카톤박스: 유통기한·제조일자 측면 인쇄.""",
    },

    "리빙": {
        "": """[리빙 규정]
정렬: 좌측 정렬 필수. 텍스트 블록의 디자인 면 내 위치와 무관하게, 메인텍스트·영문·카피가 서로 왼쪽 기준 정렬.
색상: 지정 컬러 PANTONE 317C (민트 계열) 필수. 317C 외 다른 컬러 사용 시 → color_and_printing_rules 0점 + FAIL.
심볼: atomy美 필수. 크기: 전면 가로폭 기준 20%.
로고 여백: 상단 여백=심볼 높이와 동일. 좌우 여백=심볼 폭의 1/2.
컬러박스: 하단, 세로 비율 1/5(20%).
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.
제품명: 국문·영문 31pt↑, stroke 0.5pt. 부제목: 14pt↑, stroke 0.3pt.
인증: HACCP 마크는 리빙에 해당 없음 — 식품 카테고리 전용. 리빙 이미지에 HACCP이 보여도 리빙 규정 위반으로 감점.
KC 인증: 해당 제품에 한함.""",
    },

    "패션": {
        "": """[패션 규정]
심볼: ⛔ 기존 그래픽 형태 atomy美 심볼 절대 금지. 반드시 텍스트 자음 조합 형태 [ㅇㅌㅁ] 심볼 사용. 가로폭 10%. 위반 시 identity_and_symbol_check 0점.
지정 컬러: PANTONE 2706C 적용 필수.
치수·사이즈 표기 누락 금지 — 반드시 확인.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.""",
    },

    "가전": {
        "": """[가전 규정]
정렬: 좌측 정렬 필수. 로고 제외, 제품명·카피 텍스트 줄들 기준 — 왼쪽 시작점이 동일한 세로선, 오른쪽 끝은 들쭉날쭉. 로고 위치: 우측 상단, 가운데 정렬 시 FAIL.
심볼: atomy美 필수. 지정 컬러: PANTONE 542C 적용 필수.
영문 타이틀 명기 시: 애터미 골드 / 55pt↑ / 선 두께 1pt 필수.
국문 제품명 가로 중앙: 애터미 블루 / 1pt 라인 필수 적용.
폰트: 한글 메인 서체 애터미 M 또는 L 필수. Bold 금지.""",
    },

    "키즈": {
        "": """[키즈 규정]
심볼: atomy美 필수. 가로폭 기준 32% (대형 배치).
메인 이미지: 75%.
서체 크로스 혼용 규정 (일반 카테고리와 반대 적용): 영문 서체=애터미 Bold (굵게), 국문 서체=애터미 Light (가늘게).""",
    },
}

# ─── 4. PDF 전면 식별 지침 (PDF 제출 시만 포함) ──────────────────────────────

_PDF_RULES = """
[PDF 판독 지침]
이 파일은 패키지 전개도(die-cut layout) 또는 라벨·파우치 전체 레이아웃 PDF입니다.
판독 범위: 첫 번째 페이지에서 전면(Front) 패널의 그래픽 요소만 채점합니다.

전면 식별 방법:
- 박스 전개도: 중앙에 위치한 가장 넓은 직사각형 패널이 전면
- 라벨·파우치: 제품명·BI·주요 그래픽이 집중된 면이 전면
- 여러 면이 동일 크기라면 텍스트·BI 밀도가 가장 높은 패널을 전면으로 판단

채점 제외: 후면·측면·상단·하단 패널의 요소는 채점하지 않습니다.
예외: 가이드라인에서 후면·상단면을 명시적으로 체크하는 항목(예: 후면 심볼 크기·위치)은 해당 패널도 확인합니다.
"""

# ─── 5. 미적 완성도 평가 지침 ────────────────────────────────────────────────

_AESTHETIC_RULES = """
[미적 완성도 — 카테고리별 세부 점수 반영]
애터미 가이드 규정 준수 여부를 채점한 뒤, 각 카테고리 점수 안에서 아래 미적 요소를 추가로 고려하여
카테고리당 최대 1~2점을 조정할 수 있다. 전체 점수를 별도로 건드리지 않는다.

카테고리별 미적 반영 기준:
- identity_and_symbol_check: 심볼·BI의 시각적 무게감, 배치 균형, 전면에서 눈에 잘 들어오는가
- color_and_printing_rules: 색상 조화, 컬러 간 대비가 자연스럽고 산만하지 않은가
- font_and_layout_check: 여백(White Space)의 여유, 타이포 크기 대비·행간·자간, 정보 흐름의 자연스러움
- graphic_and_legal_mark: 그래픽 요소의 구성 밸런스, 레이아웃 완성도

조정 원칙:
- 규정을 완벽히 지켰으나 미적으로 아쉬운 경우 1~2점 차감 가능 (예: 28/30, 23/25)
- 규정을 지키면서 미적 완성도도 높은 경우 만점 유지
- 규정 위반이 있는 경우 미적 점수는 별도 조정하지 않음 (이미 감점됨)

aesthetic_tips: 위 미적 평가를 바탕으로, 가이드 규정이 아닌 순수 감각적 관점의 개선 조언 2~3개.
- "~하면 더 ~해 보입니다" / "~가 다소 ~해 보입니다. ~를 검토해 보세요" 형식.
- 전문 디자이너가 동료에게 말하듯 건설적이고 따뜻한 톤.
- 디자인이 이미 훌륭하면 잘된 점 1개 언급 후 아주 작은 개선 제안 1~2개.
"""

# ─── 6. 출력 포맷 (항상 포함) ────────────────────────────────────────────────

_OUTPUT_FORMAT = """{
  "evaluation_result": "PASS 또는 FAIL",
  "score": 총점(0~100 정수),
  "category_detected": "뷰티/헤어바디/옴므/건기식/식품/리빙/패션/가전/키즈",
  "line_type_detected": "프리미엄/스탠다드/색조/헤어에센스/해당없음",
  "product_type_detected": "단박스/세트박스/카톤박스/용기/파우치",
  "layout_mismatch": false,
  "details": {
    "identity_and_symbol_check": {"score": 0~30, "max_score": 30, "status": "PASS/WARN/FAIL", "feedback": "구체적 근거 (미적 요소 포함)"},
    "color_and_printing_rules":  {"score": 0~25, "max_score": 25, "status": "PASS/WARN/FAIL", "feedback": "구체적 근거 (미적 요소 포함)"},
    "font_and_layout_check":     {"score": 0~25, "max_score": 25, "status": "PASS/WARN/FAIL", "feedback": "구체적 근거 (미적 요소 포함)"},
    "graphic_and_legal_mark":    {"score": 0~20, "max_score": 20, "status": "PASS/WARN/FAIL", "feedback": "구체적 근거 (미적 요소 포함)"}
  },
  "aesthetic_tips": ["조언 1", "조언 2", "조언 3(선택)"],
  "improvement_points": ["가이드 규정 위반 수정 항목 (없으면 빈 배열)"]
}"""


_LIVING_SINGLE_BOX_EXCEPTION = """
[리빙 단박스 — 317C 색상바 위치 예외]
제출된 용기 타입이 단박스(Single Box)입니다.
리빙 단박스는 PANTONE 317C 색상바가 전면(Front) 하단 대신 박스 옆면(Side Panel)에 적용되는 것이 허용됩니다.

판독 규칙:
- 전면에 317C 색상바가 없어도 color_and_printing_rules에서 감점하지 않습니다.
- 317C 색상 자체의 사용 여부(옆면 포함 전체 박스 기준)는 정상 채점합니다.

aesthetic_tips 조건부 조언:
- 전면 배경이 화이트(흰색) 계열이 아니고, 317C가 전면에 보이지 않는다면:
  aesthetic_tips에 "단박스 옆면에 PANTONE 317C 색상바를 적용하면 리빙 라인 아이덴티티가 강화됩니다." 를 포함하세요.
- 전면이 이미 화이트/연회색 계열이거나 317C가 전면에 있다면 이 조언은 생략합니다.
"""

_OVERSEAS_EXEMPTION = """
[해외전용 디자인 예외]
이 디자인은 해외전용(Overseas Exclusive) 디자인으로 제출되었습니다.
예외 규정: 현지 언어(한국어·영어 이외의 언어)가 한국어 또는 영어보다 더 크게 표기되어 있어도
font_and_layout_check 에서 언어 크기 규정 위반(국문>영문·현지어 규정)으로 감점하지 않습니다.
현지 언어의 크기·비중은 해당 국가 규정에 따르며, 나머지 모든 디자인 규정은 동일하게 적용합니다.
"""


def _build_prompt(
    category: str, line_type: str, product_type: str,
    content_type: str = "", is_overseas: bool = False,
) -> str:
    """선택된 카테고리 규정만 포함한 프롬프트를 생성한다."""
    context = _CONTEXT_TEMPLATE.format(
        category=category,
        line_type=line_type if line_type else "해당없음",
        product_type=product_type,
    )
    cat_rules = _RULES.get(category, {})
    specific = cat_rules.get(line_type) or cat_rules.get("", "")
    pdf_section = _PDF_RULES if content_type == "application/pdf" else ""
    overseas_section = _OVERSEAS_EXEMPTION if is_overseas else ""
    living_single_box_section = (
        _LIVING_SINGLE_BOX_EXCEPTION
        if category == "리빙" and product_type == "단박스"
        else ""
    )

    return (
        context
        + _COMMON_RULES
        + pdf_section
        + overseas_section
        + "\n" + specific + "\n"
        + living_single_box_section
        + _AESTHETIC_RULES
        + "\n[Output Format] — JSON만 출력, 외부 텍스트 금지:\n"
        + _OUTPUT_FORMAT
    )


def _call_gemini_sync(image_bytes: bytes, content_type: str, prompt: str) -> dict:
    """Gemini Vision API 동기 호출 — MAX_ANALYSIS_RETRIES 재시도 포함."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    last_error: Exception = RuntimeError("알 수 없는 오류")
    # image/jpg 는 표준 MIME 타입이 아니므로 정규화
    mime = "image/jpeg" if content_type == "image/jpg" else content_type

    for attempt in range(MAX_ANALYSIS_RETRIES):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime),
                    prompt,
                ],
            )
            return _parse_json_response(response.text)
        except Exception as e:
            last_error = e
            if attempt < MAX_ANALYSIS_RETRIES - 1:
                is_overload = "503" in str(e) or "UNAVAILABLE" in str(e)
                # 503 과부하: 지수 백오프 (10s → 20s → 40s → 60s)
                wait = min(10.0 * (2 ** attempt), 60.0) if is_overload else 2.0
                time.sleep(wait)

    raise last_error


def _parse_json_response(raw: str) -> dict:
    """Gemini 응답 텍스트에서 JSON을 파싱한다."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"JSON 파싱 실패: {raw[:200]}")


_DETAIL_KEYS = [
    ("identity_and_symbol_check", 30),
    ("color_and_printing_rules", 25),
    ("font_and_layout_check", 25),
    ("graphic_and_legal_mark", 20),
]


def _finalize_result(result: dict) -> dict:
    """AI 응답을 기반으로 총점 계산 및 합격/불합격을 최종 판정한다."""
    details = result.get("details", {})

    if result.get("layout_mismatch", False):
        item = details.get("graphic_and_legal_mark", {})
        item["score"] = 0
        item["status"] = "FAIL"

    total = sum(details.get(k, {}).get("score", 0) for k, _ in _DETAIL_KEYS)
    total = max(0, min(100, int(total)))
    result["score"] = total
    result["total_score"] = total

    # aesthetic_tips 없으면 빈 배열로 보정
    if not isinstance(result.get("aesthetic_tips"), list):
        result["aesthetic_tips"] = []

    any_fail = any(details.get(k, {}).get("status") == "FAIL" for k, _ in _DETAIL_KEYS)

    if total < 90 or any_fail or result.get("layout_mismatch", False):
        result["evaluation_result"] = "FAIL"
    else:
        result["evaluation_result"] = "PASS"

    for key, max_score in _DETAIL_KEYS:
        item = details.get(key, {})
        if item.get("status") not in ("PASS", "WARN", "FAIL"):
            ratio = item.get("score", 0) / max_score if max_score else 0
            item["status"] = "PASS" if ratio >= 0.9 else ("WARN" if ratio >= 0.6 else "FAIL")

    return result


async def score_design(
    image_bytes: bytes,
    content_type: str,
    category: str,
    line_type: str,
    product_type: str,
    is_overseas: bool = False,
) -> dict:
    """패키지 디자인 이미지·PDF를 채점하고 결과를 반환한다."""
    prompt = _build_prompt(category, line_type, product_type, content_type, is_overseas)
    result = await asyncio.to_thread(_call_gemini_sync, image_bytes, content_type, prompt)
    return _finalize_result(result)
