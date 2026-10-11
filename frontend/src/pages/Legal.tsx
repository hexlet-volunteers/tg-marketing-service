import {
  Container,
  Paper,
  SegmentedControl,
  Text,
  Title,
} from '@mantine/core';
import React from 'react';
import type { LegalPageProps } from '@/types/legal';
import mockLegalContent from '@/shared/mocks/legalContent';

const LegalPage = ({ legalContent = mockLegalContent }: LegalPageProps) => {
  const [tab, setTab] = React.useState('privacy');

  return (
    <Container>
      <Title order={1} mb="lg">
        Правовая информация
      </Title>
      <SegmentedControl
        data={[
          { label: 'Конфиденциальность', value: 'privacy' },
          { label: 'Соглашение', value: 'terms' },
          { label: 'Оферта', value: 'offer' },
        ]}
        value={tab}
        onChange={(v) => setTab(v as string)}
        mb="lg"
        fullWidth
      />
      <Paper p="lg">
        {(() => {
          const content = legalContent[tab];
          return (
            <>
              <Title order={3} mb="md">{content.title}</Title>
              <Text size="sm" c="dimmed">{content.text}</Text>
            </>
          );
        })()}
      </Paper>
    </Container>
  );
};

export default LegalPage;
