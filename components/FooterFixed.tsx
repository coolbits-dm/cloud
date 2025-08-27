'use client'

export default function FooterFixed() {
  return (
    <footer className="fixed bottom-0 left-0 right-0 z-30 border-t bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2 text-xs text-gray-500">
        <div className="flex items-center gap-2">
          <span>© {new Date().getFullYear()} CoolBits.ai</span>
          <span className="hidden md:inline">•</span>
          <span className="hidden md:inline">All rights reserved.</span>
        </div>
        <div className="flex items-center gap-4">
          <a className="hover:text-gray-700" href="/privacy">Privacy</a>
          <a className="hover:text-gray-700" href="/contact">Contact</a>
        </div>
      </div>
    </footer>
  )
}
