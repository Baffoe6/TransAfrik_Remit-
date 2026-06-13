import { ProtectedRoute } from "@/components/auth/protected-route";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute requireCustomer>
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">{children}</div>
    </ProtectedRoute>
  );
}
