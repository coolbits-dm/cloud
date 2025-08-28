'use client'

export type VTCallback = () => void | Promise<void>

// Minimal TS types (so you get intellisense without a lib update)
declare global {
  interface Document {
    startViewTransition?: (callback: VTCallback) => ViewTransition
  }
  interface ViewTransition {
    finished: Promise<void>
    ready: Promise<void>
    updateCallbackDone: Promise<void>
    skipTransition: () => void
  }
}

/** Progressive-enhanced startViewTransition(). */
export function startViewTransition(callback: VTCallback) {
  if (typeof document !== 'undefined' && document.startViewTransition) {
    return document.startViewTransition(() => callback())
  }
  // Fallback: run immediately and return a dummy object that looks like a transition
  const p = Promise.resolve()
  void callback()
  return {
    finished: p,
    ready: p,
    updateCallbackDone: p,
    skipTransition() {},
  } as ViewTransition
}
