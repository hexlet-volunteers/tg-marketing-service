import { Box, Container, SimpleGrid, Title } from '@mantine/core';
import React, { useState } from 'react';
import type { TariffsBlockProps } from '../model/types';
import { useTariffsBlock } from '../model/useTariffsBlock';
import { TariffCard } from './TariffCard';

export const TariffsBlock: React.FC<TariffsBlockProps> = ({ tariffs: propsTariffs }) => {
  const { tariffs: tariffFromPage } = useTariffsBlock();
  const tariffs = propsTariffs ?? tariffFromPage;

  const [activeTariffId, setActiveTariffId] = useState<number>(
    tariffs?.find((t) => t.isHighlighted)?.id || tariffs?.[0]?.id || 0
  );

  if (!tariffs || tariffs.length === 0) return null;

  return (
    <Box
      component="section"
      bg="white"
      py={80}>
      <Container>
        <Title order={2} fw={800} c="primary" ta="center" mb={60} fz="32px">
          Тарифы
        </Title>

        <SimpleGrid cols={{ base: 1, md: 3 }} spacing={32}>
          {tariffs.map((tariff) => (
            <TariffCard
              key={tariff.id}
              {...tariff}
              isHighlighted={tariff.id === activeTariffId}
              onClick={() => setActiveTariffId(tariff.id)}
            />
          ))}
        </SimpleGrid>
      </Container>
    </Box>
  );
};
