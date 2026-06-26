"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { strings } from "./strings";

export type Lang = "ko" | "en";
type Strings = typeof strings.ko;

interface I18nCtx {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: keyof Strings) => string;
}

const I18nContext = createContext<I18nCtx>({
  lang: "ko",
  setLang: () => {},
  t: (key) => strings.ko[key] ?? (key as string),
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("ko");

  useEffect(() => {
    const saved = localStorage.getItem("atomy-lang") as Lang | null;
    if (saved === "ko" || saved === "en") setLangState(saved);
  }, []);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem("atomy-lang", l);
  };

  const t = (key: keyof Strings): string =>
    strings[lang]?.[key] ?? strings.ko[key] ?? (key as string);

  return <I18nContext.Provider value={{ lang, setLang, t }}>{children}</I18nContext.Provider>;
}

export const useI18n = () => useContext(I18nContext);
