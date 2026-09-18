import { useState } from 'react';
import type { Tariff } from './types';
import { tariffsFixture } from '@/shared/mocks/widgets';

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
