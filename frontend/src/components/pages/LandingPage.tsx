import { InsightCard } from '@/components/ui/InsightCard';
import { TariffsBlock } from '@/widgets/TariffsBlock';
import {
  Badge,
  Box,
  Button,
  Container,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import {
  IconPresentationAnalytics,
  IconScale,
  IconSparkles,
} from '@tabler/icons-react';
import React from 'react';
import { useNavigate } from 'react-router-dom';

const stats = [
  { value: '2.4M', label: 'каналов в базе' },
  { value: '18 млрд', label: 'проанализ. постов' },
  { value: '120K', label: 'авторов' },
];

const features = [
  {
    icon: IconPresentationAnalytics,
    iconColor: 'var(--mantine-color-tgred-5)',
    iconBg: 'var(--mantine-color-tgred-0)',
    title: 'Статистика каналов',
    description: 'Подписчики, охваты, ER, индекс цитирования, прирост по дням и вовлечённость каждого поста.',
  },
  {
    icon: IconSparkles,
    iconColor: 'var(--mantine-color-tgpurple-5)',
    iconBg: 'var(--mantine-color-tgpurple-0)',
    title: 'AI: о чём писать',
    description: 'ИИ анализирует реакции и спрос, предлагает темы постов и лучшее время публикации для роста.',
  },
  {
    icon: IconScale,
    iconColor: 'var(--mantine-color-tggreen-6)',
    iconBg: 'var(--mantine-color-tggreen-0)',
    title: 'Сравнение и подбор',
    description: 'Сравнивайте каналы для закупки рекламы: цена контакта, накрутки, пересечение аудиторий.',
  },
];


const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box component="section" bg="white">
        <Container>
          <Group gap={60} align="center" wrap="wrap">
            <Stack flex="1.1 1 0" miw={320} gap="xl">
              <Badge
                variant="light"
                color="tgblue"
                size="lg"
                tt="none"
                fw={600}
                p="8px 16px"
                h="auto"
                fz="sm"
              >
                ✦ Аналитика Telegram с искусственным интеллектом
              </Badge>

              <Title order={1}>
                Знайте о своём канале
                <br />
                больше, чем вы сами
              </Title>

              <Text size="lg" c="dimmed" maw={500}>
                Статистика, охваты и реакции каждого поста — и AI, который подсказывает,{' '}
                <Text component="span" fw={700} c="primary.5">о чём писать дальше</Text>, чтобы расти быстрее.
              </Text>

              <Group gap="md">
                <Button
                  size="md"
                  onClick={() => navigate('/channels')}
                >
                  Добавить свой канал
                </Button>
                <Button
                  variant="default"
                  size="md"
                  onClick={() => navigate('/channels')}
                >
                  Каталог каналов
                </Button>
              </Group>

              <Group gap={48} mt="lg">
                {stats.map((stat) => (
                  <div key={stat.label}>
                    <Text fw={800} c="primary" lh={1.1} fz="32px">
                      {stat.value}
                    </Text>
                    <Text size="sm" c="dimmed" mt="xs">
                      {stat.label}
                    </Text>
                  </div>
                ))}
              </Group>
            </Stack>
            <Box flex="0.9 1 0" miw={320}>
              <Paper
                p="lg"
                radius="lg"
                bd="1px solid gray.3"
                shadow="heroCard"
                w="100%"
                maw={430}
                mx="auto"
              >
                <Group justify="space-between" mb="lg">
                  <Group gap={6}>
                    <ThemeIcon size={22} color="tgblue">
                      <IconSparkles size={12} />
                    </ThemeIcon>
                    <Text size="md" fw={700} c="primary">
                      AI-помощник редактора
                    </Text>
                  </Group>
                  <Text size="xs" c="gray.5">
                    @product_radar
                  </Text>
                </Group>

                <Stack>
                  <InsightCard color="green" label="РЕКОМЕНДАЦИЯ">
                    <Text size="xs" c="secondary" lh={1.4}>
                      Разборы кейсов дают <Text component="span" fw={700}>+34%</Text> реакций. Запланируйте один на этой неделе.
                    </Text>
                  </InsightCard>

                  <InsightCard color="blue" label="ТРЕНД">
                    <Text size="xs" c="secondary" lh={1.4}>
                      Тема <Text component="span" fw={700}>AI-агентов +180%</Text> за 30 дней — ниша ещё свободна.
                    </Text>
                  </InsightCard>

                  <InsightCard color="purple">
                    <Group gap={6} align="flex-start" wrap="nowrap">
                      <Text size="lg">🎯</Text>
                      <Box>
                        <Text size="sm" fw={700} c="primary" mb={2}>
                          «Как AI-агенты меняют онбординг»
                        </Text>
                        <Text size="xs" fw={600} c="tggreen.7">
                          Прогноз ~48K охват <Text component="span" fw={400} c="muted.5">• чт 19:30</Text>
                        </Text>
                      </Box>
                    </Group>
                  </InsightCard>
                </Stack>
              </Paper>
            </Box>
          </Group>
      </Container>

      <Box component="section" bg="gray.0" px="md" py={80}>
        <Box>
          <Stack gap={10} align="center" mb={50}>
            <Title order={2} ta="center">
              Всё, что умеет tgstats — и AI сверху
            </Title>
            <Text c="dimmed" ta="center" maw={600} fz="15px">
              Полная статистика каналов плюс рекомендательный слой на искусственном интеллекте
            </Text>
          </Stack>

          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="xl">
            {features.map((f) => (
              <Paper
                key={f.title}
                p="lg"
                radius="lg"
                bd="1px solid gray.3"
                shadow="featureCard"
              >
                <ThemeIcon
                  size={48}
                  radius="md"
                  bg={f.iconBg}
                  c={f.iconColor}
                  mb={20}
                >
                  <f.icon size={24} />
                </ThemeIcon>
                <Title order={3} mb="xs">
                  {f.title}
                </Title>
                <Text size="sm" c="dimmed">
                  {f.description}
                </Text>
              </Paper>
            ))}
          </SimpleGrid>
        </Box>
      </Box>

      <TariffsBlock />
    </Box>
  );
};

export default LandingPage;
