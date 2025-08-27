// Lightweight event bus (browser only)
export type BusEvent = 'channel:open' | 'channel:close';

export function on(ev: BusEvent, cb: (detail?: any) => void) {
  const h = ((e: CustomEvent) => cb(e.detail)) as EventListener;
  window.addEventListener(ev, h as EventListener);
  return () => window.removeEventListener(ev, h as EventListener);
}
export function emit(ev: BusEvent, detail?: any) {
  window.dispatchEvent(new CustomEvent(ev, { detail }));
}
