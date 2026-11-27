import React, { useState } from "react";
import {
 Stack,
 Group,
 Text,
 ActionIcon,
 Tooltip,
 Collapse,
 Transition,
} from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";
import { InsightCard } from "@/components/ui/InsightCard";
import { SectionCard } from "@/components/ui/SectionCard";
import { useWeeklyInsights } from "../model/useWeeklyInsights";
import { InsightsEmptyState } from "./InsightsEmptyState";
import type { WeeklyInsightsProps } from "@/types/aiCabinet";

/**
 * Блок «Инсайты недели» в AI-кабинете автора.
 *
 * Отображает:
 * - Список ключевых наблюдений, рекомендаций и трендов канала с цветовой индикацией и иконками.
 * - Интерактивное скрытие карточки по кнопке «Прочитано» (ActionIcon).
 * - Плавную двухуровневую анимацию удаления (Collapse для схлопывания высоты и Transition для fade-out эффекта).
 * - Состояния отсутствия данных (Empty State):
 *   1) Пользователь прочитал все инсайты на этой неделе.
 *   2) Инсайты ещё не сформированы/отсутствуют для нового канала.
 */
const WeeklyInsights: React.FC<WeeklyInsightsProps> = ({
 /** Исходный список инсайтов недели, поступающий через пропсы */
 insights: initialInsights = [],
}) => {
 const { list, deletingIds, handleDismiss, isEmpty, emptyStateVariant } =
  useWeeklyInsights(initialInsights);

 return (
  <SectionCard title="Инсайты недели">
   {isEmpty ? (
    /* Компонент с пустыми состояниями */
     <InsightsEmptyState
      variant={emptyStateVariant}
    />
    ) : (
    /* Список инсайтов с анимацией */
    <Stack gap="sm">
     {list.map((ins, itemId) => {
      const isDeleting = deletingIds.has(itemId);

      return (
       <Collapse
        key={itemId}
        expanded={!isDeleting}
        transitionDuration={250}
        transitionTimingFunction="ease"
       >
        <Transition mounted={!isDeleting} transition="fade" duration={200}>
         {(transitionStyles) => (
          <div style={transitionStyles}>
           <InsightCard color={ins.color ?? "blue"}>
            <Group justify="space-between" wrap="nowrap" w="100%">
             <Group gap="xs" flex={1}>
              <ins.icon
               size={16}
               color={`var(--mantine-color-tg${ins.color}-6)`}
              />
              <Text size="sm">{ins.text}</Text>
             </Group>

             <Tooltip label="Прочитано" withArrow position="left">
              <ActionIcon
               variant="subtle"
               color="gray"
               size="sm"
               onClick={() => handleDismiss(itemId)}
               aria-label="Отметить как прочитанное"
              >
               <IconCheck size={14} />
              </ActionIcon>
             </Tooltip>
            </Group>
           </InsightCard>
          </div>
         )}
        </Transition>
       </Collapse>
      );
     })}
    </Stack>
   )}
  </SectionCard>
 );
};

export default WeeklyInsights;
