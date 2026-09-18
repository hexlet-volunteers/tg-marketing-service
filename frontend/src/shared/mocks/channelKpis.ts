import type { Kpi, GrowthSubscribersData } from "@/types/channel";

export const mockKpis: Kpi[] = [
  { label: 'Подписчики', value: 142340, delta: 2480, percentDelta: 1.8, positive: true },
  { label: 'Ср. охват', value: 38200, percentDelta: 4.1, positive: true },
  { label: 'ER', value: 26.9, percentDelta: -1.2, positive: false },
  { label: 'Индекс цитирования', value: 184, delta: 9, positive: true },
];

export const mockGrowthData: GrowthSubscribersData[] = [
  { date: '01.06', подписчики: 134200 },
  { date: '05.06', подписчики: 135800 },
  { date: '10.06', подписчики: 136400 },
  { date: '15.06', подписчики: 137900 },
  { date: '20.06', подписчики: 139100 },
  { date: '25.06', подписчики: 140300 },
  { date: '30.06', подписчики: 142340 },
];
