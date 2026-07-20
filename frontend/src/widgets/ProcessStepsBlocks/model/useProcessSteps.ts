import type { Step } from './types';

const stepsFixture: Step[] = [
  { id: 1, title: 'Добавьте канал', description: 'Подключите свой Telegram-канал к платформе за несколько кликов.' },
  { id: 2, title: 'Получите аналитику', description: 'AI анализирует контент, аудиторию и динамику роста вашего канала.' },
  { id: 3, title: 'Растите быстрее', description: 'Следуйте персональным рекомендациям и увеличивайте вовлечённость.' },
];

export const useProcessSteps = (): { steps: Step[] } => {
  return { steps: stepsFixture };
};
