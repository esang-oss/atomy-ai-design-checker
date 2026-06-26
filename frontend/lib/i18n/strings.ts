const ko = {
  /* ── 공통 ─────────────────────────────── */
  "lang.ko": "한국어",
  "lang.en": "English",

  /* ── 홈 ──────────────────────────────── */
  "home.title": "애터미 디자인 AI가이드",
  "home.subtitle": "패키지 디자인 가이드 준수도 자동 채점",
  "home.checker.title": "디자인 판독기",
  "home.checker.desc1": "이미지 업로드 → AI 채점",
  "home.checker.desc2": "항목별 피드백 제공",
  "home.guide.title": "디자인 가이드",
  "home.guide.desc1": "카테고리별 규정 전체 조회",
  "home.guide.desc2": "체크리스트 형식으로 확인",
  "home.footer": "2021 Atomy Package Design Guide VER 3.0 기반",

  /* ── 판독기 ───────────────────────────── */
  "check.title": "애터미 디자인 판독기",
  "check.subtitle": "이미지 업로드 후 카테고리를 선택하면 AI가 가이드라인 준수 여부를 판독합니다.",
  "check.step1.title": "STEP 1   디자인 이미지 업로드",
  "check.step1.guide.title": "📌 정확한 판독을 위한 이미지 가이드",
  "check.step1.guide.best": "최적: 디자인 시안(AI 파일)에서 캡처한 전면 평면 이미지",
  "check.step1.guide.ok": "가능: 실제 제품을 정면 직각으로 촬영한 사진",
  "check.step1.guide.bad": "비추천: 비스듬한 각도·원근감 있는 사진 (비율 왜곡으로 판독 정확도 저하)",
  "check.step1.select": "이미지 파일 선택",
  "check.step1.drag": "또는 드래그 (JPG · PNG · WEBP · PDF · 최대 20MB)",
  "check.step1.paste.hint": "Ctrl+V / ⌘V 로 붙여넣기도 가능합니다",
  "check.step1.pasted": "이미지 붙여넣기 완료",
  "check.step1.change": "클릭하여 변경",
  "check.step1.pdf.title": "📄 PDF 파일 감지",
  "check.step1.pdf.desc": "첫 번째 페이지에서 전면(Front) 패널을 자동 식별하여 판독합니다. 전개도·라벨 전체가 포함된 경우, 제품명·BI가 집중된 면을 전면으로 판단합니다.",
  "check.step2.title": "STEP 2   카테고리 선택",
  "check.step2.category": "카테고리",
  "check.step2.line": "라인",
  "check.step2.product": "용기 / 제품 타입",
  "check.overseas.label": "해외전용 디자인",
  "check.overseas.desc": "체크 시, 현지 언어 크기가 국문·영문보다 클 수 있는 규정 예외가 적용됩니다.",
  "check.warn": "⚠️ 카테고리·라인·용기 타입을 모두 선택해주세요.",
  "check.submit": "판독 시작",
  "check.loading": "판독 중… (약 15~30초 소요)",

  /* ── 판독기 — 결과 ────────────────────── */
  "result.details": "세부 판독 결과",
  "result.improvements": "🔧 개선 필요 사항",
  "result.aesthetic.title": "🎨 디자이너 조언",
  "result.aesthetic.bonus.pos": "미적 완성도 보정",
  "result.aesthetic.bonus.neg": "미적 완성도 보정",
  "result.disclaimer": "⚠️ 본 판독 결과는 애터미 패키지 디자인 가이드 준수 여부를 사전 점검하기 위한 참고 자료입니다.\n디자인 시안 확정 전, 반드시 본사 디자인팀의 공식 검토 및 컨펌을 받으시기 바랍니다.",
  "result.powered": "ATOMY AI DESIGN CHECKER · Powered by Gemini Vision AI",
  "result.mismatch": "⚠️ 레이아웃 불일치 — 선택한 용기 타입과 디자인 구조가 맞지 않습니다",

  /* ── 세부 항목 레이블 ─────────────────── */
  "detail.identity": "심볼 & 아이덴티티",
  "detail.color": "컬러 & 인쇄 규정",
  "detail.font": "폰트 & 레이아웃",
  "detail.graphic": "그래픽 & 법적 마크",

  /* ── 가이드 ───────────────────────────── */
  "guide.title": "애터미 디자인 가이드",
  "guide.subtitle": "카테고리를 선택하면 해당 디자인 규정을 확인할 수 있습니다.",
  "guide.category": "카테고리",
  "guide.line": "라인",
  "guide.select.placeholder": "위에서 카테고리를 선택해주세요",
  "guide.select.line": "라인을 선택해주세요",
  "guide.legend.required": "✅ 필수 규정",
  "guide.legend.warn": "⚠️ 주의 사항",
  "guide.legend.info": "ℹ️ 참고 사항",
  "guide.common.title": "📌 전 카테고리 공통 원칙",
  "guide.common.rule1": "한글 주표시면 서체: 반드시 애터미 Medium 또는 Light — Bold 사용 절대 금지",
  "guide.common.rule2": "AI 판독 결과는 참고용 — 최종 컨펌은 반드시 본사 디자인팀 공식 확인 필요",

  /* ── 카테고리 레이블 ──────────────────── */
  "cat.뷰티": "뷰티 (Beauty)",
  "cat.헤어바디": "헤어 & 바디 (Hair & Body)",
  "cat.옴므": "옴므 (Homme)",
  "cat.건기식": "건강기능식품",
  "cat.식품": "식품",
  "cat.리빙": "리빙 (Living)",
  "cat.패션": "패션 (Fashion)",
  "cat.가전": "가전 (Appliances)",
  "cat.키즈": "키즈 (Kids)",

  /* ── 라인 레이블 (카테고리별) ─────────── */
  "line.뷰티.프리미엄": "프리미엄 — 애터미 앱솔루트",
  "line.뷰티.스탠다드": "스탠다드 — 기초라인",
  "line.뷰티.색조": "색조 — 메이크업",
  "line.헤어바디.프리미엄": "프리미엄 — 앱솔루트 헤어",
  "line.헤어바디.스탠다드": "스탠다드 — 기초 바디/헤어",
  "line.헤어바디.헤어에센스": "헤어에센스 특화 라인",
  "line.옴므.스탠다드": "스탠다드 — 기초",
  "line.옴므.색조": "색조 — 메이크업",

  /* ── 용기 / 제품 타입 ────────────────── */
  "pt.단박스": "단박스",
  "pt.세트박스": "세트박스",
  "pt.카톤박스": "카톤박스",
  "pt.용기": "용기",
  "pt.파우치": "파우치",
};

const en: typeof ko = {
  /* ── Common ──────────────────────────── */
  "lang.ko": "한국어",
  "lang.en": "English",

  /* ── Home ────────────────────────────── */
  "home.title": "Atomy Design AI Guide",
  "home.subtitle": "Automated Package Design Guideline Compliance Scoring",
  "home.checker.title": "Design Checker",
  "home.checker.desc1": "Upload Image → AI Scoring",
  "home.checker.desc2": "Item-by-item Feedback",
  "home.guide.title": "Design Guide",
  "home.guide.desc1": "View All Category Regulations",
  "home.guide.desc2": "Checklist Format",
  "home.footer": "Based on 2021 Atomy Package Design Guide VER 3.0",

  /* ── Checker ─────────────────────────── */
  "check.title": "Atomy Design Checker",
  "check.subtitle": "Upload an image and select a category for AI guideline compliance analysis.",
  "check.step1.title": "STEP 1   Upload Design Image",
  "check.step1.guide.title": "📌 Image Guide for Accurate Analysis",
  "check.step1.guide.best": "Best: Flat front-face image captured from design file (AI file)",
  "check.step1.guide.ok": "OK: Photo taken straight-on at 90° from the actual product",
  "check.step1.guide.bad": "Not recommended: Angled or perspective photos (reduces accuracy due to distortion)",
  "check.step1.select": "Select Image File",
  "check.step1.drag": "or drag & drop (JPG · PNG · WEBP · PDF · Max 20MB)",
  "check.step1.paste.hint": "You can also paste with Ctrl+V / ⌘V",
  "check.step1.pasted": "Image pasted",
  "check.step1.change": "Click to change",
  "check.step1.pdf.title": "📄 PDF File Detected",
  "check.step1.pdf.desc": "The front panel will be automatically identified from the first page. For full die-cut or label layouts, the face with the densest product name and BI will be treated as the front.",
  "check.step2.title": "STEP 2   Select Category",
  "check.step2.category": "Category",
  "check.step2.line": "Line",
  "check.step2.product": "Container / Product Type",
  "check.overseas.label": "Overseas Exclusive Design",
  "check.overseas.desc": "When checked, exceptions apply for rules requiring Korean text to be the largest — local language may be larger.",
  "check.warn": "⚠️ Please select category, line, and container type.",
  "check.submit": "Start Analysis",
  "check.loading": "Analyzing… (approx. 15–30 seconds)",

  /* ── Checker — Results ───────────────── */
  "result.details": "Detailed Analysis Results",
  "result.improvements": "🔧 Improvements Required",
  "result.aesthetic.title": "🎨 Designer's Eye",
  "result.aesthetic.bonus.pos": "Aesthetic quality bonus",
  "result.aesthetic.bonus.neg": "Aesthetic quality deduction",
  "result.disclaimer": "⚠️ This result is for preliminary reference only, to verify compliance with Atomy package design guidelines.\nBefore finalizing any design, official review and approval from the HQ Design Team is mandatory.",
  "result.powered": "ATOMY AI DESIGN CHECKER · Powered by Gemini Vision AI",
  "result.mismatch": "⚠️ Layout mismatch — selected container type does not match the design structure",

  /* ── Detail labels ───────────────────── */
  "detail.identity": "Symbol & Identity",
  "detail.color": "Color & Print Rules",
  "detail.font": "Font & Layout",
  "detail.graphic": "Graphics & Legal Marks",

  /* ── Guide ───────────────────────────── */
  "guide.title": "Atomy Design Guide",
  "guide.subtitle": "Select a category to view the applicable design regulations.",
  "guide.category": "Category",
  "guide.line": "Line",
  "guide.select.placeholder": "Please select a category above",
  "guide.select.line": "Please select a line",
  "guide.legend.required": "✅ Required",
  "guide.legend.warn": "⚠️ Caution",
  "guide.legend.info": "ℹ️ Reference",
  "guide.common.title": "📌 Common Principles (All Categories)",
  "guide.common.rule1": "Korean main display typeface: Atomy Medium or Light only — Bold strictly prohibited",
  "guide.common.rule2": "AI analysis results are for reference only — final approval must be confirmed by HQ Design Team",

  /* ── Category labels ─────────────────── */
  "cat.뷰티": "Beauty",
  "cat.헤어바디": "Hair & Body",
  "cat.옴므": "Homme",
  "cat.건기식": "Health Food",
  "cat.식품": "Food",
  "cat.리빙": "Living",
  "cat.패션": "Fashion",
  "cat.가전": "Appliances",
  "cat.키즈": "Kids",

  /* ── Line labels ─────────────────────── */
  "line.뷰티.프리미엄": "Premium — Atomy Absolute",
  "line.뷰티.스탠다드": "Standard — Basic Line",
  "line.뷰티.색조": "Tinted — Makeup",
  "line.헤어바디.프리미엄": "Premium — Absolute Hair",
  "line.헤어바디.스탠다드": "Standard — Basic Body/Hair",
  "line.헤어바디.헤어에센스": "Hair Essence Specialized",
  "line.옴므.스탠다드": "Standard — Basic",
  "line.옴므.색조": "Tinted — Makeup",

  /* ── Container / product types ───────── */
  "pt.단박스": "Single Box",
  "pt.세트박스": "Set Box",
  "pt.카톤박스": "Carton Box",
  "pt.용기": "Container",
  "pt.파우치": "Pouch",
};

export const strings = { ko, en };
