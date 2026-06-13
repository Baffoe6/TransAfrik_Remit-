"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth, getHomeForRole, isAgent, isStaff } from "@/lib/auth";
import { cn } from "@/lib/utils";

export function Header() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isProd = process.env.NODE_ENV === "production";

  const customerLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/dashboard/profile", label: "Profile" },
    { href: "/dashboard/kyc", label: "KYC" },
    { href: "/dashboard/beneficiaries", label: "Beneficiaries" },
    { href: "/dashboard/transfers", label: "Transfers" },
    { href: "/dashboard/wallet", label: "Wallet" },
    ...(isProd ? [] : [{ href: "/dashboard/pilot", label: "Pilot" }]),
    { href: "/dashboard/referrals", label: "Referrals" },
    { href: "/dashboard/support", label: "Support" },
  ];

  const adminLinks = [
    { href: "/admin", label: "Dashboard" },
    { href: "/admin/operations", label: "Operations" },
    { href: "/admin/compliance", label: "Compliance" },
    { href: "/admin/waitlist", label: "Waitlist" },
    { href: "/admin/launch-readiness", label: "Launch Readiness" },
    { href: "/admin/corridors", label: "Corridors" },
    { href: "/admin/customers", label: "Customers" },
    { href: "/admin/kyc", label: "KYC" },
    { href: "/admin/transfers", label: "Transfers" },
    { href: "/admin/payments", label: "Payments" },
    { href: "/admin/providers", label: "Providers" },
    ...(isProd ? [] : [
      { href: "/admin/pilot", label: "Pilot Admin" },
      { href: "/admin/demo", label: "Demo" },
      { href: "/admin/launch-checklist", label: "Launch" },
    ]),
    { href: "/admin/founder", label: "Founder" },
    { href: "/admin/runbook", label: "Runbook" },
    { href: "/admin/support", label: "Support" },
  ];

  const agentLinks = [
    { href: "/agent", label: "Dashboard" },
    { href: "/agent/commissions", label: "Commissions" },
    { href: "/agent/referrals", label: "Referrals" },
  ];

  const links = user
    ? isAgent(user.role)
      ? agentLinks
      : isStaff(user.role)
        ? adminLinks
        : customerLinks
    : [];

  return (
    <header className="sticky top-0 z-50 border-b border-[#1B5E3B]/20 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href={user ? getHomeForRole(user.role) : "/"} className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#1B5E3B] text-sm font-bold text-[#C9A227]">
            TA
          </div>
          <span className="text-lg font-bold text-[#1B5E3B]">TransAfrik Remit</span>
        </Link>

        {user && (
          <nav className="hidden items-center gap-1 md:flex">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  pathname === link.href
                    ? "bg-[#1B5E3B] text-white"
                    : "text-[#2d2d2d] hover:bg-[#1B5E3B]/10",
                )}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="hidden text-sm text-gray-500 sm:inline">{user.email}</span>
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
              <button className="md:hidden" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </>
          ) : (
            <>
              <Link href="/login">
                <Button variant="ghost" size="sm">Login</Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Get Started</Button>
              </Link>
            </>
          )}
        </div>
      </div>

      {mobileOpen && user && (
        <nav className="border-t border-gray-200 bg-white px-4 py-2 md:hidden">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                "block rounded-md px-3 py-2 text-sm font-medium",
                pathname === link.href ? "bg-[#1B5E3B] text-white" : "text-[#2d2d2d]",
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
