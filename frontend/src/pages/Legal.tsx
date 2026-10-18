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
 * Данные для сегментированного переключателя вкладок.
 * Используются для переключения вкладок, 
 * и проверяет корректность значения параметра запроса через функцию {@link checkTab}.
 */
const segmentedControlData: {label: string, value: string}[] = [
  { label: 'Конфиденциальность', value: 'privacy' },
  { label: 'Соглашение', value: 'terms' },
  { label: 'Оферта', value: 'offer' },
];

/**
 * Вкладка по умолчанию.
 * Отображается при отсутствии или некорректности параметра запроса tab.
 */
const defaultTab = 'privacy';

/**
 * Проверяет, является ли переданное значение допустимой вкладкой.
 * @param tab - Значение параметра запроса для проверки.
 * @returns `true`, если значение присутствует в {@link segmentedControlData}, иначе `false`.
 */
function checkTab(tab: string): boolean {
  return segmentedControlData.some(({ value }) => value === tab);
}

/**
 * Страница с правовой информацией.
 *
 * Отображает содержимое одной из вкладок (конфиденциальность, соглашение, оферта)
 * в зависимости от query-параметра tab. 
 * Если параметр отсутствует или содержитнедопустимое значение,
 * используется вкладка по умолчанию ({@link defaultTab}).
 *
 * @param props - свойства компонента.
 * @param props.legalContent - объект с правовым контентом для каждой вкладки.
 * По умолчанию используется {@link mockLegalContent}.
 * @returns React-компонент страницы с правовой информацией.
 * В случае недопустимого значения tab, setSearchParams в UseEffect исправляет URL на вкладку по умолчанию.
 */
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
