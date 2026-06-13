"use client";

import { ProtectedRoute } from "@/components/auth/protected-route";

export default function AgentLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requireAgent>
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</div>
    </ProtectedRoute>
  );
}
