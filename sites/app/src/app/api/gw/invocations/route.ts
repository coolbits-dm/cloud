export const runtime = "nodejs";
export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";
import { gwGet } from "@/lib/gw";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const postId = url.searchParams.get("post_id") ?? "";
  const data = await gwGet(`/v1/invocations?post_id=${encodeURIComponent(postId)}`);
  return NextResponse.json(data);
}
