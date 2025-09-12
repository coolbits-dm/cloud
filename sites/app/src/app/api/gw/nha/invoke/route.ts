export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { gwPost, ORG_ID } from "@/lib/gw";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const payload = {
    post: { org_id: ORG_ID, panel: body.panel, text: body.text }
  };
  const data = await gwPost("/v1/nha/invoke", payload, true);
  return NextResponse.json(data);
}
