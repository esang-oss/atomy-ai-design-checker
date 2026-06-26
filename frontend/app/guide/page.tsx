"use client";

import Link from "next/link";
import { useState } from "react";
import { useI18n } from "@/lib/i18n/context";
import { LanguageSelector } from "@/components/LanguageSelector";
import { getGuideData } from "@/lib/i18n/guide-data";

const BLUE = "#00B5EF";

type RuleLevel = "required" | "warn" | "info";

const LEVEL_STYLE: Record<RuleLevel, { bg: string; border: string; accent: string; color: string; icon: string }> = {
  required: { bg: "#f0fdfa", border: "#99f6e4", accent: "#0d9488", color: "#0f766e", icon: "✅" },
  warn:     { bg: "#fffbeb", border: "#fde68a", accent: "#d97706", color: "#92400e", icon: "⚠️" },
  info:     { bg: "#f0f9ff", border: "#bae6fd", accent: "#0ea5e9", color: "#0c4a6e", icon: "ℹ️" },
};

export default function GuidePage() {
  const { lang, t } = useI18n();
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedLine, setSelectedLine]         = useState("");

  const { guide, categoryGroups } = getGuideData(lang);

  const currentGroup = categoryGroups.find((g) => g.value === selectedCategory);
  const hasLines = (currentGroup?.lines?.length ?? 0) > 0;

  const handleCategoryChange = (cat: string) => {
    setSelectedCategory(cat);
    setSelectedLine("");
  };

  const sections = (() => {
    if (!selectedCategory) return [];
    const cat = guide[selectedCategory];
    if (!cat) return [];
    if (cat.sections && cat.sections.length > 0) return cat.sections;
    if (!selectedLine || !cat.lines) return [];
    return cat.lines[selectedLine]?.sections ?? [];
  })();

  const lineLabel = (() => {
    if (!selectedCategory || !selectedLine) return "";
    return guide[selectedCategory]?.lines?.[selectedLine]?.label ?? "";
  })();

  /* ── 칩 스타일 헬퍼 ── */
  const chipStyle = (sel: boolean): React.CSSProperties => ({
    display: "flex", alignItems: "center", gap: 6,
    padding: "8px 16px",
    border: `2px solid ${sel ? BLUE : "#e5e7eb"}`,
    borderRadius: 8,
    background: sel ? "#e0f5fd" : "#fff",
    cursor: "pointer",
    fontWeight: sel ? 700 : 400,
    color: sel ? "#0077a8" : "#374151",
    fontSize: "0.875rem",
    userSelect: "none" as const,
    boxShadow: sel ? "0 0 0 3px rgba(0,181,239,0.15)" : "none",
    transition: "all 0.12s ease",
  });

  return (
    <main style={{ maxWidth: 800, margin: "0 auto", padding: "32px 24px", fontFamily: "sans-serif", color: "#1a1a1a" }}>

      {/* 헤더 */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", borderBottom: `3px solid ${BLUE}`, paddingBottom: 16, marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
          <Link href="/" style={{ color: BLUE, textDecoration: "none", fontSize: "1.25rem", paddingTop: 2 }}>←</Link>
          <div>
            <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, letterSpacing: "-0.01em" }}>{t("guide.title")}</h1>
            <p style={{ margin: "6px 0 0", color: "#6b7280", fontSize: "0.875rem", lineHeight: 1.5 }}>
              {t("guide.subtitle")}
            </p>
          </div>
        </div>
        <div style={{ flexShrink: 0, marginLeft: 16, paddingTop: 4 }}>
          <LanguageSelector variant="dark" />
        </div>
      </div>

      {/* 카테고리 선택 */}
      <section style={{ marginBottom: 28, background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 12, padding: "20px 24px" }}>
        <div style={{ marginBottom: 16 }}>
          <p style={{ margin: "0 0 8px", fontSize: "0.72rem", fontWeight: 600, color: "#9ca3af", letterSpacing: "0.05em", textTransform: "uppercase" }}>{t("guide.category")}</p>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {categoryGroups.map((group) => {
              const sel = selectedCategory === group.value;
              return (
                <label key={group.value} className="chip-label" style={chipStyle(sel)}>
                  <input type="radio" name="category" checked={sel} onChange={() => handleCategoryChange(group.value)} style={{ display: "none" }} />
                  {sel && <span style={{ color: BLUE, fontSize: "0.8rem" }}>✓</span>}
                  {group.label}
                </label>
              );
            })}
          </div>
        </div>

        {hasLines && currentGroup && (
          <div>
            <p style={{ margin: "0 0 8px", fontSize: "0.72rem", fontWeight: 600, color: "#9ca3af", letterSpacing: "0.05em", textTransform: "uppercase" }}>{t("guide.line")}</p>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {currentGroup.lines.map((line) => {
                const sel = selectedLine === line.value;
                return (
                  <label key={line.value} className="chip-label" style={{ ...chipStyle(sel), padding: "6px 14px", fontSize: "0.84rem" }}>
                    <input type="radio" name="line" checked={sel} onChange={() => setSelectedLine(line.value)} style={{ display: "none" }} />
                    {sel && <span style={{ color: BLUE, fontSize: "0.75rem" }}>✓</span>}
                    {line.label}
                  </label>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {/* 라인 선택 안내 */}
      {selectedCategory && sections.length === 0 && hasLines && !selectedLine && (
        <div style={{ textAlign: "center", padding: "48px 32px", color: "#9ca3af" }}>
          <div style={{ fontSize: "2rem", marginBottom: 8 }}>↑</div>
          <p style={{ margin: 0, fontSize: "0.95rem" }}>{t("guide.select.line")}</p>
        </div>
      )}

      {/* 가이드 본문 */}
      {sections.length > 0 && (
        <div>
          {/* 섹션 제목 */}
          <div style={{ marginBottom: 20 }}>
            <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 800, letterSpacing: "-0.01em" }}>
              {currentGroup?.label}
              {lineLabel && (
                <span style={{ fontSize: "0.95rem", fontWeight: 500, color: "#6b7280", marginLeft: 8 }}>— {lineLabel}</span>
              )}
            </h2>
            <div style={{ display: "flex", gap: 12, marginTop: 10, fontSize: "0.78rem" }}>
              <span style={{ display: "flex", alignItems: "center", gap: 4, color: "#0d9488", fontWeight: 600 }}>{t("guide.legend.required")}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 4, color: "#b45309", fontWeight: 600 }}>{t("guide.legend.warn")}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 4, color: "#0369a1", fontWeight: 600 }}>{t("guide.legend.info")}</span>
            </div>
          </div>

          {/* 섹션별 규정 */}
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {sections.map((section, si) => (
              <div key={si}>
                <h3 style={{ margin: "0 0 10px", fontSize: "0.95rem", fontWeight: 700, color: "#374151", paddingBottom: 8, borderBottom: "2px solid #e5e7eb" }}>
                  {section.title}
                </h3>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {section.rules.map((rule, ri) => {
                    const s = LEVEL_STYLE[rule.level as RuleLevel];
                    return (
                      <div key={ri} className="rule-card" style={{
                        display: "flex", gap: 10, padding: "12px 14px",
                        background: s.bg,
                        border: `1px solid ${s.border}`,
                        borderTop: `3px solid ${s.accent}`,
                        borderRadius: 8,
                      }}>
                        <span style={{ flexShrink: 0, fontSize: "0.95rem", marginTop: 1 }}>{s.icon}</span>
                        <p style={{ margin: 0, fontSize: "0.875rem", color: "#1a1a1a", lineHeight: 1.7 }}>{rule.text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* 공통 원칙 */}
          <div style={{ marginTop: 32, padding: "16px 20px", background: "#f0f9ff", border: "1px solid #bae6fd", borderTop: "4px solid #0ea5e9", borderRadius: 10 }}>
            <h4 style={{ margin: "0 0 8px", fontSize: "0.85rem", fontWeight: 700, color: "#0369a1" }}>{t("guide.common.title")}</h4>
            <ul style={{ margin: 0, paddingLeft: 20, lineHeight: 2, fontSize: "0.84rem", color: "#374151" }}>
              <li dangerouslySetInnerHTML={{ __html: t("guide.common.rule1").replace("Bold", "<strong>Bold</strong>") }} />
              <li>{t("guide.common.rule2")}</li>
            </ul>
          </div>
        </div>
      )}

      {/* 초기 안내 */}
      {!selectedCategory && (
        <div style={{ textAlign: "center", padding: "64px 32px", color: "#9ca3af" }}>
          <div style={{ fontSize: "3rem", marginBottom: 16 }}>📋</div>
          <p style={{ margin: 0, fontSize: "1rem", fontWeight: 500 }}>{t("guide.select.placeholder")}</p>
        </div>
      )}
    </main>
  );
}
