"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n/context";
import { LanguageSelector } from "@/components/LanguageSelector";

const BLUE = "#00B5EF";

type StatusType = "PASS" | "WARN" | "FAIL";

interface DetailItem {
  score: number;
  max_score: number;
  status: StatusType;
  feedback: string;
}

interface ScoreResult {
  evaluation_result: "PASS" | "FAIL";
  total_score: number;
  score?: number;
  category_detected: string;
  line_type_detected: string;
  product_type_detected: string;
  details: {
    identity_and_symbol_check: DetailItem;
    color_and_printing_rules: DetailItem;
    font_and_layout_check: DetailItem;
    graphic_and_legal_mark: DetailItem;
  };
  layout_mismatch: boolean;
  improvement_points: string[];
  aesthetic_tips: string[];
}

const STATUS_STYLE: Record<StatusType, { bg: string; color: string; border: string; accent: string; label: string }> = {
  PASS: { bg: "#f0fdf4", color: "#16a34a", border: "#bbf7d0", accent: "#16a34a", label: "✅ PASS" },
  WARN: { bg: "#fffbeb", color: "#b45309", border: "#fde68a", accent: "#d97706", label: "⚠️ WARN" },
  FAIL: { bg: "#fef2f2", color: "#dc2626", border: "#fecaca", accent: "#dc2626", label: "❌ FAIL" },
};

const CATEGORY_VALUES = ["뷰티", "헤어바디", "옴므", "건기식", "식품", "리빙", "패션", "가전", "키즈"] as const;
const LINES_BY_CATEGORY: Record<string, string[]> = {
  뷰티:    ["프리미엄", "스탠다드", "색조"],
  헤어바디: ["프리미엄", "스탠다드", "헤어에센스"],
  옴므:    ["스탠다드", "색조"],
};
const PRODUCT_TYPES = ["단박스", "세트박스", "카톤박스", "용기", "파우치"] as const;
type ProductType = (typeof PRODUCT_TYPES)[number];

/* ── 스켈레톤 컴포넌트 ────────────────────────────────────────── */
function SkeletonCard() {
  return (
    <div style={{ padding: "20px 18px", background: "#fff", border: "1px solid #e5e7eb", borderRadius: 12, borderTop: "4px solid #e5e7eb" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <div className="skeleton" style={{ width: 160, height: 16 }} />
        <div className="skeleton" style={{ width: 60, height: 20, borderRadius: 4 }} />
      </div>
      <div className="skeleton" style={{ height: 8, borderRadius: 4, marginBottom: 10 }} />
      <div className="skeleton" style={{ height: 14, width: "90%" }} />
      <div className="skeleton" style={{ height: 14, width: "70%", marginTop: 6 }} />
    </div>
  );
}

function ResultSkeleton() {
  return (
    <div style={{ marginTop: 32 }}>
      {/* 종합 판정 스켈레톤 */}
      <div style={{ padding: 28, textAlign: "center", background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 12, marginBottom: 24 }}>
        <div className="skeleton" style={{ width: 120, height: 36, borderRadius: 8, margin: "0 auto 12px" }} />
        <div className="skeleton" style={{ width: 80, height: 56, borderRadius: 8, margin: "0 auto 12px" }} />
        <div style={{ display: "flex", justifyContent: "center", gap: 8 }}>
          {[80, 60, 70].map((w, i) => (
            <div key={i} className="skeleton" style={{ width: w, height: 24, borderRadius: 12 }} />
          ))}
        </div>
      </div>
      {/* 세부 항목 스켈레톤 */}
      <div className="skeleton" style={{ width: 120, height: 18, marginBottom: 12, borderRadius: 4 }} />
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {[0, 1, 2, 3].map((i) => <SkeletonCard key={i} />)}
      </div>
    </div>
  );
}

export default function CheckPage() {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile]             = useState<File | null>(null);
  const [preview, setPreview]       = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [selectedLine, setSelectedLine]         = useState<string>("");
  const [selectedProduct, setSelectedProduct]   = useState<ProductType | "">("");
  const [isOverseas, setIsOverseas]             = useState(false);

  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState<ScoreResult | null>(null);
  const [error, setError]         = useState("");
  const [pasteToast, setPasteToast] = useState(false);

  const detailLabels = {
    identity_and_symbol_check: t("detail.identity"),
    color_and_printing_rules:  t("detail.color"),
    font_and_layout_check:     t("detail.font"),
    graphic_and_legal_mark:    t("detail.graphic"),
  } as const;

  const categoryGroups = CATEGORY_VALUES.map((val) => ({
    value: val,
    label: t(`cat.${val}` as Parameters<typeof t>[0]),
    lines: (LINES_BY_CATEGORY[val] ?? []).map((line) => ({
      value: line,
      label: t(`line.${val}.${line}` as Parameters<typeof t>[0]),
    })),
  }));

  const applyFile = (f: File) => {
    setFile(f);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError("");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) applyFile(f);
  };

  const handleDragEnter = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); };
  const handleDragOver  = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setIsDragging(true); };
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    if (!e.currentTarget.contains(e.relatedTarget as Node)) setIsDragging(false);
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation(); setIsDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (!f) return;
    const ext = f.name.split(".").pop()?.toLowerCase() ?? "";
    const validMime = ["image/jpeg","image/jpg","image/png","image/webp","application/pdf"].includes(f.type);
    const validExt  = ["jpg","jpeg","png","webp","pdf"].includes(ext);
    if (validMime || validExt) applyFile(f);
  };

  /* ── 클립보드 붙여넣기 지원 ── */
  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (const item of Array.from(items)) {
        if (item.type.startsWith("image/")) {
          const f = item.getAsFile();
          if (!f) continue;
          setFile(f);
          setPreview(URL.createObjectURL(f));
          setResult(null);
          setError("");
          setPasteToast(true);
          setTimeout(() => setPasteToast(false), 2500);
          break;
        }
      }
    };
    window.addEventListener("paste", handlePaste);
    return () => window.removeEventListener("paste", handlePaste);
  }, []); // state setters are stable

  const handleCategoryChange = (cat: string) => {
    setSelectedCategory(cat);
    setSelectedLine("");
    setResult(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("image", file!);
      fd.append("category", selectedCategory);
      fd.append("line_type", selectedLine);
      fd.append("product_type", selectedProduct);
      fd.append("is_overseas", isOverseas ? "true" : "false");
      const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${api}/api/score`, { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "채점 중 오류가 발생했습니다.");
      }
      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const currentGroup = categoryGroups.find((g) => g.value === selectedCategory);
  const hasLines = (currentGroup?.lines?.length ?? 0) > 0;
  const canSubmit = !!file && !!selectedCategory && (!hasLines || !!selectedLine) && !!selectedProduct && !loading;
  const overallStyle = result
    ? result.evaluation_result === "PASS"
      ? { bg: "#f0fdf4", color: "#16a34a", border: "#16a34a" }
      : { bg: "#fef2f2", color: "#dc2626", border: "#dc2626" }
    : null;

  /* ── 공통 라디오 칩 스타일 헬퍼 ─────────── */
  const chipStyle = (sel: boolean, size: "md" | "sm" = "md"): React.CSSProperties => ({
    display: "flex", alignItems: "center", gap: 6,
    padding: size === "md" ? "8px 16px" : "6px 14px",
    border: `2px solid ${sel ? BLUE : "#e5e7eb"}`,
    borderRadius: 8,
    background: sel ? "#e0f5fd" : "#fff",
    cursor: "pointer",
    fontWeight: sel ? 700 : 400,
    color: sel ? "#0077a8" : "#374151",
    fontSize: size === "md" ? "0.875rem" : "0.84rem",
    userSelect: "none" as const,
    boxShadow: sel ? `0 0 0 3px rgba(0,181,239,0.15)` : "none",
    transition: "all 0.12s ease",
  });

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "32px 24px", fontFamily: "sans-serif", color: "#1a1a1a" }}>

      {/* 헤더 */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", borderBottom: `3px solid ${BLUE}`, paddingBottom: 16, marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
          <Link href="/" style={{ color: BLUE, textDecoration: "none", fontSize: "1.25rem", paddingTop: 2 }}>←</Link>
          <div>
            <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, letterSpacing: "-0.01em" }}>{t("check.title")}</h1>
            <p style={{ margin: "6px 0 0", color: "#6b7280", fontSize: "0.875rem", lineHeight: 1.5 }}>
              {t("check.subtitle")}
            </p>
          </div>
        </div>
        <div style={{ flexShrink: 0, marginLeft: 16, paddingTop: 4 }}>
          <LanguageSelector variant="dark" />
        </div>
      </div>

      <form onSubmit={handleSubmit}>

        {/* STEP 1 */}
        <section style={{ marginBottom: 28 }}>
          <h2 style={{ fontSize: "0.8rem", fontWeight: 700, margin: "0 0 12px", color: "#374151", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            {t("check.step1.title")}
          </h2>

          <div style={{ background: "#f0f9ff", border: "1px solid #bae6fd", borderRadius: 8, padding: "10px 14px", marginBottom: 12, fontSize: "0.8rem", color: "#0369a1", lineHeight: 1.6 }}>
            <strong>{t("check.step1.guide.title")}</strong>
            <ul style={{ margin: "4px 0 0", paddingLeft: 20 }}>
              <li>{t("check.step1.guide.best")}</li>
              <li>{t("check.step1.guide.ok")}</li>
              <li>{t("check.step1.guide.bad")}</li>
            </ul>
          </div>

          <div
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
            style={{
              position: "relative",
              display: "block",
              border: `2px dashed ${isDragging ? BLUE : "#d1d5db"}`,
              borderRadius: 10,
              padding: "32px 24px",
              textAlign: "center",
              background: isDragging ? "#e0f5fd" : "#f9fafb",
              cursor: "pointer",
              transition: "all 0.15s ease",
              boxShadow: isDragging ? `0 0 0 4px rgba(0,181,239,0.15)` : "none",
            }}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp,application/pdf" onChange={handleFileChange} style={{ display: "none" }} />
            {pasteToast && (
              <div style={{
                position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)",
                background: "#16a34a", color: "#fff", fontSize: "0.8rem", fontWeight: 600,
                padding: "6px 14px", borderRadius: 20, whiteSpace: "nowrap",
                boxShadow: "0 2px 8px rgba(0,0,0,0.15)", pointerEvents: "none",
                animation: "fadeInUp 0.2s ease",
              }}>
                📋 {t("check.step1.pasted")}
              </div>
            )}
            {!file ? (
              <>
                <div style={{ fontSize: "2rem", marginBottom: 8 }}>🖼️</div>
                <div style={{ fontSize: "0.875rem" }}>
                  <span style={{ color: BLUE, fontWeight: 700 }}>{t("check.step1.select")}</span>
                  <span style={{ color: "#6b7280" }}> {t("check.step1.drag")}</span>
                </div>
                <div style={{ marginTop: 8, fontSize: "0.78rem", color: "#9ca3af" }}>
                  {t("check.step1.paste.hint")}
                </div>
              </>
            ) : (
              <p style={{ margin: 0, fontSize: "0.875rem", color: "#374151", fontWeight: 500 }}>
                ✅ {file.name} <span style={{ color: "#9ca3af", fontWeight: 400 }}>({(file.size / 1024 / 1024).toFixed(2)} MB)</span> — {t("check.step1.change")}
              </p>
            )}
          </div>

          {preview && (
            <div style={{ textAlign: "center", marginTop: 14 }}>
              {file?.name.toLowerCase().endsWith(".pdf") ? (
                <div style={{ padding: "16px 20px", background: "#fef3c7", border: "1px solid #fde68a", borderRadius: 8, fontSize: "0.875rem", color: "#92400e", textAlign: "left" }}>
                  <div style={{ fontWeight: 700, marginBottom: 6 }}>{t("check.step1.pdf.title")}</div>
                  <div style={{ lineHeight: 1.7 }}>{t("check.step1.pdf.desc")}</div>
                </div>
              ) : (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img src={preview} alt="preview" style={{ maxWidth: "100%", maxHeight: 280, objectFit: "contain", borderRadius: 10, border: "1px solid #e5e7eb", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }} />
              )}
            </div>
          )}
        </section>

        {/* STEP 2 */}
        <section style={{ marginBottom: 28, background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 12, padding: "20px 24px" }}>
          <h2 style={{ fontSize: "0.8rem", fontWeight: 700, margin: "0 0 16px", color: "#374151", letterSpacing: "0.06em", textTransform: "uppercase" }}>
            {t("check.step2.title")}
          </h2>

          {/* 카테고리 */}
          <div style={{ marginBottom: 16 }}>
            <p style={{ margin: "0 0 8px", fontSize: "0.72rem", fontWeight: 600, color: "#9ca3af", letterSpacing: "0.05em", textTransform: "uppercase" }}>{t("check.step2.category")}</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {categoryGroups.map((group) => {
                const sel = selectedCategory === group.value;
                return (
                  <label key={group.value} className="chip-label" style={chipStyle(sel)}>
                    <input type="radio" name="category" value={group.value} checked={sel} onChange={() => handleCategoryChange(group.value)} style={{ display: "none" }} />
                    {sel && <span style={{ color: BLUE, fontSize: "0.8rem" }}>✓</span>}
                    {group.label}
                  </label>
                );
              })}
            </div>
          </div>

          {/* 라인 */}
          {currentGroup && hasLines && (
            <div style={{ marginBottom: 16 }}>
              <p style={{ margin: "0 0 8px", fontSize: "0.72rem", fontWeight: 600, color: "#9ca3af", letterSpacing: "0.05em", textTransform: "uppercase" }}>{t("check.step2.line")}</p>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {currentGroup.lines.map((line) => {
                  const sel = selectedLine === line.value;
                  return (
                    <label key={line.value} className="chip-label" style={chipStyle(sel, "sm")}>
                      <input type="radio" name="line" value={line.value} checked={sel} onChange={() => { setSelectedLine(line.value); setResult(null); }} style={{ display: "none" }} />
                      {sel && <span style={{ color: BLUE, fontSize: "0.75rem" }}>✓</span>}
                      {line.label}
                    </label>
                  );
                })}
              </div>
            </div>
          )}

          {/* 용기 타입 */}
          <div style={{ marginBottom: 16 }}>
            <p style={{ margin: "0 0 8px", fontSize: "0.72rem", fontWeight: 600, color: "#9ca3af", letterSpacing: "0.05em", textTransform: "uppercase" }}>{t("check.step2.product")}</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {PRODUCT_TYPES.map((pt) => {
                const sel = selectedProduct === pt;
                const ptLabel = t(`pt.${pt}` as Parameters<typeof t>[0]);
                return (
                  <label key={pt} className="chip-label" style={chipStyle(sel, "sm")}>
                    <input type="radio" name="product_type" value={pt} checked={sel} onChange={() => { setSelectedProduct(pt); setResult(null); }} style={{ display: "none" }} />
                    {sel && <span style={{ color: BLUE, fontSize: "0.75rem" }}>✓</span>}
                    {ptLabel}
                  </label>
                );
              })}
            </div>
          </div>

          {/* 해외전용 체크박스 */}
          <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: 16 }}>
            <label style={{ display: "flex", alignItems: "flex-start", gap: 10, cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={isOverseas}
                onChange={(e) => { setIsOverseas(e.target.checked); setResult(null); }}
                style={{ marginTop: 3, width: 16, height: 16, accentColor: BLUE, cursor: "pointer", flexShrink: 0 }}
              />
              <div>
                <span style={{ fontWeight: 600, fontSize: "0.875rem", color: "#374151" }}>{t("check.overseas.label")}</span>
                <p style={{ margin: "4px 0 0", fontSize: "0.78rem", color: "#6b7280", lineHeight: 1.55 }}>{t("check.overseas.desc")}</p>
              </div>
            </label>
          </div>
        </section>

        {!canSubmit && file && (
          <p style={{ color: "#d97706", fontSize: "0.85rem", marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
            {t("check.warn")}
          </p>
        )}

        <button
          type="submit"
          disabled={!canSubmit}
          className={canSubmit ? "btn-primary" : ""}
          style={{
            width: "100%",
            padding: "14px",
            background: canSubmit ? BLUE : "#d1d5db",
            color: canSubmit ? "#fff" : "#9ca3af",
            border: "none",
            borderRadius: 10,
            fontSize: "1rem",
            fontWeight: 700,
            cursor: canSubmit ? "pointer" : "not-allowed",
            letterSpacing: "0.02em",
          }}
        >
          {loading ? t("check.loading") : t("check.submit")}
        </button>
      </form>

      {/* 에러 */}
      {error && (
        <div style={{ marginTop: 16, padding: "16px 20px", background: "#fef2f2", border: "1px solid #fecaca", borderTop: "4px solid #dc2626", borderRadius: 10 }}>
          <div style={{ fontWeight: 700, color: "#dc2626", fontSize: "0.9rem", marginBottom: 6 }}>⚠️ 판독 오류</div>
          <p style={{ margin: "0 0 12px", color: "#991b1b", fontSize: "0.875rem", lineHeight: 1.6 }}>{error}</p>
          <button
            onClick={() => { setError(""); }}
            style={{ padding: "6px 16px", background: "#dc2626", color: "#fff", border: "none", borderRadius: 6, fontSize: "0.82rem", fontWeight: 600, cursor: "pointer" }}
          >
            닫기
          </button>
        </div>
      )}

      {/* 로딩 스켈레톤 */}
      {loading && <ResultSkeleton />}

      {/* 결과 */}
      {result && overallStyle && !loading && (
        <div style={{ marginTop: 32 }}>

          {/* 종합 판정 카드 */}
          <div style={{
            padding: "28px 24px",
            textAlign: "center",
            background: overallStyle.bg,
            border: `1px solid ${overallStyle.border}`,
            borderTop: `4px solid ${overallStyle.border}`,
            borderRadius: 12,
            marginBottom: 12,
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
          }}>
            <div style={{ fontSize: "2.25rem", fontWeight: 900, lineHeight: 1, color: overallStyle.color }}>
              {result.evaluation_result === "PASS" ? "✅ PASS" : "❌ FAIL"}
            </div>
            <div style={{ fontSize: "3.5rem", fontWeight: 900, marginTop: 4, color: overallStyle.color, lineHeight: 1.1 }}>
              {result.total_score ?? result.score}
              <span style={{ fontSize: "1.1rem", fontWeight: 500, color: overallStyle.color, opacity: 0.7 }}>점</span>
            </div>
            {result.layout_mismatch && (
              <div style={{ marginTop: 10, padding: "6px 14px", background: "#fef2f2", border: "1px solid #dc2626", borderRadius: 6, fontSize: "0.82rem", color: "#dc2626", fontWeight: 600, display: "inline-block" }}>
                {t("result.mismatch")}
              </div>
            )}
            <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
              {[result.category_detected, result.line_type_detected, result.product_type_detected].map((tag, i) =>
                tag ? (
                  <span key={i} style={{ padding: "4px 12px", background: "#fff", border: `1px solid ${overallStyle.border}`, borderRadius: 20, fontSize: "0.8rem", color: overallStyle.color, fontWeight: 600 }}>
                    {tag}
                  </span>
                ) : null
              )}
            </div>
          </div>

          {/* 면책 고지 — 점수 바로 아래 */}
          <div style={{ marginBottom: 24, padding: "12px 16px", background: "#fffbeb", border: "1px solid #fde68a", borderLeft: "4px solid #f59e0b", borderRadius: 8 }}>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "#78350f", lineHeight: 1.75, whiteSpace: "pre-line", fontWeight: 500 }}>
              {t("result.disclaimer")}
            </p>
          </div>

          {/* 세부 항목 */}
          <h3 style={{ fontSize: "0.875rem", fontWeight: 700, margin: "0 0 12px", color: "#374151", letterSpacing: "0.04em", textTransform: "uppercase" }}>{t("result.details")}</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 24 }}>
            {(Object.keys(result.details) as Array<keyof ScoreResult["details"]>).map((key) => {
              const item = result.details[key];
              const s = STATUS_STYLE[item.status];
              const pct = item.max_score ? Math.round((item.score ?? 0) / item.max_score * 100) : 0;
              return (
                <div key={key} className="result-card" style={{
                  padding: "16px 18px",
                  background: s.bg,
                  border: `1px solid ${s.border}`,
                  borderTop: `4px solid ${s.accent}`,
                  borderRadius: 10,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                    <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#1a1a1a" }}>{detailLabels[key]}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span style={{ fontWeight: 800, fontSize: "1rem", color: s.color }}>
                        {item.score ?? "–"}<span style={{ fontSize: "0.72rem", fontWeight: 500, color: "#6b7280" }}>/{item.max_score}</span>
                      </span>
                      <span style={{ padding: "3px 10px", borderRadius: 4, fontSize: "0.72rem", fontWeight: 700, background: "#fff", color: s.color, border: `1px solid ${s.border}` }}>
                        {s.label}
                      </span>
                    </div>
                  </div>
                  {item.max_score && (
                    <div style={{ height: 8, background: "#e5e7eb", borderRadius: 4, marginBottom: 10, overflow: "hidden" }}>
                      <div style={{ height: "100%", width: `${pct}%`, background: s.accent, borderRadius: 4, transition: "width 0.6s ease" }} />
                    </div>
                  )}
                  <p style={{ margin: 0, color: "#374151", fontSize: "0.875rem", lineHeight: 1.65 }}>{item.feedback}</p>
                </div>
              );
            })}
          </div>

          {/* 개선 포인트 */}
          {result.improvement_points.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: "0.875rem", fontWeight: 700, margin: "0 0 10px", color: "#374151", letterSpacing: "0.04em", textTransform: "uppercase" }}>{t("result.improvements")}</h3>
              <ul style={{ margin: 0, padding: "16px 16px 16px 28px", background: "#fffbeb", border: "1px solid #fde68a", borderTop: "4px solid #d97706", borderRadius: 10, lineHeight: 2 }}>
                {result.improvement_points.map((point, i) => (
                  <li key={i} style={{ color: "#92400e", fontSize: "0.875rem" }}>{point}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 디자이너 조언 */}
          {result.aesthetic_tips && result.aesthetic_tips.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <h3 style={{ fontSize: "0.875rem", fontWeight: 700, margin: "0 0 10px", color: "#374151", letterSpacing: "0.04em", textTransform: "uppercase" }}>{t("result.aesthetic.title")}</h3>
              <div style={{ padding: "16px 20px", background: "linear-gradient(135deg, #faf5ff 0%, #f0f9ff 100%)", border: "1px solid #e9d5ff", borderTop: "4px solid #a855f7", borderRadius: 10 }}>
                <ul style={{ margin: 0, padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
                  {result.aesthetic_tips.map((tip, i) => (
                    <li key={i} style={{ display: "flex", gap: 10, fontSize: "0.875rem", color: "#4b5563", lineHeight: 1.65 }}>
                      <span style={{ flexShrink: 0, color: "#a855f7", fontWeight: 700 }}>{i + 1}.</span>
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* 하단 powered by */}
          <div style={{ borderTop: "1px solid #e5e7eb", paddingTop: 16, marginTop: 8, textAlign: "center" }}>
            <p style={{ margin: 0, fontSize: "0.68rem", color: "#c4c9d4", letterSpacing: "0.04em" }}>
              {t("result.powered")}
            </p>
          </div>
        </div>
      )}
    </main>
  );
}
