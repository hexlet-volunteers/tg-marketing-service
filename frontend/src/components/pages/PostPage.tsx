import React from 'react';
import {
  Badge,
  Button,
  Container,
  Group,
  Paper,
  Progress,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core';
import { InsightCard } from '@/components/ui/InsightCard';
import { IconArrowLeft } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

const reactions = [
  { emoji: '🔥', label: 'Огонь', percent: 42, count: 374 },
  { emoji: '❤️', label: 'Сердце', percent: 28, count: 250 },
  { emoji: '👍', label: 'Лайк', percent: 20, count: 178 },
  { emoji: '🤯', label: 'Восторг', percent: 10, count: 89 },
];

const PostPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container>
      <Button
        variant="subtle"
        color="tgblue"
        leftSection={<IconArrowLeft size={16} />}
        mb="md"
        onClick={() => navigate(-1)}
      >
        Назад к каналу
      </Button>

      <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg" mb="lg">
        <Paper withBorder p="lg" radius="md">
          <Title order={3} mb="md">
            Обзор нового iPhone 16 Pro
          </Title>
          <Text size="sm" c="dimmed" mb="md">
            Apple представила новый iPhone 16 Pro с чипом A18 Pro, титановым корпусом
            и улучшенной камерой. Главные изменения: новый дизайн, увеличенный экран
            и поддержка Apple Intelligence.
          </Text>
          <Group gap="xs" mb="md">
            <Text size="xs" c="dimmed">#apple</Text>
            <Text size="xs" c="dimmed">#iphone</Text>
            <Text size="xs" c="dimmed">#tech</Text>
          </Group>
          <Group gap="lg">
            <Text size="sm">👁 42.1K</Text>
            <Text size="sm">❤️ 890</Text>
            <Text size="sm">↗ 234</Text>
            <Text size="sm">💬 45</Text>
          </Group>
        </Paper>

        <Paper withBorder p="lg" radius="md">
          <Title order={3} mb="md">
            Разбивка реакций
          </Title>
          <Stack>
            {reactions.map((r) => (
              <div key={r.label}>
                <Group justify="space-between" mb={4}>
                  <Text size="sm">
                    {r.emoji} {r.label}
                  </Text>
                  <Text size="xs" c="dimmed">
                    {r.count} ({r.percent}%)
                  </Text>
                </Group>
                <Progress
                  value={r.percent}
                  size="sm"
                  radius="xl"
                  color="tgblue"
                />
              </div>
            ))}
          </Stack>
          <Group justify="space-between" mt="md" pt="md" bd="1px solid gray.2">
            <Text fw={600}>ER</Text>
            <Badge size="lg" color="tggreen">
              31.2%
            </Badge>
          </Group>
        </Paper>
      </SimpleGrid>

      <Title order={3} mb="md">
        AI-разбор
      </Title>
      <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
        <InsightCard color="green" label="Почему зашёл">
          <Text size="sm">
            Актуальная тема, эмоциональный заголовок, подробный разбор с
            скриншотами и сравнением с конкурентами.
          </Text>
        </InsightCard>
        <InsightCard color="orange" label="Что улучшить">
          <Text size="sm">
            Добавить больше данных и графиков, сократить воду в начале,
            добавить CTA в конце.
          </Text>
        </InsightCard>
        <InsightCard color="purple" label="Похожие идеи">
          <Text size="sm">
            Обзор Samsung S25 Ultra, Сравнение Android vs iOS 2026,
            Топ-5 аксессуаров для iPhone.
          </Text>
        </InsightCard>
      </SimpleGrid>
    </Container>
  );
};

export default PostPage;
