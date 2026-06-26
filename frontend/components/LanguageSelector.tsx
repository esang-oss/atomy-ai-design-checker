"use client";

import { useI18n, type Lang } from "@/lib/i18n/context";

interface Props {
  /** "light" — white text (for dark backgrounds), "dark" — dark text (for light backgrounds) */
  variant?: "light" | "dark";
}

export function LanguageSelector({ variant = "dark" }: Props) {
  const { lang, setLang, t } = useI18n();

  const isLight = variant === "light";

  return (
    <select
      value={lang}
      onChange={(e) => setLang(e.target.value as Lang)}
      style={{
        padding: "0.35rem 0.625rem",
        border: `1px solid ${isLight ? "rgba(255,255,255,0.4)" : "#d1d5db"}`,
        borderRadius: 6,
        background: isLight ? "rgba(255,255,255,0.15)" : "#fff",
        color: isLight ? "#fff" : "#374151",
        fontSize: "0.82rem",
        fontWeight: 500,
        cursor: "pointer",
        backdropFilter: isLight ? "blur(4px)" : undefined,
        outline: "none",
        minWidth: 90,
      }}
    >
      <option value="ko" style={{ color: "#1a1a1a", background: "#fff" }}>{t("lang.ko")}</option>
      <option value="en" style={{ color: "#1a1a1a", background: "#fff" }}>{t("lang.en")}</option>
    </select>
  );
}
