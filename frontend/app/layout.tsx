import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n/context";

export const metadata: Metadata = {
  title: "Atomy Design Checker",
  description: "애터미 패키지 디자인 가이드 준수도 자동 채점 서비스",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
