import React, { useState } from 'react';
import {
  Badge,
  Box,
  Button,
  Container,
  Grid,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Title,
  UnstyledButton,
  ScrollArea,
} from '@mantine/core';
import { InsightCard } from '@/components/ui/InsightCard';
import { SectionCard } from '@/components/ui/SectionCard';
import { IconBulb, IconSend, IconSparkles, IconTrendingUp, IconAlertTriangle, IconThumbUp } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';

const ideas = [
  {
    icon: IconBulb,
    title: 'Обзор новых функций Telegram',
    reason: 'Актуальная тема, растущий интерес',
    chips: ['~48K охват', 'чт 19:30'],
  },
  {
    icon: IconTrendingUp,
    title: 'Как монетизировать Telegram-канал',
    reason: 'Высокий спрос среди авторов',
    chips: ['~62K охват', 'ср 20:00'],
  },
  {
    icon: IconBulb,
    title: 'Топ-10 ботов для автоматизации',
    reason: 'Техническая аудитория ищет инструменты',
    chips: ['~35K охват', 'пт 18:00'],
  },
];

const insightColorMap: Record<string, 'green' | 'blue' | 'orange' | 'purple'> = {
  green: 'green',
  tgblue: 'blue',
  orange: 'orange',
};

const insights = [
  { type: 'recommendation', icon: IconBulb, color: 'green', bg: 'var(--mantine-color-tggreen-0)', text: 'Публикуйте посты в среду в 19:00 — пик активности' },
  { type: 'trend', icon: IconTrendingUp, color: 'tgblue', bg: 'var(--mantine-color-tgblue-0)', text: 'Вовлечённость выросла на 12% за месяц' },
  { type: 'warning', icon: IconAlertTriangle, color: 'orange', bg: 'var(--mantine-color-tgorange-0)', text: 'Частота публикаций упала — рекомендуем 3-4 поста в неделю' },
  { type: 'positive', icon: IconThumbUp, color: 'green', bg: 'var(--mantine-color-tggreen-0)', text: 'Новых подписчиков больше, чем отписок в 3.2 раза' },
];

const competitors = [
  { name: '@techreview', er: 9.2, delta: +1.1 },
  { name: '@droider', er: 7.8, delta: -0.5 },
  { name: '@habr', er: 6.1, delta: -2.2 },
];

const quickQuestions = [
  'Лучшее время для постов',
  'Как увеличить охват',
  'Тренды недели',
  'Анализ конкурентов',
];

const daysOfWeek = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
const hours = Array.from({ length: 24 }, (_, i) => i);

const heatmapData: Record<string, Record<number, number>> = {
  Пн: { 9: 3, 10: 5, 12: 7, 14: 6, 17: 8, 19: 9, 20: 10, 21: 8 },
  Вт: { 10: 4, 12: 6, 14: 5, 17: 7, 19: 8, 20: 9, 21: 7 },
  Ср: { 9: 4, 10: 6, 12: 8, 14: 7, 17: 9, 19: 10, 20: 10, 21: 9 },
  Чт: { 10: 5, 12: 7, 14: 6, 17: 8, 19: 9, 20: 8, 21: 7 },
  Пт: { 10: 4, 12: 6, 14: 5, 17: 6, 19: 7, 20: 8, 21: 6 },
  Сб: { 11: 3, 13: 4, 15: 5, 17: 5, 19: 6, 20: 7 },
  Вс: { 12: 3, 14: 4, 16: 5, 18: 5, 20: 6, 21: 5 },
};

const getHeatColor = (value: number) => {
  if (value === 0) return 'var(--mantine-color-gray-1)';
  if (value <= 3) return 'var(--mantine-color-tgblue-1)';
  if (value <= 5) return 'var(--mantine-color-tgblue-2)';
  if (value <= 7) return 'var(--mantine-color-tgblue-3)';
  if (value <= 9) return 'var(--mantine-color-tgblue-4)';
  return 'var(--mantine-color-tgblue-5)';
};

const AICabinetPage: React.FC = () => {
  const navigate = useNavigate();
  const [questionText, setQuestionText] = useState('');

  return (
    <Container>
      <Group gap="sm" mb="lg">
        <ThemeIcon size={36} variant="gradient" gradient={{ from: 'tgblue', to: 'tgpurple', deg: 135 }}>
          <IconSparkles size={20} />
        </ThemeIcon>
        <Title order={1}>AI-кабинет автора</Title>
      </Group>

      <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg">
        <Stack gap="lg">
          <SectionCard title="О чём написать на этой неделе">
            <Stack>
              {ideas.map((idea) => (
                <Paper key={idea.title} p="md">
                  <Group gap="sm" mb="xs">
                    <ThemeIcon size={28} color="tgpurple">
                      <idea.icon size={16} />
                    </ThemeIcon>
                    <Text fw={700} size="sm">
                      {idea.title}
                    </Text>
                  </Group>
                  <Text size="xs" c="dimmed" mb="xs">
                    {idea.reason}
                  </Text>
                  <Group justify="space-between">
                    <Group gap="xs">
                      {idea.chips.map((chip) => (
                        <Badge key={chip} size="xs" color="gray">
                          {chip}
                        </Badge>
                      ))}
                    </Group>
                    <Button
                      size="xs"
                      variant="filled"
                      color="tgpurple"
                      onClick={() => console.log('Write post:', idea.title)}
                    >
                      Написать
                    </Button>
                  </Group>
                </Paper>
              ))}
            </Stack>
          </SectionCard>

          <Paper p="lg">
            <Title order={3} mb="md">
              Конкуренты
            </Title>
            <Stack gap="sm">
              {competitors.map((c) => (
                <Group key={c.name} justify="space-between">
                  <Text size="sm" fw={500}>
                    {c.name}
                  </Text>
                  <Group gap="xs">
                    <Text size="xs" c="dimmed">
                      ER {c.er}%
                    </Text>
                    <Badge
                      size="xs"

                      color={c.delta >= 0 ? 'green' : 'red'}
                    >
                      {c.delta >= 0 ? '+' : ''}{c.delta}%
                    </Badge>
                  </Group>
                </Group>
              ))}
            </Stack>
            <Group mt="md" gap="sm">
              <Button size="xs" color="tgblue" onClick={() => console.log('Add competitor')}>
                + Добавить
              </Button>
              <Button
                size="xs"
                variant="subtle"
                color="tgblue"
                onClick={() => navigate('/compare')}
              >
                Сравнить все каналы
              </Button>
            </Group>
          </Paper>

          <SectionCard title="Лучшее время для публикаций">
            <Text size="xs" c="dimmed" mb="sm">
              Тепловая карта активности подписчиков по дням и часам
            </Text>
            <ScrollArea>
              <Grid columns={16} gap={2} maw={580}>
                <Grid.Col span={1} />
                {hours.filter((h) => h >= 8 && h <= 22).map((h) => (
                  <Grid.Col key={h} span={1}>
                    <Box ta="center" fz="10px" c="dimmed">
                      {h}
                    </Box>
                  </Grid.Col>
                ))}
                {daysOfWeek.map((day) => (
                  <React.Fragment key={day}>
                    <Grid.Col span={1}>
                      <Text fz="10px" c="dimmed">
                        {day}
                      </Text>
                    </Grid.Col>
                    {hours.filter((h) => h >= 8 && h <= 22).map((h) => {
                      const val = heatmapData[day]?.[h] ?? 0;
                      return (
                        <Grid.Col key={`${day}-${h}`} span={1}>
                          <Box
                            h={24}
                            bdrs={3}
                            bg={getHeatColor(val)}
                            title={`${day} ${h}:00 — ${val > 0 ? `${val}/10 активность` : 'нет данных'}`}
                            style={{ aspectRatio: '1' }}
                          />
                        </Grid.Col>
                      );
                    })}
                  </React.Fragment>
                ))}
              </Grid>
            </ScrollArea>
            <Group mt="sm" gap="xs">
              <Text size="xs" c="dimmed">Меньше</Text>
              {[0, 3, 5, 7, 9, 10].map((v) => (
                <Box key={v} w={12} h={12} bdrs={2} bg={getHeatColor(v)} />
              ))}
              <Text size="xs" c="dimmed">Больше</Text>
            </Group>
          </SectionCard>
        </Stack>

        <Stack gap="lg">
          <SectionCard title="Инсайты недели">
            <Stack gap="sm">
              {insights.map((ins, i) => (
                <InsightCard key={i} color={insightColorMap[ins.color] ?? 'blue'}>
                  <Group gap="xs">
                    <ins.icon size={14} color={`var(--mantine-color-${ins.color}-6)`} />
                    <Text size="sm">{ins.text}</Text>
                  </Group>
                </InsightCard>
              ))}
            </Stack>
          </SectionCard>

          <SectionCard title="Спросить AI о канале">
            <Group gap="xs" mb="md" wrap="wrap">
              {quickQuestions.map((q) => (
                <Button
                  key={q}
                  variant="light"
                  color="tgpurple"
                  onClick={() => setQuestionText(q)}
                >
                  {q}
                </Button>
              ))}
            </Group>
            <TextInput
              placeholder="Задайте вопрос..."
              value={questionText}
              onChange={(e) => setQuestionText(e.currentTarget.value)}
              rightSection={
                <UnstyledButton
                  onClick={() => {
                    if (questionText.trim()) {
                      setQuestionText('');
                    }
                  }}
                >
                  <IconSend
                    size={16}
                    color="var(--mantine-color-tgpurple-5)"
                  />
                </UnstyledButton>
              }
            />
          </SectionCard>
        </Stack>
      </SimpleGrid>
    </Container>
  );
};

export default AICabinetPage;
