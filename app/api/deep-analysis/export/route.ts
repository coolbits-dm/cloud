// app/api/deep-analysis/export/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(req: NextRequest) {
  const url = new URL(req.url)
  const id = url.searchParams.get('id') || 'job'
  // TODO: generează PDF real (puppeteer/pdfkit). Momentan placeholder.
  const pdfBuffer = Buffer.from(`CoolBits Deep Analysis\nJob: ${id}\n(placeholder PDF)`, 'utf-8')

  return new NextResponse(pdfBuffer, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="deep-analysis-${id}.pdf"`,
    }
  })
}
