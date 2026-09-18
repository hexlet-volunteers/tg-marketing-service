import { BrandAvatar } from '@/components/ui/BrandAvatar';
import { InsightCard } from '@/components/ui/InsightCard';
import channelsCol from '@/shared/mocks/channelsCollection';
import { AreaChart } from '@mantine/charts';
import {
  Badge,
  Box,
  Button,
  Container,
  Group,
  Paper,
  ScrollArea,
  SegmentedControl,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from '@mantine/core';
import { IconCheck, IconDownload } from '@tabler/icons-react';
import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { ChannelData } from '@/types/channel';
import type { PostProps } from '@/types/post';
import { mockKpis, mockGrowthData } from '@/shared/mocks/channelKpis';
import { mockPosts } from '@/shared/mocks/posts';
import deltaFormatter from '@/utils/deltaFormatter'

interface DashBoardProps extends ChannelData, PostProps {}

const channel = channelsCol[0];

const DashboardPage: React.FC<DashBoardProps> = ({
  kpis = mockKpis, 
  growthData = mockGrowthData, 
  posts = mockPosts
}) => {
  const navigate = useNavigate();

  return (
    <Container>
      <Group justify="space-between" mb="md">
        <Group gap="md">
          <BrandAvatar name={channel.name} size={58} />
          <div>
            <Group gap={4}>
              <Title order={2}>{channel.name}</Title>
              {channel.verified && <IconCheck size={18} color="var(--mantine-color-tgblue-5)" />}
            </Group>
            <Box c="dimmed" fz="sm">
              {channel.username} · <Badge size="xs">{channel.category}</Badge>
            </Box>
          </div>
        </Group>
        <Group gap="sm">
          <SegmentedControl
            data={[
              { label: '7д', value: '7d' },
              { label: '30д', value: '30d' },
              { label: '90д', value: '90d' },
            ]}
            defaultValue="30d"
            size="sm"
          />
          <Button variant="outline" leftSection={<IconDownload size={16} />} size="sm">
            Экспорт
          </Button>
        </Group>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="md" mb="lg">
        {kpis.map((kpi) => (
          <Paper key={kpi.label} p="md" radius="md" withBorder>
            <Text size="xs" c="dimmed" mb={4}>
              {kpi.label}
            </Text>
            <Text fw={800} size="xl" mb={4}>
              {kpi.label === 'ER' ? `${kpi.value}%` : kpi.value.toLocaleString('ru-RU')}
            </Text>
            <Text
              size="xs"
              fw={600}
              c={kpi.positive ? 'tggreen' : 'tgred'}
            >
              {kpi.positive ? '▲' : '▼'} {deltaFormatter(kpi.delta, kpi.percentDelta)}
            </Text>
          </Paper>
        ))}
      </SimpleGrid>

      <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg" mb="lg">
        <Paper p="md" radius="md" withBorder>
          <Title order={3} mb="md">
            Рост подписчиков
          </Title>
          <AreaChart
            h={200}
            data={growthData}
            dataKey="date"
            series={[{ name: "подписчики", color: "tgblue.5" }]}
            curveType="monotone"
            withGradient
            withYAxis={false}
            withXAxis
            withTooltip
            withDots={false}
            strokeWidth={2}
          />
        </Paper>

        <Paper p="md" radius="md" withBorder>
          <Title order={3} mb="md">
            AI-советы
          </Title>
          <Stack gap="sm">
            <InsightCard color="green" label="Рекомендация">
              <Text size="xs" c="dimmed">
                Публикуйте посты в среду в 19:00 — ваша аудитория наиболее активна
              </Text>
            </InsightCard>
            <InsightCard color="blue" label="Тренд">
              <Text size="xs" c="dimmed">
                Вовлечённость выросла на 12% за последние 30 дней
              </Text>
            </InsightCard>
          </Stack>
          <Button

            color="tgblue"
            size="sm"
            mt="md"
            fullWidth
            onClick={() => navigate('/ai-cabinet')}
          >
            Открыть AI-кабинет
          </Button>
        </Paper>
      </SimpleGrid>

      <Paper p="sm" radius="md" withBorder>
        <Title order={3} mb="md">
          Последние посты
        </Title>
        <ScrollArea>
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Пост</Table.Th>
                <Table.Th ta="right">Просмотры</Table.Th>
                <Table.Th ta="right">Реакции</Table.Th>
                <Table.Th ta="right">Пересылки</Table.Th>
                <Table.Th ta="right">ER</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {posts.map((post) => (
                <Table.Tr
                  key={post.title}
                  styles={{ tr: { cursor: 'pointer' } }}
                  onClick={() => navigate('/post')}
                >
                  <Table.Td>{post.title}</Table.Td>
                  <Table.Td ta="right">{post.views.toLocaleString('ru-RU')}</Table.Td>
                  <Table.Td ta="right" c="tggreen">
                    {post.reactions}
                  </Table.Td>
                  <Table.Td ta="right">{post.forwards}</Table.Td>
                  <Table.Td ta="right">
                    <Badge
                      size="sm"

                      color={post.er >= 25 ? 'tggreen' : post.er >= 15 ? 'tgorange' : 'tgred'}
                    >
                      {post.er}%
                    </Badge>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </ScrollArea>
      </Paper>
    </Container>
  );
};

export default DashboardPage;
