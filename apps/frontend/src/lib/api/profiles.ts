/** Profile API helpers (owner-scoped `/profiles/me/*`). */

import { apiFetch } from './client';

export interface ProfileWire {
  id: string;
  owner_id: string;
  bio: string | null;
  headline: string | null;
  skills: string[] | null;
  experience_years: number | null;
  profile_summary: Record<string, unknown> | null;
  has_cv: boolean;
  has_extracted_text: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ProfileUpdateBody {
  bio?: string | null;
  headline?: string | null;
  skills?: string[] | null;
  experience_years?: number | null;
}

export interface ProfileSummaryWire {
  profile_summary: Record<string, unknown> | null;
  skills: string[] | null;
  experience_years: number | null;
}

export interface CVUploadWire {
  cv_file_path: string;
  filename: string;
  content_type: string;
  size_bytes: number;
}

export interface CVJobWire {
  id: string;
  owner_id: string;
  status: string;
  cv_file_path: string;
  error_message: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export function getMyProfile(token: string): Promise<ProfileWire> {
  return apiFetch<ProfileWire>('/profiles/me', { token });
}

export function updateMyProfile(token: string, body: ProfileUpdateBody): Promise<ProfileWire> {
  return apiFetch<ProfileWire>('/profiles/me', {
    method: 'PUT',
    token,
    body: JSON.stringify(body),
  });
}

export function getMySummary(token: string): Promise<ProfileSummaryWire> {
  return apiFetch<ProfileSummaryWire>('/profiles/me/summary', { token });
}

export function updateMySummary(
  token: string,
  body: {
    profile_summary: Record<string, unknown>;
    skills?: string[] | null;
    experience_years?: number | null;
  },
): Promise<ProfileSummaryWire> {
  return apiFetch<ProfileSummaryWire>('/profiles/me/summary', {
    method: 'PUT',
    token,
    body: JSON.stringify(body),
  });
}

export function regenerateMySummary(token: string): Promise<ProfileSummaryWire> {
  return apiFetch<ProfileSummaryWire>('/profiles/me/summary/regenerate', {
    method: 'POST',
    token,
  });
}

export function uploadMyCv(token: string, file: File): Promise<CVUploadWire> {
  const form = new FormData();
  form.append('file', file);
  return apiFetch<CVUploadWire>('/profiles/me/cv', {
    method: 'POST',
    token,
    body: form,
    skipJsonContentType: true,
  });
}

export function processMyCv(token: string): Promise<CVJobWire> {
  return apiFetch<CVJobWire>('/profiles/me/process-cv', {
    method: 'POST',
    token,
  });
}

export function getMyCvJob(token: string, jobId: string): Promise<CVJobWire> {
  return apiFetch<CVJobWire>(`/profiles/me/cv/jobs/${jobId}`, { token });
}
