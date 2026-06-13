import { Check, Circle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { TimelineEvent } from "@/types";

const TIMELINE_ORDER = [
  "draft",
  "awaiting_payment",
  "payment_pending_verification",
  "payment_verified",
  "compliance_review",
  "ready_for_processing",
  "submitted_to_mukuru",
  "processing",
  "completed",
];

export function TransferTimeline({ timeline, currentStatus }: { timeline: TimelineEvent[]; currentStatus: string }) {
  const reached = new Set(timeline.map((t) => t.status));
  const currentIdx = TIMELINE_ORDER.indexOf(currentStatus);

  const steps = TIMELINE_ORDER.map((status) => {
    const event = timeline.find((t) => t.status === status);
    const idx = TIMELINE_ORDER.indexOf(status);
    const isComplete = reached.has(status) || idx < currentIdx;
    const isCurrent = status === currentStatus;
    return {
      status,
      label: event?.label || status.replace(/_/g, " "),
      timestamp: event?.timestamp,
      isComplete,
      isCurrent,
    };
  }).filter((s) => s.isComplete || s.isCurrent || TIMELINE_ORDER.indexOf(s.status) <= currentIdx + 1);

  return (
    <div className="space-y-0">
      {steps.map((step, i) => (
        <div key={step.status} className="flex gap-3">
          <div className="flex flex-col items-center">
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-full border-2",
                step.isComplete ? "border-[#1B5E3B] bg-[#1B5E3B] text-white" :
                step.isCurrent ? "border-[#C9A227] bg-[#C9A227]/20 text-[#1B5E3B]" :
                "border-gray-300 bg-white text-gray-400",
              )}
            >
              {step.isComplete ? <Check className="h-4 w-4" /> : <Circle className="h-3 w-3" />}
            </div>
            {i < steps.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 min-h-[24px]" />}
          </div>
          <div className="pb-6">
            <p className={cn("font-medium text-sm", step.isComplete || step.isCurrent ? "text-[#1B5E3B]" : "text-gray-400")}>
              {step.label}
            </p>
            {step.timestamp && (
              <p className="text-xs text-gray-500">{new Date(step.timestamp).toLocaleString("en-ZA")}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
