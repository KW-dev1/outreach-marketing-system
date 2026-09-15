"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createContact } from "@/lib/api";

export default function AddContactPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const form = new FormData(e.currentTarget);
    try {
      await createContact({
        name: String(form.get("name") || ""),
        emails: String(form.get("emails") || ""),
        subject: String(form.get("subject") || ""),
        first_body: String(form.get("first_body") || ""),
        followup1_body: String(form.get("followup1_body") || ""),
        followup2_body: String(form.get("followup2_body") || ""),
      });
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-semibold">Add Contact</h1>

      {error && (
        <p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Name" name="name" required />
        <Field
          label="Email(s)"
          name="emails"
          required
          placeholder="jane@example.com, jane.doe@work.com"
        />
        <Field label="Subject" name="subject" required />
        <TextArea label="First Message" name="first_body" required />
        <TextArea label="Follow-up 1 (optional)" name="followup1_body" />
        <TextArea label="Follow-up 2 (optional)" name="followup2_body" />

        <button
          type="submit"
          disabled={submitting}
          className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
        >
          {submitting ? "Saving..." : "Create & Send"}
        </button>
      </form>
    </main>
  );
}

function Field({
  label,
  name,
  required,
  placeholder,
}: {
  label: string;
  name: string;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium">{label}</label>
      <input
        name={name}
        required={required}
        placeholder={placeholder}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
      />
    </div>
  );
}

function TextArea({
  label,
  name,
  required,
}: {
  label: string;
  name: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium">{label}</label>
      <textarea
        name={name}
        required={required}
        rows={5}
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
      />
    </div>
  );
}
