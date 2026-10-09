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
import { useEffect } from 'react';

/**
 * Для отображения соответствующего контента используется параметр tab из query string.
 * По умолчанию tab имеет значение 'privacy', если параметр запроса отсутствует или недействителен.
 * Данные компонента SegmentedControl определены отдельно в массиве объектов со свойствами label и value.
 * Массив используется для рендеринга вкладок и проверки допустимости запрашиваемой вкладки через функцию checkTab.
 * В случае недопустимого значения tab, setSearchParams в UseEffect исправляет URL на вкладку по умолчанию.
 */
const segmentedControlData: {label: string, value: string}[] = [
  { label: 'Конфиденциальность', value: 'privacy' },
  { label: 'Соглашение', value: 'terms' },
  { label: 'Оферта', value: 'offer' },
];

const defaultTab = 'privacy';

function checkTab(tab: string): boolean {
  return segmentedControlData.some(({ value }) => value === tab);
}

const LegalPage = ({ legalContent = mockLegalContent }: LegalPageProps) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedTab = searchParams.get('tab') ?? defaultTab;
  const isTabValid = checkTab(requestedTab);
  const tab = isTabValid ? requestedTab : defaultTab;

  useEffect(() => {
    if (!isTabValid) {
      setSearchParams({ tab: defaultTab }, { replace: true });
    }
  }, [isTabValid, setSearchParams]);

/**
 * Исправлен обработчик onChange для обновления параметра запроса вместо состояния.
 * Добавлены CSS свойства для компонента SegmentedControl, чтобы соответствовать дизайну.
 */
  return (
    <Container>
      <Title order={1} mb="lg">
        Правовая информация
      </Title>
      <SegmentedControl
        data={segmentedControlData}
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
