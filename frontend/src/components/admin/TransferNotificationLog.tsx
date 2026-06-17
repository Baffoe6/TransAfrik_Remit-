"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";

interface Delivery {
  id: number;
  channel: string;
  status: string;
  recipient: string | null;
  error_message: string | null;
  created_at: string;
}

interface FeedItem {
  notification: {
    id: number;
    event_code: string;
    title: string;
    message: string;
    transfer_reference: string | null;
    read_status: string;
    created_at: string;
  };
  deliveries: Delivery[];
}

const CHANNEL_LABELS: Record<string, string> = {
  in_app: "In-app",
  push: "Push",
  sms: "SMS",
  whatsapp: "WhatsApp",
  email: "Email",
};

export function TransferNotificationLog({ transferId }: { transferId: number }) {
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api<FeedItem[]>(`/admin/transfers/${transferId}/notifications`)
      .then(setFeed)
      .catch((e) => setError(e.message));
  }, [transferId]);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (feed.length === 0) return <p className="text-sm text-gray-500">No notifications sent for this transfer yet.</p>;

  return (
    <div className="space-y-4">
      {feed.map((item) => (
        <Card key={item.notification.id}>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{item.notification.title}</CardTitle>
            <p className="text-xs text-gray-500">{formatDate(item.notification.created_at)} · {item.notification.event_code}</p>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>{item.notification.message}</p>
            <div className="rounded border">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b bg-gray-50 text-left text-gray-500">
                    <th className="p-2">Channel</th>
                    <th className="p-2">Status</th>
                    <th className="p-2">Recipient</th>
                    <th className="p-2">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {item.deliveries.map((d) => (
                    <tr key={d.id} className="border-b">
                      <td className="p-2">{CHANNEL_LABELS[d.channel] ?? d.channel}</td>
                      <td className={`p-2 font-medium ${d.status === "failed" ? "text-red-600" : d.status === "sent" ? "text-green-700" : "text-gray-500"}`}>
                        {d.status}
                      </td>
                      <td className="p-2">{d.recipient ?? "—"}</td>
                      <td className="p-2 text-red-600">{d.error_message ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
