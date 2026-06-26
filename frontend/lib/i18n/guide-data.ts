// 애터미 패키지 디자인 가이드 데이터 — 한국어 / 영어 이중 언어 지원
// Single Source of Truth: 이 파일을 수정하면 가이드 페이지 전체에 반영됩니다.

/* ─── 타입 정의 ───────────────────────────────────────────────────────── */
type RuleLevel = "required" | "warn" | "info";

interface Rule {
  text: string;
  level: RuleLevel;
}

interface Section {
  title: string;
  rules: Rule[];
}

interface LineGuide {
  label: string;
  sections: Section[];
}

interface CategoryGuide {
  lines?: Record<string, LineGuide>;
  sections?: Section[];
}

interface CategoryGroup {
  label: string;
  value: string;
  lines: { label: string; value: string }[];
}

export interface GuideData {
  guide: Record<string, CategoryGuide>;
  categoryGroups: CategoryGroup[];
}

/* ─── 한국어 데이터 ───────────────────────────────────────────────────── */
const KO: GuideData = {
  guide: {
    뷰티: {
      lines: {
        프리미엄: {
          label: "프리미엄 (애터미 앱솔루트)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피·로고 모두 가로 중앙 정렬 필수." },
              ],
            },
            {
              title: "BI & 심볼",
              rules: [
                { level: "required", text: "[ATOMY ABSOLUTE] 형태 BI 필수. 단박스 전면에 Line Box(두께 2.0pt 이상, 앱솔루트 금박) 구조 적용. 단박스 전면의 33% 이상 차지." },
                { level: "required", text: "단박스 전면 모든 요소(BI, 제품명 등)는 앱솔루트 금박 필수. 후면 표시사항은 애터미 다크그레이." },
                { level: "required", text: "용기(본품) 직접 인쇄 시 금박 절대 금지 — 애터미 다크그레이 적용. 후면 심볼만 애터미 블루." },
              ],
            },
            {
              title: "폰트 & 텍스트",
              rules: [
                { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. 애터미 Bold는 영문 서체에만 허용." },
                { level: "info", text: "라인명 서체: 애터미 L / 품목명·카피: DINOT-L 또는 애터미 L." },
              ],
            },
            {
              title: "레이아웃",
              rules: [
                { level: "info", text: "전면 구성 순서: BI(ATOMY ABSOLUTE) → 라인명 → 영문 품목명 → 카피 → 내용량(최하단)." },
                { level: "info", text: "사방간격(상하좌우 여백) 동일 필수." },
              ],
            },
          ],
        },
        스탠다드: {
          label: "스탠다드 (기초라인)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피·로고 모두 가로 중앙 정렬 필수." },
              ],
            },
            {
              title: "BI & 심볼",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 애터미 블루, 가로폭 20~25% 이상." },
                { level: "required", text: "Line Box 금지. 애터미 다크그레이 컬러로 BI 직접 배치." },
                { level: "info", text: "흰색·밝은 용기 → 애터미 블루 BI. 컬러 용기 → 흰색 BI. 그 외 색상은 본사 디자인팀 확인 필요." },
              ],
            },
            {
              title: "포인트 라인",
              rules: [
                { level: "required", text: "전면 가로 포인트 라인: 애터미 다크그레이 / 두께 0.3pt 이하 / 제품명 길이의 30% 또는 문안 끝까지." },
              ],
            },
            {
              title: "폰트 & 컬러",
              rules: [
                { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
                { level: "required", text: "품목명·국문 제품명·기능성 표기 등 강조 요소에 반드시 컨셉 컬러 적용." },
                { level: "info", text: "카피 서체: DINOT-L, 4.5pt 이상." },
              ],
            },
            {
              title: "레이아웃",
              rules: [
                { level: "info", text: "사방간격 동일 필수." },
              ],
            },
          ],
        },
        색조: {
          label: "색조 (메이크업)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피·로고 모두 가로 중앙 정렬 필수." },
              ],
            },
            {
              title: "BI & 심볼",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 단, 색조 특성상 후면 심볼은 애터미 블루 대신 다크그레이(또는 그레이)로 예외 적용." },
                { level: "required", text: "팩트(Pact) 타입 단박스: 전면 주요 요소(BI, 제품명, 라인 등)에 은박(Silver) 후가공 필수." },
                { level: "required", text: "용기/스틱 타입: 전면 BI·식별 요소에 컨셉 컬러 적용. 기능성 표기는 앱솔루트 금박 혼용." },
              ],
            },
            {
              title: "홋수 표기",
              rules: [
                { level: "required", text: "상단면 또는 전/후면에 홋수 및 색상라벨 누락 없이 표기. 서체: 애터미 M 또는 DINOT-M." },
              ],
            },
            {
              title: "레이아웃",
              rules: [],
            },
          ],
        },
      },
    },
    헤어바디: {
      lines: {
        프리미엄: {
          label: "프리미엄 (앱솔루트 헤어)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피 반드시 좌측 정렬. 가운데 정렬 확인 시 즉시 FAIL." },
                { level: "info", text: "로고 위치: 박스/용기 타입에 따라 다르게 적용 가능 (일반적으로 우측 상단 권장)." },
              ],
            },
            {
              title: "BI & Line Box",
              rules: [
                { level: "required", text: "BI 로고: ATOMY ABSOLUTE 형태, 애터미 다크그레이. 용기/튜브 가로폭 40% 이상, 단박스 50% 이상." },
                { level: "required", text: "단박스 전면: BI 하단에 Line Box 필수 (두께 2.4pt, 컨셉 컬러)." },
              ],
            },
            {
              title: "제품명 & 폰트",
              rules: [
                { level: "required", text: "펌프 용기 전면 — 영문 제품명: 애터미 M, 컨셉컬러, 20pt 이상. 국문 제품명: 애터미 M, 컨셉컬러, 10.5pt 이상." },
                { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
                { level: "info", text: "영문 카피: 첫 글자만 대문자 유지." },
              ],
            },
            {
              title: "레이아웃",
              rules: [
                { level: "info", text: "사방간격 동일 필수." },
              ],
            },
          ],
        },
        스탠다드: {
          label: "스탠다드 (기초 바디/헤어)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피 반드시 좌측 정렬. 가운데 정렬 확인 시 즉시 FAIL." },
                { level: "info", text: "로고 위치: 박스/용기 타입에 따라 다르게 적용 가능 (일반적으로 우측 상단 권장)." },
              ],
            },
            {
              title: "캡 & 심볼",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 애터미 블루, 가로폭 20~35%." },
                { level: "required", text: "⚠️ 펌프 타입 바디류: 상단 캡 컬러 반드시 화이트로 통일." },
              ],
            },
            {
              title: "제품명 & 포인트 라인",
              rules: [
                { level: "required", text: "영문·국문 제품명에 컨셉 컬러 적용 필수." },
                { level: "required", text: "포인트 라인 두께: 0.3pt~0.5pt 준수." },
                { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
              ],
            },
            {
              title: "레이아웃",
              rules: [],
            },
          ],
        },
        헤어에센스: {
          label: "헤어에센스 특화 라인",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피 반드시 좌측 정렬. 가운데 정렬 확인 시 즉시 FAIL." },
                { level: "info", text: "로고 위치: 박스/용기 타입에 따라 다르게 적용 가능 (일반적으로 우측 상단 권장)." },
              ],
            },
            {
              title: "BI & 심볼",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 애터미 블루, 가로폭 30~35% 이상." },
              ],
            },
            {
              title: "전용 컬러 & 그래픽",
              rules: [
                { level: "required", text: "영문·국문 제품명 전용 컬러: 반드시 Pantone 2116C 적용. 타 색상 사용 시 FAIL." },
                { level: "required", text: "⚠️ 스페셜 그래픽: 영문 카피와 하단 용량 표기 사이에 Pantone 7444C 웨이브 그래픽 필수. 크기는 두 요소 사이 간격의 정확히 40%." },
              ],
            },
            {
              title: "단박스 상단면",
              rules: [
                { level: "required", text: "BI: 전면 BI 크기의 70~80% 스케일. 애터미 M 서체 + 좌측 정렬 필수." },
              ],
            },
            {
              title: "레이아웃",
              rules: [
                { level: "info", text: "사방간격 동일 필수." },
              ],
            },
          ],
        },
      },
    },
    옴므: {
      lines: {
        스탠다드: {
          label: "옴므 스탠다드 (기초)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피·로고 모두 가로 중앙 정렬 필수." },
              ],
            },
            {
              title: "펌프 용기 (본품)",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 용기 후면에 애터미 블루로 표기." },
                { level: "required", text: "인쇄 컬러 제한: 전/후면 모든 문안·심볼은 화이트/애터미 블루 1도 인쇄만 허용." },
                { level: "required", text: "전면 사각 Line Box 필수: 용량 제외 전체 문안 감싸는 사각 라인. 가로폭의 70% / 두께 1~2pt." },
                { level: "required", text: "서체: 품목명 DIN OT-M (6pt 이상), 영문카피·내용량 DIN OT-L." },
                { level: "info", text: "후면: 애터미 로고 가로폭 25% 이상, 국문 제품명 애터미 M (5pt 이상, 두께 0.2pt 이상), 표시사항 Noto Sans CJK KR-Regular (4.5pt 이상)." },
              ],
            },
            {
              title: "단박스",
              rules: [
                { level: "required", text: "전면 사각 Line Box: 컨셉 컬러 사각 박스 필수. 가로폭의 70% 이하 / 두께 1~2pt." },
                { level: "required", text: "전면 모든 요소(BI·영문 제품명·카피·내용량): 컨셉 컬러 적용. 영문 제품명 DINOT-M / 6pt 이상." },
                { level: "required", text: "후면 심볼: 애터미 블루 / 가로폭 30% 이상 필수." },
              ],
            },
            {
              title: "레이아웃",
              rules: [],
            },
          ],
        },
        색조: {
          label: "옴므 색조 (메이크업)",
          sections: [
            {
              title: "전면 정렬",
              rules: [
                { level: "required", text: "전면 메인 텍스트·카피·로고 모두 가로 중앙 정렬 필수." },
              ],
            },
            {
              title: "용기 (본품) — 인쇄 규정",
              rules: [
                { level: "required", text: "atomy美 심볼 필수 표기. 용기 후면에 화이트로 표기 (1도 인쇄 규정)." },
                { level: "required", text: "다크 블루 용기 위에 화이트 1도 인쇄만 허용. 후면 심볼도 화이트 처리." },
                { level: "required", text: "전면 사각 Line Box: 화이트 / 가로폭 80% 이하 / 두께 1~2pt." },
                { level: "required", text: "⚠️ 홋수 공식: 전면에 홋수(*01, 02, 03) 표기 필수. DINOT-L / 두께 0.5 / 영문 제품명 크기의 정확히 2배. 미준수 시 FAIL." },
                { level: "required", text: "내용량 표기: DINOT-L / 두께 0.2 이하 / 5pt 이상." },
              ],
            },
            {
              title: "단박스 — 지정 컬러",
              rules: [
                { level: "required", text: "전용 컬러: 메인 그래픽·BI·테두리 박스 전부 Pantone 2728C 적용 필수." },
                { level: "required", text: "전면 사각 Line Box: Pantone 2728C / 가로폭 80% 이하 / 두께 1~2pt." },
                { level: "required", text: "⚠️ 홋수 공식: 전면·상단면 필수. Pantone 2728C / DINOT-L / 두께 0.5pt / 제품명 크기의 2배." },
                { level: "info", text: "후면: 심볼 애터미 블루 20% 이상, 국문 제품명·기능성 표기 Pantone 2728C, 표시사항 애터미 다크그레이 / Noto Sans CJK Bold / 4.5pt 이상." },
              ],
            },
          ],
        },
      },
    },
    건기식: {
      sections: [
        {
          title: "전면 정렬",
          rules: [
            { level: "required", text: "전면 메인 텍스트·카피 좌측 정렬 필수." },
            { level: "required", text: "로고는 우측 상단에 적당한 여백을 두고 배치. 가운데 정렬 시 FAIL." },
          ],
        },
        {
          title: "심볼 & BI",
          rules: [
            { level: "required", text: "atomy美 로고: 애터미 블루, 전면 가로폭 기준 20%." },
            { level: "info", text: "건강기능식품 인증마크 + GMP 마크 표기 (해당 시)." },
          ],
        },
        {
          title: "컬러박스 비율",
          rules: [
            { level: "required", text: "하단 컬러박스 세로 비율: 세로형 소 = 1/4 (25%), 가로형 중·대 = 1/3 (33%)." },
            { level: "info", text: "컬러박스 색상: 영문 제품명 서브 컬러와 동일 사용." },
          ],
        },
        {
          title: "폰트 & 사이즈",
          rules: [
            { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
            { level: "required", text: "국문 제품명: 25pt 이상 (대형 30pt 이상). 영문 제품명: 14pt 이상 (대형 20pt 이상). stroke 0.3pt." },
            { level: "required", text: "⚠️ 내용량 표기: 반드시 제품명 크기의 1/2 미만이어야 함." },
          ],
        },
        {
          title: "레이아웃",
          rules: [
            { level: "info", text: "컨셉 이미지: 가로폭 30~45%." },
            { level: "info", text: "카톤박스(외상자): 유통기한·제조일자는 측면 인쇄 대신 스티커 별도 부착." },
          ],
        },
      ],
    },
    식품: {
      sections: [
        {
          title: "전면 정렬",
          rules: [
            { level: "required", text: "전면 메인 텍스트·카피 좌측 정렬 필수." },
            { level: "required", text: "로고는 우측 상단에 적당한 여백을 두고 배치. 가운데 정렬 시 FAIL." },
          ],
        },
        {
          title: "심볼 & BI",
          rules: [
            { level: "required", text: "atomy美 로고: 애터미 블루, 전면 가로폭 기준 12%." },
            { level: "info", text: "HACCP 등 인증 마크 (해당 시)." },
          ],
        },
        {
          title: "컬러박스 비율",
          rules: [
            { level: "required", text: "하단 컬러박스 세로 비율: 소형 = 1/4 (25%), 대형(가로) = 1/3 (33%)." },
          ],
        },
        {
          title: "폰트 & 사이즈",
          rules: [
            { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
            { level: "required", text: "국문 제품명: 25pt 이상. 영문 제품명: 14pt 이상. stroke 0.25~0.4pt." },
            { level: "required", text: "세트박스·파우치·단박스 주표시면(전면)에 메인 카피 없이 제품 BI만 배치." },
          ],
        },
        {
          title: "레이아웃",
          rules: [
            { level: "info", text: "컨셉 이미지: 가로폭 30~35%." },
            { level: "info", text: "카톤박스: 유통기한·제조일자 측면 인쇄." },
          ],
        },
      ],
    },
    리빙: {
      sections: [
        {
          title: "전면 정렬",
          rules: [
            { level: "required", text: "텍스트들끼리 좌측 정렬 필수. (텍스트 블록의 디자인 면 내 위치와 무관하게, 메인텍스트·영문·카피가 서로 왼쪽 기준 정렬이어야 함)" },
          ],
        },
        {
          title: "브랜드 컬러",
          rules: [
            { level: "required", text: "지정 컬러 PANTONE 317C (민트 계열) 필수. 317C 외 다른 컬러 사용 시 FAIL." },
            { level: "required", text: "atomy美 심볼 필수." },
          ],
        },
        {
          title: "심볼 & 로고 위치",
          rules: [
            { level: "required", text: "심볼 크기: 전면 가로폭 기준 20%." },
            { level: "required", text: "로고 여백: 상단 여백 = 심볼 높이와 동일. 좌우 여백 = 심볼 폭의 1/2." },
          ],
        },
        {
          title: "컬러박스 & 레이아웃",
          rules: [
            { level: "required", text: "하단 컬러박스 세로 비율: 1/5 (20%)." },
            { level: "required", text: "주표시면에 메인 카피 없이 제품 BI만 적용." },
          ],
        },
        {
          title: "폰트",
          rules: [
            { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
            { level: "info", text: "제품명: 국문·영문 31pt 이상, stroke 0.5pt. 부제목: 14pt 이상, stroke 0.3pt." },
          ],
        },
        {
          title: "인증 마크",
          rules: [
            { level: "required", text: "HACCP 마크 없음 — HACCP은 식품 카테고리 전용. 리빙에 표기 시 오류." },
            { level: "info", text: "KC 인증 (해당 제품에 한함)." },
          ],
        },
      ],
    },
    패션: {
      sections: [
        {
          title: "⚠️ 심볼 오사용 금지 (치명적 규정)",
          rules: [
            { level: "required", text: "⛔ 기존 그래픽 형태 atomy美 심볼 절대 금지. 반드시 텍스트 자음 조합 형태 [ㅇㅌㅁ] 심볼 사용. 가로폭 10%." },
          ],
        },
        {
          title: "브랜드 컬러",
          rules: [
            { level: "required", text: "지정 컬러: PANTONE 2706C 적용 필수." },
          ],
        },
        {
          title: "표기 사항",
          rules: [
            { level: "required", text: "치수 및 사이즈 표기 누락 금지 — 반드시 확인." },
            { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
          ],
        },
        {
          title: "레이아웃",
          rules: [],
        },
      ],
    },
    가전: {
      sections: [
        {
          title: "전면 정렬",
          rules: [
            { level: "required", text: "전면 메인 텍스트·카피 좌측 정렬 필수." },
            { level: "required", text: "로고는 우측 상단에 적당한 여백을 두고 배치. 가운데 정렬 시 FAIL." },
          ],
        },
        {
          title: "브랜드 컬러",
          rules: [
            { level: "required", text: "atomy美 심볼 필수 표기." },
            { level: "required", text: "지정 컬러: PANTONE 542C 적용 필수." },
          ],
        },
        {
          title: "전면 특수 규정",
          rules: [
            { level: "required", text: "영문 타이틀 명기 시: 애터미 골드 / 55pt 이상 / 선 두께 1pt 필수." },
            { level: "required", text: "국문 제품명 가로 중앙을 관통하는 애터미 블루 / 1pt 라인 필수 적용." },
          ],
        },
        {
          title: "폰트",
          rules: [
            { level: "required", text: "한글 메인 서체: 애터미 Medium 또는 Light. Bold 금지." },
          ],
        },
        {
          title: "레이아웃",
          rules: [],
        },
      ],
    },
    키즈: {
      sections: [
        {
          title: "심볼 & 이미지 비율",
          rules: [
            { level: "required", text: "atomy美 심볼 필수 표기. 가로폭 기준 32% (대형 배치)." },
            { level: "required", text: "메인 이미지: 75%." },
          ],
        },
        {
          title: "폰트 (크로스 혼용 규정)",
          rules: [
            { level: "required", text: "영문 서체: 애터미 Bold (굵게). 국문 서체: 애터미 Light (가늘게). 굵기 크로스 혼용 적용." },
            { level: "warn", text: "일반 카테고리와 반대로 영문에 Bold, 국문에 Light를 쓰는 예외 카테고리." },
          ],
        },
        {
          title: "레이아웃",
          rules: [],
        },
      ],
    },
  },
  categoryGroups: [
    {
      label: "뷰티 (Beauty)",
      value: "뷰티",
      lines: [
        { label: "프리미엄", value: "프리미엄" },
        { label: "스탠다드", value: "스탠다드" },
        { label: "색조", value: "색조" },
      ],
    },
    {
      label: "헤어 & 바디 (Hair & Body)",
      value: "헤어바디",
      lines: [
        { label: "프리미엄", value: "프리미엄" },
        { label: "스탠다드", value: "스탠다드" },
        { label: "헤어에센스", value: "헤어에센스" },
      ],
    },
    {
      label: "옴므 (Homme)",
      value: "옴므",
      lines: [
        { label: "스탠다드", value: "스탠다드" },
        { label: "색조", value: "색조" },
      ],
    },
    { label: "건강기능식품", value: "건기식", lines: [] },
    { label: "식품",          value: "식품",  lines: [] },
    { label: "리빙 (Living)", value: "리빙",  lines: [] },
    { label: "패션 (Fashion)", value: "패션", lines: [] },
    { label: "가전 (Appliances)", value: "가전", lines: [] },
    { label: "키즈 (Kids)",   value: "키즈",  lines: [] },
  ],
};

/* ─── 영어 데이터 ─────────────────────────────────────────────────────── */
const EN: GuideData = {
  guide: {
    뷰티: {
      lines: {
        프리미엄: {
          label: "Premium (ATOMY ABSOLUTE)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "All front-panel main text, copy, and logo must be horizontally centered." },
              ],
            },
            {
              title: "BI & Symbol",
              rules: [
                { level: "required", text: "[ATOMY ABSOLUTE] BI form is required. Apply Line Box structure (min. 2.0pt thickness, ABSOLUTE gold foil) on the front of the single box. Must occupy at least 33% of the single-box front." },
                { level: "required", text: "All elements on the single-box front (BI, product name, etc.) must use ABSOLUTE gold foil. Back-panel label text uses Atomy Dark Gray." },
                { level: "required", text: "Gold foil is strictly prohibited for direct printing on containers (primary product) — apply Atomy Dark Gray instead. Only the back symbol uses Atomy Blue." },
              ],
            },
            {
              title: "Font & Text",
              rules: [
                { level: "required", text: "Korean main typeface: Atomy Medium or Light. Atomy Bold is permitted for English typeface only." },
                { level: "info", text: "Line name typeface: Atomy L / Item name & copy: DINOT-L or Atomy L." },
              ],
            },
            {
              title: "Layout",
              rules: [
                { level: "info", text: "Front panel order: BI (ATOMY ABSOLUTE) → Line name → English item name → Copy → Net contents (bottom)." },
                { level: "info", text: "Equal margins on all four sides (top/bottom/left/right) are required." },
              ],
            },
          ],
        },
        스탠다드: {
          label: "Standard (Basic Line)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "All front-panel main text, copy, and logo must be horizontally centered." },
              ],
            },
            {
              title: "BI & Symbol",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Atomy Blue; width 20–25% or more of the front panel." },
                { level: "required", text: "Line Box is prohibited. Place BI directly in Atomy Dark Gray color." },
                { level: "info", text: "White or light containers → Atomy Blue BI. Colored containers → White BI. Other colors require confirmation from HQ Design Team." },
              ],
            },
            {
              title: "Point Line",
              rules: [
                { level: "required", text: "Horizontal point line on the front: Atomy Dark Gray / max 0.3pt thickness / 30% of product name length or extending to the end of the text." },
              ],
            },
            {
              title: "Font & Color",
              rules: [
                { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
                { level: "required", text: "Apply concept color to all emphasized elements: item name, Korean product name, functional claims, etc." },
                { level: "info", text: "Copy typeface: DINOT-L, 4.5pt or larger." },
              ],
            },
            {
              title: "Layout",
              rules: [
                { level: "info", text: "Equal margins on all four sides are required." },
              ],
            },
          ],
        },
        색조: {
          label: "Tinted (Makeup)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "All front-panel main text, copy, and logo must be horizontally centered." },
              ],
            },
            {
              title: "BI & Symbol",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Due to the nature of tinted products, the back symbol is applied in Dark Gray (or Gray) instead of Atomy Blue as an exception." },
                { level: "required", text: "Pact-type single box: Silver foil stamping is required on key front elements (BI, product name, line, etc.)." },
                { level: "required", text: "Container/stick type: Apply concept color to front BI and identification elements. Functional claims may use ABSOLUTE gold foil in combination." },
              ],
            },
            {
              title: "Shade Number Notation",
              rules: [
                { level: "required", text: "Shade numbers and color labels must be printed on the top panel or front/back without omission. Typeface: Atomy M or DINOT-M." },
              ],
            },
            {
              title: "Layout",
              rules: [],
            },
          ],
        },
      },
    },
    헤어바디: {
      lines: {
        프리미엄: {
          label: "Premium (ABSOLUTE Hair)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "Front main text and copy must be left-aligned. Center alignment results in immediate FAIL." },
                { level: "info", text: "Logo position: May vary depending on box/container type (upper right recommended in general)." },
              ],
            },
            {
              title: "BI & Line Box",
              rules: [
                { level: "required", text: "BI logo: ATOMY ABSOLUTE form, Atomy Dark Gray. Min. 40% width for containers/tubes; min. 50% for single boxes." },
                { level: "required", text: "Single-box front: Line Box is required below the BI (2.4pt thickness, concept color)." },
              ],
            },
            {
              title: "Product Name & Font",
              rules: [
                { level: "required", text: "Pump container front — English product name: Atomy M, concept color, 20pt or larger. Korean product name: Atomy M, concept color, 10.5pt or larger." },
                { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
                { level: "info", text: "English copy: Only the first letter capitalized." },
              ],
            },
            {
              title: "Layout",
              rules: [
                { level: "info", text: "Equal margins on all four sides are required." },
              ],
            },
          ],
        },
        스탠다드: {
          label: "Standard (Basic Body/Hair)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "Front main text and copy must be left-aligned. Center alignment results in immediate FAIL." },
                { level: "info", text: "Logo position: May vary depending on box/container type (upper right recommended in general)." },
              ],
            },
            {
              title: "Cap & Symbol",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Atomy Blue; width 20–35% of front panel." },
                { level: "required", text: "⚠️ Pump-type body products: The top cap color must be unified to white." },
              ],
            },
            {
              title: "Product Name & Point Line",
              rules: [
                { level: "required", text: "Apply concept color to both English and Korean product names." },
                { level: "required", text: "Point line thickness: 0.3pt–0.5pt." },
                { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
              ],
            },
            {
              title: "Layout",
              rules: [],
            },
          ],
        },
        헤어에센스: {
          label: "Hair Essence Specialized Line",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "Front main text and copy must be left-aligned. Center alignment results in immediate FAIL." },
                { level: "info", text: "Logo position: May vary depending on box/container type (upper right recommended in general)." },
              ],
            },
            {
              title: "BI & Symbol",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Atomy Blue; width 30–35% or more of the front panel." },
              ],
            },
            {
              title: "Exclusive Color & Graphic",
              rules: [
                { level: "required", text: "Exclusive color for English and Korean product names: Pantone 2116C must be applied. Any other color results in FAIL." },
                { level: "required", text: "⚠️ Special graphic: A Pantone 7444C wave graphic is required between the English copy and the bottom volume notation. Its size must be exactly 40% of the gap between those two elements." },
              ],
            },
            {
              title: "Single-Box Top Panel",
              rules: [
                { level: "required", text: "BI: 70–80% scale of the front BI. Atomy M typeface + left alignment required." },
              ],
            },
            {
              title: "Layout",
              rules: [
                { level: "info", text: "Equal margins on all four sides are required." },
              ],
            },
          ],
        },
      },
    },
    옴므: {
      lines: {
        스탠다드: {
          label: "Homme Standard (Basic)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "All front-panel main text, copy, and logo must be horizontally centered." },
              ],
            },
            {
              title: "Pump Container (Primary Product)",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Printed on the back of the container in Atomy Blue." },
                { level: "required", text: "Print color restriction: All text and symbols on front/back panels must use white or Atomy Blue single-color printing only." },
                { level: "required", text: "Front rectangular Line Box required: A rectangular line enclosing all text except net contents. 70% of the panel width / 1–2pt thickness." },
                { level: "required", text: "Typeface: Item name DIN OT-M (6pt or larger), English copy and net contents DIN OT-L." },
                { level: "info", text: "Back: Atomy logo min. 25% width, Korean product name Atomy M (5pt or larger, stroke 0.2pt or more), label text Noto Sans CJK KR-Regular (4.5pt or larger)." },
              ],
            },
            {
              title: "Single Box",
              rules: [
                { level: "required", text: "Front rectangular Line Box: Concept color box required. Max 70% of panel width / 1–2pt thickness." },
                { level: "required", text: "All front elements (BI, English product name, copy, net contents): Apply concept color. English product name DINOT-M / 6pt or larger." },
                { level: "required", text: "Back symbol: Atomy Blue / min. 30% width required." },
              ],
            },
            {
              title: "Layout",
              rules: [],
            },
          ],
        },
        색조: {
          label: "Homme Tinted (Makeup)",
          sections: [
            {
              title: "Front Alignment",
              rules: [
                { level: "required", text: "All front-panel main text, copy, and logo must be horizontally centered." },
              ],
            },
            {
              title: "Container (Primary Product) — Print Rules",
              rules: [
                { level: "required", text: "atomy美 symbol is required. Printed on the back of the container in white (single-color print rule)." },
                { level: "required", text: "Only white single-color printing is allowed on dark blue containers. Back symbol must also be in white." },
                { level: "required", text: "Front rectangular Line Box: White / max 80% of panel width / 1–2pt thickness." },
                { level: "required", text: "⚠️ Shade number formula: Shade numbers (*01, 02, 03) must be shown on the front. DINOT-L / stroke 0.5 / exactly 2× the size of the English product name. Non-compliance results in FAIL." },
                { level: "required", text: "Net contents notation: DINOT-L / stroke 0.2 or less / 5pt or larger." },
              ],
            },
            {
              title: "Single Box — Designated Color",
              rules: [
                { level: "required", text: "Exclusive color: Main graphic, BI, and border box must all use Pantone 2728C." },
                { level: "required", text: "Front rectangular Line Box: Pantone 2728C / max 80% of panel width / 1–2pt thickness." },
                { level: "required", text: "⚠️ Shade number formula: Required on front and top panel. Pantone 2728C / DINOT-L / stroke 0.5pt / 2× the product name size." },
                { level: "info", text: "Back: Symbol Atomy Blue min. 20%; Korean product name and functional claims in Pantone 2728C; label text in Atomy Dark Gray / Noto Sans CJK Bold / 4.5pt or larger." },
              ],
            },
          ],
        },
      },
    },
    건기식: {
      sections: [
        {
          title: "Front Alignment",
          rules: [
            { level: "required", text: "Front main text and copy must be left-aligned." },
            { level: "required", text: "Logo must be placed in the upper right with adequate margin. Center alignment results in FAIL." },
          ],
        },
        {
          title: "Symbol & BI",
          rules: [
            { level: "required", text: "atomy美 logo: Atomy Blue, 20% of the front panel width." },
            { level: "info", text: "Health functional food certification mark + GMP mark (where applicable)." },
          ],
        },
        {
          title: "Color Box Ratio",
          rules: [
            { level: "required", text: "Bottom color box height ratio: Vertical small = 1/4 (25%); horizontal medium/large = 1/3 (33%)." },
            { level: "info", text: "Color box color: Use the same sub-color as the English product name." },
          ],
        },
        {
          title: "Font & Size",
          rules: [
            { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
            { level: "required", text: "Korean product name: 25pt or larger (large format: 30pt or larger). English product name: 14pt or larger (large format: 20pt or larger). Stroke 0.3pt." },
            { level: "required", text: "⚠️ Net contents notation: Must be less than 1/2 the size of the product name." },
          ],
        },
        {
          title: "Layout",
          rules: [
            { level: "info", text: "Concept image: 30–45% of the front panel width." },
            { level: "info", text: "Carton box (outer box): Expiry date and manufacturing date should be on a separately affixed sticker rather than side-panel printing." },
          ],
        },
      ],
    },
    식품: {
      sections: [
        {
          title: "Front Alignment",
          rules: [
            { level: "required", text: "Front main text and copy must be left-aligned." },
            { level: "required", text: "Logo must be placed in the upper right with adequate margin. Center alignment results in FAIL." },
          ],
        },
        {
          title: "Symbol & BI",
          rules: [
            { level: "required", text: "atomy美 logo: Atomy Blue, 12% of the front panel width." },
            { level: "info", text: "HACCP and other certification marks (where applicable)." },
          ],
        },
        {
          title: "Color Box Ratio",
          rules: [
            { level: "required", text: "Bottom color box height ratio: Small = 1/4 (25%); large horizontal = 1/3 (33%)." },
          ],
        },
        {
          title: "Font & Size",
          rules: [
            { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
            { level: "required", text: "Korean product name: 25pt or larger. English product name: 14pt or larger. Stroke 0.25–0.4pt." },
            { level: "required", text: "Set boxes, pouches, and single-box primary display panels should show only the product BI without a main copy tagline." },
          ],
        },
        {
          title: "Layout",
          rules: [
            { level: "info", text: "Concept image: 30–35% of the front panel width." },
            { level: "info", text: "Carton box: Expiry date and manufacturing date are printed on the side panel." },
          ],
        },
      ],
    },
    리빙: {
      sections: [
        {
          title: "Front Alignment",
          rules: [
            { level: "required", text: "All text elements must be left-aligned with each other. (Regardless of the text block's position within the design surface, the main text, English text, and copy must all share a common left edge.)" },
          ],
        },
        {
          title: "Brand Color",
          rules: [
            { level: "required", text: "Designated color PANTONE 317C (mint family) is required. Any color other than 317C results in FAIL." },
            { level: "required", text: "atomy美 symbol is required." },
          ],
        },
        {
          title: "Symbol & Logo Position",
          rules: [
            { level: "required", text: "Symbol size: 20% of the front panel width." },
            { level: "required", text: "Logo margin: Top margin = same as symbol height. Left/right margins = 1/2 of the symbol width." },
          ],
        },
        {
          title: "Color Box & Layout",
          rules: [
            { level: "required", text: "Bottom color box height ratio: 1/5 (20%)." },
            { level: "required", text: "Primary display panel shows only the product BI without a main copy tagline." },
          ],
        },
        {
          title: "Font",
          rules: [
            { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
            { level: "info", text: "Product name: Korean and English 31pt or larger, stroke 0.5pt. Subtitle: 14pt or larger, stroke 0.3pt." },
          ],
        },
        {
          title: "Certification Marks",
          rules: [
            { level: "required", text: "No HACCP mark — HACCP is exclusive to the Food category. Placing it on Living products is an error." },
            { level: "info", text: "KC certification (for applicable products only)." },
          ],
        },
      ],
    },
    패션: {
      sections: [
        {
          title: "⚠️ Symbol Misuse Prohibition (Critical Rule)",
          rules: [
            { level: "required", text: "⛔ The existing graphic-form atomy美 symbol is strictly prohibited. The text consonant combination symbol [ㅇㅌㅁ] must be used. Width 10% of the panel." },
          ],
        },
        {
          title: "Brand Color",
          rules: [
            { level: "required", text: "Designated color: PANTONE 2706C must be applied." },
          ],
        },
        {
          title: "Required Notations",
          rules: [
            { level: "required", text: "Measurements and size notations must not be omitted — verify without fail." },
            { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
          ],
        },
        {
          title: "Layout",
          rules: [],
        },
      ],
    },
    가전: {
      sections: [
        {
          title: "Front Alignment",
          rules: [
            { level: "required", text: "Front main text and copy must be left-aligned." },
            { level: "required", text: "Logo must be placed in the upper right with adequate margin. Center alignment results in FAIL." },
          ],
        },
        {
          title: "Brand Color",
          rules: [
            { level: "required", text: "atomy美 symbol is required." },
            { level: "required", text: "Designated color: PANTONE 542C must be applied." },
          ],
        },
        {
          title: "Front Panel Special Rules",
          rules: [
            { level: "required", text: "When specifying an English title: Atomy Gold / 55pt or larger / 1pt stroke required." },
            { level: "required", text: "An Atomy Blue / 1pt line passing through the horizontal center of the Korean product name must be applied." },
          ],
        },
        {
          title: "Font",
          rules: [
            { level: "required", text: "Korean main typeface: Atomy Medium or Light. Bold is prohibited." },
          ],
        },
        {
          title: "Layout",
          rules: [],
        },
      ],
    },
    키즈: {
      sections: [
        {
          title: "Symbol & Image Ratio",
          rules: [
            { level: "required", text: "atomy美 symbol is required. 32% of the panel width (large placement)." },
            { level: "required", text: "Main image: 75%." },
          ],
        },
        {
          title: "Font (Cross-Weight Mix Rule)",
          rules: [
            { level: "required", text: "English typeface: Atomy Bold (heavy). Korean typeface: Atomy Light (thin). Cross-weight combination applies." },
            { level: "warn", text: "This is an exception category — Bold for English and Light for Korean, opposite of the general rule." },
          ],
        },
        {
          title: "Layout",
          rules: [],
        },
      ],
    },
  },
  categoryGroups: [
    {
      label: "Beauty",
      value: "뷰티",
      lines: [
        { label: "Premium", value: "프리미엄" },
        { label: "Standard", value: "스탠다드" },
        { label: "Tinted", value: "색조" },
      ],
    },
    {
      label: "Hair & Body",
      value: "헤어바디",
      lines: [
        { label: "Premium", value: "프리미엄" },
        { label: "Standard", value: "스탠다드" },
        { label: "Hair Essence", value: "헤어에센스" },
      ],
    },
    {
      label: "Homme",
      value: "옴므",
      lines: [
        { label: "Standard", value: "스탠다드" },
        { label: "Tinted", value: "색조" },
      ],
    },
    { label: "Health Food", value: "건기식", lines: [] },
    { label: "Food",              value: "식품",  lines: [] },
    { label: "Living",            value: "리빙",  lines: [] },
    { label: "Fashion",           value: "패션",  lines: [] },
    { label: "Appliances",        value: "가전",  lines: [] },
    { label: "Kids",              value: "키즈",  lines: [] },
  ],
};

/* ─── 내보내기 함수 ───────────────────────────────────────────────────── */
/**
 * 언어 코드를 받아 해당 언어의 가이드 데이터를 반환합니다.
 * @param lang - 'ko' (한국어) 또는 'en' (영어)
 */
export function getGuideData(lang: "ko" | "en"): GuideData {
  return lang === "en" ? EN : KO;
}
