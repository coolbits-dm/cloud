import fs from 'node:fs'
import path from 'node:path'

const ROOT = process.env.CB_DATA_ROOT || path.resolve(process.cwd(), '../../artifacts/dev')

export function readJson<T=unknown>(rel: string): T {
  const p = path.resolve(ROOT, rel)
  const raw = fs.readFileSync(p, 'utf8')
  return JSON.parse(raw)
}

export function writeJson<T=unknown>(rel: string, data: T): void {
  const p = path.resolve(ROOT, rel)
  const dir = path.dirname(p)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
  fs.writeFileSync(p, JSON.stringify(data, null, 2), 'utf8')
}
