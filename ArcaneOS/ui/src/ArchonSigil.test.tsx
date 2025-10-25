import React from 'react';
import { render, screen } from '@testing-library/react';
import { ArchonSigil } from './components/ArchonSigil';
import { useArchonSocket } from './lib/events';

jest.mock('./lib/events', () => ({
  useArchonSocket: jest.fn(),
}));

describe('ArchonSigil', () => {
  beforeEach(() => {
    (useArchonSocket as jest.Mock).mockReturnValue({
      archonState: 'idle',
      message: null,
      clearMessage: jest.fn(),
    });
  });

  test('renders with correct class for fantasy mode', () => {
    render(<ArchonSigil isFantasyMode={true} />);
    expect(screen.getByTestId('archon-sigil')).not.toHaveClass('wireframe');
  });

  test('renders with correct class for dev mode', () => {
    render(<ArchonSigil isFantasyMode={false} />);
    expect(screen.getByTestId('archon-sigil')).toHaveClass('wireframe');
  });

  test('displays a toast message', () => {
    (useArchonSocket as jest.Mock).mockReturnValue({
      archonState: 'idle',
      message: 'A test message',
      clearMessage: jest.fn(),
    });
    render(<ArchonSigil isFantasyMode={true} />);
    expect(screen.getByText(/A test message/i)).toBeInTheDocument();
  });
});
