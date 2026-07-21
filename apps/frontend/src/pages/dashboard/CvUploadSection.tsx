import { useCallback, useEffect, useRef, useState, type JSX } from 'react';
import { Button } from 'frontend-shared';

import { ApiClientError } from '../../lib/api/client';
import {
  getMyCvJob,
  getMyProfile,
  processMyCv,
  uploadMyCv,
  type CVJobWire,
  type ProfileWire,
} from '../../lib/api/profiles';
import styles from '../Page.module.css';

const TERMINAL = new Set(['completed', 'failed', 'succeeded', 'done', 'error']);

function isTerminal(status: string): boolean {
  const s = status.toLowerCase();
  return TERMINAL.has(s) || s.includes('complete') || s.includes('fail') || s.includes('error');
}

export interface CvUploadSectionProps {
  token: string;
  profile: ProfileWire | null;
  onProfileRefresh: (profile: ProfileWire) => void;
}

export function CvUploadSection({
  token,
  profile,
  onProfileRefresh,
}: CvUploadSectionProps): JSX.Element {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [job, setJob] = useState<CVJobWire | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback((): void => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => () => stopPolling(), [stopPolling]);

  const pollJob = useCallback(
    (jobId: string): void => {
      stopPolling();
      pollRef.current = setInterval(() => {
        void (async () => {
          try {
            const next = await getMyCvJob(token, jobId);
            setJob(next);
            if (isTerminal(next.status)) {
              stopPolling();
              setProcessing(false);
              if (next.status.toLowerCase().includes('fail') || next.error_message) {
                setError(next.error_message || `Job ${next.status}`);
              } else {
                setMessage(`Processing ${next.status}.`);
                const refreshed = await getMyProfile(token);
                onProfileRefresh(refreshed);
              }
            }
          } catch (err) {
            stopPolling();
            setProcessing(false);
            setError(err instanceof ApiClientError ? err.message : 'Failed to poll job status.');
          }
        })();
      }, 1500);
    },
    [token, onProfileRefresh, stopPolling],
  );

  async function onUpload(): Promise<void> {
    if (!file) {
      setError('Choose a PDF or DOCX file first.');
      return;
    }
    setUploading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await uploadMyCv(token, file);
      setMessage(`Uploaded ${result.filename} (${result.size_bytes} bytes).`);
      const refreshed = await getMyProfile(token);
      onProfileRefresh(refreshed);
      setFile(null);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : 'Upload failed.');
    } finally {
      setUploading(false);
    }
  }

  async function onProcess(): Promise<void> {
    setProcessing(true);
    setError(null);
    setMessage(null);
    try {
      const created = await processMyCv(token);
      setJob(created);
      setMessage(`Job ${created.id.slice(0, 8)}… status: ${created.status}`);
      if (!isTerminal(created.status)) {
        pollJob(created.id);
      } else {
        setProcessing(false);
        const refreshed = await getMyProfile(token);
        onProfileRefresh(refreshed);
      }
    } catch (err) {
      setProcessing(false);
      setError(err instanceof ApiClientError ? err.message : 'Failed to start CV processing.');
    }
  }

  return (
    <section className={styles.panel} aria-labelledby="cv-upload-heading">
      <h2 id="cv-upload-heading">CV upload</h2>
      <p className={styles.muted}>
        Upload a PDF or DOCX, then run processing to extract text and generate a profile summary.
        {profile?.has_cv ? ' A CV is already on file.' : ' No CV on file yet.'}
      </p>
      <div className={styles.fileRow}>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          aria-label="CV file"
          onChange={(ev) => setFile(ev.target.files?.[0] ?? null)}
        />
        <Button
          type="button"
          isLoading={uploading}
          disabled={!file}
          onClick={() => void onUpload()}
        >
          Upload
        </Button>
        <Button
          type="button"
          variant="secondary"
          isLoading={processing}
          disabled={!profile?.has_cv}
          onClick={() => void onProcess()}
        >
          Process CV
        </Button>
      </div>
      {job && (
        <p className={styles.muted} role="status">
          Job status: <strong>{job.status}</strong>
          {job.error_message ? ` — ${job.error_message}` : ''}
        </p>
      )}
      {error && (
        <p className={styles.formError} role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className={styles.formSuccess} role="status">
          {message}
        </p>
      )}
    </section>
  );
}
