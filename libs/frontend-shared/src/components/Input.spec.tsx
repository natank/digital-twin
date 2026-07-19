import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { Input } from './Input';

describe('Input', () => {
  it('associates the label with the input', () => {
    render(<Input label="Email" />);
    // getByLabelText only resolves if the label/input wiring is correct.
    expect(screen.getByLabelText('Email')).toBeTruthy();
  });

  it('accepts typed input', async () => {
    render(<Input label="Email" />);

    const input = screen.getByLabelText<HTMLInputElement>('Email');
    await userEvent.type(input, 'user@example.com');

    expect(input.value).toBe('user@example.com');
  });

  it('shows an error message and marks the field invalid', () => {
    render(<Input label="Email" error="Email is required" />);

    const input = screen.getByLabelText('Email');
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(screen.getByRole('alert').textContent).toBe('Email is required');
  });

  it('shows helper text when there is no error', () => {
    render(<Input label="Email" helperText="We never share this" />);

    expect(screen.getByText('We never share this')).toBeTruthy();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('prefers the error over helper text', () => {
    render(<Input label="Email" helperText="Helper" error="Bad email" />);

    expect(screen.getByText('Bad email')).toBeTruthy();
    expect(screen.queryByText('Helper')).toBeNull();
  });

  it('links the message to the input via aria-describedby', () => {
    render(<Input label="Email" error="Bad email" />);

    const describedBy = screen.getByLabelText('Email').getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();
    expect(document.getElementById(describedBy as string)?.textContent).toBe('Bad email');
  });

  it('is not marked invalid when there is no error', () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText('Email').getAttribute('aria-invalid')).toBeNull();
  });

  it('gives each instance a unique id', () => {
    render(
      <>
        <Input label="First" />
        <Input label="Second" />
      </>
    );

    const first = screen.getByLabelText('First').getAttribute('id');
    const second = screen.getByLabelText('Second').getAttribute('id');
    expect(first).not.toBe(second);
  });
});
