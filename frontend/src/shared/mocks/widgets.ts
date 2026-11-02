import type { AiDemoBlockProps } from '@/widgets/AiDemoBlock/model/types';
import type { FaqItem } from '@/widgets/FaqBlock/model/types';
import type { Step } from '@/widgets/ProcessStepsBlocks/model/types';

export const aiDemoFixture: AiDemoBlockProps = {
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


export const faqFixture: FaqItem[] = [
  { id: 1, question: 'Что такое TG Pulse?', answer: 'TG Pulse — это сервис аналитики Telegram-каналов с AI-инсайтами. Мы помогаем авторам и рекламодателям принимать решения на основе данных.' },
  { id: 2, question: 'Как добавить свой канал?', answer: 'Перейдите в каталог каналов и нажмите «Добавить свой канал». Следуйте инструкциям для подключения и модерации.' },
  { id: 3, question: 'Безопасны ли мои данные?', answer: 'Да, мы не передаём данные третьим лицам и храним их на защищённых серверах. Ознакомьтесь с политикой конфиденциальности.' },
  { id: 4, question: 'Можно ли использовать сервис бесплатно?', answer: 'Да, у нас есть бесплатный тариф с базовой функциональностью. Для расширенных возможностей доступны платные планы.' },
  { id: 5, question: 'Как работает AI-анализ?', answer: 'Наш AI анализирует контент канала, вовлечённость аудитории и даёт персонализированные рекомендации по улучшению.' },
];

export const stepsFixture: Step[] = [
  { id: 1, title: 'Добавьте канал', description: 'Подключите свой Telegram-канал к платформе за несколько кликов.' },
  { id: 2, title: 'Получите аналитику', description: 'AI анализирует контент, аудиторию и динамику роста вашего канала.' },
  { id: 3, title: 'Растите быстрее', description: 'Следуйте персональным рекомендациям и увеличивайте вовлечённость.' },
];
