"use client";
import { useEffect, useState } from "react";

export default function HeaderBalance() {
  const [bal, setBal] = useState<number | null>(null);
  const [up, setUp] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch("/api/gw/balance")
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(j => { if (alive) { setBal(j.balance ?? 0); setUp(true); } })
      .catch(() => setUp(false));
    return () => { alive = false; };
  }, []);

  return (
    <div className={`rounded-md px-3 py-1 text-sm ${up ? "bg-green-100" : "bg-red-100"}`}>
      {up ? `${bal?.toFixed(1)} cbT` : "GW: DOWN"}
    </div>
  );
}
