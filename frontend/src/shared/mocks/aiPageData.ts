import type { IdeaData, InsightData, Competitor, HeatMapData } from '@/types/aiCabinet'

export const mockIdeasData: IdeaData[] = [
  {
    title: 'Обзор новых функций Telegram',
    reason: 'Актуальная тема, растущий интерес',
    scope: 48222,
    date: 'чт 19:30',
  },
  {
    title: 'Как монетизировать Telegram-канал',
    reason: 'Высокий спрос среди авторов',
    scope: 61800,
    date: 'ср 20:00',
  },
  {
    title: 'Топ-10 ботов для автоматизации',
    reason: 'Техническая аудитория ищет инструменты',
    scope: 35123,
    date: 'пт 18:00',
  },
];

export const mockInsightsData: InsightData[] = [
  { type: 'recommendation', text: 'Публикуйте посты в среду в 19:00 — пик активности' },
  { type: 'trend', text: 'Вовлечённость выросла на 12% за месяц' },
  { type: 'warning', text: 'Частота публикаций упала — рекомендуем 3-4 поста в неделю' },
  { type: 'positive', text: 'Новых подписчиков больше, чем отписок в 3.2 раза' },
];

export const mockCompetitors: Competitor[] = [
  { name: '@techreview', er: 9.2, delta: 1.1 },
  { name: '@droider', er: 7.8, delta: -0.5 },
  { name: '@habr', er: 6.1, delta: -2.2 },
];

export const mockHeatMapData: HeatMapData = {
  Пн: { 9: 3, 10: 5, 12: 7, 14: 6, 17: 8, 19: 9, 20: 10, 21: 8 },
  Вт: { 10: 4, 12: 6, 14: 5, 17: 7, 19: 8, 20: 9, 21: 7 },
  Ср: { 9: 4, 10: 6, 12: 8, 14: 7, 17: 9, 19: 10, 20: 10, 21: 9 },
  Чт: { 10: 5, 12: 7, 14: 6, 17: 8, 19: 9, 20: 8, 21: 7 },
  Пт: { 10: 4, 12: 6, 14: 5, 17: 6, 19: 7, 20: 8, 21: 6 },
  Сб: { 11: 3, 13: 4, 15: 5, 17: 5, 19: 6, 20: 7 },
  Вс: { 12: 3, 14: 4, 16: 5, 18: 5, 20: 6, 21: 5 },
};