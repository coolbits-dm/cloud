'use client'

import { createContext, useContext, useMemo, useState } from 'react'
import type { Facts, FactsContextType, PartialFacts } from './types'

const FactsContext = createContext<FactsContextType | null>(null)

function uniqMerge<T>(a?: T[], b?: T[]): T[] | undefined {
  if (!a && !b) return undefined
  const set = new Set<T>([...(a ?? []), ...(b ?? [])])
  return Array.from(set)
}

function deepMerge(a: any, b: any): any {
  if (b === undefined || b === null) return a
  if (Array.isArray(a) && Array.isArray(b)) return uniqMerge(a, b)
  if (Array.isArray(b)) return uniqMerge(undefined, b)
  if (typeof a === 'object' && typeof b === 'object') {
    const out: any = { ...(a || {}) }
    for (const k of Object.keys(b)) {
      const av = a?.[k]
      const bv = b[k]
      if (Array.isArray(bv)) out[k] = uniqMerge(av, bv)
      else if (bv && typeof bv === 'object') out[k] = deepMerge(av ?? {}, bv)
      else if (bv !== undefined) out[k] = bv
    }
    return out
  }
  return b
}

export function FactsProvider({ children }: { children: React.ReactNode }) {
  const [facts, setFacts] = useState<Facts>({})

  const ctx = useMemo<FactsContextType>(() => ({
    facts,
    upsertManual: (patch: PartialFacts) => {
      setFacts(prev => deepMerge(prev, patch) as Facts)
    },
    reset: () => setFacts({}),
  }), [facts])

  return <FactsContext.Provider value={ctx}>{children}</FactsContext.Provider>
}

export const useFacts = (): FactsContextType => {
  const ctx = useContext(FactsContext)
  if (!ctx) throw new Error('useFacts must be used within a FactProvider')
  return ctx
}
