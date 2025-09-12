// src/components/Header.tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { HeaderBalance } from './HeaderBalance'
import { MessageSquare, Users, Settings, BarChart3 } from 'lucide-react'

export function Header() {
  const pathname = usePathname()

  const navItems = [
    { href: '/user/wall', label: 'User Wall', icon: MessageSquare },
    { href: '/user/board', label: 'User Board', icon: Users },
    { href: '/business/wall', label: 'Business Wall', icon: MessageSquare },
    { href: '/business/board', label: 'Business Board', icon: Users },
    { href: '/agency/wall', label: 'Agency Wall', icon: MessageSquare },
    { href: '/agency/board', label: 'Agency Board', icon: Users },
    { href: '/dev/wall', label: 'Dev Wall', icon: MessageSquare },
    { href: '/dev/board', label: 'Dev Board', icon: Users },
    { href: '/bits', label: 'Bits Orchestrator', icon: Settings },
  ]

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CB</span>
            </div>
            <span className="text-xl font-bold text-gray-900">CoolBits.ai</span>
            <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">M18.2</span>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>

          {/* cbT Balance */}
          <HeaderBalance />
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-gray-200 py-2">
          <nav className="flex flex-wrap gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-3 h-3" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </header>
  )
}
