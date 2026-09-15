"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchSequences, SequenceSummary } from "@/lib/api";

const REFRESH_INTERVAL_MS = 15000;

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-200 text-gray-700",
  active: "bg-blue-100 text-blue-700",
  replied: "bg-green-100 text-green-700",
  completed: "bg-purple-100 text-purple-700",
};

export default function DashboardPage() {
  const [sequences, setSequences] = useState<SequenceSummary[]>([]);
  const [trackingEnabled, setTrackingEnabled] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchSequences();
        if (cancelled) return;
        setSequences(data.sequences);
        setTrackingEnabled(data.tracking_enabled);
        setError(null);
      } catch {
        if (cancelled) return;
        setError("Can't reach the backend API. Is it running on the configured URL?");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, REFRESH_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <main>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Outreach Sequences</h1>
        <Link
          href="/add"
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700"
        >
          Add Contact
        </Link>
      </div>

      {!trackingEnabled && !error && (
        <p className="mb-4 rounded-md bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
          Open tracking is off (PUBLIC_BASE_URL not configured on the backend).
        </p>
      )}

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}

      {!error && loading && <p className="text-sm text-gray-500">Loading...</p>}

      {!error && !loading && (
        <div className="overflow-x-auto rounded-md border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left font-medium">Contact</th>
                <th className="px-4 py-2 text-left font-medium">Subject</th>
                <th className="px-4 py-2 text-left font-medium">Status</th>
                <th className="px-4 py-2 text-left font-medium">Step</th>
                <th className="px-4 py-2 text-left font-medium">Sent</th>
                <th className="px-4 py-2 text-left font-medium">Opened</th>
                <th className="px-4 py-2 text-left font-medium">Last Sent</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {sequences.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-gray-400">
                    No sequences yet.
                  </td>
                </tr>
              )}
              {sequences.map((seq) => (
                <tr key={seq.id}>
                  <td className="px-4 py-2">{seq.contact_name}</td>
                  <td className="px-4 py-2">{seq.subject}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${
                        STATUS_STYLES[seq.status] ?? "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {seq.status}
                    </span>
                  </td>
                  <td className="px-4 py-2">{seq.current_step}</td>
                  <td className="px-4 py-2">{seq.sent_count}</td>
                  <td className="px-4 py-2">{trackingEnabled ? seq.opened_count : "—"}</td>
                  <td className="px-4 py-2">
                    {seq.last_sent_at ? new Date(seq.last_sent_at).toLocaleString() : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
