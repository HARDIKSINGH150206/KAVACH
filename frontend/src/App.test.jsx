import { render, screen, fireEvent } from '@testing-library/react';
import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest';
import App from './App.jsx';

// Mock the custom hooks
vi.mock('./hooks/useWebSocket.js', () => ({
      useWebSocket: vi.fn(),
}));

vi.mock('./hooks/useBackendStatus.js', () => ({
      useBackendStatus: vi.fn(),
}));

import { useWebSocket } from './hooks/useWebSocket.js';
import { useBackendStatus } from './hooks/useBackendStatus.js';

describe('App', () => {
      beforeEach(() => {
            HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
                  clearRect: vi.fn(),
                  fillRect: vi.fn(),
                  beginPath: vi.fn(),
                  moveTo: vi.fn(),
                  lineTo: vi.fn(),
                  stroke: vi.fn(),
                  fill: vi.fn(),
            }));
            // Default mock implementations
            useWebSocket.mockReturnValue({
                  data: null,
                  connected: true,
                  error: null,
                  lastMessageAt: null,
                  retryCount: 0,
            });
            useBackendStatus.mockReturnValue({
                  health: { mode: 'demo' },
                  config: { audio_weight: 0.55 },
                  error: null,
            });
      });

      afterEach(() => {
            vi.clearAllMocks();
      });

      it('renders the main app structure', () => {
            render(<App />);
            expect(screen.getByText('KAVACH')).toBeInTheDocument();
            expect(screen.getByText('India’s first real-time, offline dual-vector AI shield')).toBeInTheDocument();
            expect(screen.getByText('LIVE')).toBeInTheDocument();
      });

      it('renders with default threat level', () => {
            render(<App />);
            expect(screen.getAllByText('SAFE').length).toBeGreaterThan(0);
            expect(screen.getByText('Awaiting stream events')).toBeInTheDocument();
      });

      it('resets dashboard when reset button is clicked', () => {
            render(<App />);

            // Find the reset button in DemoControls
            const resetButton = screen.getByRole('button', { name: /reset dashboard/i });
            fireEvent.click(resetButton);

            // The component should still render without error
            expect(screen.getByText('KAVACH')).toBeInTheDocument();
      });
});
