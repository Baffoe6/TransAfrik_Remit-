"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { TransferTimeline } from "./transfer-timeline";
import type { TimelineEvent } from "@/types";

interface TrackingData {
  current_status: string;
  current_label: string;
  next_expected_status: string | null;
  next_expected_label: string | null;
  timeline: TimelineEvent[];
  events: { label: string; message?: string; timestamp?: string }[];
  is_terminal: boolean;
}

export function LiveTransferTracking({ transferId, initialStatus }: { transferId: number; initialStatus: string }) {
  const [tracking, setTracking] = useState<TrackingData | null>(null);

  useEffect(() => {
    const load = () => api<TrackingData>(`/transfers/${transferId}/tracking`).then(setTracking).catch(() => {});
    load();
    if (initialStatus === "completed" || initialStatus === "failed") return;
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, [transferId, initialStatus]);

  if (!tracking) return <p className="text-sm text-gray-500">Loading live tracking...</p>;

  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-[#1B5E3B]/5 p-4 text-sm">
        <p><strong>Current:</strong> {tracking.current_label}</p>
        {tracking.next_expected_label && !tracking.is_terminal && (
          <p className="text-gray-600 mt-1">Next: {tracking.next_expected_label}</p>
        )}
      </div>
      <TransferTimeline timeline={tracking.timeline} currentStatus={tracking.current_status} />
      {tracking.events.length > 0 && (
        <div className="space-y-1 text-xs text-gray-600">
          {tracking.events.slice(-5).map((e, i) => (
            <p key={i}>• {e.label}{e.timestamp ? ` — ${new Date(e.timestamp).toLocaleString()}` : ""}</p>
          ))}
        </div>
      )}
    </div>
  );
}
