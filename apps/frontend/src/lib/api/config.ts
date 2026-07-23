/** Digital twin config API (`/config/me/*`). */

import { apiFetch } from './client';

export interface TwinConfigWire {
  id: string;
  owner_id: string;
  system_prompt: string;
  tone: string;
  response_length: string;
  allowed_topics: string[] | null;
  forbidden_topics: string[] | null;
  brand_guidelines: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface PromptVersionWire {
  version_number: number;
  system_prompt: string;
  created_at?: string | null;
}

export function getTwinConfig(token: string): Promise<TwinConfigWire> {
  return apiFetch<TwinConfigWire>('/config/me', { token });
}

export function updateTwinConfig(
  token: string,
  body: Partial<{
    system_prompt: string;
    tone: string;
    response_length: string;
    allowed_topics: string[] | null;
    forbidden_topics: string[] | null;
    brand_guidelines: string | null;
  }>,
): Promise<TwinConfigWire> {
  return apiFetch<TwinConfigWire>('/config/me', {
    method: 'PUT',
    token,
    body: JSON.stringify(body),
  });
}

export function listPromptVersions(token: string): Promise<{ versions: PromptVersionWire[] }> {
  return apiFetch<{ versions: PromptVersionWire[] }>('/config/me/system-prompt/versions', {
    token,
  });
}

export function previewSystemPrompt(
  token: string,
  body: { system_prompt: string; sample_question: string },
): Promise<{ rendered_system_prompt: string; sample_reply: string }> {
  return apiFetch('/config/me/system-prompt/preview', {
    method: 'POST',
    token,
    body: JSON.stringify(body),
  });
}

export function restorePromptVersion(
  token: string,
  versionNumber: number,
): Promise<{ system_prompt: string; version_number?: number | null }> {
  return apiFetch(`/config/me/system-prompt/restore/${versionNumber}`, {
    method: 'POST',
    token,
  });
}
