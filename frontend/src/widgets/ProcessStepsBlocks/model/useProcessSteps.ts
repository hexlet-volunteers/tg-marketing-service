import type { Step } from './types';
import { stepsFixture } from '@/shared/mocks/widgets';

export const useProcessSteps = (): { steps: Step[] } => {
  return { steps: stepsFixture };
};
