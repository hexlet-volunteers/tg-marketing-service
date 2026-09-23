import type { AiDemoBlockProps } from '@/widgets/AiDemoBlock/model/types';
import type { FaqItem } from '@/widgets/FaqBlock/model/types';
import type { Step } from '@/widgets/ProcessStepsBlocks/model/types';
import type { Tariff } from '@/widgets/TariffsBlock/model/types';

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

export const tariffsFixture: Tariff[] = [
  {
    id: 1, name: 'Free', label: undefined, description: 'Для тех, кто начинает изучать Telegram-аналитику',
    price: '0 ₽', period: 'навсегда', monthlyPrice: 0,
    features: [
      { id: 1, text: 'Базовая статистика' },
      { id: 2, text: '5 AI-разборов / мес' },
      { id: 3, text: 'Каталог каналов' },
    ],
    button: { label: 'Начать бесплатно', variant: 'default' },
  },
  {
    id: 2, name: 'Pro', label: 'Популярный', description: 'Для авторов и рекламодателей, которым важны данные',
    price: '990 ₽', period: 'в месяц', monthlyPrice: 990,
    features: [
      { id: 1, text: 'Всё из Free' },
      { id: 2, text: 'Безлимит AI-разборов' },
      { id: 3, text: 'Контент-план на неделю' },
      { id: 4, text: 'Сравнение до 5 каналов' },
      { id: 5, text: 'Экспорт отчётов' },
    ],
    button: { label: 'Выбрать Pro', variant: 'primary' },
    isHighlighted: true,
    isPopular: true,
  },
  {
    id: 3, name: 'Agency', label: undefined, description: 'Для агентств и команд, работающих с множеством каналов',
    price: '4 900 ₽', period: 'в месяц', monthlyPrice: 4900,
    features: [
      { id: 1, text: 'Всё из Pro' },
      { id: 2, text: 'До 50 каналов' },
      { id: 3, text: 'API-доступ' },
      { id: 4, text: 'Командный доступ' },
    ],
    button: { label: 'Выбрать Agency', variant: 'default' },
  },
];