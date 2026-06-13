import Link from "next/link";
import { ArrowRight, Globe, Shield, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function LandingPage() {
  return (
    <div>
      <section className="relative overflow-hidden bg-gradient-to-br from-[#1B5E3B] via-[#164d31] to-[#0f3d25] text-white">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-[#C9A227]" />
          <div className="absolute -bottom-20 -left-20 h-72 w-72 rounded-full bg-[#C9A227]" />
        </div>
        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28">
          <div className="max-w-2xl">
            <p className="mb-4 text-sm font-medium uppercase tracking-wider text-[#C9A227]">
              IPAYGO (Pty) Ltd
            </p>
            <h1 className="text-4xl font-bold leading-tight sm:text-5xl">
              Send money from South Africa to Ghana — fast, secure, transparent
            </h1>
            <p className="mt-6 text-lg text-green-100">
              TransAfrik Remit connects you to trusted mobile money networks in Ghana.
              Competitive rates, clear fees, and full transfer tracking.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link href="/register">
                <Button size="lg" variant="secondary">
                  Start Sending <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-bold text-[#1B5E3B]">Why TransAfrik Remit?</h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          {[
            { icon: Zap, title: "Fast Transfers", desc: "ZAR to GHS with competitive exchange rates and transparent fees." },
            { icon: Shield, title: "Secure & Compliant", desc: "KYC verification, AML monitoring, and POPIA-ready data protection." },
            { icon: Globe, title: "Ghana Mobile Money", desc: "Send directly to MTN, Vodafone Cash, and other mobile wallets." },
          ].map((item) => (
            <Card key={item.title}>
              <CardHeader>
                <item.icon className="h-8 w-8 text-[#C9A227]" />
                <CardTitle>{item.title}</CardTitle>
                <CardDescription>{item.desc}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid items-center gap-10 lg:grid-cols-2">
            <div>
              <h2 className="text-2xl font-bold text-[#1B5E3B]">How it works</h2>
              <ol className="mt-6 space-y-4">
                {[
                  "Create your account and complete KYC verification",
                  "Add your beneficiary in Ghana with mobile money details",
                  "Calculate your transfer and choose a payment method",
                  "Pay via Pay@, EasyPay, EFT, or instant payment (coming soon)",
                  "Track your transfer until funds arrive",
                ].map((step, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#1B5E3B] text-sm font-bold text-[#C9A227]">
                      {i + 1}
                    </span>
                    <span className="text-[#2d2d2d]">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
            <Card className="border-[#C9A227]/30 bg-gradient-to-br from-[#1B5E3B]/5 to-[#C9A227]/5">
              <CardHeader>
                <CardTitle>Sample Calculator</CardTitle>
                <CardDescription>Illustrative rates — register for live pricing</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between"><span>You send</span><span className="font-semibold">R 1,000.00</span></div>
                <div className="flex justify-between"><span>Fee</span><span className="font-semibold">R 49.00</span></div>
                <div className="flex justify-between"><span>Rate</span><span className="font-semibold">1 ZAR = 0.72 GHS</span></div>
                <div className="border-t pt-3 flex justify-between text-[#1B5E3B]">
                  <span className="font-medium">Recipient receives</span>
                  <span className="text-xl font-bold">₵ 720.00</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
