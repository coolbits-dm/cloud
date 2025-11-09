// src/lib/cbtokens.ts - cbT Economy v0
export const TARIFF = {
  WALL_POST: -1.0,
  NHA_INVOCATION: -2.0,
  BOARD_MEETING: -3.0,
  BITS_DRY_RUN: -1.0
} as const

export type TariffAction = keyof typeof TARIFF

export function getTariffCost(action: TariffAction): number {
  return TARIFF[action]
}

export function calculateNewBalance(currentBalance: number, delta: number): number {
  return currentBalance + delta
}

export function formatTokens(amount: number): string {
  return `${amount.toFixed(1)} cbT`
}

export function isLowBalance(balance: number): boolean {
  return balance < 10
}

export function isNegativeBalance(balance: number): boolean {
  return balance < 0
}

export function getBalanceStatus(balance: number): 'healthy' | 'low' | 'negative' {
  if (isNegativeBalance(balance)) return 'negative'
  if (isLowBalance(balance)) return 'low'
  return 'healthy'
}

export function getBalanceColor(balance: number): string {
  const status = getBalanceStatus(balance)
  switch (status) {
    case 'healthy': return 'text-green-600'
    case 'low': return 'text-yellow-600'
    case 'negative': return 'text-red-600'
    default: return 'text-gray-600'
  }
}

export function getBalanceBgColor(balance: number): string {
  const status = getBalanceStatus(balance)
  switch (status) {
    case 'healthy': return 'bg-green-50 border-green-200'
    case 'low': return 'bg-yellow-50 border-yellow-200'
    case 'negative': return 'bg-red-50 border-red-200'
    default: return 'bg-gray-50 border-gray-200'
  }
}
