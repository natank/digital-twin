import { useId, type InputHTMLAttributes } from 'react';

import styles from './Input.module.css';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string;
  /** Validation message; when set, the field is marked invalid. */
  error?: string;
  /** Hint shown below the field when there is no error. */
  helperText?: string;
}

export function Input({
  label,
  error,
  helperText,
  className,
  required,
  ...rest
}: InputProps) {
  // Generated so multiple Inputs on one page never collide, and so the
  // label/description associations stay correct without caller effort.
  const inputId = useId();
  const messageId = `${inputId}-message`;
  const message = error ?? helperText;

  return (
    <div className={styles['field']}>
      <label className={styles['label']} htmlFor={inputId}>
        {label}
        {required && (
          <span className={styles['required']} aria-hidden="true">
            {' '}
            *
          </span>
        )}
      </label>
      <input
        id={inputId}
        className={[styles['input'], error && styles['inputError'], className]
          .filter(Boolean)
          .join(' ')}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={message ? messageId : undefined}
        {...rest}
      />
      {message && (
        <p
          id={messageId}
          className={error ? styles['errorText'] : styles['helperText']}
          // Announce validation failures to screen readers as they appear.
          role={error ? 'alert' : undefined}
        >
          {message}
        </p>
      )}
    </div>
  );
}

export default Input;
