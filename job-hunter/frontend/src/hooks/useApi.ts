import { JobSource } from '../types';

const BASE = '/api';

export async function startSession(cvText: string, threadId: string): Promise<{
  status: string;
  sources: JobSource[];
  message: string;
}> {
  const res = await fetch(`${BASE}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cv_text: cvText, thread_id: threadId }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function approveSources(threadId: string, approvedIndices: number[]): Promise<{
  status: string;
  approved_sources: JobSource[];
  summary: string;
}> {
  const res = await fetch(`${BASE}/approve-sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, approved_indices: approvedIndices }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
