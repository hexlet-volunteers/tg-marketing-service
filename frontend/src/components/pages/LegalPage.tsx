import {
  Container,
  Paper,
  SegmentedControl,
  Text,
  Title,
} from '@mantine/core';
import type { LegalPageProps } from '@/types/legal';
import mockLegalContent from '@/shared/mocks/legalContent';
import { useSearchParams } from 'react-router-dom';

const LegalPage = ({ legalContent = mockLegalContent }: LegalPageProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = searchParams.get('tab') || 'privacy';

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
        onChange={(v: string) => setSearchParams({ tab: v })}
        mb="lg"
        radius={99}
        color='tgblue.5'
        bg='white'
        autoContrast
        withItemsBorders={false}
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
