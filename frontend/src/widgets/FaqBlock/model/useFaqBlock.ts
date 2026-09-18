import type { FaqItem } from './types';
import { faqFixture } from '@/shared/mocks/widgets';

export const useFaqBlock = (): { faqs: FaqItem[] } => {
  return { faqs: faqFixture };
};
