"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth, isAgent, isStaff } from "@/lib/auth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireStaff?: boolean;
  requireCustomer?: boolean;
  requireAgent?: boolean;
}

export function ProtectedRoute({ children, requireStaff, requireCustomer, requireAgent }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    if (requireAgent && !isAgent(user.role)) {
      router.replace("/dashboard");
      return;
    }
    if (requireStaff && !isStaff(user.role)) {
      router.replace("/dashboard");
      return;
    }
    if (requireCustomer && (isStaff(user.role) || isAgent(user.role))) {
      router.replace(isAgent(user.role) ? "/agent" : "/admin");
    }
  }, [user, loading, router, requireStaff, requireCustomer, requireAgent]);

  if (loading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#1B5E3B] border-t-transparent" />
      </div>
    );
  }

  if (!user) return null;
  if (requireAgent && !isAgent(user.role)) return null;
  if (requireStaff && !isStaff(user.role)) return null;
  if (requireCustomer && (isStaff(user.role) || isAgent(user.role))) return null;

  return <>{children}</>;
}
