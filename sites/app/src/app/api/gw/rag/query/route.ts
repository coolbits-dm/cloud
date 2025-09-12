export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { gwPost, ORG_ID } from "@/lib/gw";

export async function POST(req: NextRequest) {
  const { panel, query, topk } = await req.json();
  const data = await gwPost("/v1/rag/query", { org_id: ORG_ID, panel, query, topk: topk ?? 3 });
  return NextResponse.json(data);
}
