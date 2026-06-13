import { DISCLAIMER } from "@/types";

export function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-[#2d2d2d] text-gray-300">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-lg font-semibold text-[#C9A227]">TransAfrik Remit</p>
            <p className="mt-1 text-sm text-gray-400">Operated by IPAYGO (Pty) Ltd</p>
          </div>
          <div className="flex flex-wrap gap-4 text-xs text-gray-400">
            <a href="/legal/terms" className="hover:text-[#C9A227]">Terms</a>
            <a href="/legal/privacy" className="hover:text-[#C9A227]">Privacy</a>
            <a href="/legal/popia" className="hover:text-[#C9A227]">POPIA</a>
            <a href="/legal/aml-fica" className="hover:text-[#C9A227]">AML/FICA</a>
            <a href="/legal/refund" className="hover:text-[#C9A227]">Refunds</a>
            <a href="/legal/complaints" className="hover:text-[#C9A227]">Complaints</a>
            <a href="/legal/partner-disclaimer" className="hover:text-[#C9A227]">Partners</a>
          </div>
          <div className="max-w-xl text-xs leading-relaxed text-gray-400">
            <p>{DISCLAIMER}</p>
          </div>
        </div>
        <div className="mt-6 border-t border-gray-700 pt-4 text-center text-xs text-gray-500">
          &copy; {new Date().getFullYear()} IPAYGO (Pty) Ltd. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
