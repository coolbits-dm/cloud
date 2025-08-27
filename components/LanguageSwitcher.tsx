'use client'

import { useI18n } from '@/lib/i18n/I18nProvider'

export default function LanguageSwitcher() {
  const { lang, setLang } = useI18n()
  return (
    <div className="inline-flex items-center rounded-lg border bg-white">
      <button
        onClick={() => setLang('en')}
        className={`px-3 py-1 text-sm rounded-l-lg ${lang === 'en' ? 'bg-gray-100 font-semibold' : 'text-gray-600 hover:bg-gray-50'}`}
        title="English"
      >
        EN
      </button>
      <button
        onClick={() => setLang('ro')}
        className={`px-3 py-1 text-sm rounded-r-lg ${lang === 'ro' ? 'bg-gray-100 font-semibold' : 'text-gray-600 hover:bg-gray-50'}`}
        title="Română"
      >
        RO
      </button>
    </div>
  )
}