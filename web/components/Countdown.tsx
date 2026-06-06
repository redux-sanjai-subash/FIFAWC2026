"use client";

import { useEffect, useState } from "react";

function format(ms: number) {
  if (ms <= 0) return null;
  const totalMin = Math.floor(ms / 60000);
  const d = Math.floor(totalMin / 1440);
  const h = Math.floor((totalMin % 1440) / 60);
  const m = totalMin % 60;
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  const s = Math.floor((ms % 60000) / 1000);
  return `${m}m ${s}s`;
}

export default function Countdown({
  target,
  prefix,
  expired = "now",
}: {
  target: string;
  prefix?: string;
  expired?: string;
}) {
  const [label, setLabel] = useState<string | null>(null);

  useEffect(() => {
    const tick = () => {
      const ms = new Date(target).getTime() - Date.now();
      setLabel(format(ms));
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, [target]);

  return (
    <span>
      {prefix ? `${prefix} ` : ""}
      <span className="tabular-nums">{label ?? expired}</span>
    </span>
  );
}
