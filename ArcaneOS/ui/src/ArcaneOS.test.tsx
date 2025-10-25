import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ArcaneOS from './ArcaneOS';

describe('ArcaneOS', () => {
  test('renders Terminal component by default', () => {
    render(<ArcaneOS />);
    expect(screen.getByText(/The weave is stable./i)).toBeInTheDocument();
  });

  test('switches to LogPane component on button click', () => {
    render(<ArcaneOS />);
    fireEvent.click(screen.getByText(/Enter Dev Mode/i));
    expect(screen.getByText(/Switching to Developer Mode.../i)).toBeInTheDocument();
  });

  test('switches back to Terminal component on button click', () => {
    render(<ArcaneOS />);
    fireEvent.click(screen.getByText(/Enter Dev Mode/i));
    fireEvent.click(screen.getByText(/Awaken Fantasy/i));
    expect(screen.getByText(/The weave is stable./i)).toBeInTheDocument();
  });
});
