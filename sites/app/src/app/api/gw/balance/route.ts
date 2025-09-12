export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { NextResponse } from "next/server";
import { gwGet, ORG_ID } from "@/lib/gw";

export async function GET() {
  const data = await gwGet(`/v1/ledger/balance?org_id=${encodeURIComponent(ORG_ID)}`);
  return NextResponse.json(data);
}
