import { useState } from 'react';
import type { AiDemoBlockProps, AiDemoButton } from './types';

const aiDemoFixture: AiDemoBlockProps = {
  description: 'AI-ассистент поможет с анализом канала, подбором контента и оптимизация постов.',
  features: [
    { id: 1, text: 'Анализ вовлечённости аудитории' },
    { id: 2, text: 'Рекомендации по времени публикации' },
    { id: 3, text: 'Генерация идей для контента' },
  ],
  tryButton: { label: 'Попробовать AI', variant: 'primary' },
  demoButton: { label: 'Смотреть демо', variant: 'default' },
  demoTitle: 'AI-ассистент',
};

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
