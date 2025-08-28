'use client'

import { useState } from 'react'
import Image from 'next/image'
import { FactsProvider } from '@/lib/facts/store'
import ChatWithMap from '@/components/ChatWithMap'

export default function Page() {
  const [started, setStarted] = useState(false)

  return (
    <FactsProvider>
      <div className="h-[calc(100vh-var(--header-h)-var(--footer-h))] overflow-hidden">
        {!started ? (
          <div className="flex h-full items-center justify-center px-6">
            <div className="max-w-3xl w-full text-center bg-white rounded-2xl shadow-sm border p-10">
              {/* LOGO centrat, fără background */}
              <Image
                src="/cb.png"
                alt="CoolBits logo"
                width={72}
                height={72}
                priority
                className="mx-auto block h-16 w-16"
              />

              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mt-4 mb-4">
                Welcome to CoolBits
              </h1>
              <p className="text-gray-600 text-lg mb-8">
                Let’s set up your Business Map. We’ll ask a few quick questions, then you can
                talk with <strong>Andy</strong> and generate your first briefing.
              </p>
              <button
                onClick={() => setStarted(true)}
                className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-primary-600 text-white text-base font-semibold hover:bg-primary-700"
              >
                Get Started
              </button>
              <p className="mt-4 text-sm text-gray-500">
                Takes about 2–3 minutes. No signup required.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-7xl h-full px-6">
            <ChatWithMap />
          </div>
        )}
      </div>
    </FactsProvider>
  )
}
