import { useState } from 'react';
import type { AiDemoBlockProps, AiDemoButton } from './types';
import { aiDemoFixture } from '@/shared/mocks/widgets';

export const useAiDemo = (): {
  data: AiDemoBlockProps;
  activeButton: string;
  handleButtonClick: (button: AiDemoButton) => void;
} => {
  const aiDemo = aiDemoFixture;

  const [activeButton, setActiveButton] = useState<string>(aiDemo.tryButton?.label || '');

  const handleButtonClick = (button: AiDemoButton) => {
    setActiveButton(button.label);
  };

  return {
    data: {
      description: aiDemo.description ?? '',
      features: aiDemo.features ?? [],
      tryButton: aiDemo.tryButton,
      demoButton: aiDemo.demoButton,
      demoTitle: aiDemo.demoTitle ?? '',
    },
    activeButton,
    handleButtonClick,
  };
};
