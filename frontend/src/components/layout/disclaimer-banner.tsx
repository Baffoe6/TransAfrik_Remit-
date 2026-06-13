import { AlertTriangle } from "lucide-react";
import { DISCLAIMER } from "@/types";

export function DisclaimerBanner() {
  return (
    <div className="border-b border-[#C9A227]/30 bg-[#C9A227]/10 px-4 py-2">
      <div className="mx-auto flex max-w-7xl items-start gap-2 text-xs text-[#5a4a10] sm:items-center">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 sm:mt-0" />
        <p>{DISCLAIMER}</p>
      </div>
    </div>
  );
}
