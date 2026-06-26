"use client";

import Image from "next/image";
import Link from "next/link";
import { useI18n } from "@/lib/i18n/context";
import { LanguageSelector } from "@/components/LanguageSelector";

export default function Home() {
  const { t } = useI18n();

  return (
    <main
      className="wave-bg"
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "sans-serif",
        padding: "2rem",
        position: "relative",
      }}
    >
      {/* 언어 선택 */}
      <div style={{ position: "absolute", top: 20, right: 24 }}>
        <LanguageSelector variant="light" />
      </div>

      {/* 로고 + 타이틀 */}
      <div style={{ textAlign: "center", marginBottom: 48 }}>
        <Image
          src="/atomy-logo.png"
          alt="atomy美"
          width={88}
          height={88}
          style={{
            objectFit: "contain",
            filter: "brightness(0) invert(1)",
            marginBottom: 20,
            opacity: 0.92,
          }}
        />
        <h1
          style={{
            margin: 0,
            fontSize: "clamp(2rem, 6vw, 3.25rem)",
            fontWeight: 800,
            color: "#fff",
            textShadow: "0 2px 16px rgba(0,100,160,0.25)",
            letterSpacing: "-0.01em",
            lineHeight: 1.2,
          }}
        >
          {t("home.title")}
        </h1>
        <p
          style={{
            marginTop: 12,
            color: "rgba(255,255,255,0.82)",
            fontSize: "1rem",
            fontWeight: 400,
            letterSpacing: "0.01em",
          }}
        >
          {t("home.subtitle")}
        </p>
      </div>

      {/* 카드 2개 */}
      <div
        style={{
          display: "flex",
          gap: 16,
          width: "100%",
          maxWidth: 680,
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        {/* 판독기 카드 */}
        <Link href="/check" style={{ textDecoration: "none", flex: "1 1 280px" }}>
          <div
            className="home-card"
            style={{
              padding: "28px 24px",
              background: "rgba(255,255,255,0.65)",
              border: "1.5px solid rgba(255,255,255,0.55)",
              borderRadius: 16,
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 10,
              textAlign: "center",
              backdropFilter: "blur(10px)",
              boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
            }}
          >
            <span style={{ fontSize: "2.5rem" }}>🔍</span>
            <div style={{ fontWeight: 700, fontSize: "1.1rem", color: "#1a1a1a" }}>
              {t("home.checker.title")}
            </div>
            <div style={{ fontSize: "0.85rem", color: "#6b7280", lineHeight: 1.6 }}>
              {t("home.checker.desc1")}<br />{t("home.checker.desc2")}
            </div>
          </div>
        </Link>

        {/* 가이드 카드 */}
        <Link href="/guide" style={{ textDecoration: "none", flex: "1 1 280px" }}>
          <div
            className="home-card"
            style={{
              padding: "28px 24px",
              background: "rgba(0,100,200,0.6)",
              border: "1.5px solid rgba(255,255,255,0.35)",
              borderRadius: 16,
              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 10,
              textAlign: "center",
              backdropFilter: "blur(10px)",
              boxShadow: "0 2px 12px rgba(0,0,0,0.12)",
            }}
          >
            <span style={{ fontSize: "2.5rem" }}>📋</span>
            <div style={{ fontWeight: 700, fontSize: "1.1rem", color: "#fff" }}>
              {t("home.guide.title")}
            </div>
            <div style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.82)", lineHeight: 1.6 }}>
              {t("home.guide.desc1")}<br />{t("home.guide.desc2")}
            </div>
          </div>
        </Link>
      </div>

      <p style={{ marginTop: 40, fontSize: "0.72rem", color: "rgba(255,255,255,0.5)", letterSpacing: "0.03em" }}>
        {t("home.footer")}
      </p>
    </main>
  );
}
