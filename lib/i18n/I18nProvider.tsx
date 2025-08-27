'use client'

import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import en from '@/locales/en'
import ro from '@/locales/ro'

type Lang = 'en' | 'ro'
type Dict = Record<string, string>
const dicts: Record<Lang, Dict> = { en, ro }

const Ctx = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (k: string) => string } | null>(null)

export function I18nProvider({ children, defaultLang = 'en' }: { children: React.ReactNode, defaultLang?: Lang }) {
  const [lang, setLang] = useState<Lang>(defaultLang)

  useEffect(() => {
    const saved = localStorage.getItem('ui_lang') as Lang | null
    if (saved === 'en' || saved === 'ro') setLang(saved)
  }, [])
  useEffect(() => {
    localStorage.setItem('ui_lang', lang)
  }, [lang])

  const t = useMemo(() => {
    const d = dicts[lang] || dicts.en
    return (k: string) => d[k] ?? k
  }, [lang])

  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>
}

export function useI18n() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}
