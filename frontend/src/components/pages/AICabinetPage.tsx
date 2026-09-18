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
import { IconSend, IconSparkles } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import type { AiCabinetPageProps } from '@/types/aiCabinet';
import { mockCompetitors, mockHeatMapData } from '@/shared/mocks/aiPageData';
import { mockIdeas, mockInsights } from '@/utils/makeIdeasAndInsights';
import { formatNumber } from '@/utils/formatNumberShort';
import getHeatColor from '@/utils/getHeatColor';
import staticData from '@/shared/const/AICabinetPageStaticData';

const AICabinetPage = ({
  ideas = mockIdeas, 
  insights = mockInsights, 
  competitors= mockCompetitors, 
  heatMapData = mockHeatMapData,
}: AiCabinetPageProps) => {
  const { quickQuestions, daysOfWeek, hours} = staticData
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
                      <Badge size="xs" color="gray">
                          {`~${formatNumber(idea.scope)} охват`}
                      </Badge>
                      <Badge size="xs" color="gray">
                          {idea.date}
                      </Badge>
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
                      const val = heatMapData[day]?.[h] ?? 0;
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
                <InsightCard key={i} color={ins.color ?? 'blue'}>
                  <Group gap="xs">
                    <ins.icon size={14} color={`var(--mantine-color-tg${ins.color}-6)`} />
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
