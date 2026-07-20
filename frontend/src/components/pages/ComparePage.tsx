import { BrandAvatar } from '@/components/ui/BrandAvatar';
import channelsCol from '@/fixtures/channelsCollection';
import {
  Badge,
  Container,
  Group,
  Paper,
  Table,
  Text,
  Title,
} from '@mantine/core';
import { IconTrophy } from '@tabler/icons-react';
import React from 'react';

const channels = channelsCol.slice(0, 3);

function formatNumberShort(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(n);
}

interface MetricDef {
  key: string;
  label: string;
  format: (v: number) => string;
}

const metrics: MetricDef[] = [
  { key: 'subscribers', label: 'Подписчики', format: (v) => formatNumberShort(v) },
  { key: 'er', label: 'ER', format: (v) => `${v.toFixed(1)}%` },
  { key: 'growth30d', label: 'Прирост 30д', format: (v) => `${v >= 0 ? '+' : ''}${v.toFixed(1)}%` },
  { key: 'avgReach', label: 'Средний охват', format: (v) => formatNumberShort(v) },
  { key: 'reachPerSub', label: 'Охват/подписчик', format: (v) => `${v.toFixed(1)}%` },
];

const ComparePage: React.FC = () => {
  const getVal = (ch: (typeof channels)[number], key: string): number => {
    const map: Record<string, number> = {
      subscribers: ch.subscribers,
      er: ch.er,
      growth30d: ch.growth30d,
      avgReach: Math.round(ch.subscribers * 0.27),
      reachPerSub: ch.er * 0.85,
    };
    return map[key] ?? 0;
  };

  const getBest = (key: string) => {
    let bestIdx = 0;
    let bestVal = -Infinity;
    channels.forEach((ch, i) => {
      const val = getVal(ch, key);
      if (val > bestVal) {
        bestVal = val;
        bestIdx = i;
      }
    });
    return bestIdx;
  };

  return (
    <Container>
      <Title order={1} mb="lg">
        Сравнение каналов
      </Title>

      <Group gap="sm" mb="lg">
        {channels.map((ch) => (
          <Badge key={ch.id} size="lg" color="tgblue" leftSection={
            <BrandAvatar name={ch.name} size={18} />
          }>
            {ch.name}
          </Badge>
        ))}
      </Group>

      <Paper withBorder radius="md" mb="lg">
        <Table>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Метрика</Table.Th>
              {channels.map((ch) => (
                <Table.Th key={ch.id}>
                  <Group gap="xs">
                    <BrandAvatar name={ch.name} size={24} />
                    <Text fw={600} size="sm">{ch.name}</Text>
                  </Group>
                </Table.Th>
              ))}
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {metrics.map((m) => {
              const bestIdx = getBest(m.key);
              return (
                <Table.Tr key={m.key}>
                  <Table.Td fw={600}>{m.label}</Table.Td>
                  {channels.map((ch, i) => (
                    <Table.Td key={ch.id}>
                      <Group gap="xs">
                        {m.format(getVal(ch, m.key))}
                        {i === bestIdx && (
                          <Badge size="xs" variant="filled" color="tggreen" leftSection={<IconTrophy size={10} />}>
                            лучший
                          </Badge>
                        )}
                      </Group>
                    </Table.Td>
                  ))}
                </Table.Tr>
              );
            })}
          </Table.Tbody>
        </Table>
      </Paper>

      <Paper withBorder radius="md" p="md">
        <Title order={3} mb="sm">
          AI-вердикт
        </Title>
        <Text size="sm" c="dimmed">
          Для рекламы лучше всего подходит канал «{channels[0].name}» — у него наивысшая вовлечённость
          и стабильный рост. Рекомендуемая стоимость размещения: от 15 000 ₽ за пост.
        </Text>
      </Paper>
    </Container>
  );
};

export default ComparePage;
