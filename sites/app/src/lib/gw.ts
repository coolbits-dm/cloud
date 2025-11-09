// server-only
import crypto from "node:crypto";

const GW = process.env.NEXT_PUBLIC_GW_BASE_URL!;
const ORG = process.env.CB_ORG_ID || "demo";
const HMAC = process.env.CB_HMAC_KEY;

function sign(payload: string) {
  return crypto.createHmac("sha256", HMAC!).update(payload).digest("hex");
}

export async function gwGet(path: string) {
  const r = await fetch(`${GW}${path}`, { cache: "no-store" });
  if (!r.ok) throw new Error(`GET ${path} -> ${r.status}`);
  return r.json();
}

export async function gwPost(path: string, body: any, useHmac = false) {
  const payload = typeof body === "string" ? body : JSON.stringify(body);
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (useHmac && HMAC) headers["x-cb-signature"] = sign(payload);
  const r = await fetch(`${GW}${path}`, { method: "POST", body: payload, headers, cache: "no-store" });
  if (!r.ok) throw new Error(`POST ${path} -> ${r.status}`);
  return r.json();
}

export const ORG_ID = ORG;
