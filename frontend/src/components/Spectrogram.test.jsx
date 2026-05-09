import { render } from '@testing-library/react';
import { beforeEach, afterEach, describe, it, expect, vi } from 'vitest';
import { Spectrogram } from './Spectrogram.jsx';

describe('Spectrogram', () => {
      beforeEach(() => {
            HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
                  clearRect: vi.fn(),
                  fillRect: vi.fn(),
            }));
      });

      afterEach(() => {
            vi.restoreAllMocks();
      });

      it('renders a canvas element', () => {
            const melData = [[-60, -30, 0], [-20, -10, 10]];
            const { container } = render(<Spectrogram melData={melData} audioScore={0.2} />);
            const canvas = container.querySelector('canvas');
            expect(canvas).toBeInTheDocument();
            expect(canvas.getContext).toHaveBeenCalledWith('2d');
      });

      it('draws spectrogram frames for incoming mel data', () => {
            const melData = [[-10, 0, 10], [5, 15, 25]];
            render(<Spectrogram melData={melData} audioScore={0.8} />);
            expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith('2d');
      });
});
