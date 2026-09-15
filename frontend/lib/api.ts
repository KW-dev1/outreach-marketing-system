const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:5000";

export type SequenceStatus = "pending" | "active" | "replied" | "completed";

export interface SequenceSummary {
  id: number;
  contact_name: string;
  subject: string;
  status: SequenceStatus;
  current_step: number;
  sent_count: number;
  opened_count: number;
  last_sent_at: string | null;
}

export interface SequencesResponse {
  sequences: SequenceSummary[];
  tracking_enabled: boolean;
}

export interface NewContactPayload {
  name: string;
  emails: string;
  subject: string;
  first_body: string;
  followup1_body?: string;
  followup2_body?: string;
}

export async function fetchSequences(): Promise<SequencesResponse> {
  const res = await fetch(`${API_URL}/api/sequences`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Request failed with status ${res.status}`);
  }
  return res.json();
}

export async function createContact(payload: NewContactPayload): Promise<void> {
  const res = await fetch(`${API_URL}/api/contacts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed with status ${res.status}`);
  }
}
