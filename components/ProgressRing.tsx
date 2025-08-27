'use client'
export default function ProgressRing({ value }: { value: number }) {
  const pct = Math.max(0, Math.min(100, value));
  const color =
    pct >= 100 ? 'text-green-600' :
    pct >= 70  ? 'text-orange-500' :
    pct >= 30  ? 'text-yellow-500' :
                 'text-gray-400';

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg viewBox="0 0 36 36" className="h-6 w-6">
        <path
          className="text-gray-200"
          stroke="currentColor"
          strokeWidth="3.5"
          fill="none"
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
        />
        <path
          className={color}
          stroke="currentColor"
          strokeWidth="3.5"
          strokeDasharray={`${pct}, 100`}
          strokeLinecap="round"
          fill="none"
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
        />
      </svg>
      <span className="absolute text-[10px] font-semibold">{pct}%</span>
    </div>
  )
}
