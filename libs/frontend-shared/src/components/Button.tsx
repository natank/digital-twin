import type { ButtonHTMLAttributes, ReactNode } from 'react';

import styles from './Button.module.css';

export type ButtonVariant = 'primary' | 'secondary' | 'danger';
export type ButtonSize = 'small' | 'medium' | 'large';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Shows a loading state and prevents interaction. */
  isLoading?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  disabled,
  children,
  className,
  ...rest
}: ButtonProps) {
  const classes = [styles['button'], styles[variant], styles[size], className]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type="button"
      className={classes}
      // A loading button must not be clickable, even if the caller didn't
      // also pass `disabled`.
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...rest}
    >
      {isLoading ? 'Loading…' : children}
    </button>
  );
}

export default Button;
