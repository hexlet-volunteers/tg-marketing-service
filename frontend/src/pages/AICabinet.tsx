import { useMemo } from "react";
import {
 Container,
 Group,
 SimpleGrid,
 Stack,
 ThemeIcon,
 Title,
} from "@mantine/core";

import { IconSparkles } from "@tabler/icons-react";
import WhatToWriteAboutThisWeek from "@/components/AICabinet/WhatToWriteAboutThisWeek";
import Competitors from "@/components/AICabinet/Competitors";
import BestTimeToPost from "@/components/AICabinet/BestTimeToPost";
import WeeklyInsights from "@/components/AICabinet/WeeklyInsights";
import AskAIAboutChannel from "@/components/AICabinet/AskAIAboutChannel";

import type { AiCabinetPageProps } from "@/types/aiCabinet";
import { makeIdeas, makeInsights } from "@/utils/makeIdeasAndInsights";

import staticData from "@/shared/const/AICabinetPageStaticData";

/**
 * Страница «AI-кабинет автора».
 *
 * Отображает аналитический дашборд с инструментами на базе искусственного интеллекта:
 * - Секцию «О чём написать на этой неделе» с генерацией идей и прогнозом охватов (WhatToWriteAboutThisWeek).
 * - Тепловую карту активности аудитории по часам и дням недели для выбора времени публикаций (BestTimeToPost).
 * - Модуль мониторинга и сравнения метрик с каналами-конкурентами (Competitors).
 * - Блок еженедельных инсайтов, трендов и предупреждений с цветовой индикацией (WeeklyInsights).
 * - Интерактивный чат с AI-ассистентом для запросов по статистике канала с готовыми пресетами вопросов (AskAIAboutChannel).
 */
const AICabinet = ({
  /** Данные с идеями для постов, поступающие с бэкенда */
  ideas: ideasData,
  /** Данные еженедельных инсайтов и трендов */
  insights: insightsData,
  /** Список каналов-конкурентов для сравнительного анализа */
  competitors,
  /** Матрица активности пользователей для построения тепловой карты */
  heatMapData,
}: AiCabinetPageProps) => {
 const { quickQuestions, daysOfWeek, hours } = staticData;

 const ideas = useMemo(() => makeIdeas(ideasData), [ideasData]);
 const insights = useMemo(() => makeInsights(insightsData), [insightsData]);

 return (
  <Container>
   <Group gap="sm" mb="lg">
    <ThemeIcon
     size={36}
     variant="gradient"
     gradient={{ from: "tgblue", to: "tgpurple", deg: 135 }}
    >
     <IconSparkles size={20} />
    </ThemeIcon>
    <Title order={1}>AI-кабинет автора</Title>
   </Group>

   <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg">
    <Stack gap="lg">
     <WhatToWriteAboutThisWeek ideas={ideas} />

     <BestTimeToPost
      hours={hours}
      daysOfWeek={daysOfWeek}
      heatMapData={heatMapData}
     />
     
     <Competitors competitors={competitors} />
    </Stack>

    <Stack gap="lg">
     <WeeklyInsights insights={insights} />

     <AskAIAboutChannel quickQuestions={quickQuestions} />
    </Stack>
   </SimpleGrid>
  </Container>
 );
};

export default AICabinet;
