import { useState } from 'react';
import type { Tariff } from './types';

const tariffsFixture: Tariff[] = [
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

export const useTariffsBlock = (): {
  tariffs: Tariff[];
  activeTariffId: number | null;
  setActiveTariffId: (id: number) => void;
} => {
  const tariffs = tariffsFixture;

  const [activeTariffId, setActiveTariffId] = useState<number | null>(
    tariffs.find(t => t.isHighlighted)?.id ?? null
  );

  return { tariffs, activeTariffId, setActiveTariffId };
};
