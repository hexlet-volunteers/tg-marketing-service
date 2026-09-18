import type { MetricDef } from "@/types/channel";
import { formatNumberShortEn } from "@/utils/formatNumberShort";

export const mockMetrics: MetricDef[] = [
  { key: 'subscribers', label: 'Подписчики', format: (v) => formatNumberShortEn(v) },
  { key: 'er', label: 'ER', format: (v) => `${v.toFixed(1)}%` },
  { key: 'growth30d', label: 'Прирост 30д', format: (v) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` },
  { key: 'avgReach', label: 'Средний охват', format: (v) => formatNumberShortEn(v) },
  { key: 'reachPerSub', label: 'Охват/подписчик', format: (v) => `${v.toFixed(1)}%` },
];