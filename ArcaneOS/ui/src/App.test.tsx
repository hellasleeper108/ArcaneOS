import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders ArcaneOS component', () => {
  render(<App />);
  const buttonElement = screen.getByText(/Enter Dev Mode/i);
  expect(buttonElement).toBeInTheDocument();
});
