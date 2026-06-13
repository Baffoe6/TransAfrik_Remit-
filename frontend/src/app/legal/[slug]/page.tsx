"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

interface LegalPage {
  slug: string;
  title: string;
  sections: { heading: string; body: string }[];
  disclaimer: string;
  operator: string;
}

export default function LegalPageView() {
  const params = useParams();
  const slug = params.slug as string;
  const [page, setPage] = useState<LegalPage | null>(null);

  useEffect(() => {
    api<LegalPage>(`/legal/pages/${slug}`).then(setPage).catch(() => {});
  }, [slug]);

  if (!page) return <div className="mx-auto max-w-3xl px-4 py-12 text-gray-500">Loading...</div>;

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <Link href="/" className="text-sm text-[#1B5E3B] hover:underline">← Home</Link>
      <h1 className="mt-4 text-3xl font-bold text-[#1B5E3B]">{page.title}</h1>
      <p className="mt-2 text-sm text-gray-500">{page.operator}</p>
      <div className="mt-8 space-y-6">
        {page.sections.map((s) => (
          <section key={s.heading}>
            <h2 className="text-lg font-semibold text-[#1B5E3B]">{s.heading}</h2>
            <p className="mt-2 text-gray-700 leading-relaxed">{s.body}</p>
          </section>
        ))}
      </div>
      <div className="mt-10 rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600">
        {page.disclaimer}
      </div>
    </div>
  );
}
