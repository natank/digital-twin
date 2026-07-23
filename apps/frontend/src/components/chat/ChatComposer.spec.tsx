import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { ChatComposer } from './ChatComposer';

describe('ChatComposer', () => {
  it('submits on button click', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onChange = vi.fn();
    render(<ChatComposer value="Hello" onChange={onChange} onSubmit={onSubmit} />);
    await user.click(screen.getByRole('button', { name: /send/i }));
    expect(onSubmit).toHaveBeenCalled();
  });

  it('submits on Enter without Shift', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ChatComposer value="Hi" onChange={vi.fn()} onSubmit={onSubmit} />);
    await user.type(screen.getByLabelText(/message/i), '{Enter}');
    expect(onSubmit).toHaveBeenCalled();
  });
});
