// components/ui/BrandIcon.tsx
'use client'

import React from 'react'
import { useState } from 'react'
import { brandFile, brandLabel } from '@/lib/brand/brand'
import type { BrandId } from '@/lib/brand/brand'

export default function BrandIcon({
  id,
  size = 16,
  title,
  className = '',
}: {
  id: BrandId
  size?: number
  title?: string
  className?: string
}) {
  const [broken, setBroken] = useState(false)
  const src = brandFile(id)
  const alt = title || brandLabel(id)

  if (broken) {
    // graceful fallback — first letter badge
    return (
      <div
        className={`inline-flex items-center justify-center rounded-md border text-[10px] ${className}`}
        style={{ width: size, height: size }}
        aria-label={alt}
        title={alt}
      >
        {alt?.[0] ?? '•'}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      width={size}
      height={size}
      className={`inline-block object-contain ${className}`}
      onError={() => setBroken(true)}
    />
  )
}
