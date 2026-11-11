import {
  Container,
  Paper,
  SegmentedControl,
  Text,
  Title,
} from '@mantine/core';
import type { LegalPageProps } from '@/types/legal';
import { router, usePage } from '@inertiajs/react';

/**
 * Данные для вкладок правовой информации.
 * Используются в компоненте SegmentedControl для отображения вкладок,
 * а также для определения, какая вкладка должна быть активной в соответствии с query-параметром `tab`.
 */

const legalLabelsData: { label: string; value: string }[] = [
  { label: "Конфиденциальность", value: "privacy" },
  { label: "Соглашение", value: "agreement" },
  { label: "Оферта", value: "offer" },
];

/**
 * Страница правовой информации.
 *
 * Отображает содержимое одной из вкладок (конфиденциальность, соглашение, оферта)
 * в соответствии с query-переметром tab.
 * 
 * Если query-параметр tab отсутствует или не соответствует ни одной из вкладок,
 * то по умолчанию отображается вкладка «Конфиденциальность».
 *
 * Содержимое вкладок передаётся через пропсы documents, которые формируются на сервере.
 */

const LegalPage = ({ documents }: LegalPageProps) => {
  const { url } = usePage();
  const params = new URL(url, window.location.origin).searchParams;
  const requestedTab: string | null = params.get('tab');
  const tab: string = (legalLabelsData.find(({ value }) => value === requestedTab))?.value ?? "privacy";


  return (
    <Container>
      <Title order={1} mb="lg">
        Правовая информация
      </Title>
      <SegmentedControl
        data={legalLabelsData}
        value={tab}
        onChange={(v) => router.visit(`/legal/?tab=${v}`)}
        mb="lg"
        fullWidth
      />
      <Paper p="lg">
        {(() => {
          const content = documents[tab];
          return (
            <>
              <Title fz={19} fw={800} mb={4}>{content.title}</Title>
              <Text fz={12} mb={18} c="dimmed">{`Обновлено: ${content.updated_at} · демонстрационный документ`}</Text>
              <Text fz={14} mb={16}>{content.text}</Text>
            </>
          );
        })()}
      </Paper>
    </Container>
  );
};

export default LegalPage;