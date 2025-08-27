'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useEffect, useRef, useState } from 'react'

export default function SiteHeader() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 relative">
                <Image
                  src="/cb.png"
                  alt="CoolBits.ai"
                  fill
                  sizes="32px"
                  className="rounded-lg object-contain"
                  priority
                />
              </div>
              <span className="text-xl font-bold text-gray-900">CoolBits.ai</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <NavLink href="/#platform">Platform</NavLink>
            <NavLink href="/features">Features</NavLink>
            <NavLink href="/pricing">Pricing</NavLink>
            <NavLink href="/about">About</NavLink>
          </nav>

          {/* User Panel */}
          <UserMiniPanel />
        </div>
      </div>
    </header>
  )
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="text-gray-700 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
    >
      {children}
    </Link>
  )
}

function UserMiniPanel() {
  const [open, setOpen] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const ref = useRef<HTMLDivElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (!ref.current) return
      if (!ref.current.contains(e.target as Node)) setOpen(false)
    }
    window.addEventListener('click', onClick)
    return () => window.removeEventListener('click', onClick)
  }, [])

  const onPick = () => fileRef.current?.click()
  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    const url = URL.createObjectURL(f)
    setPreview(url)
    // TODO: upload + persist
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center gap-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors px-2 py-1"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label="Account menu"
      >
        <div className="w-8 h-8 rounded-full overflow-hidden bg-gray-300 flex items-center justify-center">
          {preview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={preview} alt="Avatar" className="w-full h-full object-cover" />
          ) : (
            /* Simple user icon (no text) */
            <svg
              viewBox="0 0 24 24"
              fill="currentColor"
              className="w-5 h-5 text-gray-700"
              aria-hidden="true"
            >
              <path d="M12 12a5 5 0 100-10 5 5 0 000 10zm-9 9a9 9 0 1118 0H3z" />
            </svg>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-gray-600 transition-transform ${open ? 'rotate-180' : ''}`}
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 10.585l3.71-3.354a.75.75 0 111.02 1.1l-4.22 3.815a.75.75 0 01-1.02 0L5.25 8.33a.75.75 0 01-.02-1.12z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 mt-2 w-56 rounded-lg border bg-white shadow-lg p-2 z-50"
        >
          <MenuItem onClick={onPick}>Upload avatar</MenuItem>
          <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={onFile} />

          <div className="my-1 border-t" />

          <MenuItem href="/account">Account</MenuItem>
          <MenuItem href="/settings">Settings</MenuItem>
          <MenuItem href="/billing">Billing</MenuItem>

          <div className="my-1 border-t" />

          <MenuItem href="/api/auth/signout">Sign out</MenuItem>
        </div>
      )}
    </div>
  )
}

function MenuItem({
  children,
  href,
  onClick,
}: {
  children: React.ReactNode
  href?: string
  onClick?: () => void
}) {
  const common =
    'w-full text-left px-3 py-2 text-sm rounded-md hover:bg-gray-100 text-gray-700 transition-colors'
  if (href) {
    return (
      <Link href={href} className={common} role="menuitem">
        {children}
      </Link>
    )
  }
  return (
    <button onClick={onClick} className={common} role="menuitem">
      {children}
    </button>
  )
}
