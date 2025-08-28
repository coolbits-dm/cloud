// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CoolBits.ai — AI Growth Copilot',
  description: 'Map your business, chat with Andy, and generate actionable audits.',
  metadataBase: new URL('https://coolbits.ai'),
  openGraph: {
    title: 'CoolBits.ai — AI Growth Copilot',
    description: 'Map your business, chat with Andy, and generate actionable audits.',
    url: 'https://coolbits.ai',
    siteName: 'CoolBits.ai',
    images: [{ url: '/og-image.jpg', width: 1200, height: 630, alt: 'CoolBits.ai' }],
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CoolBits.ai — AI Growth Copilot',
    description: 'Map your business, chat with Andy, and generate actionable audits.',
    images: ['/og-image.jpg'],
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head>
        {/* Favicon (use cb.png from /public) */}
        <link rel="icon" href="/cb.png" />
        <link rel="apple-touch-icon" href="/cb.png" />
        <meta name="theme-color" content="#0F60F6" />
      </head>
      <body className={`${inter.className} h-full bg-gray-50`}>
        {/* Header FIX */}
        <header className="fixed inset-x-0 top-0 z-40 h-[var(--header-h)] bg-white border-b">
          <div className="mx-auto max-w-7xl h-full px-4 sm:px-6 lg:px-8">
            <div className="flex h-full items-center justify-between">
              {/* Logo */}
              <a href="/" className="flex items-center gap-2">
                <img src="/cb.png" alt="CoolBits.ai" className="h-6 w-6" />
                <span className="text-lg font-semibold text-gray-900">CoolBits.ai</span>
              </a>

              {/* Nav */}
              <nav className="hidden md:flex items-center gap-8 text-sm">
                <a className="text-gray-700 hover:text-primary-600" href="/#platform">Platform</a>
                <a className="text-gray-700 hover:text-primary-600" href="/#features">Features</a>
                <a className="text-gray-700 hover:text-primary-600" href="/#pricing">Pricing</a>
                <a className="text-gray-700 hover:text-primary-600" href="/#about">About</a>
              </nav>

              {/* Mini user */}
              <div className="h-9 w-9 rounded-full bg-gray-100 border flex items-center justify-center">
                <svg viewBox="0 0 24 24" className="h-5 w-5 text-gray-600" fill="none" stroke="currentColor">
                  <path strokeWidth="1.8" d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm7 9a7 7 0 0 0-14 0"/>
                </svg>
              </div>
            </div>
          </div>
        </header>

        {/* Content area: blochează între header și footer, fără scroll pe body */}
        <main className="pt-[var(--header-h)] pb-[var(--footer-h)]">
          {children}
        </main>

        {/* Footer FIX */}
        <footer className="fixed inset-x-0 bottom-0 z-40 h-[var(--footer-h)] bg-gray-900 text-white">
          <div className="mx-auto max-w-7xl h-full px-4 sm:px-6 lg:px-8">
            <div className="flex h-full items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <img src="/cb.png" alt="CoolBits.ai" className="h-4 w-4" />
                <span className="opacity-80">© 2025 CoolBits.ai</span>
              </div>
              <div className="flex gap-4 opacity-80">
                <a href="/privacy" className="hover:opacity-100">Privacy</a>
                <a href="/contact" className="hover:opacity-100">Contact</a>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
